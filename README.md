# AIexandria indexes

A small, curated Pinakes collection for [AIexandria](https://github.com/HelloNoel/aiexandria).
It contains metadata and Git file references, not copies of upstream documentation.

AIexandria v0.3.0 uses the v1 branch by default when no registry is configured.
For a custom registry, add:

~~~yaml
indexes:
  public-docs:
    repo:
      url: https://github.com/HelloNoel/aiexandria-indexes.git
      branch: v1
      submodules: false
    path: pinakes.yaml
    refresh: 24h
~~~

## Coverage

Twenty English-language topics, each with eight selected documents:

| Group | Topics |
| --- | --- |
| Languages | Python 3.14, JavaScript.info, TypeScript, Go, Rust, Node.js 24 |
| Web | React, Vue 3, Django 5.2, FastAPI |
| Workflow | Git, GitHub Actions, npm, pytest, Python packaging, uv |
| Infrastructure and data | Docker, Kubernetes, Redis, DuckDB 1.4 |

Descriptions distinguish selected releases from rolling documentation. JavaScript.info
is a community tutorial; other sources use project documentation. This is a starter
selection, not comprehensive coverage or automatic package-version resolution.

All discovery metadata is in this repository. Discovery does not clone the 20
upstream repositories; reading or deep-searching a selected topic can acquire its
upstream. Some repositories are large. Raw source may contain front matter,
template directives, or both API variants. Search finds only these listed pages.

No search command or external ripgrep installation is required. Metadata edits
are reviewed on main and promoted to v1 after validation. Keep v1 compatible with
Pinakes v1 and AIexandria v0.3.0. Pin a full commit ID for a reproducible collection.
AIexandria's own help is maintained separately in the application repository.

## Contribute

Edit a topic YAML in indexes/, preserve IDs, and verify the selected ref and every
path. Explain the subject, version, and coverage using terms users search for.
Prefer useful source-specific descriptions over generic keyword repetition.

~~~sh
python -m pip install -r tools/requirements.txt
python tools/validate.py
python tools/validate.py --remote
python tools/discovery.py --aiexandria /path/to/aiexandria
~~~

Local validation checks the vendored Pinakes v1 schema, routes, unique IDs,
references, and the metadata-only discovery layout. Remote checks fetch each
listed text file and reject missing, empty, or non-UTF-8 content. They do not
replace a real clone/read test. The schema comes from HelloNoel/pinakes; update
it deliberately when the specification changes.

Before adding a topic, check discovery queries and first-use clone cost. Keep the
default collection focused; use an opt-in collection for broader specialist packs.
Upstream documentation retains its own copyright and license. Catalog metadata
and tooling are Apache-2.0 licensed; no upstream content is relicensed here.

See [initial evaluation results](EVALUATION.md) for source selection and measured cold-read costs.
