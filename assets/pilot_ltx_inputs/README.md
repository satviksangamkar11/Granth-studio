# LTX start images for the provisional 45-second pilot (scenes 1-3, style-anchor keyframes)

- `s{n}_style_anchor/04_ltx_start_768x512.png`: made from the owner-approved style-anchor keyframe `docs/evidence/sdxl_scenes/style_anchor_16d48472/scene{n}_keyframe.png`
  (SDXL output, 1216x832) with `ffmpeg -vf "scale=768:-2:flags=lanczos,crop=768:512"` (scale to 768 wide, centre-crop the height to 512; no aspect distortion).
  Scene 1 only: `ffmpeg -vf "scale=800:-2:flags=lanczos,crop=768:512:0:0"` (about 4 % tighter, anchored top-left) so that a small pseudo-signature SDXL drew in the
  bottom-right corner falls outside the frame (the frozen style forbids text and signatures). This is a reframing of the AI image, not a retouch: no pixel was painted.
  Owner decision 2026-10-24: "Use these three style-anchor keyframes for the pilot video and move on to the video stage."
- `prompt.txt`: written by the assistant to describe ONLY what each keyframe shows, plus gentle motion. A slow push-in is allowed instead of fought: the
  camera-lock experiment (docs/evidence/kaggle_dual_t4/gpu0_attempt6_camera_lock) showed that the tested camera-lock prompt did not prevent a push-in with LTX 0.9.8 on a T4, and the owner
  asked not to spend more GPU on static-camera prompts.
- Known content gaps (owner accepted the keyframes as they are; the scene 1 keyframe also carried a pseudo-signature, removed by the crop above): scene 1 shows an adult with a beard, not the young man of the text; scene 2 shows two seated
  townsmen and no young man; scene 3 shows two men eating, not the householder serving the young man. The prompts follow the images, not the planned actions.
- `negative_prompt.txt`: copied from assets/ltx_test_inputs/painted_courtyard_01 (recorded, not applied at cfg 1).
- PROVISIONAL TECHNICAL TEST inputs; not Granth canon; human review NOT_DONE.
