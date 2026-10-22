extends Node2D

const WORLD_RECT := Rect2(0.0, 0.0, 900.0, 520.0)
const HAZE_RADIUS := 210.0
const ATTACK_REACH := 140.0
const PANEL_SCALE := 684.0 / WORLD_RECT.size.x
const PANEL_HEIGHT := 395.0

var mode := 0
var hero_texture: Texture2D
var hero_texture_size := Vector2.ZERO
var hero_position := Vector2.ZERO
var hero_velocity := Vector2.ZERO
var enemy_position := Vector2.ZERO
var haze_center := Vector2.ZERO
var haze_active := false
var haze_age := 0.0
var dodge_active := false
var dodge_timer := 0.0
var attack_active := false
var attack_age := -1.0
var attack_hit_feedback := 0.0
var enemy_state := "windup"
var enemy_health := 3
var enemy_phase_age := 0.0
var hero_health := 3
var simulation_time := 0.0
const HERO_REFERENCE_SIZE := Vector2(870.0, 938.0)
const ACTOR_DRAW_HEIGHT := 150.0
const HAZE_PALETTE := [Color(0.54, 0.27, 0.76, 0.15), Color(0.67, 0.36, 0.88, 0.13), Color(0.82, 0.58, 0.97, 0.12)]

func _process(delta: float) -> void:
	simulation_time += delta
	queue_redraw()
	queue_redraw()

func _draw() -> void:
	# Both camera views share the same route geometry; only world-depth projection differs.
	draw_rect(Rect2(0, 0, 900 * PANEL_SCALE, 160 * PANEL_SCALE), Color("#39464e"), true)
	draw_rect(Rect2(0, 160 * PANEL_SCALE, 900 * PANEL_SCALE, 130 * PANEL_SCALE), Color("#303c41"), true)
	var floor_top := _project(Vector2(0, 290)).y
	var floor_bottom := _project(Vector2(0, 520)).y
	draw_rect(Rect2(0, floor_top, 900 * PANEL_SCALE, floor_bottom - floor_top), Color("#343a3b"), true)
	var ruin := Color("#596166")
	_draw_world_rect(Rect2(690, 86, 12, 146), ruin)
	_draw_world_rect(Rect2(840, 78, 12, 154), ruin)
	_draw_world_rect(Rect2(683, 79, 178, 19), ruin)
	_draw_world_rect(Rect2(714, 104, 18, 96), Color("#202b31"))
	_draw_world_rect(Rect2(786, 104, 18, 96), Color("#202b31"))
	for i in range(7):
		var x := 66.0 + float(i) * 21.0
		var y := 300.0 + float((i * 37) % 39)
		_draw_world_polygon(PackedVector2Array([Vector2(x, y), Vector2(x + 23, y - 13), Vector2(x + 42, y + 4), Vector2(x + 14, y + 18)]), Color("#50565a"))
	for i in range(6):
		var x := 762.0 + float(i) * 18.0
		var y := 324.0 + float((i * 29) % 35)
		_draw_world_polygon(PackedVector2Array([Vector2(x, y), Vector2(x + 18, y - 10), Vector2(x + 38, y + 5), Vector2(x + 8, y + 17)]), Color("#50565a"))
	var route := PackedVector2Array([Vector2(24, 368), Vector2(108, 324), Vector2(260, 330), Vector2(394, 348), Vector2(574, 326), Vector2(748, 343), Vector2(882, 390), Vector2(882, 478), Vector2(30, 478)])
	_draw_world_polygon(route, Color("#555754"))
	var edge_a := PackedVector2Array([Vector2(32, 392), Vector2(164, 366), Vector2(322, 381), Vector2(474, 393), Vector2(629, 369), Vector2(820, 390), Vector2(874, 420)])
	var edge_b := PackedVector2Array([Vector2(40, 450), Vector2(188, 430), Vector2(344, 445), Vector2(502, 452), Vector2(685, 429), Vector2(870, 451)])
	_draw_world_polyline(edge_a, Color(0.69, 0.65, 0.56, 0.55), 3.0)
	_draw_world_polyline(edge_b, Color(0.22, 0.28, 0.28, 0.72), 4.0)
	for point in [Vector2(108, 405), Vector2(335, 418), Vector2(745, 410), Vector2(819, 368)]:
		draw_circle(_project(point), 5.0 * PANEL_SCALE, Color("#e2a36b"))
		draw_circle(_project(point), 10.0 * PANEL_SCALE, Color(0.94, 0.45, 0.16, 0.16))
	_draw_world_polyline(PackedVector2Array([Vector2(20, 435), Vector2(880, 435)]), Color(0.79, 0.71, 0.60, 0.48), 2.0)
	_draw_route_landmarks()
	if haze_active:
		_draw_haze()
	_draw_enemy()
	_draw_dodge_vfx()
	_draw_hero()
	if enemy_state in ["windup", "strike"]:
		_draw_telegraph()
	_draw_actor_labels()

func _project(point: Vector2) -> Vector2:
	var projected := point
	if mode == 0:
		projected.y = 435.0 + (point.y - 435.0) * 0.18
	else:
		projected.y = WORLD_RECT.size.y * 0.5 + (point.y - WORLD_RECT.size.y * 0.5) * 0.70
	projected *= PANEL_SCALE
	if mode == 1:
		projected += Vector2(0.0, 28.0 * PANEL_SCALE)
	return projected

func _draw_world_rect(rect: Rect2, color: Color) -> void:
	var top_left := _project(rect.position)
	var height_factor := 0.18 if mode == 0 else 0.70
	var size := Vector2(rect.size.x * PANEL_SCALE, rect.size.y * height_factor * PANEL_SCALE)
	draw_rect(Rect2(top_left, size), color, true)

func _draw_world_polygon(points: PackedVector2Array, color: Color) -> void:
	var projected := PackedVector2Array()
	for point in points:
		projected.append(_project(point))
	draw_colored_polygon(projected, color)

func _draw_world_polyline(points: PackedVector2Array, color: Color, width: float) -> void:
	var projected := PackedVector2Array()
	for point in points:
		projected.append(_project(point))
	draw_polyline(projected, color, width * PANEL_SCALE, true)

