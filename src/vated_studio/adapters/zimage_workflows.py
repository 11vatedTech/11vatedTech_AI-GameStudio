"""Z-Image Turbo API-format workflow builder for ComfyUI.

Mirrors the official ComfyUI workflow template ``image_z_image_turbo``
(Comfy-Org workflow_templates): UNETLoader + CLIPLoader (Qwen 3 4B,
type ``lumina2`` per template) + VAELoader (``ae.safetensors``) +
CLIPTextEncode(positive) + ConditioningZeroOut(negative) +
EmptySD3LatentImage + ModelSamplingAuraFlow(shift 3) +
KSampler(res_multistep, simple, 8 steps, cfg 1.0) + VAEDecode.

License: model is Apache-2.0 (Tongyi-MAI); commercial game-asset use
permitted subject to ordinary depicted-content checks.
VRAM: bf16 weights need ~14-16GB in practice; 12GB GPUs are NOT a
dependable fit. This builder defaults to 512px to minimize working
memory, but that does not remove the weight constraint — expect the
bake-off to disqualify bf16 on 12GB fast if it OOMs.
"""
from __future__ import annotations

from typing import Any

ZIMAGE_UNET = "z_image_turbo_bf16.safetensors"
QWEN_ENCODER = "qwen_3_4b.safetensors"
ZIMAGE_VAE = "ae.safetensors"


def make_zimage_txt2img(*, prompt: str, width: int = 512, height: int = 512,
                        seed: int = 1, steps: int = 8,
                        cfg: float = 1.0) -> dict[str, Any]:
    """Build a native ComfyUI API-format Z-Image Turbo workflow."""
    if not prompt.strip():
        raise ValueError("prompt is required")
    if width % 16 or height % 16 or not (256 <= width <= 1024 and 256 <= height <= 1024):
        raise ValueError("width/height must be multiples of 16 in 256..1024")
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": ZIMAGE_UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": QWEN_ENCODER, "type": "lumina2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": ZIMAGE_VAE}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "6": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}},
        "7": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.0}},
        "8": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "9": {"class_type": "KSampler", "inputs": {
            "model": ["7", 0], "positive": ["4", 0], "negative": ["6", 0],
            "latent_image": ["8", 0], "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1.0}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "zimage-bakeoff"}},
    }
