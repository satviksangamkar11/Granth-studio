NOT SAFE

MAJOR — [director_test.py:115](/D:/aai%20work/granthstudio/scripts/source/director_test.py:115): Removing word boundaries lets source `राम आला` accept quote `रामा ला`; both normalize identically. This violates “exact words.” Preserve word boundaries while tolerating danda/punctuation spacing.

It cannot skip intervening letters or join non-adjacent words. The 300-character cap raises no MAJOR issue. Review is static; execution verification did not complete.