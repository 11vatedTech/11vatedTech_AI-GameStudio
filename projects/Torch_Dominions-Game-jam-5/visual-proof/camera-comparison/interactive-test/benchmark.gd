extends Node2D

const HERO_PATH := "res://hero-cutout-candidate.png"
const HERO_SHA256 := "32644a536e278461ad4dc13ec7e2a7cdd49d3389708671a13128e76fc8a344e5"
const PANEL_SIZE := Vector2(684, 395)
const PANEL_TOP := 150.0
const WORLD_RECT := Rect2(0, 0, 900, 520)
const HERO_START := Vector2(286, 435)
const ENEMY_START := Vector2(616, 435)
const HAZE_RADIUS := 210.0
const ENEMY_WINDUP := 0.82
const ATTACK_REACH := 140.0
const HAZE_DURATION := 4.0
const TEST_END_TIME := 2.10

var test_mode := ""
var hero_pos := HERO_START
var enemy_pos := ENEMY_START
var haze_center := Vector2.ZERO
var hero_health := 3
var enemy_health := 3
var enemy_state := "windup"
var enemy_timer := ENEMY_WINDUP
var haze_timer := 0.0
var haze_damage_timer := 0.0
var dodge_timer := 0.0
var dodge_cooldown := 0.0
var attack_timer := 0.0
var attack_cooldown := 0.0
var attack_hit_feedback_timer := 0.0
var attack_hits := 0
var dodge_count := 0
var enemy_strikes := 0
var enemy_hits_received := 0
var haze_casts := 0
var haze_zone_ticks := 0
var resets := 0
var scenario_events: Array[String] = []
var locomotion_distance := 0.0
var locomotion_reversal_count := 0
var last_automated_direction := 0.0
var automated := false
var automation_elapsed := 0.0
var simulation_time := 0.0
var ending_reported := false
var focus_mode := -1
var hero_texture: Texture2D
var hero_texture_size := Vector2.ZERO
var panels: Array[Dictionary] = []
var hud: Label

func _ready() -> void:
	DisplayServer.window_set_title("Torch: Dominions — Matched Camera Benchmark")
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()):
		if args[i] == "--test-mode" and i + 1 < args.size():
			test_mode = args[i + 1]
			break
	var image := Image.load_from_file(ProjectSettings.globalize_path(HERO_PATH))
	if image.is_empty():
		push_error("Missing static hero identity reference: %s" % HERO_PATH)
		return
	hero_texture_size = Vector2(image.get_width(), image.get_height())
	hero_texture = ImageTexture.create_from_image(image)
	_build_panels()
	hud = Label.new()
	hud.position = Vector2(30, 54)
	hud.size = Vector2(1380, 88)
	hud.add_theme_font_size_override("font_size", 17)
	hud.add_theme_color_override("font_color", Color("#e9e5dd"))
	hud.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	hud.add_theme_constant_override("shadow_offset_x", 2)
	hud.add_theme_constant_override("shadow_offset_y", 2)
	add_child(hud)
	_update_hud()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://captures"))
	if test_mode in ["side", "elevated", "paired"]:
		automated = true
		focus_mode = 0 if test_mode == "side" else (1 if test_mode == "elevated" else -1)
		_apply_focus()
		print("BENCHMARK_TEST_START mode=%s" % test_mode)
		_capture_async("initial")
	print("BENCHMARK_READY hero=%s sha256=%s paired_views=true" % [HERO_PATH, HERO_SHA256])
	queue_redraw()

func _build_panels() -> void:
	for i in range(2):
		var viewport := SubViewport.new()
		viewport.name = "ViewSideOn" if i == 0 else "ViewElevated"
		viewport.size = Vector2i(int(PANEL_SIZE.x), int(PANEL_SIZE.y))
		viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		viewport.transparent_bg = false
		viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_LINEAR
		add_child(viewport)
		var world := Node2D.new()
		world.name = "WorldSideOn" if i == 0 else "WorldElevated"
		world.set_script(load("res://benchmark_world.gd"))
		world.set("mode", i)
		world.set("hero_texture", hero_texture)
		world.set("hero_texture_size", hero_texture_size)
		viewport.add_child(world)
		var camera := Camera2D.new()
		camera.position = PANEL_SIZE * 0.5
		camera.zoom = Vector2.ONE
		world.add_child(camera)
		var view := TextureRect.new()
		view.name = "PanelSideOn" if i == 0 else "PanelElevated"
		view.position = Vector2(24 + i * (PANEL_SIZE.x + 24), PANEL_TOP)
		view.size = PANEL_SIZE
		view.texture = viewport.get_texture()
		view.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(view)
		panels.append({"world": world, "view": view, "mode": i})

