NOT SAFE

- **MAJOR — [draft_source.py:181](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:181):** EOF without completion, or `finish_reason="length"`, returns content as success. Reproduced offline. Require valid terminal completion; reject partial and whitespace-only content.
- **MAJOR — [draft_source.py:185](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:185):** `finish` and usage field names retain echoed secrets in `info`. Reproduced offline. Allowlist metadata and scrub all returned strings.
- **MAJOR — [draft_source.py:140](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:140):** Deadline is checked only after a complete line arrives. Continuous bytes without a newline can evade both the deadline and socket idle timeout. Enforce a monotonic deadline during bounded reads.
- **MAJOR — [draft_source.py:153](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:153):** SSE `{"choices":1}` raises uncaught `TypeError`, aborting the run. Reproduced offline. Validate the collection type and return a controlled failure.

Fixed URL, redirect refusal, key retirement/cooling and retry count look correct. Both tests pass in isolation; normal pytest execution was blocked by environment permissions.