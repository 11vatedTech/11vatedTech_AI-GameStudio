import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("validate_pose_spec",ROOT/"tools/blender/validate_pose_spec.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
EX=ROOT/"examples/blender/torch_sweep_pose_spec.example.json"
class TestPoseSpec(unittest.TestCase):
 def setUp(self): self.data=json.loads(EX.read_text(encoding="utf-8"))
 def test_example_is_valid(self): self.assertEqual(mod.validate_pose_spec(self.data),[])
 def test_mismatched_bone_set_rejected(self): self.data["poses"][1]["bones"].pop("hand.R");self.assertTrue(any("same set of bones" in x for x in mod.validate_pose_spec(self.data)))
 def test_attack_without_semantic_phases_rejected(self): self.data["poses"][0]["purpose"]="start";self.assertTrue(any("requires pose purpose phases" in x for x in mod.validate_pose_spec(self.data)))
 def test_missing_impact_event_rejected(self): self.data["events"]=[e for e in self.data["events"] if e["kind"]!="impact"];self.assertTrue(any("impact" in x for x in mod.validate_pose_spec(self.data)))
 def test_bad_frame_outside_range_rejected(self): self.data["poses"][0]["frame"]=99;self.assertTrue(mod.validate_pose_spec(self.data))
if __name__=="__main__":unittest.main()
