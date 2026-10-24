No BLOCKER or MAJOR remains in this narrow re-check of `570784b`. All four prior findings are closed by inspection: twelve negatives restored, shot shifts continuous, fixation-plane behavior documented and tested with known dots, and relative-path confinement applied before heavy imports.

- **MINOR — `scripts/animation/parallax.py:47–68`:** With identical camera endpoints and `ease: "hold"`, validation accepts parallax `start: -0.008, end: 0.008`, but every frame stays at `-0.008`. A following shot starting at the declared end therefore jumps. Reject unequal parallax endpoints for hold easing and add a regression test.

Tests were inspected, not executed; current test-pass evidence was not verified. No files modified, GPU, downloads, or network used.