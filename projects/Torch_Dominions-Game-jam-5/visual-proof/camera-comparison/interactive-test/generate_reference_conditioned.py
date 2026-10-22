from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[5]
PROJECT = ROOT / "projects/Torch_Dominions-Game-jam-5/visual-proof/camera-comparison/interactive-test"
SOURCE = ROOT / "assets/generated/torch-animation-proof/01_klein-bench_00043_.png"
WORKFLOW = PROJECT / "hero-sweep-anticipation-workflow.json"
BASE = "http://127.0.0.1:8188"

PROMPT = (
    "Draw the same original Torch: Dominions female wayfarer as the supplied identity reference. Preserve her exact young face, long dark auburn ponytail, "
    "teal torn-edge asymmetrical mantle, charcoal leather armor, brown crossed belts and copper fasteners, trousers and brown high boots. Preserve the "
    "exact single violet-glass perforated lantern staff in her right hand and do not add, replace, duplicate or lose it. Use the same painterly anime game-art "
    "rendering, materials, palette and proportions. Full body, head and both boots entirely in frame, neutral flat cool-gray backdrop. Create one distinct "
    "torch-sweep ANTICIPATION action key pose: a low coiled stance with both knees visibly bent, torso and shoulders twisted away from intended swing, hips "
    "loaded over a deeply bent rear leg, forward boot planted, rear boot grounded, staff drawn close and diagonally behind the shoulder ready to reverse into "
    "the forward sweep, cape trailing opposite the loaded torso. Show a clearly different limb/torso/staff silhouette from the upright reference pose; this is "
    "not a finished strike or idle pose. One body, one pose, no collage, no motion blur. Avoid straight standing legs, upright centered stance, straight torso, "
    "or unchanged staff resting in the forward diagonal reference position. No text, logos, watermark, extra limbs, characters, props or weapons."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upload_image(path: Path) -> dict[str, object]:
    boundary = "----11vtTorchReferenceBoundary"
    payload = path.read_bytes()
    pieces = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"torch-hero-identity-reference.png\"\r\nContent-Type: image/png\r\n\r\n".encode(),
        payload,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    request = Request(
        BASE + "/upload/image",
        data=b"".join(pieces),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("name") != "torch-hero-identity-reference.png":
        raise RuntimeError(f"Unexpected local ComfyUI upload response: {result}")
    return result


def main() -> None:
    uploaded = upload_image(SOURCE)
    graph = json.loads((PROJECT / "encounter-art-workflow.json").read_text(encoding="utf-8"))
    graph["15"] = {"class_type": "LoadImage", "inputs": {"image": uploaded["name"]}}
    graph["16"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["15", 0], "vae": ["3", 0]}}
    graph["17"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": ["4", 0], "latent": ["16", 0]}}
    graph["18"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": ["6", 0], "latent": ["16", 0]}}
    graph["7"]["inputs"]["positive"] = ["17", 0]
    graph["7"]["inputs"]["negative"] = ["18", 0]
    graph["14"]["inputs"]["filename_prefix"] = "torch-dominions/hero-sweep-anticipation"
    graph["10"]["inputs"]["noise_seed"] = 7183418
    graph["4"]["inputs"]["text"] = PROMPT
    WORKFLOW.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    record = {
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(SOURCE),
        "source_use": "immutable identity and costume reference; original asset remains unchanged",
        "upload": uploaded,
        "workflow": WORKFLOW.relative_to(ROOT).as_posix(),
        "workflow_sha256": sha256(WORKFLOW),
        "prompt": PROMPT,
        "provider": "local ComfyUI 0.40.0 on 127.0.0.1; ComfyUI model and nodes are local",
        "model": "FLUX.2 Klein 4B distilled FP8; qwen_3_4b; flux2-vae",
        "seed": 7183418,
        "steps": 4,
        "cfg": 1.0,
        "conditioning": "VAEEncode the uploaded immutable hero image, then attach that same reference latent to positive and negative conditioning with ReferenceLatent",
        "output_folder": "generated-candidates",
        "review_status": "not_generated",
        "rights_review": "pending",
    }
    (PROJECT / "hero-sweep-anticipation-generation.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"uploaded": uploaded, "workflow": str(WORKFLOW), "workflow_sha256": record["workflow_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
