extends Node3D

@onready var model: Node3D = $ImportedAction
@onready var animation_player: AnimationPlayer = _find_animation_player(model)

func _ready() -> void:
	if animation_player == null:
		push_error("Imported glTF has no AnimationPlayer")
		return
	var clips := animation_player.get_animation_list()
	if clips.is_empty():
		push_error("Imported glTF contains no animation clips")
		return
	var candidates: Array[StringName] = []
	for clip in clips:
		if str(clip).contains("Torch_Sweep_Runtime_Proof"):
			candidates.append(clip)
	if candidates.is_empty():
		push_error("Torch sweep action was not imported: %s" % [clips])
		return
	animation_player.play(candidates[0])
	print("ACTION_RUNTIME_PLAYING name=%s duration=%.3f tracks=%d" % [candidates[0], animation_player.get_animation(candidates[0]).length, animation_player.get_animation(candidates[0]).get_track_count()])

func _find_animation_player(node: Node) -> AnimationPlayer:
	if node is AnimationPlayer:
		return node
	for child in node.get_children():
		var found := _find_animation_player(child)
		if found != null:
			return found
	return null
