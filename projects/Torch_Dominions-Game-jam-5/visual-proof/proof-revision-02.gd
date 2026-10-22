extends Node2D

const ART_PATH := "res://comfyui-output/revision-02/01_candidate_00001_.png"
const NOTE := "REVISION 02 · GENERATED STYLE CANDIDATE · NOT FINAL ART · NOT GAMEPLAY"

func _ready() -> void:
	var image := Image.load_from_file(ProjectSettings.globalize_path(ART_PATH))
	if image.is_empty():
		push_error("Could not load revision candidate: %s" % ART_PATH)
		return
	var texture := ImageTexture.create_from_image(image)
	var art := Sprite2D.new()
	art.name = "Revision02GeneratedSceneCandidate"
	art.texture = texture
	art.position = Vector2(512, 512)
	art.centered = true
	add_child(art)

	var status := Label.new()
	status.text = NOTE
	status.position = Vector2(20, 18)
	status.add_theme_font_size_override("font_size", 18)
	status.add_theme_color_override("font_color", Color(1.0, 0.88, 0.60))
	status.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.95))
	status.add_theme_constant_override("shadow_offset_x", 2)
	status.add_theme_constant_override("shadow_offset_y", 2)
	add_child(status)

	var info := Label.new()
	info.text = "Torch: Dominions / Cinderwild — FLUX.2 Klein 4B · revision 02 · 1024×1024"
	info.position = Vector2(20, 986)
	info.add_theme_font_size_override("font_size", 14)
	info.add_theme_color_override("font_color", Color(0.93, 0.93, 0.88))
	info.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.95))
	info.add_theme_constant_override("shadow_offset_x", 2)
	info.add_theme_constant_override("shadow_offset_y", 2)
	add_child(info)

	print("TORCH_VISUAL_PROOF_REVISION_LOADED path=%s size=%s" % [ART_PATH, image.get_size()])