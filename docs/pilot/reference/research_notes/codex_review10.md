NOT SAFE

- **MAJOR — [draft_source.py:146](<D:/aai work/granthstudio/scripts/source/draft_source.py:146>):** `readline(65536)` still blocks during newline-free trickling, preventing deadline checks. Local socket reproduction: 0.05-second deadline returned after 0.366 seconds, only upon EOF. Enforce the deadline during underlying reads and add a trickle regression.

Five streaming tests passed in isolation; normal pytest execution was blocked by environment permissions.