func _input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo or automated:
		return
	if event.keycode == KEY_TAB:
		focus_mode = 1 - focus_mode if focus_mode >= 0 else 1
		_apply_focus()
	elif event.keycode == KEY_R:
		_reset_encounter()
	elif event.keycode == KEY_SHIFT and dodge_cooldown <= 0.0:
		var direction := _current_direction()
		_start_dodge(direction if direction.length_squared() > 0.0 else Vector2(-1, 0))
	elif event.keycode == KEY_SPACE and attack_cooldown <= 0.0:
		_start_attack()
	elif event.keycode == KEY_H and haze_timer <= 0.0:
		_start_haze()

func _current_direction() -> Vector2:
	var direction := Vector2.ZERO
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A): direction.x -= 1
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D): direction.x += 1
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W): direction.y -= 1
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S): direction.y += 1
	return direction.normalized() if direction.length() > 1.0 else direction

func _process(delta: float) -> void:
	simulation_time += delta
	if automated:
		_run_scenario(delta)
	else:
		_read_input(delta)
	_update_world(delta)
	_sync_worlds()
	_update_hud()
	queue_redraw()
	if automated and not ending_reported and automation_elapsed >= TEST_END_TIME:
		ending_reported = true
		var passed := _scenario_passed()
		var result := {
			"mode": test_mode, "passed": passed, "shared_state": true,
			"hero_health": hero_health, "enemy_health": enemy_health,
			"attack_hits": attack_hits, "dodges": dodge_count,
		"locomotion_distance": roundf(locomotion_distance * 100.0) / 100.0,			"locomotion_reversal_count": locomotion_reversal_count,
			"enemy_strikes": enemy_strikes, "enemy_hits_received": enemy_hits_received,

			"haze_casts": haze_casts, "haze_zone_ticks": haze_zone_ticks,
			"scenario_events": scenario_events, "world_rect": WORLD_RECT,
			"panel_size": PANEL_SIZE, "source_hero_sha256": HERO_SHA256
		}
		print("BENCHMARK_TEST_RESULT %s" % JSON.stringify(result))
		_capture_async("final")
		await get_tree().create_timer(0.12).timeout
		get_tree().quit(0 if passed else 1)

func _sync_worlds() -> void:
	for panel in panels:
		var world = panel.world
		world.set("hero_position", hero_pos)
		world.set("hero_velocity", _current_direction() * 250.0 if not automated and dodge_timer <= 0.0 else _automated_locomotion_velocity() if automated and automation_elapsed < 1.45 else Vector2.ZERO)

		world.set("enemy_position", enemy_pos)
		world.set("haze_center", haze_center)
		world.set("haze_active", haze_timer > 0)
		world.set("dodge_active", dodge_timer > 0)
		world.set("attack_active", attack_timer > 0.0)
		world.set("enemy_state", enemy_state)
		world.set("enemy_health", enemy_health)
		world.set("enemy_phase_age", _enemy_phase_duration() - enemy_timer)
		world.set("attack_age", 0.44 - attack_timer if attack_timer > 0.0 else -1.0)
		world.set("attack_hit_feedback", attack_hit_feedback_timer)
		world.set("dodge_timer", dodge_timer)
		world.set("hero_health", hero_health)
		world.set("haze_age", HAZE_DURATION - haze_timer if haze_timer > 0.0 else 0.0)
		world.set("simulation_time", simulation_time)

func _enemy_phase_duration() -> float:
	match enemy_state:
		"windup": return ENEMY_WINDUP
		"strike": return 0.16
		"recovery": return 0.55
	return ENEMY_WINDUP

func _read_input(delta: float) -> void:
	var direction := Vector2.ZERO
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A): direction.x -= 1
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D): direction.x += 1
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W): direction.y -= 1
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S): direction.y += 1
	if direction.length() > 1:
		direction = direction.normalized()
	if dodge_timer <= 0:
		hero_pos += direction * 250.0 * delta
		hero_pos.x = clampf(hero_pos.x, 45, WORLD_RECT.end.x - 45)
		hero_pos.y = clampf(hero_pos.y, 65, WORLD_RECT.end.y - 20)

