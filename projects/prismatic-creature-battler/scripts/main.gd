extends Node2D

# The Prismatic Creature Battler — Godot 4 Vertical Slice Runtime
# Implements the 8-creature roster, 3-tier masked foil card inspection,
# 6v6 Frontline/Backline formation, Refractive Resonance chains, and Prism Gauge Convergence.

const VIEW_W := 1440.0
const VIEW_H := 900.0

const ROSTER := [
	{
		"id": "tempest-wyrm",
		"name": "Tempest Wyrm",
		"origin": "Storm",
		"instinct": "Hunter",
		"signature": "Voltbrand",
		"hp": 1180,
		"atk": 185,
		"def": 35,
		"spd": 1.35,
		"color": Color("38E5FF"),
		"foil": "Prismatic Spectrum",
		"desc": "Opening strike marks target with [VOLTBRAND].Marked targets take +30% resonance damage."
	},
	{
		"id": "prismhart",
		"name": "Prismhart",
		"origin": "Crystal",
		"instinct": "Guardian",
		"signature": "Refractive Ward",
		"hp": 1820,
		"atk": 115,
		"def": 68,
		"spd": 0.95,
		"color": Color("7AF0FF"),
		"foil": "Prismatic Spectrum",
		"desc": "When an ally triggers [VOLTBRAND], grants [REFRACTIVE WARD] shield and arcs lightning."
	},
	{
		"id": "riftstalker",
		"name": "Riftstalker",
		"origin": "Void",
		"instinct": "Assassin",
		"signature": "Phase Rend",
		"hp": 1040,
		"atk": 225,
		"def": 28,
		"spd": 1.45,
		"color": Color("B55CFF"),
		"foil": "Phantom Foil",
		"desc": "Phases past enemy Frontline to strike [VOLTBRAND] or [ECLIPSE] marked targets for 180% DMG."
	},
	{
		"id": "pyrewarden",
		"name": "Pyrewarden",
		"origin": "Flame",
		"instinct": "Bruiser",
		"signature": "Solar Crucible",
		"hp": 1680,
		"atk": 168,
		"def": 55,
		"spd": 1.05,
		"color": Color("FF6B4A"),
		"foil": "Relic Foil",
		"desc": "Cleaves frontline and applies [SOLAR BRAND]. Shielded allies ignite a molten shockwave."
	},
	{
		"id": "sylvan-aegis",
		"name": "Sylvan Aegis",
		"origin": "Verdant",
		"instinct": "Healer",
		"signature": "Heartwood Bloom",
		"hp": 1460,
		"atk": 122,
		"def": 48,
		"spd": 1.10,
		"color": Color("2CEAA3"),
		"foil": "Relic Foil",
		"desc": "Restores 190 HP to lowest ally and converts [TIDAL] or [WARD] into +25 ATK Overgrowth."
	},
	{
		"id": "abyssal-ryu",
		"name": "Abyssal Ryu",
		"origin": "Tide",
		"instinct": "Controller",
		"signature": "Sacred Current",
		"hp": 1540,
		"atk": 152,
		"def": 52,
		"spd": 1.15,
		"color": Color("00E5B8"),
		"foil": "Prismatic Spectrum",
		"desc": "Applies [TIDAL LOCK] (-25% SPD) and refracts [VOLTBRAND] across adjacent enemies."
	},
	{
		"id": "solarius",
		"name": "Solarius",
		"origin": "Astral",
		"instinct": "Support",
		"signature": "Astrolabe Halo",
		"hp": 1320,
		"atk": 145,
		"def": 42,
		"spd": 1.25,
		"color": Color("F5C451"),
		"foil": "Prismatic Spectrum",
		"desc": "Amplifies Prism Gauge gain by +35% and detonates [SOLAR BRAND] into radiant shields."
	},
	{
		"id": "umbral-weaver",
		"name": "Umbral Weaver",
		"origin": "Eclipse",
		"instinct": "Disruptor",
		"signature": "Crescent Tether",
		"hp": 1260,
		"atk": 162,
		"def": 40,
		"spd": 1.30,
		"color": Color("D06BFF"),
		"foil": "Phantom Foil",
		"desc": "Links enemy backline with [ECLIPSE TETHER], sharing 40% of Resonance damage."
	}
]

const FOIL_MODES := ["Prismatic Spectrum", "Phantom Foil", "Relic Foil"]

var textures := {}
var selected_index := 0
var current_foil_idx := 0
var phase := "PREPARE" # PREPARE, BATTLE, RESULT
var prism_gauge := 0.0
var enemy_prism_gauge := 0.0
var time_acc := 0.0
var tick_timer := 0.0
var round_number := 1
var player_team := []
var enemy_team := []
var combat_log := []
var active_beams := []
var convergence_flash := 0.0
var battle_winner := ""