func _actor_scale() -> float:
	return ACTOR_DRAW_HEIGHT / maxf(hero_texture_size.y, 1.0) * PANEL_SCALE

func _project_actor(root: Vector2, offset: Vector2) -> Vector2:
	# Compress actor placement by camera depth, but keep anatomical height upright and legible.
	return _project(root) + offset * PANEL_SCALE

func _draw_route_landmarks() -> void:
	# Directional ink marks keep the same route cues legible in the compressed side-on projection.
	for marker in range(5):
		var x := 170.0 + marker * 54.0
		var y := 390.0 + sin(float(marker) * 1.7 + simulation_time * 0.35) * 4.0
		var line := PackedVector2Array([Vector2(x, y), Vector2(x + 15.0, y - 2.0), Vector2(x + 27.0, y + 1.0)])
		_draw_world_polyline(line, Color(0.82, 0.68, 0.49, 0.33), 1.4)
	for point in [Vector2(108.0, 405.0), Vector2(335.0, 418.0), Vector2(745.0, 410.0), Vector2(819.0, 368.0)]:
		var glint := 0.5 + 0.5 * sin(simulation_time * 2.0 + point.x * 0.03)
		_draw_ellipse(_project(point), Vector2(8.0 + glint * 3.0, 4.0 + glint) * PANEL_SCALE, Color(0.98, 0.56, 0.25, 0.07 + glint * 0.05))

func _draw_haze() -> void:
	var age := maxf(haze_age, 0.0)
	var phase := clampf(age / 0.85, 0.0, 1.0)
	var arrival := Vector2(lerpf(hero_position.x, haze_center.x, phase), lerpf(hero_position.y - 50.0, haze_center.y, phase))
	var center := _project(haze_center)
	var vertical_factor := 0.18 if mode == 0 else 0.70
	var radius := Vector2(HAZE_RADIUS * PANEL_SCALE, HAZE_RADIUS * vertical_factor * PANEL_SCALE)
	var rise := smoothstep(0.0, 0.85, age)
	var dissolve := 1.0 - 0.36 * smoothstep(3.25, 4.0, age)
	var drift := age * 18.0 * PANEL_SCALE
	for band in range(3):
		var band_radius := radius * (0.42 + 0.18 * band)
		var offset := Vector2(sin(age * 2.0 + band) * 7.0, cos(age * 1.5 + band * 1.7) * 3.0) * PANEL_SCALE
		var tint: Color = HAZE_PALETTE[band]
		_draw_ellipse(center + offset + Vector2(drift * 0.22, 0), band_radius, Color(tint.r, tint.g, tint.b, tint.a * rise * dissolve))
	for i in range(7):
		var angle := TAU * float(i) / 7.0 + age * (0.20 if i % 2 == 0 else -0.14)
		var scallop := center + Vector2(cos(angle) * radius.x * 0.78 + drift, sin(angle) * radius.y * 0.58)
		var lobe_size := Vector2(30.0 + 5.0 * sin(age * 4.1 + i), maxf(7.0, radius.y * 0.16)) * PANEL_SCALE
		_draw_ellipse(scallop, lobe_size, Color(0.66, 0.38, 0.89, 0.18 * rise * dissolve))
	var ribbons := PackedVector2Array()
	for i in range(13):
		var t := float(i) / 12.0
		var p := arrival.lerp(haze_center, t)
		p.y += sin(t * TAU * 1.3 + age * 5.0) * 11.0
		ribbons.append(_project(p))
	draw_polyline(ribbons, Color(0.76, 0.51, 0.96, 0.48 * (1.0 - phase)), 2.0 * PANEL_SCALE, true)
	var source := _project(hero_position + Vector2(28.0, -84.0))
	var cast_flicker := 0.5 + 0.5 * sin(simulation_time * 10.0)
	_draw_ellipse(source, Vector2(9.0 + cast_flicker * 3.0, 14.0 + cast_flicker * 4.0) * PANEL_SCALE, Color(0.88, 0.64, 1.0, 0.26 * (1.0 - phase)))
	for curl in range(5):
		var base := haze_center + Vector2(float(curl - 2) * 28.0, -25.0 - curl * 6.0)
		base += Vector2(sin(simulation_time * 2.7 + curl) * 9.0, cos(simulation_time * 3.1 + curl) * 4.0)
		var points := PackedVector2Array([base, base + Vector2(10.0, -12.0 + curl), base + Vector2(17.0 + sin(simulation_time * 4.0 + curl) * 5.0, 0.0)])
		_draw_world_polyline(points, Color(0.78, 0.55, 0.96, 0.30 * (1.0 - smoothstep(0.0, 4.0, age))), 2.2)
	var remaining := clampf(4.0 - age, 0.0, 4.0) / 4.0
	var meter := _project(haze_center + Vector2(-58.0, -73.0))
	draw_rect(Rect2(meter, Vector2(116.0, 3.0) * PANEL_SCALE), Color(0.05, 0.04, 0.09, 0.78), true)
	draw_rect(Rect2(meter, Vector2(116.0 * remaining, 3.0) * PANEL_SCALE), Color("#bb82ed"), true)

