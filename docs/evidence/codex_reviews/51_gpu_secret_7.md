PASS — prior receipt-token BLOCKER is closed. `write_receipt()` scrubs serialized JSON before writing either receipt file.

The new regression passed with filesystem writes mocked in memory. Mocked child output also verified redaction in page output, `notebook.log`, and tee files.

No remaining BLOCKER/MAJOR token-leakage findings in the two scripts’ notebook execution flow. No changes, network, or GPU use.