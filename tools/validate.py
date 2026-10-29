"""Validate the curated, command-free collection; optionally check upstream text."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

import jsonschema
import yaml

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--remote", action="store_true")
args = parser.parse_args()
validator = jsonschema.Draft202012Validator(json.loads((root / "schema/pinakes.schema.json").read_text()))
visited, documents = set(), []
def walk(path, ancestors=()):
    assert path not in ancestors, f"Cycle: {path}"
    assert path.resolve().is_relative_to(root), path
    data = yaml.safe_load(path.read_text())
    validator.validate(data)
    assert data.get("description"), f"Missing source description: {path}"
    ids = [e["id"] for e in data["entries"]]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {path}"
    visited.add(path)
    for entry in data["entries"]:
        relative = PurePosixPath(entry["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        if entry["kind"] == "index":
            assert "repo" not in entry, "Keep discovery metadata in the collection"
            walk(root / entry["path"], ancestors + (path,))
        else:
            assert entry["kind"] == "doc", "Default collection contains no commands or merges"
            repo = entry["repo"]
            assert repo.get("submodules") is False
            url = urlparse(repo["url"])
            assert url.scheme == "https" and url.netloc == "github.com" and not url.username
            ref = repo.get("tag") or repo.get("branch") or repo.get("commit")
            assert ref, f"Choose an explicit ref: {entry['id']}"
            project = url.path.removesuffix(".git").strip("/")
            raw = "https://raw.githubusercontent.com/" + project + "/" + quote(ref, safe="/") + "/" + quote(entry["path"], safe="/")
            documents.append((entry["id"], raw))
walk(root / "pinakes.yaml")
assert visited == {root / "pinakes.yaml", *root.glob("indexes/*.yaml")}, "Unreachable index file"
if args.remote:
    def check(item):
        name, url = item
        with urlopen(Request(url, headers={"User-Agent": "AIexandria-index-validation"}), timeout=60) as response:
            body = response.read()
        assert body.strip(), name
        body.decode("utf-8")
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(check, documents))
print(f"Validated {len(visited)} index files and {len(documents)} document entries" + (" including upstream text" if args.remote else ""))
