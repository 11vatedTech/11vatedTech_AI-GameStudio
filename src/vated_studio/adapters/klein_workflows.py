"""FLUX.2 Klein 4B API-format workflow builder for ComfyUI.

Config B of the Visual Ceiling Challenge. Mirrors the official ComfyUI
workflow template ``image_flux2_klein_text_to_image`` (subgraph
"Text to Image (Flux.2 Klein 4B Distilled)"):

  UNETLoader -> CFGGuider <- CLIPTextEncode(positive)
  ConditioningZeroOut(CLIPTextEncode("")) -> CFGGuider(negative)
  KSamplerSelect(euler) + Flux2Scheduler(steps,w,h) + RandomNoise(seed)
  + EmptyFlux2LatentImage -> SamplerCustomAdvanced -> VAEDecode

Distilled = 4 steps / cfg 1.0. Base = 20 steps / cfg 5.0.
Deliberately NO ModelSamplingFlux / FluxGuidance: the distilled model has
guidance baked in, and patching it collapses output to unstructured fields
(verified experimentally: prompt-responsive noise).

Required files (see docs/research/model-and-tool-license-register.json):
  models/diffusion_models/flux-2-klein-4b-fp8.safetensors  (Apache-2.0, BFL)
  models/text_encoders/qwen_3_4b.safetensors               (Apache-2.0, Qwen)
  models/vae/flux2-vae.safetensors                        (Apache-2.0, BFL)
"""
from __future__ import annotations

from typing import Any

DISTILLED_UNET = "flux-2-klein-4b-fp8.safetensors"
BASE_UNET = "flux-2-klein-base-4b-fp8.safetensors"
QWEN_ENCODER = "qwen_3_4b.safetensors"
KLEIN_VAE = "flux2-vae.safetensors"
# UNETLoader "default" dtype silently mishandles BFL's fp8 file (flat-field
# output); explicit fp8_e4m3fn verified working on RTX 5070 Ti Laptop 12GB.
WEIGHT_DTYPE = "fp8_e4m3fn"


def make_klein_txt2img(*, prompt: str, width: int = 1024, height: int = 1024,
                       seed: int = 1, steps: int | None = None,
                       cfg: float | None = None, distilled: bool = True,
                       weight_dtype: str = WEIGHT_DTYPE) -> dict[str, Any]:
    """Build a native ComfyUI API-format Klein text-to-image workflow."""
    if not prompt.strip():
        raise ValueError("prompt is required")
    if width % 16 or height % 16 or not (256 <= width <= 2048 and 256 <= height <= 2048):
        raise ValueError("width/height must be multiples of 16 in 256..2048")
    unet = DISTILLED_UNET if distilled else BASE_UNET
    steps = 4 if steps is None and distilled else (20 if steps is None else steps)
    cfg = (1.0 if distilled else 5.0) if cfg is None else cfg
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": unet, "weight_dtype": weight_dtype}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": QWEN_ENCODER, "type": "flux2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": KLEIN_VAE}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {
            "clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {
            "clip": ["2", 0], "text": ""}},
        "6": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}},
        "7": {"class_type": "CFGGuider", "inputs": {
            "model": ["1", 0], "positive": ["4", 0],
            "negative": ["6", 0], "cfg": cfg}},
        "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9": {"class_type": "Flux2Scheduler", "inputs": {
            "steps": steps, "width": width, "height": height}},
        "10": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "11": {"class_type": "EmptyFlux2LatentImage", "inputs": {
            "width": width, "height": height, "batch_size": 1}},
        "12": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["10", 0], "guider": ["7", 0], "sampler": ["8", 0],
            "sigmas": ["9", 0], "latent_image": ["11", 0]}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["3", 0]}},
        "14": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": "11vatedtech/klein-bench", "images": ["13", 0]}},
    }


CEILING_BRIEF = {
    "hero": ("ember knight warden",
             "Ember Warden hero concept: lone fantasy action-game protagonist, tall ember-forged knight in deep crimson cloak over steel-blue plate, greatblade with living orange flame edge, strong readable silhouette, controlled metal and cloth materials, dramatic warm rim light against cold dark void, painterly game key art, no text, no watermark"),
    "enemy": ("frost wraith opponent",
              "Frost wraith enemy concept: menacing floating ice-shard creature, jagged translucent cyan body with white glowing core, sharp crystalline spikes, proportions utterly different from a human knight, cold blue-white palette, dark slate background, painterly game key art, no text, no watermark"),
    "arena": ("ember-forged arena environment",
              "Ember-forged battle arena concept: circular stone arena with scorched battleground, glowing ember cracks, ancient hearth-brazier at center, layered dark slate architecture ringed around, cold blue void pressing in beyond the ward-line, warm hearth light falloff against icy rim, atmospheric depth, clear central gameplay focal point, wide establishing shot, painterly game environment art, no characters, no text, no watermark"),
}
