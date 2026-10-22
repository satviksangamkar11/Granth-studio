"""Frozen 5.4 word-level alignment data: pure validation and the unvalidated-runner refusal. Synthetic only."""
from __future__ import annotations

import pytest

from granthstudio.errors import GateFailure, IntegrationUnavailable
from granthstudio.speech import align_words, validate_alignment

TEXT = "राम वन गए।"


def w(word, s, e):
    return {"word": word, "start_s": s, "end_s": e}


GOOD = [w("राम", 0.0, 0.4), w("वन", 0.4, 0.8), w("गए", 0.85, 1.2)]


def test_valid_alignment_passes_and_ends_may_touch_duration():
    assert validate_alignment(GOOD, TEXT, 1.2) == GOOD
    assert validate_alignment([w("राम", 0, 0.4), w("वन", 0.3995, 0.8), w("गए", 0.8, 1.2)], TEXT, 1.2005)  # <1 ms overlap


@pytest.mark.parametrize("words,duration", [
    (GOOD[:2], 2.0),                                           # missing word
    ([GOOD[1], GOOD[0], GOOD[2]], 2.0),                        # reordered
    ([w("राम", -0.1, 0.4), *GOOD[1:]], 2.0),                    # negative start
    ([w("राम", 0.5, 0.4), *GOOD[1:]], 2.0),                     # end before start
    ([GOOD[0], w("वन", 0.2, 0.8), GOOD[2]], 2.0),               # overlap beyond 1 ms
    ([*GOOD[:2], w("गए", 0.9, 1.5)], 1.2),                      # past the audio
    ("nope", 2.0),
])
def test_invalid_alignments_are_refused(words, duration):
    with pytest.raises(GateFailure):
        validate_alignment(words, TEXT, duration)


def test_unvalidated_aligner_is_not_validated():
    models = {"aligner": {"status": "unvalidated", "command": None, "model": None, "revision": None, "timeout_s": 1}}
    with pytest.raises(IntegrationUnavailable, match="NOT VALIDATED"):
        align_words(None, models, 1, "mr", "x")