func _ready() -> void:
	for item in ROSTER:
		var p := "res://assets/sprites/%s.png" % item["id"]
		if ResourceLoader.exists(p):
			textures[item["id"]] = load(p)
	if ResourceLoader.exists("res://assets/sprites/sanctuary-arena.png"):
		textures["arena"] = load("res://assets/sprites/sanctuary-arena.png")
	_load_archetype(0)

func _load_archetype(preset: int) -> void:
	player_team.clear()
	enemy_team.clear()
	var p_indices := [0, 1, 2, 5, 6, 3]
	if preset == 1:
		p_indices = [3, 6, 7, 1, 0, 4]
	elif preset == 2:
		p_indices = [5, 4, 1, 6, 0, 2]
	var e_indices := [3, 1, 4, 0, 7, 5]
	for slot in range(6):
		player_team.append(_make_unit(ROSTER[p_indices[slot]], slot, true))
		enemy_team.append(_make_unit(ROSTER[e_indices[slot]], slot, false))
	prism_gauge = 0.0
	enemy_prism_gauge = 0.0
	phase = "PREPARE"
	combat_log = [
		"[PREP] Formation ready: Tempest Wyrm + Prismhart + Riftstalker Voltbrand Chain active.",
		"[RULE] Foil Edition (%s) is 100%% cosmetic — competitive stats remain standardized." % FOIL_MODES[current_foil_idx]
	]
	active_beams.clear()
	queue_redraw()

func _make_unit(proto: Dictionary, slot: int, is_player: bool) -> Dictionary:
	return {
		"id": proto["id"],
		"name": proto["name"],
		"origin": proto["origin"],
		"instinct": proto["instinct"],
		"signature": proto["signature"],
		"max_hp": float(proto["hp"]),
		"hp": float(proto["hp"]),
		"atk": float(proto["atk"]),
		"def": float(proto["def"]),
		"spd": float(proto["spd"]),
		"color": proto["color"],
		"slot": slot,
		"row": "Frontline" if slot < 3 else "Backline",
		"is_player": is_player,
		"captain": slot == 0,
		"shield": 0.0,
		"marks": {},
		"cooldown": 1.0 / float(proto["spd"])
	}

func _process(delta: float) -> void:
	time_acc += delta
	if convergence_flash > 0.0:
		convergence_flash = maxf(0.0, convergence_flash - delta * 1.6)
	for i in range(active_beams.size() - 1, -1, -1):
		active_beams[i]["ttl"] -= delta
		if active_beams[i]["ttl"] <= 0.0:
			active_beams.remove_at(i)
	if phase == "BATTLE":
		tick_timer += delta
		if tick_timer >= 0.55:
			tick_timer = 0.0
			_step_combat()
	queue_redraw()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if event.keycode >= KEY_1 and event.keycode <= KEY_8:
			selected_index = int(event.keycode - KEY_1)
		elif event.keycode == KEY_F:
			current_foil_idx = (current_foil_idx + 1) % FOIL_MODES.size()
			combat_log.push_front("[FOIL] Switched card shader to %s (0 stat delta)." % FOIL_MODES[current_foil_idx])
		elif event.keycode == KEY_SPACE or event.keycode == KEY_ENTER:
			if phase == "PREPARE":
				phase = "BATTLE"
				combat_log.push_front("[BATTLE] Cards materialize onto the Prismatic Sanctuary!")
			else:
				_load_archetype(round_number % 3)
				round_number += 1
		elif event.keycode == KEY_R:
			_load_archetype(0)

