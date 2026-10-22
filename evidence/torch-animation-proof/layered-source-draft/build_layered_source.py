from __future__ import annotations

"""Build a reversible layer-review package from one opaque Torch concept pose.

This is an extraction experiment, not an approved rig or game-ready sprite.
Uses system Python with OpenCV, NumPy, and Pillow available in this workspace.
"""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZIP_STORED
import hashlib
import json
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "evidence/torch-animation-proof"
OUT = EVIDENCE / "layered-source-draft"
SOURCE = ROOT / "assets/generated/torch-animation-proof/01_klein-bench_00043_.png"
WHOLE_MASK = EVIDENCE / "grabcut-alpha-mask.png"
SOURCE_SIZE = (1024, 1024)
# Whole-character GrabCut mask was tightly cropped at this source-image origin.
MASK_ORIGIN = (90, 60)

# Coarse hand-traced contour for a review-only extraction: lantern + staff +
# gripping hand + partial attached sleeve. It deliberately avoids swallowing
# torso/cape pixels; the blunt sleeve end is NOT a finished shoulder seam.
ARM_TORCH_POLYGON = [
    (112, 97), (144, 96), (171, 107), (191, 125), (209, 147),
    (229, 171), (250, 196), (270, 218), (291, 239), (310, 258),
    (330, 276), (350, 291), (371, 302), (389, 308),
    # Keep the arm as a narrow extension from the grip; cap at the sleeve
    # overlap rather than crossing into the breastplate or cape.
    (385, 307), (399, 311), (411, 319), (421, 329), (428, 341),
    (430, 352), (424, 361), (414, 364), (402, 359), (390, 350),
    (381, 339), (373, 323), (356, 316), (338, 308), (319, 298),
        (356, 316), (338, 308), (319, 298), (301, 287), (283, 274),
    (264, 259), (246, 242), (228, 224), (209, 204), (191, 184),
    (173, 163), (155, 144), (138, 126), (123, 110),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGB")
    if source.size != SOURCE_SIZE:
        raise ValueError(f"Expected {SOURCE_SIZE}, got {source.size}")
    mask_image = Image.open(WHOLE_MASK).convert("L")
    if mask_image.size != (870, 938):
        raise ValueError(f"Unexpected prior whole-character mask size: {mask_image.size}")

    full_alpha = Image.new("L", SOURCE_SIZE, 0)
    full_alpha.paste(mask_image, MASK_ORIGIN)
    character_alpha = np.asarray(full_alpha, dtype=np.uint8)

    polygon = Image.new("L", SOURCE_SIZE, 0)
    ImageDraw.Draw(polygon).polygon(ARM_TORCH_POLYGON, fill=255)
    polygon_alpha = np.asarray(polygon, dtype=np.uint8)
    # Use the earlier whole-character matte to avoid including the flat backdrop.
    arm_alpha = np.minimum(character_alpha, polygon_alpha)
    # Slight antialias only, not edge reconstruction. Keep layer on full canvas.
    arm_alpha = cv2.GaussianBlur(arm_alpha, (3, 3), 0.45)
    rgba = source.convert("RGBA")
    rgba.putalpha(Image.fromarray(arm_alpha, mode="L"))

    save_png(source, OUT / "source-reference.png")
    save_png(rgba, OUT / "torch-arm-lantern-cutout-candidate.png")
    save_png(Image.fromarray(arm_alpha, mode="L"), OUT / "torch-arm-lantern-mask-candidate.png")

    # The highlight image reveals what the candidate mask covers over the source.
    marked = source.convert("RGBA")
    tint = Image.new("RGBA", SOURCE_SIZE, (85, 210, 255, 0))
    tint.putalpha(Image.fromarray((arm_alpha.astype(np.float32) * 0.38).clip(0, 255).astype(np.uint8)))
    marked = Image.alpha_composite(marked, tint)
    edge = cv2.Canny(arm_alpha, 50, 150)
    edge_image = Image.fromarray(edge).convert("L")
    red = Image.new("RGBA", SOURCE_SIZE, (255, 80, 90, 0))
    red.putalpha(edge_image)
    marked = Image.alpha_composite(marked, red)
    save_png(marked.convert("RGB"), OUT / "mask-review-overlay.jpg")

    # Contact sheet: source, alpha-matted extracted part, and mask against a checkerboard.
    tile_w, tile_h = 512, 560
    sheet = Image.new("RGB", (tile_w * 3, tile_h + 58), (20, 25, 29))
    labels = ["LOCKED SOURCE · ORIGINAL", "CANDIDATE · PARTIAL ARM + TORCH", "CANDIDATE · ALPHA MASK"]
    font_path = "C:/Windows/Fonts/arial.ttf"
    font = ImageFont.truetype(font_path, 19) if Path(font_path).exists() else ImageFont.load_default()
    for idx, label in enumerate(labels):
        x = idx * tile_w
        if idx == 0:
            panel = source.copy()
        elif idx == 1:
            panel = rgba.copy()
        else:
            panel = Image.new("RGBA", SOURCE_SIZE, (0, 0, 0, 0))
            panel.paste((235, 235, 235, 255), (0, 0, *SOURCE_SIZE), Image.fromarray(arm_alpha, mode="L"))
        panel.thumbnail((tile_w - 20, tile_h - 20), Image.Resampling.LANCZOS)
        back = Image.new("RGBA", (tile_w, tile_h), (49, 54, 58, 255))
        draw = ImageDraw.Draw(back)
        checker = 24
        for yy in range(0, tile_h, checker):
            for xx in range(0, tile_w, checker):
                if ((xx // checker) + (yy // checker)) % 2:
                    draw.rectangle((xx, yy, xx + checker - 1, yy + checker - 1), fill=(68, 73, 78, 255))
        back.alpha_composite(panel.convert("RGBA"), ((tile_w-panel.width)//2, (tile_h-panel.height)//2))
        sheet.paste(back.convert("RGB"), (x, 0))
        ImageDraw.Draw(sheet).text((x + 12, tile_h + 12), label, font=font, fill=(231, 220, 248))
    save_png(sheet, OUT / "layered-source-contact-sheet.png")

    # Close-up alpha preview: transparency, antialiasing, and the blunt sleeve
    # endpoint are visible against a checkerboard, not mistaken for finished art.
    detail_box = (80, 75, 670, 500)
    detail = rgba.crop(detail_box)
    detail_back = Image.new("RGBA", detail.size, (45, 50, 56, 255))
    detail_draw = ImageDraw.Draw(detail_back)
    for yy in range(0, detail.height, 20):
        for xx in range(0, detail.width, 20):
            if ((xx // 20) + (yy // 20)) % 2:
                detail_draw.rectangle((xx, yy, xx + 19, yy + 19), fill=(70, 75, 82, 255))
    detail_back.alpha_composite(detail)
    save_png(detail_back.convert("RGB").resize((1180, 850), Image.Resampling.LANCZOS), OUT / "arm-torch-transparent-detail.png")

    # Focused mask coverage overlay in the source coordinate window.
    overlay = source.crop(detail_box).convert("RGBA")
    local_alpha = Image.fromarray(arm_alpha, mode="L").crop(detail_box)
    cyan = Image.new("RGBA", overlay.size, (35, 190, 255, 0))
    cyan.putalpha(local_alpha.point(lambda value: int(value * 0.46)))
    overlay = Image.alpha_composite(overlay, cyan).convert("RGB")
    save_png(overlay.resize((1180, 850), Image.Resampling.LANCZOS), OUT / "mask-coordinate-review.png")

    source_hash = sha256(SOURCE)
    mask_hash = sha256(WHOLE_MASK)
    arm_path = OUT / "torch-arm-lantern-cutout-candidate.png"
    alpha_bbox = Image.fromarray(arm_alpha, "L").getbbox()
    manifest = {
        "format": "torch-layered-source-draft/1",
        "status": "prototype_requires_manual_cleanup",
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": source_hash,
            "size": list(SOURCE_SIZE),
            "mode": "RGB",
            "preserved_unchanged": True,
        },
        "derived_from": {
            "whole_character_mask": WHOLE_MASK.relative_to(ROOT).as_posix(),
            "whole_character_mask_sha256": mask_hash,
            "mask_origin_on_source": list(MASK_ORIGIN),
        },
        "method": {
            "foreground": "Intersect prior local GrabCut whole-character matte with a manually traced arm/lantern polygon; apply 3x3 Gaussian alpha antialias.",
            "software": {"opencv": cv2.__version__, "numpy": np.__version__, "pillow": Image.__version__},
            "remote_services": False,
            "new_model_weights": False,
        },
        "canvas": {"width": SOURCE_SIZE[0], "height": SOURCE_SIZE[1], "coordinate_origin": "top-left"},
        "proposed_pivot": None,
        "pivot_status": "Not set: the candidate ends in a partial sleeve cut and does not reach an approved shoulder joint.",
        "candidate_part": {
            "name": "Torch + gripping hand + partial attached arm/sleeve (single review layer; grip preserved)",
            "path": arm_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(arm_path),
            "mask_bbox": list(alpha_bbox) if alpha_bbox else None,
            "mask_polygon_source_xy": ARM_TORCH_POLYGON,
            "known_defects": [
                "The first contour swallowed torso/cape pixels; this revised contour removes that broad wedge, but the remaining sleeve end is visibly blunt and incomplete.",
                "No repaired body plate or overlap exists beneath the extracted part; the source keeps the original full character visible as a locked reference.",
                "No valid shoulder pivot or elbow articulation: staff, grip, hand, and partial sleeve remain one review layer.",
                "Lantern plume/smoke pixels are not isolated and remain attached to the prop candidate.",
                "This is not a production-ready rig, at-rest replacement composite, or motion pass.",
            ],
        },
        "layers": [
            {"name": "Torch + hand + partial sleeve — review mask only; hidden by default", "path": arm_path.relative_to(ROOT).as_posix(), "visible": False},
            {"name": "Original pose — locked reference; visible by default", "path": (OUT / "source-reference.png").relative_to(ROOT).as_posix(), "visible": True},
        ],
        "next_required_work": [
            "Have an artist author a clean shoulder/sleeve separation and recover the occluded body pixels in a separate, non-destructive body plate.",
            "Isolate the lantern plume/smoke as a separate VFX layer and approve the staff/hand ownership boundary.",
            "Set a shoulder pivot only after the arm part reaches a hand-clean anatomical joint; preserve the original source unchanged.",
            "Only then test a small shoulder rotation and cutout seams at actual game scale.",
        ],
    }
    manifest_path = OUT / "layer-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # OpenRaster: standard ZIP-based multilayer interchange. Original is the
    # merged/visible base; cutout remains separate and hidden pending repair.
    ora = OUT / "torch-protagonist-layer-source-draft.ora"
    root = ET.Element("image", {"version": "0.0.1", "w": "1024", "h": "1024", "name": "Torch protagonist — layer source draft"})
    stack = ET.SubElement(root, "stack")
    ET.SubElement(stack, "layer", {
        "name": "Torch + gripping hand + partial arm — review mask only; hidden by default",
        "src": "data/arm.png", "opacity": "1.0", "visibility": "hidden", "composite-op": "svg:src-over", "x": "0", "y": "0",
    })
    ET.SubElement(stack, "layer", {
        "name": "Original pose — locked reference",
        "src": "data/source.png", "opacity": "1.0", "visibility": "visible", "composite-op": "svg:src-over", "x": "0", "y": "0",
    })
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    thumb = source.copy()
    thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
    with ZipFile(ora, "w") as zf:
        zf.writestr("mimetype", "image/openraster", compress_type=ZIP_STORED)
        zf.writestr("stack.xml", xml_bytes, compress_type=ZIP_DEFLATED)
        zf.write(OUT / "torch-arm-lantern-cutout-candidate.png", "data/arm.png", compress_type=ZIP_DEFLATED)
        zf.write(OUT / "source-reference.png", "data/source.png", compress_type=ZIP_DEFLATED)
        zf.write(OUT / "layer-manifest.json", "data/layer-manifest.json", compress_type=ZIP_DEFLATED)
        zf.writestr("mergedimage.png", source_to_png_bytes(source), compress_type=ZIP_DEFLATED)
        zf.writestr("Thumbnails/thumbnail.png", image_to_png_bytes(thumb), compress_type=ZIP_DEFLATED)

    result = {
        "source_sha256": source_hash,
        "whole_mask_sha256": mask_hash,
        "arm_layer_sha256": sha256(arm_path),
        "ora_sha256": sha256(ora),
        "arm_layer_size": list(rgba.size),
        "alpha_bbox": list(alpha_bbox) if alpha_bbox else None,
        "alpha_coverage_fraction": round(float((arm_alpha > 0).mean()), 6),
        "output_dir": OUT.relative_to(ROOT).as_posix(),
    }
    (OUT / "build-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    board = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Torch layered-source review · draft</title>
<style>
:root{color-scheme:dark}body{margin:0;background:#101318;color:#eee;font:16px/1.5 system-ui,sans-serif}main{max-width:1320px;margin:auto;padding:28px}h1,h2{line-height:1.15}p,li{color:#c7cbd4}.status{padding:14px 18px;border:1px solid #b77d39;background:#332719;border-radius:8px;color:#ffe0ae}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}.card{background:#1a1e25;border:1px solid #343b47;border-radius:10px;padding:12px}.card img{display:block;width:100%;height:auto;background:repeating-conic-gradient(#555 0 25%,#383838 0 50%) 50%/24px 24px}.wide{grid-column:1/-1}.mono{font:13px/1.45 ui-monospace,monospace;overflow-wrap:anywhere;color:#aeb7c6}a{color:#a7ccff}footer{margin-top:28px;border-top:1px solid #343b47;padding-top:16px;color:#9ca4b1}
</style><main>
<h1>Torch pose · layered-source extraction review</h1>
<p class="status"><strong>Draft only — not a usable rig.</strong> The broad torso/cape mask contamination was removed. Current extraction retains the staff, torch, painted grip, and a partial sleeve; its blunt sleeve termination has no valid shoulder pivot or repaired body plate.</p>
<p>Source image is kept unchanged. Layer candidate is hidden by default in the OpenRaster file; the visible layer and merged preview remain the original full pose. Review images expose defects rather than implying approval.</p>
<section class="grid">
<article class="card wide"><h2>Source / extraction / alpha mask</h2><img src="layered-source-contact-sheet.png" alt="Original source beside partial arm and torch extraction and alpha mask"></article>
<article class="card"><h2>Mask coverage on source</h2><img src="mask-coordinate-review.png" alt="Cyan overlay shows extracted pixels and partial sleeve end"></article>
<article class="card"><h2>Transparent-edge review</h2><img src="arm-torch-transparent-detail.png" alt="Torch and partial sleeve on checkerboard transparency"></article>
<article class="card"><h2>Full-source mask overlay</h2><img src="mask-review-overlay.jpg" alt="Full character with extraction boundary"></article>
<article class="card"><h2>Layered interchange file</h2><p><a href="torch-protagonist-layer-source-draft.ora">OpenRaster draft (.ora)</a></p><p><a href="layer-manifest.json">Layer manifest / provenance</a> · <a href="build-result.json">Build hashes</a></p><p class="mono">Candidate layer: hidden by default. Original pose: visible, locked reference.</p></article>
<article class="card"><h2>Human art gate</h2><ul><li>Author a hand-clean shoulder/sleeve separation and separate body plate.</li><li>Separate lantern plume/smoke; review staff and hand ownership.</li><li>Approve the pivot, then test overlap and motion at game scale.</li></ul></article>
</section><footer>Local extraction prototype. No remote service/model was used. No animation, engine integration, art-direction approval, or human approval is claimed.</footer></main></html>'''
    (OUT / "index.html").write_text(board, encoding="utf-8")
    print(json.dumps(result, indent=2))


def source_to_png_bytes(image: Image.Image) -> bytes:
    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def image_to_png_bytes(image: Image.Image) -> bytes:
    return source_to_png_bytes(image)


if __name__ == "__main__":
    main()