func _run_scenario(delta: float) -> void:
	automation_elapsed += delta
	if automation_elapsed < 1.45:
		var movement := 250.0 if automation_elapsed < 0.90 else -190.0
		hero_pos.x = clampf(hero_pos.x + movement * delta, 45.0, WORLD_RECT.end.x - 45.0)
		locomotion_distance += absf(movement) * delta
		var movement_direction := signf(movement)
		if last_automated_direction != 0.0 and movement_direction != last_automated_direction:
			locomotion_reversal_count += 1
			if not scenario_events.has("locomotion_direction_reversed"):
				scenario_events.append("locomotion_direction_reversed")
		last_automated_direction = movement_direction
	if automation_elapsed >= 0.28 and not scenario_events.has("locomotion_capture"):
		scenario_events.append("locomotion_capture")
		_capture_async("locomotion")
	if automation_elapsed >= 0.60 and not scenario_events.has("torch_attack_started"):
		_start_attack()
		_capture_async("attack-active")
	if automation_elapsed >= 0.90 and not scenario_events.has("haze_cast_ground_zone_started"):
		_start_haze()
	if automation_elapsed >= 1.45 and not scenario_events.has("dodge_started_invulnerable"):
		enemy_state = "windup"
		enemy_timer = 0.20
		_start_dodge(Vector2(1.0, 0.0))

func _automated_locomotion_velocity() -> Vector2:
	return Vector2(250.0 if automation_elapsed < 0.90 else -190.0, 0.0)

func _update_world(delta: float) -> void:
	dodge_timer = maxf(0, dodge_timer - delta)
	dodge_cooldown = maxf(0, dodge_cooldown - delta)
	attack_timer = maxf(0, attack_timer - delta)
	attack_cooldown = maxf(0, attack_cooldown - delta)
	attack_hit_feedback_timer = maxf(0.0, attack_hit_feedback_timer - delta)
	if haze_timer > 0:
		haze_timer = maxf(0, haze_timer - delta)
		haze_damage_timer -= delta
		if haze_damage_timer <= 0:
			if enemy_pos.distance_to(haze_center) <= HAZE_RADIUS and enemy_health > 0:
				enemy_health = maxi(0, enemy_health - 1)
				haze_zone_ticks += 1
				scenario_events.append("haze_zone_enemy_damage_tick")
			haze_damage_timer = 0.70
	if enemy_state == "windup":
		enemy_timer -= delta
		if enemy_timer <= 0:
			enemy_state = "strike"
			enemy_timer = 0.16
			enemy_strikes += 1
			var in_lane := absf(hero_pos.x - enemy_pos.x) < 112 and absf(hero_pos.y - enemy_pos.y) < 82
			if in_lane and dodge_timer <= 0:
				hero_health = maxi(0, hero_health - 1)
				enemy_hits_received += 1
				scenario_events.append("hero_hit_by_enemy")
			elif in_lane:
				scenario_events.append("hero_invulnerable_during_strike")
	elif enemy_state == "strike":
		enemy_timer -= delta
		if enemy_timer <= 0:
			enemy_state = "recovery"
			enemy_timer = 0.55
	elif enemy_state == "recovery":
		enemy_timer -= delta
		if enemy_timer <= 0:
			enemy_state = "windup"
			enemy_timer = ENEMY_WINDUP
	if attack_timer > 0.12 and attack_timer < 0.30:
		var in_range := absf(hero_pos.x - enemy_pos.x) <= ATTACK_REACH and absf(hero_pos.y - enemy_pos.y) <= 100
		if in_range and enemy_health > 0:
			enemy_health -= 1
			attack_hits += 1
			attack_hit_feedback_timer = 0.10
			scenario_events.append("torch_attack_hit_enemy")
			attack_timer = 0

func _start_dodge(direction: Vector2) -> void:
	dodge_timer = 0.38
	dodge_cooldown = 0.72
	hero_pos += direction.normalized() * 105
	hero_pos.x = clampf(hero_pos.x, 45, WORLD_RECT.end.x - 45)
	hero_pos.y = clampf(hero_pos.y, 65, WORLD_RECT.end.y - 20)
	dodge_count += 1
	scenario_events.append("dodge_started_invulnerable")