func _draw_telegraph() -> void:
	var facing := -1.0 if hero_position.x < enemy_position.x else 1.0
	if enemy_state == "windup":
		var phase := clampf(enemy_phase_age / 0.82, 0.0, 1.0)
		var pulse := 0.5 + 0.5 * sin(simulation_time * 8.0)
		var start := _project(enemy_position + Vector2(facing * 28.0, -88.0))
		var end := _project(enemy_position + Vector2(facing * 132.0, -95.0 + 10.0 * phase))
		draw_line(start, end, Color(1.0, 0.48, 0.18, 0.22 + phase * 0.34), 4.0 * PANEL_SCALE, true)
		for i in range(3):
			var t := 0.25 + float(i) * 0.25
			var point := start.lerp(end, t)
			var width := (6.0 + 3.0 * pulse + phase * 3.0) * PANEL_SCALE
			draw_line(point - Vector2(facing * width, width * 0.75), point, Color(1.0, 0.75, 0.36, 0.40 + phase * 0.45), 2.0 * PANEL_SCALE, true)
			draw_line(point + Vector2(facing * width, width * 0.75), point, Color(1.0, 0.75, 0.36, 0.40 + phase * 0.45), 2.0 * PANEL_SCALE, true)
		var threat := _project(enemy_position + Vector2(facing * 92.0, -92.0))
		_draw_ellipse(threat, Vector2(12.0, 10.0) * PANEL_SCALE, Color(1.0, 0.68, 0.28, 0.10 + 0.12 * pulse))
	else:
		var origin := _project(enemy_position + Vector2(facing * 25.0, -93.0))
		var tip := _project(enemy_position + Vector2(facing * 122.0, -123.0))
		draw_line(origin, tip, Color(1.0, 0.40, 0.20, 0.78), 5.0 * PANEL_SCALE, true)
		for i in range(6):
			var angle := simulation_time * 5.0 + TAU * float(i) / 6.0
			var ray := Vector2(cos(angle), sin(angle))
			draw_line(tip + ray * 3.0 * PANEL_SCALE, tip + ray * (10.0 + 7.0 * sin(enemy_phase_age * 30.0)) * PANEL_SCALE, Color(1.0, 0.82, 0.50, 0.85), 1.8 * PANEL_SCALE, true)

func _draw_text_plate(position: Vector2, text: String, color: Color, background: Color) -> void:
	var font_size := 10
	var text_size := ThemeDB.fallback_font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)
	var safe := Vector2(clampf(position.x, 4.0, 900.0 * PANEL_SCALE - text_size.x - 10.0), clampf(position.y, 14.0, PANEL_HEIGHT - 18.0))
	draw_rect(Rect2(safe - Vector2(3.0, 11.0), text_size + Vector2(7.0, 14.0)), background, true)
	draw_string(ThemeDB.fallback_font, safe, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)

