"""Phase 8 graphics rows: one zoomed EN | JP crop per graphics-text element (docs/re/graphics.md), from two tours' finals.

gfxshots.py [--en work/qa/tour] [--jp work/qa/tour_jp] [--out work/qa/gfx]
then: qa_gate.py init work/qa/manifest.tsv ... work/qa/gfx --glob "*.png" and a verdict per crop.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

# name: (scene, crop x,y,w,h or None for the whole frame, JP override path or None)
SHOTS = {
    "g1_buttons_field": ("field_menu", "16,104,112,64", None),
    "g1_buttons_rest": ("field_menu2", "16,104,112,64", None),
    "g1_buttons_battle": ("battle_menu2", "40,108,96,64", None),
    "g1_buttons_map": ("field_map_town", "8,48,96,64", None),
    "g2_title_menu": ("title", None, None),
    "g4_status_box": ("field_status", "0,0,192,32", None),
    "g4_rank_list": ("field_status", "196,0,60,224", None),
    "g6_panel": ("field_menu", "0,174,256,50", None),
    "g7_race": ("field_status_equip", "0,0,256,52", None),
    "g8_year": ("config", "0,40,256,28", None),
    "g9_hud_rank": ("field_menu2", "0,0,256,24", None),
    "config_title": ("config", "0,0,256,40", None),
    "player_select_title": ("player_select", "0,0,256,32", None),
    "name_entry": ("name_entry", None, "work/qa/ne_jp2000/final.png"),
    "defeat": ("defeat", None, None),
    "credits": ("credits", None, None),
    "the_end": ("the_end", "0,150,256,60", None),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", default="work/qa/tour")
    ap.add_argument("--jp", default="work/qa/tour_jp")
    ap.add_argument("--out", default="work/qa/gfx")
    a = ap.parse_args()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name, (scene, crop, jp) in SHOTS.items():
        en = ROOT / a.en / scene / "final.png"
        jp = ROOT / (jp or f"{a.jp}/{scene}/final.png")
        cmd = [sys.executable, "-X", "utf8", f"{SKILL}/scripts/sheet.py", str(en), "--compare", str(jp),
               "--zoom", "3" if crop else "2", "--out", str(out / f"{name}.png")]
        if crop:
            cmd += ["--crop", crop]
        if not en.exists() or subprocess.run(cmd, capture_output=True).returncode:
            print("FAILED", name, en)
            bad += 1
    print(len(SHOTS) - bad, "of", len(SHOTS), "crops in", out)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