func _step_combat() -> void:
	var alive_p := player_team.filter(func(u): return u["hp"] > 0.0)
	var alive_e := enemy_team.filter(func(u): return u["hp"] > 0.0)
	if alive_p.is_empty() or alive_e.is_empty():
		phase = "RESULT"
		battle_winner = "PLAYER VICTORY — REFRACTIVE CONVERGENCE" if not alive_p.is_empty() else "OPPONENT VICTORY"
		combat_log.push_front("[OUTCOME] %s" % battle_winner)
		return
	var all_units := alive_p + alive_e
	all_units.sort_custom(func(a, b): return a["spd"] > b["spd"])
	var actor: Dictionary = all_units[int(time_acc * 10.0) % all_units.size()]
	var allies := alive_p if actor["is_player"] else alive_e
	var foes := alive_e if actor["is_player"] else alive_p
	if foes.is_empty():
		return
	var target: Dictionary = foes[0]
	# Riftstalker Phase Rend: bypass frontline to hit Voltbrand-marked target
	if actor["id"] == "riftstalker":
		for f in foes:
			if f["marks"].has("VOLTBRAND"):
				target = f
				break
	else:
		var front := foes.filter(func(f): return f["slot"] < 3)
		target = front[0] if not front.is_empty() else foes[0]

	var dmg := maxf(28.0, actor["atk"] * (100.0 / (100.0 + target["def"])))
	if actor["captain"]:
		dmg *= 1.12

	if actor["id"] == "tempest-wyrm":
		target["marks"]["VOLTBRAND"] = true
		_add_gauge(actor["is_player"], 22.0)
		_push_beam(_unit_pos(actor), _unit_pos(target), Color("38E5FF"), "VOLTBRAND MARK")
		combat_log.push_front("%s strikes %s with Voltbrand (+22 Prism)!" % [actor["name"], target["name"]])
		# Trigger adjacent Prismhart Refractive Ward!
		for ally in allies:
			if ally["id"] == "prismhart" and ally["hp"] > 0.0:
				ally["shield"] += 140.0
				actor["shield"] += 110.0
				_add_gauge(actor["is_player"], 26.0)
				_push_beam(_unit_pos(ally), _unit_pos(actor), Color("7AF0FF"), "REFRACTIVE WARD")
				combat_log.push_front("RESONANCE: Prismhart refracts Voltbrand -> +140 Shield & Secondary Arc!")
	elif actor["id"] == "riftstalker" and target["marks"].has("VOLTBRAND"):
		dmg *= 1.75
		_add_gauge(actor["is_player"], 28.0)
		_push_beam(_unit_pos(actor), _unit_pos(target), Color("D06BFF"), "PHASE REND CRIT")
		combat_log.push_front("RESONANCE: Riftstalker Phase Rends marked %s for %d DMG!" % [target["name"], int(dmg)])
	else:
		_add_gauge(actor["is_player"], 14.0)
		_push_beam(_unit_pos(actor), _unit_pos(target), actor["color"], actor["signature"])
		combat_log.push_front("%s casts %s on %s (%d DMG)." % [actor["name"], actor["signature"], target["name"], int(dmg)])

	_apply_damage(target, dmg)
	if combat_log.size() > 9:
		combat_log.resize(9)

func _add_gauge(is_player: bool, amount: float) -> void:
	if is_player:
		prism_gauge = minf(100.0, prism_gauge + amount)
		if prism_gauge >= 100.0:
			prism_gauge = 0.0
			convergence_flash = 1.0
			for foe in enemy_team:
				if foe["hp"] > 0.0:
					_apply_damage(foe, 240.0)
			for ally in player_team:
				if ally["hp"] > 0.0:
					ally["shield"] += 160.0
			combat_log.push_front("CONVERGENCE UNLEASHED: Prismatic Storm Surge deals 240 AOE DMG & +160 Team Shield!")
	else:
		enemy_prism_gauge = minf(100.0, enemy_prism_gauge + amount)

func _apply_damage(target: Dictionary, amount: float) -> void:
	var rem := amount
	if target["shield"] > 0.0:
		var absorbed := minf(target["shield"], rem)
		target["shield"] -= absorbed
		rem -= absorbed
	target["hp"] = maxf(0.0, target["hp"] - rem)

func _push_beam(a: Vector2, b: Vector2, col: Color, label: String) -> void:
	active_beams.append({"a": a, "b": b, "color": col, "label": label, "ttl": 0.55})

