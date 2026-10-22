"""Render a camera-only study from one Torch: Dominions concept frame.

This intentionally animates the camera over a single generated image plane. It does
not animate the character, torch flame, or smoke. Output is an editorial motion
proof only, not an engine-ready game asset.
"""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/generated/torch-haze-proof/01_klein-bench_00041_.png"
OUT = ROOT / "evidence/torch-haze-motion/blender"
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
# Blender 5.2 in this installation exposes EEVEE under the legacy enum.
engine_ids = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_ids else "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 8
scene.render.fps = 8
scene.frame_start = 1
scene.frame_end = 24
scene.render.image_settings.color_depth = "8"
scene.render.filepath = str(OUT / "frame_")
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.display.shading.light = "STUDIO"
scene.render.film_transparent = False

# One textured card preserves the generated art faithfully; the World provides a
# dark margin during the camera's small crop/push. No shapes stand in for actors.
image = bpy.data.images.load(str(SOURCE), check_existing=False)
image.pack()
mesh = bpy.data.meshes.new("Generated concept image card")
mesh.from_pydata(
    [(-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)],
    [],
    [(0, 1, 2, 3)],
)
mesh.uv_layers.new(name="UVMap")
for loop_index, loop in enumerate(mesh.uv_layers.active.data):
    # from_pydata loop order matches the quad's four corners
    loop.uv = ((0, 0), (1, 0), (1, 1), (0, 1))[mesh.loops[loop_index].vertex_index]
card = bpy.data.objects.new("Haze concept (unmodified artwork)", mesh)
scene.collection.objects.link(card)

mat = bpy.data.materials.new("Unlit concept art")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()
tex = nodes.new("ShaderNodeTexImage")
tex.image = image
emission = nodes.new("ShaderNodeEmission")
output = nodes.new("ShaderNodeOutputMaterial")
mat.node_tree.links.new(tex.outputs["Color"], emission.inputs["Color"])
mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
card.data.materials.append(mat)

world = bpy.data.worlds.new("Obsidian margin")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.014, 0.020, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
scene.world = world

camera_data = bpy.data.cameras.new("Camera-only proof")
camera_data.type = "ORTHO"
camera = bpy.data.objects.new("Slow push across Haze concept", camera_data)
scene.collection.objects.link(camera)
camera.location = (0.0, 0.0, 2.0)
camera.rotation_euler = (0.0, 0.0, 0.0)
camera_data.ortho_scale = 1.12
scene.camera = camera

# Ease into the smoky center, then ease back. This is a gentle editorial move.
keys = [
    (1, 0.00, -0.005, 1.12),
    (12, 0.025, 0.015, 1.00),
    (24, 0.00, -0.005, 1.12),
]
for frame, x, y, scale in keys:
    camera.location.x = x
    camera.location.y = y
    camera_data.ortho_scale = scale
    camera.keyframe_insert(data_path="location", frame=frame, group="Camera drift")
    camera_data.keyframe_insert(data_path="ortho_scale", frame=frame, group="Camera drift")
# Blender 5 uses slotted Action storage; leave native interpolation as generated.

# Still renders can be opened individually and rebuilt into a preview GIF/video.
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    scene.render.filepath = str(OUT / f"frame_{frame:03d}.png")
    bpy.ops.render.render(write_still=True)

print(f"CAMERA_STUDY_SOURCE={SOURCE}")
print(f"CAMERA_STUDY_OUTPUT={OUT}")
print("CAMERA_STUDY_CLAIM=single-image camera drift only; no character or smoke animation")
