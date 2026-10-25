# V5 preset library (schema v2, Builder v2)

Eleven reusable shot presets. Each file is a complete shot JSON for Builder v2 (`scripts/image_trials/v5_schema2.py`); asset names are ROLES (sky, mid, fg, char, face, ...)
that you map to real images (one find-and-replace per role). Use: copy the preset, set `shot_id`, rename the roles, validate with `v5_schema2.validate`, render with `v5_shots2.py`.
`index.json` lists each preset, the roles it needs and the simplest renderer that can produce it.

| Preset | Use | Needs | Simplest renderer |
|---|---|---|---|
| 01_establishing_shot | Wide place-setting dolly with sky/mid/fg and light | sky, mid, fx, fg | Blender v2 |
| 02_environmental_parallax | Lateral move through 4 depth layers | sky, far, mid, near | Blender v2 |
| 03_slow_cinematic_push | One image, slow push, nothing else | img | **motion.py** (CPU, 6 s for 144 frames) |
| 04_character_entrance | A figure walks in toward another | char, other | Blender v2 |
| 05_bowing_prayer | Tilt down onto the bow | pose | Blender v2 |
| 06_blessing_gesture | Push toward a raised hand (LIMITED, see results) | pose | Blender v2 |
| 07_character_reaction | Face close-up with breathing | face | Blender v2 |
| 08_emotional_closeup | Slower, closer push with soft halo | face | Blender v2 |
| 09_dialogue_composition | Two figures facing each other | left, right | Blender v2 |
| 10_object_hand_insert | Insert on hands/object | insert | Blender v2 |
| 11_scene_transition | Two scenes joined by a 6-frame pan bridge | scene_a, scene_b | Blender v2 |

Rules: keep dust, gloss and halos subtle (they serve the scene); no slow dissolves between full-body poses; add a new preset only when an approved shot needs it.
Renderer choice: `motion.py` for a single still with a simple move, `parallax.py` for a single painted still with a depth map, Blender v2 only when layers, breathing, sway, glow or transitions are needed.