func _draw_actor_labels() -> void:
	# Nameplates use state-aware screen-space clearance so converging actors never stack labels.
	var hero_floor := _project(hero_position)
	var enemy_floor := _project(enemy_position)
	var hero_left := hero_position.x <= enemy_position.x
	var hero_text := "WAYFARER %d/3" % hero_health
	var hero_width := ThemeDB.fallback_font.get_string_size(hero_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
	var hero_x := hero_floor.x - hero_width - 8.0 if hero_left else hero_floor.x + 8.0
	_draw_text_plate(Vector2(hero_x, hero_floor.y - 130.0 * PANEL_SCALE), hero_text, Color("#d4f4e9"), Color(0.035, 0.08, 0.09, 0.92))
	if enemy_health > 0:
		var enemy_text := "ASH ROGUE %d/3" % enemy_health
		var enemy_width := ThemeDB.fallback_font.get_string_size(enemy_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
		var enemy_x := enemy_floor.x + 8.0 if hero_left else enemy_floor.x - enemy_width - 8.0
		var enemy_label := Vector2(enemy_x, enemy_floor.y - 153.0 * PANEL_SCALE)
		_draw_text_plate(enemy_label, enemy_text, Color("#f4dfc7"), Color(0.09, 0.05, 0.05, 0.92))
		if enemy_state == "windup":
			_draw_text_plate(enemy_label + Vector2(0.0, -21.0), "WIND-UP %.1fs" % maxf(0.0, 0.82 - enemy_phase_age), Color("#ffe39c"), Color(0.13, 0.08, 0.025, 0.92))
		elif enemy_state == "strike":
			_draw_text_plate(enemy_label + Vector2(0.0, -21.0), "STRIKE", Color("#ff9a7f"), Color(0.15, 0.035, 0.025, 0.94))
	if haze_active:
		var haze_screen := _project(haze_center)
		var vertical_factor := 0.18 if mode == 0 else 0.70
		_draw_text_plate(haze_screen + Vector2(-35.0 * PANEL_SCALE, HAZE_RADIUS * vertical_factor * 0.58 * PANEL_SCALE + 15.0), "PURPLE HAZE", Color("#ecd8ff"), Color(0.08, 0.035, 0.13, 0.92))
	if attack_active and attack_age >= 0.0:
		_draw_text_plate(hero_floor + Vector2(-27.0 * PANEL_SCALE, -150.0 * PANEL_SCALE), "SWEEP %.2fs" % attack_age, Color("#ffd293"), Color(0.12, 0.06, 0.02, 0.92))

func _draw_hero() -> void:
	var floor := _project(hero_position)
	var actor_scale := _actor_scale()
	var height := hero_texture_size.y * actor_scale
	var width := hero_texture_size.x * actor_scale
	var direction := -1.0 if hero_position.x < enemy_position.x else 1.0
	var idle_center := floor - Vector2(0.0, height * 0.48)
	var age := clampf(attack_age, 0.0, 0.44)
	var anticipation := 1.0 - smoothstep(0.0, 0.16, age) if attack_active else 0.0
	var strike := smoothstep(0.14, 0.22, age) * (1.0 - smoothstep(0.29, 0.38, age)) if attack_active else 0.0
	var follow_through := smoothstep(0.25, 0.36, age) * (1.0 - smoothstep(0.38, 0.44, age)) if attack_active else 0.0
	var recovery := smoothstep(0.34, 0.44, age) if attack_active else 0.0
	# Dodge phases: compression -> committed directional burst -> grounded recovery.
	var dodge_phase := clampf((0.38 - dodge_timer) / 0.38, 0.0, 1.0) if dodge_active else 0.0
	var compress := 1.0 - smoothstep(0.04, 0.17, dodge_phase)
	var extend := smoothstep(0.13, 0.31, dodge_phase) * (1.0 - smoothstep(0.72, 1.0, dodge_phase))
	var settle := smoothstep(0.73, 1.0, dodge_phase)
	var base := Vector2(0.0, -81.0)
	var sway := 2.0 * sin(simulation_time * 2.2)
	var hip := base + Vector2(-3.0 * direction * anticipation + 3.0 * direction * strike, compress * 8.0 - strike * 3.0 + settle * 5.0 + sway)
	var torso := base + Vector2(-7.0 * direction * anticipation + 7.0 * direction * strike - 6.0 * direction * extend, -29.0 + compress * 7.0 + strike * 2.0 - extend * 5.0 + settle * 2.0 + sway * 0.4)
	var head := base + Vector2(-10.0 * direction * anticipation + 6.0 * direction * strike - 8.0 * direction * extend, -73.0 + compress * 6.0 + strike * 2.0 - extend * 4.0 + settle + sway * 0.25)
	var foot_a := base + Vector2(-19.0 + 4.0 * anticipation - 5.0 * extend, 0.0)
	var foot_b := base + Vector2(19.0 + 7.0 * strike + 5.0 * extend, 0.0)
	var knee_a := foot_a.lerp(hip + Vector2(-7.0, -4.0), 0.52) + Vector2(-4.0 * anticipation, -10.0 * compress + 5.0 * extend)
	var knee_b := foot_b.lerp(hip + Vector2(7.0, -4.0), 0.50) + Vector2(4.0 * strike, -5.0 * compress - 4.0 * extend)
	var shoulder_a := torso + Vector2(-10.0 * direction, 6.0)
	var shoulder_b := torso + Vector2(10.0 * direction, 6.0)
	var hand_a := torso + Vector2(-direction * (23.0 + 8.0 * anticipation + 6.0 * extend), 5.0 - 6.0 * compress)
	var hand_b := torso + Vector2(direction * (17.0 + 15.0 * anticipation + 31.0 * strike - 12.0 * recovery + 7.0 * extend), 3.0 - 4.0 * anticipation - 12.0 * strike + 5.0 * recovery)
	var head_point := _project_actor(hero_position, head)
	var torso_point := _project_actor(hero_position, torso)
	var hip_point := _project_actor(hero_position, hip)
	var foot_a_point := _project_actor(hero_position, foot_a)
	var foot_b_point := _project_actor(hero_position, foot_b)
	var knee_a_point := _project_actor(hero_position, knee_a)
	var knee_b_point := _project_actor(hero_position, knee_b)
	var shoulder_a_point := _project_actor(hero_position, shoulder_a)
	var shoulder_b_point := _project_actor(hero_position, shoulder_b)
	var hand_a_point := _project_actor(hero_position, hand_a)
	var hand_b_point := _project_actor(hero_position, hand_b)
	var action_active := attack_active or dodge_active
	if dodge_active:
		_draw_hero_action_rig(hero_position, direction, age, 0.0, 0.0, 0.0, extend, settle, 0.0, 0.0)
		var motion_trail := PackedVector2Array([_project(hero_position + Vector2(direction * 30.0, -65.0)), _project(hero_position + Vector2(direction * 14.0, -83.0)), _project(hero_position + Vector2(-direction * 7.0, -100.0))])
		draw_polyline(motion_trail, Color(0.43, 0.91, 0.96, 0.24 + 0.2 * extend), 7.0 * PANEL_SCALE, true)
		return
	if not action_active and hero_velocity.length_squared() > 1.0:
		var walk_direction := signf(hero_velocity.x) if absf(hero_velocity.x) > 1.0 else direction
		var locomotion := clampf(hero_velocity.length() / 250.0, 0.0, 1.0)
		_draw_hero_action_rig(hero_position, walk_direction, age, 0.0, 0.0, 0.0, 0.0, 0.0, locomotion, simulation_time * 9.0)
		return
	if not action_active:
		draw_set_transform(idle_center, 0.0, Vector2.ONE)
		draw_texture_rect(hero_texture, Rect2(Vector2(-width * 0.5, -height * 0.48), Vector2(width, height)), false)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		return
	if attack_active:
		_draw_hero_action_rig(hero_position, direction, age, anticipation, strike, follow_through, compress, recovery, 0.0, 0.0)
		return
	# Dynamic, anchored body pose replaces rather than stacks over the fused neutral cutout.
	# Feet plant against the same world anchor through attack anticipation/contact/recovery.
	_draw_world_polyline(PackedVector2Array([foot_a_point, knee_a_point, hip_point]), Color("#29252d"), 11.0)
	_draw_world_polyline(PackedVector2Array([foot_b_point, knee_b_point, hip_point]), Color("#302832"), 11.0)
	_draw_world_polyline(PackedVector2Array([foot_a_point + Vector2(-5.0, 0.0) * PANEL_SCALE, foot_a_point + Vector2(7.0, 0.0) * PANEL_SCALE]), Color("#5c3d35"), 5.0)
	_draw_world_polyline(PackedVector2Array([foot_b_point + Vector2(-5.0, 0.0) * PANEL_SCALE, foot_b_point + Vector2(7.0, 0.0) * PANEL_SCALE]), Color("#5c3d35"), 5.0)
	_draw_ellipse(hip_point, Vector2(12.0, 8.0) * PANEL_SCALE, Color("#44343b"))
	_draw_world_polyline(PackedVector2Array([hip_point, torso_point]), Color("#273137"), 15.0)
	_draw_ellipse(torso_point, Vector2(12.0, 16.0) * PANEL_SCALE, Color("#394b52"))
	var mantle_tail := torso_point + Vector2(-direction * (31.0 + 14.0 * strike + 8.0 * follow_through + 8.0 * extend), 26.0 + sin(simulation_time * 7.0 + age * 10.0) * (3.0 + 4.0 * strike)) * PANEL_SCALE
	var mantle := PackedVector2Array([torso_point + Vector2(-9.0 * direction, -7.0) * PANEL_SCALE, torso_point + Vector2(-22.0 * direction, 5.0) * PANEL_SCALE, mantle_tail, torso_point + Vector2(1.0 * direction, 13.0) * PANEL_SCALE])
	draw_colored_polygon(mantle, Color(0.10, 0.36, 0.37, 0.94))
	draw_polyline(PackedVector2Array([mantle[1], mantle[2]]), Color("#75b9aa"), 1.6 * PANEL_SCALE, true)
	_draw_capsule(shoulder_a_point, hand_a_point, 5.5 * PANEL_SCALE, Color("#314248"))
	_draw_capsule(shoulder_b_point, hand_b_point, 6.5 * PANEL_SCALE, Color("#32444b"))
	_draw_ellipse(hand_a_point, Vector2(4.5, 4.5) * PANEL_SCALE, Color("#ad795d"))
	_draw_ellipse(hand_b_point, Vector2(5.0, 5.0) * PANEL_SCALE, Color("#bf8965"))
	_draw_ellipse(head_point, Vector2(7.5, 9.0) * PANEL_SCALE, Color("#d0a17d"))
	_draw_ellipse(head_point + Vector2(direction * 1.0, -4.0) * PANEL_SCALE, Vector2(8.0, 3.5) * PANEL_SCALE, Color("#542e38"))
	var braid := PackedVector2Array([head_point + Vector2(-5.0 * direction, 0.0) * PANEL_SCALE, head_point + Vector2(-16.0 * direction, 4.0) * PANEL_SCALE, head_point + Vector2(-27.0 * direction, 10.0 + sin(simulation_time * 11.0 + age * 14.0) * 4.0) * PANEL_SCALE, head_point + Vector2(-32.0 * direction, 15.0 + sin(simulation_time * 11.0 + age * 14.0 + 0.8) * 4.0) * PANEL_SCALE])
	draw_polyline(braid, Color("#542e38"), 3.0 * PANEL_SCALE, true)
	draw_polyline(braid.slice(1, 4), Color("#94616b"), 1.0 * PANEL_SCALE, true)
	var lantern := hand_b_point
	var handle := lantern + Vector2(direction * 8.0, 2.0) * PANEL_SCALE
	var lantern_tip := handle + Vector2(direction * (52.0 + 30.0 * strike - 10.0 * recovery - 8.0 * settle), -22.0 + 11.0 * follow_through + 5.0 * extend) * PANEL_SCALE
	var sweep_origin := _project(hero_position + torso + Vector2(direction * 7.0, 5.0))
	_draw_capsule(hand_a_point, handle, 4.0 * PANEL_SCALE, Color("#bd895f"))
	draw_line(handle, lantern_tip, Color("#382b24"), 5.5 * PANEL_SCALE, true)
	draw_line(handle, handle.lerp(lantern_tip, 0.44), Color("#9c714b"), 1.8 * PANEL_SCALE, true)
	_draw_ellipse(lantern_tip, Vector2(8.0, 9.0) * PANEL_SCALE, Color("#dfad5d"))
	_draw_flame(lantern_tip, (8.0 + 7.0 * strike) * PANEL_SCALE, simulation_time * 10.0 + age * 8.0, Color("#ffc970"))
	if anticipation > 0.02:
		var wind_start := handle + Vector2(-direction * 17.0, -4.0) * PANEL_SCALE
		var wind_end := wind_start + Vector2(direction * 28.0, 5.0) * PANEL_SCALE
		draw_line(wind_start, wind_end, Color(1.0, 0.76, 0.38, 0.30 + anticipation * 0.48), 2.6 * PANEL_SCALE, true)
	if strike > 0.02:
		var sweep_end := lantern_tip + Vector2(direction * (21.0 + 26.0 * strike), -16.0 * strike) * PANEL_SCALE
		var sweep_path := PackedVector2Array([sweep_origin, sweep_origin.lerp(sweep_end, 0.33) + Vector2(0.0, -13.0) * PANEL_SCALE, sweep_origin.lerp(sweep_end, 0.70) + Vector2(0.0, -7.0) * PANEL_SCALE, sweep_end])
		draw_polyline(sweep_path, Color(1.0, 0.72, 0.31, 0.84 * strike), 5.0 * PANEL_SCALE, true)
		_draw_flame(sweep_end, (8.0 + 8.0 * strike) * PANEL_SCALE, simulation_time * 12.0 + age * 10.0, Color("#ffe18a"))
		for ember in range(6):
			var u := float(ember) / 5.0
			var point: Vector2 = sweep_end.lerp(sweep_origin, u) + Vector2(0.0, sin(simulation_time * 12.0 + ember) * 4.0) * PANEL_SCALE
			draw_circle(point, (1.5 + float(ember % 2)) * PANEL_SCALE, Color(1.0, 0.69, 0.28, 0.78 * strike * (1.0 - u * 0.35)))
	if follow_through > 0.02:
		var trailing_arc := PackedVector2Array([lantern_tip, lantern_tip.lerp(sweep_origin, 0.38) + Vector2(direction * 4.0, 5.0) * PANEL_SCALE, sweep_origin + Vector2(-direction * 7.0, 8.0) * PANEL_SCALE])
		draw_polyline(trailing_arc, Color(1.0, 0.56, 0.22, 0.52 * follow_through), 2.5 * PANEL_SCALE, true)
	if attack_active:
		var action_beat := clampf(age / 0.44, 0.0, 1.0)
		var beat_anchor := _project(hero_position + Vector2(-28.0, -222.0))
		draw_rect(Rect2(beat_anchor, Vector2(56.0, 3.0) * PANEL_SCALE), Color(0.10, 0.08, 0.06, 0.78), true)
		draw_rect(Rect2(beat_anchor, Vector2(56.0 * action_beat, 3.0) * PANEL_SCALE), Color("#ffc06a"), true)
	if attack_hit_feedback > 0.0:
		var hit_anchor := _project(enemy_position + Vector2(-direction * 16.0, -107.0))
		var fade := clampf(attack_hit_feedback / 0.10, 0.0, 1.0)
		_draw_ellipse(hit_anchor, Vector2(13.0, 12.0) * PANEL_SCALE, Color(1.0, 0.86, 0.50, 0.24 * fade))
		for ray in range(9):
			var angle := simulation_time * 5.0 + TAU * float(ray) / 9.0
			var unit := Vector2(cos(angle), sin(angle))
			draw_line(hit_anchor + unit * 4.0 * PANEL_SCALE, hit_anchor + unit * (16.0 + 10.0 * fade) * PANEL_SCALE, Color(1.0, 0.89, 0.55, 0.90 * fade), 1.8 * PANEL_SCALE, true)

func _draw_hero_action_rig(root: Vector2, direction: float, age: float, anticipation: float, strike: float, follow_through: float, extend: float, recovery: float, locomotion: float = 0.0, walk_phase: float = 0.0) -> void:
	# Authored diagnostic cutout rig: distinct anchored head, torso, leg, arm, cloak, grip and lantern parts.
	var compression := anticipation if attack_active else (1.0 - smoothstep(0.04, 0.17, extend) if dodge_active else 0.0)
	var gait := sin(walk_phase) * locomotion
	var lift_a := maxf(0.0, cos(walk_phase)) * 9.0 * locomotion
	var lift_b := maxf(0.0, -cos(walk_phase)) * 9.0 * locomotion
	var body_bob := absf(sin(walk_phase * 2.0)) * 2.4 * locomotion
	var hip := _project_actor(root, Vector2(-3.0 * direction * anticipation + 3.0 * direction * strike, -73.0 + 7.0 * compression - 3.0 * strike + 4.0 * recovery - body_bob))
	var torso := _project_actor(root, Vector2(-7.0 * direction * anticipation + 8.0 * direction * strike - 8.0 * direction * extend, -105.0 + 9.0 * compression + 3.0 * strike - 4.0 * extend + 2.0 * recovery - body_bob))
	var head := _project_actor(root, Vector2(-10.0 * direction * anticipation + 6.0 * direction * strike - 8.0 * direction * extend, -149.0 + 6.0 * compression + 2.0 * strike - body_bob * 1.25))
	var foot_a := _project_actor(root, Vector2(-19.0 + 4.0 * anticipation - 5.0 * extend + 14.0 * gait, -6.0 + 4.0 * compression - lift_a))
	var foot_b := _project_actor(root, Vector2(19.0 + 7.0 * strike + 5.0 * extend - 14.0 * gait, -6.0 - lift_b))
	var knee_a := foot_a.lerp(hip + Vector2(-7.0, 0.0) * PANEL_SCALE, 0.58) + Vector2(-3.0 * anticipation, -9.0 * compression + 4.0 * extend) * PANEL_SCALE
	var knee_b := foot_b.lerp(hip + Vector2(7.0, 0.0) * PANEL_SCALE, 0.54) + Vector2(4.0 * strike, -4.0 * compression - 4.0 * extend) * PANEL_SCALE
	var arm_swing := sin(walk_phase) * locomotion
	var hand_a := _project_actor(root, Vector2(-direction * (29.0 + 8.0 * anticipation + 7.0 * extend + 8.0 * arm_swing), -104.0 + 6.0 * compression - 4.0 * locomotion))
	var hand_b := _project_actor(root, Vector2(direction * (17.0 + 16.0 * anticipation + 31.0 * strike - 12.0 * recovery + 6.0 * extend - 5.0 * arm_swing), -102.0 - 4.0 * anticipation - 11.0 * strike + 5.0 * recovery + 3.0 * locomotion))
	draw_polyline(PackedVector2Array([foot_a, knee_a, hip + Vector2(-7.0, 0.0) * PANEL_SCALE]), Color("#29252d"), 12.0 * PANEL_SCALE, true)
	draw_polyline(PackedVector2Array([foot_b, knee_b, hip + Vector2(7.0, 0.0) * PANEL_SCALE]), Color("#302832"), 12.0 * PANEL_SCALE, true)
	draw_polyline(PackedVector2Array([foot_a + Vector2(-5.0, 0.0) * PANEL_SCALE, foot_a + Vector2(7.0, 0.0) * PANEL_SCALE]), Color("#5c3d35"), 5.0 * PANEL_SCALE, true)
	draw_polyline(PackedVector2Array([foot_b + Vector2(-5.0, 0.0) * PANEL_SCALE, foot_b + Vector2(7.0, 0.0) * PANEL_SCALE]), Color("#5c3d35"), 5.0 * PANEL_SCALE, true)
	_draw_ellipse(hip, Vector2(12.0, 8.0) * PANEL_SCALE, Color("#44343b"))
	draw_line(hip, torso, Color("#273137"), 16.0 * PANEL_SCALE, true)
	_draw_ellipse(torso, Vector2(12.0, 16.0) * PANEL_SCALE, Color("#394b52"))
	var mantle_tail := torso + Vector2(-direction * (31.0 + 16.0 * strike + 10.0 * follow_through + 9.0 * extend + 8.0 * locomotion), 28.0 + sin(simulation_time * 7.0 + age * 10.0 + walk_phase) * (3.0 + 3.0 * strike + 2.0 * locomotion)) * PANEL_SCALE
	var mantle := PackedVector2Array([torso + Vector2(-9.0 * direction, -7.0) * PANEL_SCALE, torso + Vector2(-22.0 * direction, 5.0) * PANEL_SCALE, mantle_tail, torso + Vector2(1.0 * direction, 13.0) * PANEL_SCALE])
	draw_colored_polygon(mantle, Color(0.10, 0.36, 0.37, 0.94))
	draw_polyline(PackedVector2Array([mantle[1], mantle[2]]), Color("#75b9aa"), 1.6 * PANEL_SCALE, true)
	_draw_capsule(torso + Vector2(-9.0 * direction, 0.0) * PANEL_SCALE, hand_a, 5.5 * PANEL_SCALE, Color("#314248"))
	_draw_capsule(torso + Vector2(9.0 * direction, 0.0) * PANEL_SCALE, hand_b, 6.5 * PANEL_SCALE, Color("#32444b"))
	_draw_ellipse(hand_a, Vector2(4.5, 4.5) * PANEL_SCALE, Color("#ad795d"))
	_draw_ellipse(hand_b, Vector2(5.0, 5.0) * PANEL_SCALE, Color("#bf8965"))
	_draw_ellipse(head, Vector2(8.0, 10.0) * PANEL_SCALE, Color("#d0a17d"))
	_draw_ellipse(head + Vector2(direction * 1.0, -5.0) * PANEL_SCALE, Vector2(8.5, 3.5) * PANEL_SCALE, Color("#542e38"))
	var braid := PackedVector2Array([head + Vector2(-5.0 * direction, 0.0) * PANEL_SCALE, head + Vector2(-16.0 * direction, 4.0) * PANEL_SCALE, head + Vector2(-27.0 * direction, 10.0 + sin(simulation_time * 11.0 + age * 13.0) * 4.0) * PANEL_SCALE, head + Vector2(-32.0 * direction, 15.0 + sin(simulation_time * 11.0 + age * 13.0 + 0.8) * 4.0) * PANEL_SCALE])
	draw_polyline(braid, Color("#542e38"), 3.0 * PANEL_SCALE, true)
	draw_polyline(braid.slice(1, 4), Color("#94616b"), 1.0 * PANEL_SCALE, true)
	var lantern_root := hand_b + Vector2(direction * 8.0, 2.0 - body_bob * 0.4) * PANEL_SCALE
	var lantern_tip := lantern_root + Vector2(direction * (52.0 + 28.0 * strike - 10.0 * recovery - 8.0 * extend), -22.0 + 10.0 * follow_through + 5.0 * extend + body_bob * 0.35) * PANEL_SCALE
	_draw_capsule(hand_a, lantern_root, 4.0 * PANEL_SCALE, Color("#bd895f"))
	draw_line(lantern_root, lantern_tip, Color("#382b24"), 5.5 * PANEL_SCALE, true)
	draw_line(lantern_root, lantern_root.lerp(lantern_tip, 0.44), Color("#9c714b"), 1.8 * PANEL_SCALE, true)
	_draw_ellipse(lantern_tip, Vector2(8.0, 9.0) * PANEL_SCALE, Color("#dfad5d"))
	_draw_flame(lantern_tip, (8.0 + 7.0 * strike) * PANEL_SCALE, simulation_time * 10.0 + age * 8.0, Color("#ffc970"))
	if anticipation > 0.02:
		var wind_start := lantern_root + Vector2(-direction * 17.0, -4.0) * PANEL_SCALE
		draw_line(wind_start, wind_start + Vector2(direction * 28.0, 5.0) * PANEL_SCALE, Color(1.0, 0.76, 0.38, 0.30 + anticipation * 0.48), 2.6 * PANEL_SCALE, true)
	if strike > 0.02:
		var sweep_origin := torso + Vector2(direction * 7.0, 5.0) * PANEL_SCALE
		var sweep_end := lantern_tip + Vector2(direction * (21.0 + 26.0 * strike), -16.0 * strike) * PANEL_SCALE
		var sweep_path := PackedVector2Array([sweep_origin, sweep_origin.lerp(sweep_end, 0.33) + Vector2(0.0, -13.0) * PANEL_SCALE, sweep_origin.lerp(sweep_end, 0.70) + Vector2(0.0, -7.0) * PANEL_SCALE, sweep_end])
		draw_polyline(sweep_path, Color(1.0, 0.72, 0.31, 0.84 * strike), 5.0 * PANEL_SCALE, true)
		_draw_flame(sweep_end, (8.0 + 8.0 * strike) * PANEL_SCALE, simulation_time * 12.0 + age * 10.0, Color("#ffe18a"))
		for ember in range(6):
			var u := float(ember) / 5.0
			var point: Vector2 = sweep_end.lerp(sweep_origin, u) + Vector2(0.0, sin(simulation_time * 12.0 + ember) * 4.0) * PANEL_SCALE
			draw_circle(point, (1.5 + float(ember % 2)) * PANEL_SCALE, Color(1.0, 0.69, 0.28, 0.78 * strike * (1.0 - u * 0.35)))
	if follow_through > 0.02:
		var trail := PackedVector2Array([lantern_tip, lantern_tip.lerp(torso, 0.42) + Vector2(direction * 4.0, 5.0) * PANEL_SCALE, torso + Vector2(-direction * 7.0, 8.0) * PANEL_SCALE])
		draw_polyline(trail, Color(1.0, 0.56, 0.22, 0.52 * follow_through), 2.5 * PANEL_SCALE, true)
	if attack_hit_feedback > 0.0:
		var hit_anchor := _project(enemy_position + Vector2(-direction * 16.0, -107.0))
		var fade := clampf(attack_hit_feedback / 0.10, 0.0, 1.0)
		for ray in range(9):
			var angle := simulation_time * 5.0 + TAU * float(ray) / 9.0
			var unit := Vector2(cos(angle), sin(angle))
			draw_line(hit_anchor + unit * 4.0 * PANEL_SCALE, hit_anchor + unit * (16.0 + 10.0 * fade) * PANEL_SCALE, Color(1.0, 0.89, 0.55, 0.90 * fade), 1.8 * PANEL_SCALE, true)

func _draw_dodge_vfx() -> void:
	if not dodge_active:
		return
	var phase := clampf((0.38 - dodge_timer) / 0.38, 0.0, 1.0)
	var invulnerability := _project(hero_position + Vector2(0.0, -83.0))
	var tint := Color(0.34, 0.86, 0.92, 0.18 + 0.08 * sin(phase * PI))
	_draw_ellipse(invulnerability, Vector2(32.0, 47.0) * PANEL_SCALE, tint, false, 2.4 * PANEL_SCALE)
	for mote_id in range(4):
		var orbit := simulation_time * 4.0 + TAU * float(mote_id) / 4.0
		var mote := invulnerability + Vector2(cos(orbit) * 26.0, sin(orbit) * 30.0) * PANEL_SCALE
		draw_circle(mote, 1.8 * PANEL_SCALE, Color(0.60, 0.94, 0.95, 0.85 * (1.0 - phase * 0.2)))

func _draw_enemy() -> void:
	if enemy_health <= 0:
		return
	var phase_age := maxf(enemy_phase_age, 0.0)
	var wind := smoothstep(0.16, 0.76, phase_age) if enemy_state == "windup" else 0.0
	var strike := (1.0 - smoothstep(0.03, 0.16, phase_age)) if enemy_state == "strike" else 0.0
	var recovery := (1.0 - smoothstep(0.34, 0.55, phase_age)) if enemy_state == "recovery" else 0.0
	var facing := -1.0 if hero_position.x < enemy_position.x else 1.0
	var floor := _project(enemy_position)
	var shift := -11.0 * wind + 29.0 * strike + 9.0 * recovery
	var crouch := 5.0 * wind - 11.0 * strike + 3.0 * recovery
	var at := func(offset: Vector2) -> Vector2:
		return floor + Vector2(offset.x * facing + shift, offset.y + crouch) * PANEL_SCALE
	_draw_ellipse(floor, Vector2(23.0, 5.0) * PANEL_SCALE, Color(0.0, 0.0, 0.0, 0.32))
	var mantle := PackedVector2Array([at.call(Vector2(-16.0, -143.0)), at.call(Vector2(15.0, -145.0)), at.call(Vector2(28.0, -110.0)), at.call(Vector2(48.0 + 22.0 * wind, -82.0 - 12.0 * wind)), at.call(Vector2(33.0 + 30.0 * strike, -71.0)), at.call(Vector2(10.0, -91.0)), at.call(Vector2(-14.0, -96.0)), at.call(Vector2(-30.0, -74.0)), at.call(Vector2(-32.0, -111.0))])
	draw_colored_polygon(mantle, Color("#583d3d"))
	draw_polyline(PackedVector2Array([mantle[1], mantle[2], mantle[3], mantle[4], mantle[5]]), Color("#dfb77b"), 2.2 * PANEL_SCALE, true)
	_draw_capsule(at.call(Vector2(-9.0, -6.0)), at.call(Vector2(-18.0 - 7.0 * wind, -48.0 - 8.0 * wind)), 10.0 * PANEL_SCALE, Color("#302632"))
	_draw_capsule(at.call(Vector2(10.0, -6.0)), at.call(Vector2(19.0 - 8.0 * strike, -49.0 - 7.0 * wind)), 10.0 * PANEL_SCALE, Color("#352930"))
	_draw_capsule(at.call(Vector2(0.0, -77.0)), at.call(Vector2(0.0, -125.0)), 17.0 * PANEL_SCALE, Color("#302632"))
	_draw_ellipse(at.call(Vector2(0.0, -100.0)), Vector2(14.0, 17.0) * PANEL_SCALE, Color("#9f7753"))
	_draw_world_polyline(PackedVector2Array([at.call(Vector2(-13.0, -97.0)), at.call(Vector2(15.0, -102.0))]), Color("#c08e5a"), 6.0)
	var shoulder: Vector2 = at.call(Vector2(13.0, -121.0))
	var elbow: Vector2 = at.call(Vector2(25.0 + 18.0 * wind + 19.0 * strike, -103.0 - 8.0 * wind))
	var hand: Vector2 = at.call(Vector2(32.0 + 31.0 * wind + 27.0 * strike, -91.0 - 10.0 * wind - 10.0 * strike))
	_draw_capsule(shoulder, elbow, 7.0 * PANEL_SCALE, Color("#583d3d"))
	_draw_capsule(elbow, hand, 5.5 * PANEL_SCALE, Color("#a57a57"))
	_draw_ellipse(hand, Vector2(5.0, 5.0) * PANEL_SCALE, Color("#d2a174"))
	var back_hand: Vector2 = at.call(Vector2(-23.0 - 10.0 * wind, -94.0))
	_draw_capsule(at.call(Vector2(-14.0, -120.0)), back_hand, 5.0 * PANEL_SCALE, Color("#583d3d"))
	var head: Vector2 = at.call(Vector2(0.0, -145.0))
	_draw_ellipse(head, Vector2(15.0, 18.0) * PANEL_SCALE, Color("#d0a17d"))
	var hood := PackedVector2Array([head + Vector2(-14.0, -6.0) * PANEL_SCALE, head + Vector2(-10.0, -18.0) * PANEL_SCALE, head + Vector2(1.0, -23.0) * PANEL_SCALE, head + Vector2(14.0, -15.0) * PANEL_SCALE, head + Vector2(16.0, -2.0) * PANEL_SCALE])
	draw_colored_polygon(hood, Color("#28242d"))
	var torch_end: Vector2 = hand + Vector2(facing * 58.0, -19.0 + 24.0 * strike) * PANEL_SCALE
	draw_line(hand, torch_end, Color("#805239"), 5.0 * PANEL_SCALE, true)
	draw_line(hand, hand.lerp(torch_end, 0.42), Color("#c69a64"), 1.8 * PANEL_SCALE, true)
	_draw_flame(torch_end, 9.0 * PANEL_SCALE, simulation_time * 9.0, Color("#ffad58"))
	if enemy_state == "strike":
		var strike_end: Vector2 = at.call(Vector2(113.0, -123.0))
		draw_line(hand, strike_end, Color(1.0, 0.48, 0.2, 0.80), 4.0 * PANEL_SCALE, true)
		for spark in range(5):
			var t := float(spark) / 4.0
			var point := hand.lerp(strike_end, t) + Vector2(0.0, sin(simulation_time * 13.0 + spark) * 2.0) * PANEL_SCALE
			draw_circle(point, 1.8 * PANEL_SCALE, Color(1.0, 0.76, 0.42, 0.82))
	if recovery > 0.0:
		var after := floor + Vector2(-facing * (15.0 + 8.0 * recovery), -72.0) * PANEL_SCALE
		_draw_ellipse(after, Vector2(15.0, 31.0) * PANEL_SCALE, Color(1.0, 0.40, 0.18, 0.13 * recovery), false, 2.0 * PANEL_SCALE)

func _draw_capsule(a: Vector2, b: Vector2, width: float, color: Color) -> void:
	draw_line(a, b, color, width, true)
	draw_circle(a, width * 0.5, color)
	draw_circle(b, width * 0.5, color)

func _draw_flame(origin: Vector2, scale: float, phase: float, color: Color) -> void:
	for tongue in range(3):
		var sway := sin(phase + float(tongue) * 1.9) * scale * 0.30
		var height := scale * (1.0 + 0.30 * cos(phase * 1.4 + tongue))
		var base := origin + Vector2(float(tongue - 1) * scale * 0.30, 0.0)
		var flame := PackedVector2Array([base + Vector2(-scale * 0.28, 0.0), base + Vector2(sway - scale * 0.22, -height * 0.58), base + Vector2(sway, -height), base + Vector2(sway + scale * 0.20, -height * 0.45), base + Vector2(scale * 0.27, 0.0)])
		draw_colored_polygon(flame, Color(color.r, color.g, color.b, 0.68 - tongue * 0.12))

func _draw_ellipse(center: Vector2, radius: Vector2, color: Color, filled := true, width := 1.0) -> void:
	var points := PackedVector2Array()
	for i in range(41):
		var angle := TAU * float(i) / 40.0
		points.append(center + Vector2(cos(angle) * radius.x, sin(angle) * radius.y))
	if filled:
		draw_colored_polygon(points, color)
	else:
		draw_polyline(points, color, width, true)
