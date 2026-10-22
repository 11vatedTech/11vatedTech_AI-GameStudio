import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("validate_sequence",ROOT/"tools/animation/validate_sequence.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def valid_attack():
 return {"schema_version":"2.0","sequence_id":"attack-01","action_kind":"attack","method":"blender-rigged-action","frame_rate":24,"frame_count":24,
 "phases":[{"name":"anticipation","start_frame":0,"end_frame":4},{"name":"contact","start_frame":8,"end_frame":10},{"name":"follow_through","start_frame":11,"end_frame":16},{"name":"recovery","start_frame":17,"end_frame":23}],
 "identity_invariants":["hair","outfit","weapon","grip","camera"],"events":[{"name":"on","frame":7,"kind":"hitbox_on"},{"name":"impact","frame":9,"kind":"impact"},{"name":"off","frame":11,"kind":"hitbox_off"}],
 "artifacts":{"source":"source.blend","review_frame_strip":"frames.png","engine_capture":None,"engine_log":None},"review":{"status":"candidate","intended_speed_reviewed":False,"slow_reviewed":False,"identity_checked":False,"prop_contact_checked":False,"integrated":False,"runtime_observed":False,"notes":"not reviewed"}}
class TestAnimationSequence(unittest.TestCase):
 def test_accepts_complete_candidate_manifest(self): self.assertTrue(mod.validate_sequence(valid_attack())["valid"])
 def test_provided_sequence_template_passes_semantic_contract(self):
  d=__import__('json').loads((ROOT/'examples/animation/torch_sweep.sequence.example.json').read_text())
  self.assertTrue(mod.validate_sequence(d)['valid'])
 def test_accepts_existing_assembled_v1_manifest_without_promoting_visual_status(self):
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  result=mod.validate_sequence(d, ROOT/'builds/anim', check_files=False)
  self.assertTrue(result['valid'], result)
  self.assertEqual(result['status'], 'valid-assembled-manifest')
  self.assertEqual(result['review_status'], 'requires_visual_review')
  self.assertIn('structural only', result['note'])
 def test_rejects_broken_legacy_assembled_manifest(self):
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  d['frame_count']=d['frame_count']+1
  result=mod.validate_sequence(d)
  self.assertFalse(result['valid'])
  self.assertIn('source_frames must contain exactly frame_count entries.', result['errors'])
 def test_rejects_malformed_legacy_frame_hash_and_empty_path(self):
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  d['source_frames'][0]['path']='  '
  d['source_frames'][1]['sha256']='not-a-digest'
  result=mod.validate_sequence(d)
  self.assertFalse(result['valid'])
  self.assertTrue(any('source_frames[0] requires a non-empty path' in e for e in result['errors']))
  self.assertTrue(any('source_frames[1] sha256 must be a 64-character' in e for e in result['errors']))
 def test_legacy_manifest_file_checks_reject_frame_path_escape(self):
  import tempfile
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp)/'manifest';base.mkdir()
   outside=Path(tmp)/'outside.png';outside.write_bytes(b'frame')
   d['source_frames'][0]['path']='../outside.png'
   result=mod.validate_sequence(d,base,check_files=True)
  self.assertFalse(result['valid'])
  self.assertTrue(any('relative path escapes manifest root' in e for e in result['errors']))
 def test_legacy_manifest_file_checks_accept_original_absolute_source_paths(self):
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  result=mod.validate_sequence(d,ROOT/'builds/anim',check_files=True)
  self.assertTrue(result['valid'],result)
 def test_legacy_manifest_file_checks_reject_output_path_escape(self):
  import tempfile
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp)/'manifest';base.mkdir()
   d['outputs']={'gif':'../outside.gif'}
   result=mod.validate_sequence(d,base,check_files=True)
  self.assertFalse(result['valid'])
  self.assertTrue(any('Output path escapes manifest root' in e for e in result['errors']))
 def test_legacy_manifest_output_shape_and_layout_are_validated(self):
  d=__import__('json').loads((ROOT/'builds/anim/tempest-wyrm_idle_animation.json').read_text())
  d['outputs']=['unexpected']
  d['layout']=[]
  result=mod.validate_sequence(d)
  self.assertFalse(result['valid'])
  self.assertIn('outputs must be an object when present.',result['errors'])
  self.assertIn('layout must contain exactly frame_count entries when present.',result['errors'])
 def test_rejects_static_pulse_as_animation(self):
  d=valid_attack();d["method"]="static-image-pulse";self.assertFalse(mod.validate_sequence(d)["valid"])
 def test_rejects_missing_contact_timeline(self):
  d=valid_attack();d["phases"]=[p for p in d["phases"] if p["name"]!="contact"];self.assertFalse(mod.validate_sequence(d)["valid"])
 def test_rejects_attack_without_hitbox_events(self):
  d=valid_attack();d["events"]=[];self.assertFalse(mod.validate_sequence(d)["valid"])
 def test_runtime_claim_requires_runtime_evidence(self):
  d=valid_attack();d["review"].update({"status":"runtime-verified","intended_speed_reviewed":True,"slow_reviewed":True,"identity_checked":True,"prop_contact_checked":True,"integrated":True,"runtime_observed":True});self.assertFalse(mod.validate_sequence(d)["valid"])
 def test_runtime_claim_passes_when_evidence_references_exist(self):
  d=valid_attack();d["review"].update({"status":"runtime-verified","intended_speed_reviewed":True,"slow_reviewed":True,"identity_checked":True,"prop_contact_checked":True,"integrated":True,"runtime_observed":True});d["artifacts"].update({"engine_capture":"capture.png","engine_log":"engine.log"});self.assertTrue(mod.validate_sequence(d)["valid"])
if __name__=="__main__":unittest.main()
