**1 MAJOR remains. Do not authorize the pinned SDXL GPU run yet.**

- **MAJOR — `scripts/sdxl_first_test.py:190–193`: endpoint ownership remains incomplete.** `port_owner.py:19–25` matches ports across IPv4/IPv6 without matching addresses. A verified worker on `::1:P` can satisfy ownership for `http://127.0.0.1:P`, while another process serves that endpoint. `localhost` also permits address-family ambiguity. **Correction:** bind ownership proof to the exact destination address and port.

- **MINOR — `scripts/kaggle/sdxl_first_test.sh:77`: `find` failure is ignored.** Process-substitution failure does not propagate through `set -euo pipefail`; failed enumeration can allow startup to continue. **Correction:** explicitly check enumeration success. Double-dot detection, EOF handling and `exit 4` inside the loop are otherwise correct.

- **MINOR — `scripts/sdxl_first_test.py:189–192`: malformed URLs escape refusal handling.** An unmatched IPv6 bracket or port `65536` raises uncaught `ValueError`, preventing a `NOT_RUN` receipt. **Correction:** catch parsing errors and explicitly require ports `1..65535`.

The prior notebook MINOR is **closed**: RAM and idleness checks precede installation; their normal output parsing is sound. Userinfo is still accepted; IPv6 is rejected; port zero ultimately fails ownership.

Saved evidence passes 10 SDXL tests but excludes the new regression. Fresh probes could not complete here. No files modified, GPU used or downloads performed.