import json
from pathlib import Path
import pytest

pytest.importorskip("PIL")
from PIL import Image, ImageDraw

from vated_studio.errors import StudioError
from vated_studio.assets.images import inspect_image, process_image, remove_edge_background, trim_transparent, build_contact_sheet
from vated_studio.assets.animation import audit_frames, assemble_animation
from vated_studio.assets.atlas import pack_atlas


def make_sprite(path: Path, *, box=(3, 3, 14, 17), color=(230, 80, 30, 255), size=(20, 20)):
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle(box, fill=color)
    image.save(path)
    return path


def test_inspect_image_provides_technical_not_aesthetic_signals(tmp_path):
    path = make_sprite(tmp_path / "sprite.png")
    report = inspect_image(path)
    assert report["nonempty"] is True
    assert report["width"] == 20 and report["height"] == 20
    assert len(report["sha256"]) == 64
    assert "not establish visual quality" in report["interpretation"]


def test_remove_edge_background_only_removes_edge_connected_color():
    image = Image.new("RGBA", (9, 9), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, 6, 6), fill=(200, 30, 30, 255))
    draw.point((4, 4), fill=(0, 0, 0, 255))
    result = remove_edge_background(image, "#000000", tolerance=0)
    assert result.getpixel((0, 0))[3] == 0
    assert result.getpixel((4, 4))[3] == 255
    assert result.getpixel((3, 3))[3] == 255


def test_trim_transparent_bounds_and_empty_image():
    image = Image.new("RGBA", (30, 20), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle((10, 5, 19, 14), fill="white")
    out = trim_transparent(image, padding=2)
    assert out.size == (14, 14)
    with pytest.raises(StudioError):
        trim_transparent(Image.new("RGBA", (5, 5), (0, 0, 0, 0)))


def test_process_image_and_invalid_operation(tmp_path):
    source = make_sprite(tmp_path / "source.png")
    destination = tmp_path / "output" / "processed.png"
    result = process_image(source, destination, {"resize": {"width": 40, "height": 40, "resample": "nearest"}})
    assert destination.is_file() and result["inspection"]["width"] == 40
    with pytest.raises(StudioError):
        process_image(source, tmp_path / "bad.png", {"magic": {}})
    with pytest.raises(StudioError):
        process_image(source, tmp_path / "bad2.png", {"resize": {"width": 0, "height": 10}})


def test_contact_sheet_and_atlas_manifests(tmp_path):
    a, b = make_sprite(tmp_path / "a.png"), make_sprite(tmp_path / "b.png", color=(20, 120, 220, 255))
    contact = build_contact_sheet([a, b], tmp_path / "contact.png", columns=2, labels=["A", "B"])
    assert contact["count"] == 2 and (tmp_path / "contact.png").is_file()
    atlas = pack_atlas([a, b], tmp_path / "atlas.png", max_width=64, padding=2)
    assert atlas["items"] == 2
    manifest = json.loads(Path(atlas["manifest"]).read_text())
    assert set(manifest["items"]) == {"a.png", "b.png"}


def test_animation_audit_and_assembly(tmp_path):
    a = make_sprite(tmp_path / "f0.png", box=(4, 3, 13, 16))
    b = make_sprite(tmp_path / "f1.png", box=(4, 2, 13, 15), color=(240, 180, 30, 255))
    audit = audit_frames([a, b], anchor="bottom-center")
    assert audit["frame_count"] == 2
    assert audit["dimensions_consistent"] is True
    outputs = assemble_animation([a, b], tmp_path / "anim" / "walk", fps=8)
    assert Path(outputs["gif"]).is_file()
    assert Path(outputs["spritesheet"]).is_file()
    manifest = json.loads(Path(outputs["manifest"]).read_text())
    assert manifest["frame_count"] == 2
    assert manifest["status"] == "assembled_requires_visual_review"


def test_animation_rejects_missing_or_invalid_frames(tmp_path):
    with pytest.raises(StudioError):
        audit_frames([])
    with pytest.raises(StudioError):
        assemble_animation([], tmp_path / "anim")
    blank = tmp_path / "blank.png"
    Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(blank)
    with pytest.raises(StudioError):
        assemble_animation([blank], tmp_path / "bad")


def test_service_protects_existing_outputs(service, workspace):
    source = make_sprite(workspace / "input.png")
    destination = workspace / "processed.png"
    destination.write_text("preserve me")
    with pytest.raises(StudioError) as exc:
        service.execute("asset.process", {"source": "input.png", "destination": "processed.png", "operations": {}})
    assert exc.value.code == "output_exists"
    assert destination.read_text() == "preserve me"