func _start_attack() -> void:
	attack_timer = 0.44
	attack_cooldown = 0.78
	scenario_events.append("torch_attack_started")

func _start_haze() -> void:
	haze_center = hero_pos + (enemy_pos - hero_pos).normalized() * 90
	haze_timer = HAZE_DURATION
	haze_damage_timer = 0.55
	haze_casts += 1
	scenario_events.append("haze_cast_ground_zone_started")
	if automated:
		_capture_async("haze-active")

func _reset_encounter() -> void:
	hero_pos = HERO_START
	enemy_pos = ENEMY_START
	hero_health = 3
	enemy_health = 3
	enemy_state = "windup"
	enemy_timer = ENEMY_WINDUP
	haze_timer = 0
	haze_damage_timer = 0
	dodge_timer = 0
	dodge_cooldown = 0
	attack_timer = 0
	attack_cooldown = 0
	attack_hit_feedback_timer = 0.0
	resets += 1
	scenario_events.append("encounter_reset")
	automated = false
	automation_elapsed = 0
	simulation_time = 0.0
	ending_reported = false
	print("BENCHMARK_RESET count=%d" % resets)

func _scenario_passed() -> bool:
	return hero_texture != null and panels.size() == 2 and attack_hits >= 1 and dodge_count >= 1 and enemy_strikes >= 1 and enemy_hits_received == 0 and haze_casts >= 1 and haze_zone_ticks > 0 and hero_health == 3 and enemy_health < 3 and scenario_events.has("hero_invulnerable_during_strike") and locomotion_distance >= 250.0 and locomotion_reversal_count >= 1

func _update_hud() -> void:
	if hud == null:
		return
	var state_label := "WIND-UP %.1fs" % enemy_timer if enemy_state == "windup" else enemy_state.to_upper()
	var haze_label := "ACTIVE %.1fs" % haze_timer if haze_timer > 0 else "READY"
	hud.text = "MOVE WASD / ARROWS   DODGE SHIFT   TORCH SWEEP SPACE   PURPLE HAZE H   RESET R   FOCUS TAB\nHERO %d/3     ROGUE %s · %d/3     HAZE %s     CAMERA GATE: OPEN / DIAGNOSTIC" % [hero_health, state_label, enemy_health, haze_label]

func _apply_focus() -> void:
	for panel in panels:
		panel.view.modulate = Color(0.54, 0.60, 0.65, 1) if focus_mode >= 0 and int(panel.mode) != focus_mode else Color.WHITE
	queue_redraw()

func _capture_async(state_name: String) -> void:
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path("res://captures/%s-%s.png" % [test_mode, state_name])
	var result := get_viewport().get_texture().get_image().save_png(path)
	if result == OK:
		print("BENCHMARK_CAPTURE path=res://captures/%s-%s.png" % [test_mode, state_name])
	else:
		push_error("Failed to save screenshot: %s" % path)

func _draw() -> void:
	draw_string(ThemeDB.fallback_font, Vector2(28, 28), "TORCH: DOMINIONS  /  CAMERA GATE 02   ·   MATCHED INTERACTIVE ENCOUNTER", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#a65cff"))
	for i in range(2):
		var x := 24.0 + i * (PANEL_SIZE.x + 24.0)
		draw_rect(Rect2(Vector2(x - 1, PANEL_TOP - 1), PANEL_SIZE + Vector2(2, 2)), Color("#7c8790"), false, 2)
		draw_string(ThemeDB.fallback_font, Vector2(x + 8, PANEL_TOP - 14), "A SIDE-ON / CINEMATIC" if i == 0 else "B ELEVATED THREE-QUARTER", HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#f0d6ad"))
		draw_string(ThemeDB.fallback_font, Vector2(x + 8, PANEL_TOP + PANEL_SIZE.y + 20), "PLAYER ACTION + TELEGRAPH" if i == 0 else "ROUTE + ZONE FOOTPRINT", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#b9c7ce"))
	draw_string(ThemeDB.fallback_font, Vector2(28, 728), "TEMPORARY BLOCKOUT · Hero cutout is a static identity reference; gameplay state is not character animation.", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#c3bbb4"))
