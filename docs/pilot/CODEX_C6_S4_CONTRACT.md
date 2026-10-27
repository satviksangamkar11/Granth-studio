1. **High — multi-cut lines omit intermediate shots.** [director_test.py](/D:/aai%20work/granthstudio/scripts/source/director_test.py:542) reports only the final shot. For example, `S9-L4` starts in shot 3 and ends in shot 5, but the packet says it continues into shot 5 without identifying shot 4. List every shot crossed, so the director can maintain the staging across each cut.

2. **Medium — a line ending exactly at a cut is falsely marked as continuing.** [director_test.py](/D:/aai%20work/granthstudio/scripts/source/director_test.py:542) treats an end time of 6.00 seconds as entering shot 2. Use an exclusive end boundary and add a boundary test. The current timing plan has no such case.

3. **Medium — incomplete duration data is silently omitted or crashes.** [director_test.py](/D:/aai%20work/granthstudio/scripts/source/director_test.py:538) skips a timed line with no `seconds`, while a missing `mr` or `hi` key raises `KeyError`. The resulting packet can omit a beat despite calling the data measured. Reject incomplete data explicitly before constructing the prompt.

4. **Medium — the binding script can produce an empty, apparently valid binding.** [build_image_binding.py](/D:/aai%20work/granthstudio/scripts/flow/build_image_binding.py:8) accepts a nonexistent or empty source directory and writes `count: 0`. Fail if the directory is missing or no images match.

The current timing windows match the audio-plan durations. The two added tests were inspected, but not executed; the binding’s source images were not verified.