func _unit_pos(u: Dictionary) -> Vector2:
	var col_idx := int(u["slot"]) % 3
	var is_front := int(u["slot"]) < 3
	var base_x := 640.0 + (col_idx - 1) * 145.0
	var base_y := 0.0
	if u["is_player"]:
		base_y = 515.0 if is_front else 655.0
	else:
		base_y = 335.0 if is_front else 205.0
	return Vector2(base_x, base_y)

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_rect(Rect2(0, 0, VIEW_W, VIEW_H), Color("090B14"), true)
	if textures.has("arena"):
		draw_texture_rect(textures["arena"], Rect2(380, 90, 680, 660), false, Color(1, 1, 1, 0.36))
	# Header bar & Prism Gauge
	draw_rect(Rect2(20, 16, VIEW_W - 40, 62), Color("121829"), true)
	draw_rect(Rect2(20, 16, VIEW_W - 40, 62), Color("38E5FF"), false, 1.5)
	draw_string(font, Vector2(40, 44), "THE PRISMATIC CREATURE BATTLER — REFRACTIVE RESONANCE VERTICAL SLICE", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("F2F6FF"))
	draw_string(font, Vector2(40, 66), "1-8 Inspect Creature   |   F Cycle Foil (%s)   |   SPACE Start/Next Battle   |   R Reset" % FOIL_MODES[current_foil_idx], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("7AF0FF"))
	# Prism Gauge
	draw_rect(Rect2(960, 28, 440, 22), Color("090B14"), true)
	draw_rect(Rect2(960, 28, 4.4 * prism_gauge, 22), Color("38E5FF"), true)
	draw_rect(Rect2(960, 28, 440, 22), Color("F5C451"), false, 1.5)
	draw_string(font, Vector2(970, 45), "PRISM GAUGE: %d%% (CONVERGENCE AT 100%%)" % int(prism_gauge), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("F2F6FF"))

	# Left Panel: Living Holographic Card Inspector
	var card_rect := Rect2(28, 96, 330, 470)
	var proto: Dictionary = ROSTER[selected_index]
	draw_rect(card_rect, Color("101728"), true)
	var foil_col: Color = proto["color"].lerp(Color("F5C451"), 0.5 + 0.5 * sin(time_acc * 2.6))
	draw_rect(card_rect, foil_col, false, 3.0)
	if textures.has(proto["id"]):
		draw_texture_rect(textures[proto["id"]], Rect2(48, 145, 290, 240), false)
	draw_string(font, Vector2(44, 128), "%s  [%s · %s]" % [proto["name"], proto["origin"], proto["instinct"]], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("F2F6FF"))
	draw_string(font, Vector2(44, 412), "Signature: %s" % proto["signature"], HORIZONTAL_ALIGNMENT_LEFT, -1, 15, proto["color"])
	draw_string(font, Vector2(44, 436), proto["desc"], HORIZONTAL_ALIGNMENT_LEFT, 298, 12, Color("C9D6EA"))
	draw_string(font, Vector2(44, 512), "ATK %d   HP %d   DEF %d   SPD %.2f" % [proto["atk"], proto["hp"], proto["def"], proto["spd"]], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("F5C451"))
	draw_string(font, Vector2(44, 542), "FOIL EDITION: %s (Cosmetic Only)" % FOIL_MODES[current_foil_idx], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("7AF0FF"))

	# Center Dimensional Sanctuary Arena
	for u in enemy_team + player_team:
		var pos := _unit_pos(u)
		var alive: bool = u["hp"] > 0.0
		var ring_col: Color = u["color"] if alive else Color("333B4D")
		draw_circle(pos + Vector2(0, 18), 44.0, Color(0.05, 0.08, 0.14, 0.85))
		draw_arc(pos + Vector2(0, 18), 44.0, 0.0, TAU, 6, ring_col, 2.5)
		if alive and textures.has(u["id"]):
			var bob := sin(time_acc * 3.2 + float(u["slot"])) * 4.0
			draw_texture_rect(textures[u["id"]], Rect2(pos.x - 42, pos.y - 46 + bob, 84, 84), false)
		if alive:
			var hp_ratio := clampf(u["hp"] / u["max_hp"], 0.0, 1.0)
			draw_rect(Rect2(pos.x - 38, pos.y + 42, 76, 7), Color("090B14"), true)
			draw_rect(Rect2(pos.x - 38, pos.y + 42, 76 * hp_ratio, 7), Color("2CEAA3") if u["is_player"] else Color("FF4D6D"), true)
			if u["shield"] > 0.0:
				draw_arc(pos, 48.0, 0.0, TAU, 6, Color("7AF0FF"), 2.0)
			if u["marks"].has("VOLTBRAND"):
				draw_string(font, pos + Vector2(-34, -52), "⚡VOLTBRAND", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("38E5FF"))
		draw_string(font, pos + Vector2(-38, 62), u["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("F2F6FF"))

	for b in active_beams:
		draw_line(b["a"], b["b"], b["color"], 3.5)
		draw_string(font, (b["a"] + b["b"]) * 0.5, b["label"], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, b["color"])

	# Right Panel: Causal Resonance Log
	var log_rect := Rect2(1075, 96, 340, 650)
	draw_rect(log_rect, Color("101728"), true)
	draw_rect(log_rect, Color("496174"), false, 1.5)
	draw_string(font, Vector2(1092, 126), "CAUSAL RESONANCE LOG (%s)" % phase, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("F5C451"))
	var y_off := 160.0
	for entry in combat_log:
		draw_string(font, Vector2(1092, y_off), entry, HORIZONTAL_ALIGNMENT_LEFT, 308, 12, Color("E2ECF8"))
		y_off += 54.0
