"""P1 proof scene for GranthStudio v4 (D-014): runs INSIDE Blender, headless:  blender -b --python p1_scene.py -- --image IMG --out DIR [--frames N] [--width W --height H] [--only-frame F --tag T]

A painted still on an unlit plane (the painting's own colours, no lighting change), a slow camera push-in, 24 fps. Every motion is a function of the frame number
(keyframes only, no random or clock input), so the same frame rendered twice must match. Renders the whole sequence, or ONE frame with --only-frame.
"""
import argparse
import sys
from pathlib import Path

import bpy


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--frames", type=int, default=240)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--only-frame", type=int, default=None)
    p.add_argument("--tag", default="frame")
    return p.parse_args(argv)


def build(a):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = a.width, a.height, 100
    scene.render.fps = 24
    scene.frame_start, scene.frame_end = 1, a.frames
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"                  # no filmic/AgX tone curve: the painting keeps its own colours
    scene.eevee.taa_render_samples = 16

    img = bpy.data.images.load(a.image)
    aspect = img.size[0] / img.size[1]
    bpy.ops.mesh.primitive_plane_add(size=1)
    plane = bpy.context.active_object
    plane.rotation_euler = (1.5707963, 0, 0)                          # stand the plane upright, facing the camera on the -Y side
    plane.scale = (aspect * 2.0, 2.0, 1.0)
    mat = bpy.data.materials.new("painting")
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Cubic"
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    plane.data.materials.append(mat)

    bpy.ops.object.camera_add(location=(0, -6.0, 0), rotation=(1.5707963, 0, 0))
    cam = bpy.context.active_object
    cam.data.lens = 50
    scene.camera = cam
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"   # works on layered actions too (Blender 5.x)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0.15, -5.0, 0.05)                                # slow push-in with a small drift, linear
    cam.keyframe_insert("location", frame=a.frames)
    scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0.9, 0.86, 0.75)
    return scene


def main():
    a = parse()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    scene = build(a)
    if a.only_frame is not None:
        scene.frame_set(a.only_frame)
        scene.render.filepath = str(out / f"{a.tag}_{a.only_frame:04d}.png")
        bpy.ops.render.render(write_still=True)
    else:
        scene.render.filepath = str(out / "f_")
        bpy.ops.render.render(animation=True)
    print("P1_SCENE_DONE", bpy.app.version_string)


main()
