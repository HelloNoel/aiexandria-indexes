# Initial collection evaluation

Measured on 2026-10-29 through the real AIexandria v0.3.0 MCP implementation.
The 80 fixed in-scope queries in tests/discovery-queries.json cover four queries
per topic. All selected the intended source in the first three results. Mean
response size was 1244 bytes, within the default five-result/8192-byte limits.
These curated queries are not an independent accuracy benchmark. To reproduce:

~~~sh
python tools/discovery.py --aiexandria /path/to/aiexandria
~~~

Discovery acquired only the metadata repository, never document-only upstreams.
A ten-topic subset passed its 40 in-scope queries. The twenty-topic catalog also
passed after adding ten experimental topic descriptions as distractors; those
metadata-only candidates are not shipped as usable indexes. Unrelated and
version-mismatched queries still need judgment: there is no general relevance
threshold or automatic version resolver.

All 160 selected files resolved and decoded as nonempty UTF-8 text. Real first
reads of four upstream repositories measured the following on one connection:

| Source | Cold read | New Git pack | Warm read |
| --- | --- | --- | --- |
| rust | 3.6 s | 14.8 MiB | 2.7 ms |
| uv | 41.8 s | 136.6 MiB | 3.3 ms |
| python | 20.5 s | 58.8 MiB | 2.7 ms |
| github-actions | 53.6 s | 156.0 MiB | 3.2 ms |

Times vary with network, checkout, and platform. Git pack size excludes working
files and is not an exact network-transfer measurement. Cold reads returned
pending errors where acquisition exceeded their foreground wait, then succeeded
on retry. A first use can take tens of seconds even though discovery is cheap.

Future evaluations should include independent user questions, mixed private/public
sources, version mismatches, and complete answer tasks alongside source selection.
