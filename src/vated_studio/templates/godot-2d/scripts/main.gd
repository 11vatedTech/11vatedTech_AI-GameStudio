extends Node2D

# ENGINE SMOKE FIXTURE ONLY. Replace this scene and its illustrative drawing with
# the approved game design before calling a project production-ready.
const MOVE_SPEED := 260.0
const ARENA := Rect2(80, 90, 1120, 540)
var player_position := Vector2(220, 360)
var interact_count := 0
var status_text := "STARTER SMOKE FIXTURE — replace with the game's designed experience"

func _process(delta: float) -> void:
    var direction := Vector2.ZERO
    if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
        direction.x -= 1.0
    if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
        direction.x += 1.0
    if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
        direction.y -= 1.0
    if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
        direction.y += 1.0
    if direction.length_squared() > 0.0:
        player_position += direction.normalized() * MOVE_SPEED * delta
        player_position.x = clampf(player_position.x, ARENA.position.x + 14.0, ARENA.end.x - 14.0)
        player_position.y = clampf(player_position.y, ARENA.position.y + 14.0, ARENA.end.y - 14.0)
        queue_redraw()
    if Input.is_key_pressed(KEY_E):
        status_text = "INPUT RECEIVED — interaction hook is alive"
        queue_redraw()
    if Input.is_key_pressed(KEY_R):
        player_position = Vector2(220, 360)
        status_text = "STARTER SMOKE FIXTURE — reset"
        queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color("080c14"), true)
    draw_rect(ARENA, Color("101a27"), true)
    draw_rect(ARENA, Color("496174"), false, 2.0)
    for x in range(ARENA.position.x + 40, int(ARENA.end.x), 40):
        draw_line(Vector2(x, ARENA.position.y), Vector2(x, ARENA.end.y), Color(0.2, 0.32, 0.39, 0.25), 1.0)
    for y in range(ARENA.position.y + 40, int(ARENA.end.y), 40):
        draw_line(Vector2(ARENA.position.x, y), Vector2(ARENA.end.x, y), Color(0.2, 0.32, 0.39, 0.25), 1.0)
    draw_circle(player_position + Vector2(0, 12), 17.0, Color(0.0, 0.0, 0.0, 0.30))
    draw_circle(player_position, 12.0, Color("f0b85b"))
    draw_circle(player_position + Vector2(-3, -3), 5.0, Color("fff0bc"))
    draw_string(ThemeDB.fallback_font, Vector2(100, 55), "STUDIO INTEGRATION FIXTURE", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("f4d7a0"))
    draw_string(ThemeDB.fallback_font, Vector2(100, 675), "WASD / ARROWS MOVE   E INTERACTION HOOK   R RESET   —   NOT FINAL GAME ART", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("c0d0de"))
    draw_string(ThemeDB.fallback_font, Vector2(100, 710), status_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("80d6c5"))
