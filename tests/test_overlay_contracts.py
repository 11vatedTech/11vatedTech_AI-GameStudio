import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestOverlayContracts(unittest.TestCase):
 def test_registries_are_valid_json_with_unique_ids(self):
  a=json.loads((ROOT/"docs/registries/asset-method-registry.json").read_text());self.assertGreaterEqual(len(a["methods"]),6);self.assertEqual(len({x["id"] for x in a["methods"]}),len(a["methods"]))
  m=json.loads((ROOT/"docs/registries/mcp-tool-registry.json").read_text());self.assertGreaterEqual(len(m["tools"]),8);self.assertEqual(len({x["id"] for x in m["tools"]}),len(m["tools"]))
 def test_schemas_are_valid_draft_2020_12(self):
  import jsonschema
  for p in (ROOT/"schemas").glob("*.schema.json"):
   s=json.loads(p.read_text());jsonschema.Draft202012Validator.check_schema(s)
 def test_new_skills_mirrored_byte_for_byte(self):
  for p in (ROOT/"skills").glob("*/SKILL.md"):
   bundled=ROOT/"src/vated_studio/data/skills"/p.parent.name/"SKILL.md"
   self.assertTrue(bundled.is_file(),str(bundled));self.assertEqual(p.read_bytes(),bundled.read_bytes())
 def test_registry_data_conforms_to_its_schema(self):
  import jsonschema
  mappings=[('mcp-tool-registry.json','mcp-tool-registry.schema.json'),('asset-method-registry.json','asset-method-registry.schema.json')]
  for data_name,schema_name in mappings:
   data=json.loads((ROOT/'docs/registries'/data_name).read_text())
   schema=json.loads((ROOT/'schemas'/schema_name).read_text())
   jsonschema.validate(data,schema)
  seq=json.loads((ROOT/'examples/animation/torch_sweep.sequence.example.json').read_text())
  seq_schema=json.loads((ROOT/'schemas/animation-sequence-v2.schema.json').read_text())
  jsonschema.validate(seq,seq_schema)
  pose=json.loads((ROOT/'examples/blender/torch_sweep_pose_spec.example.json').read_text())
  pose_schema=json.loads((ROOT/'schemas/blender-pose-spec-v1.schema.json').read_text())
  jsonschema.validate(pose,pose_schema)
 def test_hard_no_placeholder_policy_exists(self):
  c=(ROOT/"docs/studio/AGENT_FIRST_CREATIVE_PRODUCTION_CONTRACT.md").read_text()
  self.assertIn("Pulsing, scaling, rotating",c);self.assertIn("operator responsible for generating images",c)
if __name__=="__main__":unittest.main()
