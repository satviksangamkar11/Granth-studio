**MAJOR — [scripts/sdxl_first_test.py:368](/D:/aai%20work/granthstudio/scripts/sdxl_first_test.py:368): character painting can become the style anchor.** Run `--style-anchor` without `--reference-set` (also possible with notebook defaults). `import_references()` registers the same painting as both Maharaj and the location (lines 167–169). The anchor selector accepts that location ID, so the character painting reaches the style adapter.

Required correction: require a distinct, approved location anchor in style-anchor mode; refuse the legacy dual-registration path. Add regression coverage for this invocation.

The remaining scoped checks look consistent by inspection, including hashing, default weight splitting, control graph, matching template copies, live probe wiring, switch validation, and documented pilot limitation.

GPU authorization remains blocked by this finding. No files changed; no tests, network, downloads, or GPU probes run.