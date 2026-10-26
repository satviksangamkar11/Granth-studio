**SAFE** relative to the previously approved `builder_v3.py`. Read the full diff and surrounding code.

- No new file, process, network, introspection, text-block, handler, driver, output-node or saving access. Existing `ASSET()` image loading and output nodes are unchanged; `bpy.data.textures` usage is removed.
- Loops remain bounded under validated schema inputs: 144 frames, ≤8 segments, ≤8 layers per segment, ≤4 inks. Existing object cleanup iterates the finite scene collection.
- Best-effort Blender 5.0 check found no remaining removed API blocker. `CompositorNodeRGB` and `CompositorNodeSeparateColor` remain registered in official [5.0 source](https://github.com/blender/blender/tree/v5.0.0/source/blender/nodes/composite/nodes).

LF-normalised UTF-8 SHA-256 **matches**:
```text
c671ab16d9d0f0af671c76236f914bd704ef406c7b867f313943694c9853598b
```

Static review only; Blender execution and later 5.x compatibility were not verified.