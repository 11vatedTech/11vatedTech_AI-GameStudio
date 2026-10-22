extends Node2D

const SIDE_PATH := "res://side-on.png"
const ELEVATED_PATH := "res://elevated.png"
const NOTE := "SOURCE CAMERA CONCEPTS · TWO DIFFERENT GENERATIONS · NOT A CONTROLLED PLAYTEST"
const VIEWPORT_SIZE := Vector2(1360.0, 800.0)
const PANEL_SIZE := Vector2(640.0, 640.0)
const PANEL_TOP := 92.0
const LEFT_X := 24.0
const GAP := 32.0

func _ready() -> void:
	_add_panel("A  /  SIDE-ON CINEMATIC", SIDE_PATH, LEFT_X)
	_add_panel("B  /  ELEVATED THREE-QUARTER", ELEVATED_PATH, LEFT_X + PANEL_SIZE.x + GAP)
	_add_label(NOTE, Vector2(24, 12), 15, Color(0.84, 0.79, 0.92))
	_add_label("Torch: Dominions  ·  Purple Haze camera gate  ·  source concepts at equal 640 px display size", Vector2(24, 752), 13, Color(0.79, 0.84, 0.85))
	print("TORCH_CAMERA_COMPARISON_LOADED side_on=%s elevated=%s viewport=%s" % [SIDE_PATH, ELEVATED_PATH, VIEWPORT_SIZE])

func _add_panel(title: String, resource_path: String, x: float) -> void:
	_add_label(title, Vector2(x, 56), 20, Color(0.95, 0.88, 0.73))
	var absolute_path := ProjectSettings.globalize_path(resource_path)
	var image := Image.load_from_file(absolute_path)
	if image.is_empty():
		push_error("Could not load camera comparison image: %s" % resource_path)
		return
	var sprite := Sprite2D.new()
	sprite.name = "SideOnSource" if resource_path == SIDE_PATH else "ElevatedSource"
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.centered = false
	sprite.position = Vector2(x, PANEL_TOP)
	var image_size := Vector2(float(image.get_width()), float(image.get_height()))
	sprite.scale = PANEL_SIZE / image_size
	add_child(sprite)
	print("TORCH_CAMERA_PANEL_LOADED path=%s native_size=%s position=%s displayed_size=%s" % [resource_path, image.get_size(), sprite.position, sprite.scale * image_size])

func _add_label(text: String, position: Vector2, size: int, color: Color) -> void:
	var label := Label.new()
	label.text = text
	label.position = position
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.96))
	label.add_theme_constant_override("shadow_offset_x", 2)
	label.add_theme_constant_override("shadow_offset_y", 2)
	add_child(label)
