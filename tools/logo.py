"""Title logo in English (docs/re/graphics.md G3, D22): ただいま 勇者募集中 おかわり -> NOW / HEROES WANTED / MORE.

The logo is BG2 tile rows 0-15, cols 4-28 (tilemap: block 795, 32 entries a row), tiles 0x000-0x0FF from block 793 and
0x300-0x324 from block 794 (gfx.title uses 794 from tile 0x25 on). Each cell has its own palette (1, 2 or 3); the stone and
sword greys sit at other indices in palette 3, so art copied between cells is remapped (P13). The four おかわり balls are
16x16 sprites, OBJ palette 7, tiles in block 789 (tile t at t * 32).

Order: clear the Japanese (text, outline, drop shadow -> stone), extend the sword blade the kanji hid (row 96's profile
slid up its axis), rebuild both crossguard arms (the upper one's root, the lower one mirrored from the upper), then the
English over it: lettering from fonts/logo_text.txt (tools/logo_text.py, Titan One) in the kanji's own indices so the
title's palette cycling still runs, and the balls redrawn with monoline letters wrapped onto the sphere.
"""
import math
from collections import Counter, defaultdict
from pathlib import Path

import font

ROOT = Path(__file__).resolve().parents[1]
C0, CW, RH = 4, 25, 16
W, H = CW * 8, RH * 8
STONE = {1: 0xD, 2: 0xD, 3: 0xC}
P13 = {0xA: 0xD, 0xB: 0xB, 0xC: 0xB, 0xD: 0xC, 0xE: 0xE, 0xF: 0xF}  # a pal 1/2 grey -> the same colour in pal 3
# never pal 3 index 1-3: the title menu lights its lines by those entries (sword flickered with the cursor)
WHITE, DARK = 0xB, 0xF
GROUPS = {"left": [(1, 2, 3), (4, 5, 6), (7, 8, 9)], "right": [(4, 5, 6), (1, 2, 3)]}  # (main, mid, light) per letter:
# green pink blue (勇 者 募 in pal 1), orange red (集 中 in pal 2)
REF, SLOPE, BX0, BX1 = 96, 1.5, 46, 85  # blade: row REF, x BX0-BX1 is its profile; 1.5 px right per row up
RING = (153, 35, 15)  # guard ring centre; radius 12 is the ring, 12-15 its rim (the blade only replaces stone there)
KNOB = (130, 11)  # end of the upper crossguard arm
BALLS = [(0xE0, 0xE2, 0xE4, 0xE6), (0xE8, 0xEA, 0xEC, 0xEE), (0x10A, 0x10C, 0x10E, 0x14E), (0x16E, 0x18E, 0x1AE, 0x1CE)]
# OAM 41-56: per ball the 16x16 sprites top left, top right, bottom left, bottom right
BALL_WORD = "MORE"


def unplanar(t):
    return [[sum((t[(p >> 1) * 16 + y * 2 + (p & 1)] >> (7 - x) & 1) << p for p in range(4)) for x in range(8)] for y in range(8)]


def dil(s, r):
    return {(x + dx, y + dy) for x, y in s for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r + r}


def text_zones():
    zones, cur = {}, None
    for line in (ROOT / "fonts/logo_text.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        if line.startswith("zone "):
            _, name, x, y, _ = line.split(" ", 4)
            cur = zones[name] = (int(x), int(y), [])
        else:
            cur[2].append(line)
    out = {}
    for name, (x0, y0, rows) in zones.items():
        letters = defaultdict(set)
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c != ".":
                    letters[int(c, 36)].add((x0 + x, y0 + y))
        out[name] = [letters[k] for k in sorted(letters)]
    return out


class Logo:
    def __init__(self, b793, b794, b795):
        self.b793, self.b794 = bytearray(b793), bytearray(b794)
        self.cells = {}
        self.idx = [[0] * W for _ in range(H)]
        self.pn = [[0] * W for _ in range(H)]
        for r in range(RH):
            for c in range(CW):
                o = r * 64 + (C0 + c) * 2
                e = b795[o] | b795[o + 1] << 8
                assert not e >> 14, (r, c)  # no flips in the logo
                t, p = e & 0x3FF, e >> 10 & 7
                assert t < 0x100 or 0x300 <= t < 0x325, hex(t)
                self.cells[r, c] = (t, p)
                for y, line in enumerate(unplanar(self.tile(t))):
                    self.idx[r * 8 + y][c * 8:c * 8 + 8] = line
                    self.pn[r * 8 + y][c * 8:c * 8 + 8] = [p] * 8

    def tile(self, t):
        b, k = (self.b793, t) if t < 0x100 else (self.b794, t - 0x300)
        return b[k * 32:k * 32 + 32]

    def store(self):
        uses = defaultdict(list)
        for rc, (t, _) in self.cells.items():
            uses[t].append(rc)
        for t, rcs in uses.items():
            px = {tuple(tuple(self.idx[r * 8 + y][c * 8:c * 8 + 8]) for y in range(8)) for r, c in rcs}
            assert len(px) == 1, f"tile {t:03X} is shared by {rcs} and would differ"
            r, c = rcs[0]
            data = font.planar([self.idx[r * 8 + y][c * 8:c * 8 + 8] for y in range(8)])
            b, k = (self.b793, t) if t < 0x100 else (self.b794, t - 0x300)
            b[k * 32:k * 32 + 32] = data
        return bytes(self.b793), bytes(self.b794)

    def put(self, x, y, v):
        if 0 <= x < W and 0 <= y < H:
            self.idx[y][x] = v

    def from_pal1(self, v, x, y):
        return P13[v] if self.pn[y][x] == 3 else v

    def clear(self, box, textidx, pals, top_edge=None):
        """Text (an index in textidx, in a cell of pals), its white outline and dark drop shadow -> stone (sky above top_edge)."""
        x0, y0, x1, y1 = box
        idx, pn = self.idx, self.pn
        t = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if pn[y][x] in pals and idx[y][x] in textidx}
        near = dil(t, 2)
        sh = {(x + k, y + k) for x, y in near for k in range(5)}
        for y in range(y0, y1):
            for x in range(x0, x1):
                if (x, y) in near or ((x, y) in sh and idx[y][x] in (0xE, 0xF, 0xB)):
                    idx[y][x] = 0 if top_edge is not None and y < top_edge else STONE[pn[y][x]]

    def sword(self, src):
        idx, pn = self.idx, self.pn
        for y in range(28, REF):
            for x in range(W):
                xs = round(x - SLOPE * (REF - y))
                d2 = (x - RING[0]) ** 2 + (y - RING[1]) ** 2
                if d2 <= 12 ** 2:
                    continue
                if BX0 <= xs < BX1 and idx[y][x] and (d2 > RING[2] ** 2 or idx[y][x] == STONE[pn[y][x]]):
                    v = src[REF][xs]
                    if v:
                        idx[y][x] = self.from_pal1(v, x, y)
        ax, ay = KNOB[0] - RING[0], KNOB[1] - RING[1]
        n = math.hypot(ax, ay)
        wx, wy = -ay / n, ax / n  # square to the arm
        arm = {(x, y) for y in range(8, 24) for x in range(124, 148) if src[y][x]}
        assert all(self.pn[y][x] == 1 for x, y in arm)

        def ring(x, y):
            return (x - RING[0]) ** 2 + (y - RING[1]) ** 2

        # the upper arm's root (cleared with き): its shaft (rows 12-20) repeated on to the ring, 2 px shadow on the stone
        upper = {}
        for y in range(18, 34):
            for x in range(128, 152):
                if ring(x, y) <= 144 or (x, y) in arm and y < 21:
                    continue
                for k in range(1, 14):
                    t = (round(x + k * ax / n), round(y + k * ay / n))
                    if t in arm and 12 <= t[1] < 21:
                        upper[x, y] = src[t[1]][t[0]]
                        break
        for x, y in {(x + k, y + k) for x, y in upper for k in (1, 2)} - set(upper) - arm:
            if idx[y][x] == STONE[pn[y][x]] and ring(x, y) > 144:
                idx[y][x] = DARK
        for (x, y), v in upper.items():
            idx[y][x] = self.from_pal1(v, x, y)

        # the lower arm (hidden by 中): the upper one mirrored across the line through the ring square to it, so it points
        # the other way and keeps its lit side; near the ring the shaft is repeated back to the ring's edge
        def refl(x, y):
            dx, dy = x - RING[0], y - RING[1]
            d = dx * wx + dy * wy
            return round(RING[0] + 2 * d * wx - dx), round(RING[1] + 2 * d * wy - dy)

        lower = {}
        for y in range(30, 75):
            for x in range(150, W):
                s = refl(x, y)
                for k in range(9 if ring(x, y) < 400 else 1):
                    t = (round(s[0] + k * ax / n), round(s[1] + k * ay / n))
                    if t in arm and t[1] < 21:
                        s = t
                        break
                if s in arm and ring(x, y) > 144:
                    lower[x, y] = src[s[1]][s[0]]
        for x, y in {(x + k, y + k) for x, y in lower for k in (1, 2)} - set(lower):
            if 0 <= x < W and 0 <= y < H and idx[y][x] and ring(x, y) > 144:
                idx[y][x] = DARK
        for (x, y), v in lower.items():
            idx[y][x] = self.from_pal1(v, x, y)
        for y in range(20, 29):  # stray bits of the old dakuten shadow left in the sky
            for x in range(40, 128):
                if idx[y][x] in (0xE, 0xF) and (x, y) not in arm:
                    idx[y][x] = 0

    def main_text(self, letters, groups):
        """Kanji style: rim-lit fill (lightest on the top/left edge, mid one in), 1 px white outline, 3 px dark shadow."""
        allb = set().union(*letters)
        ol = dil(allb, 1)
        sh = {(x + k, y + k) for x, y in ol for k in (1, 2, 3)}
        for x, y in sh - ol:
            self.put(x, y, DARK)
        for x, y in ol - allb:
            self.put(x, y, WHITE)
        for i, p in enumerate(letters):
            main, mid, light = groups[i % len(groups)]
            for x, y in p:
                if (x, y - 1) not in p or (x - 1, y) not in p:
                    v = light
                elif (x, y - 2) not in p or (x - 2, y) not in p:
                    v = mid
                else:
                    v = main
                self.put(x, y, v)

    def top_text(self, letters):
        """ただいま style (pal 3): grey fill c, rim a, red border 9 (dark red 8 lower right), 2 px dark shadow."""
        allb = set().union(*letters)
        bd = dil(allb, 1) - allb
        for x, y in {(x + k, y + k) for x, y in bd | allb for k in (1, 2)} - bd - allb:
            self.put(x, y, DARK)
        for x, y in bd:
            self.put(x, y, 8 if (x - 1, y - 1) in allb and (x + 1, y + 1) not in allb else 9)
        for x, y in allb:
            edge = any(q not in allb for q in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
            self.put(x, y, 0xA if edge else 0xC)


def bg(b793, b794, b795):
    """Blocks 793 and 794 with the English logo."""
    lg = Logo(b793, b794, b795)
    src = [row[:] for row in lg.idx]
    lg.clear((0, 46, 200, 92), set(range(1, 10)), {1, 2})  # 勇者募集中
    lg.clear((40, 22, 144, 50), {8, 9, 0xA}, {3}, top_edge=29)  # ただいま
    lg.sword(src)
    z = text_zones()
    assert all(x < 96 for p in z["left"] for x, _ in p) and all(96 <= x < 192 for p in z["right"] for x, _ in p)  # palette halves
    lg.main_text(z["left"], GROUPS["left"])
    lg.main_text(z["right"], GROUPS["right"])
    lg.top_text(z["top"])
    return lg.store()


# --- balls -------------------------------------------------------------------------------------------------------------
_O = [(0.5 + 0.5 * math.sin(a * math.pi / 12), 0.5 - 0.5 * math.cos(a * math.pi / 12)) for a in range(25)]
STROKES = {  # monoline centrelines in a unit box (x right, y down), and the box's width / height
    "M": ([[(0, 1), (0, 0), (0.5, 0.6), (1, 0), (1, 1)]], 0.95),
    "O": ([_O], 0.9),
    "R": ([[(0, 1), (0, 0), (0.62, 0), (0.88, 0.1), (0.95, 0.27), (0.88, 0.42), (0.62, 0.52), (0, 0.52)],
           [(0.5, 0.52), (0.95, 1)]], 0.78),
    "E": ([[(0.95, 0), (0, 0), (0, 1), (0.95, 1)], [(0, 0.5), (0.8, 0.5)]], 0.7),
}
ORANGE = {1, 2, 3, 4}
BLUE_OF = {1: 8, 2: 6, 3: 7, 4: 0xF}  # the ball's shade under a letter pixel -> the letter's shade
SPAN, HALF, TILT = 0.6, 0.16, -0.1  # letter half height and half stroke on the sphere (radians), latitude of its centre
SHINE = [".rrr.", "rcbcr", "rbbbr", "rcbcr", ".rrr."]  # at ball (10, 9), as on お か わ: r = pale blue 5 / pale orange 1


def ball_px(b789, tiles):
    g = [[0] * 32 for _ in range(32)]
    for s, t in enumerate(tiles):
        for dy in range(2):
            for dx in range(2):
                tt = ((t & ~0xF) | (t + dx) & 0xF) + dy * 16
                for y, line in enumerate(unplanar(b789[tt * 32:tt * 32 + 32])):
                    g[s // 2 * 16 + dy * 8 + y][s % 2 * 16 + dx * 8:s % 2 * 16 + dx * 8 + 8] = line
    return g


def seg_dist(px, py, a, b):
    (ax, ay), (bx, by) = a, b
    vx, vy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy or 1)))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


def balls(b789):
    """Block 789 with M O R E on the balls: a pixel is ink when its point on the sphere (longitude, latitude) is within HALF
    of the letter's centreline, so strokes have one width on the surface and only foreshorten toward the rim. The ball's
    shading under the letters comes from the four originals (the commonest orange at each pixel)."""
    out = bytearray(b789)
    org = [ball_px(b789, t) for t in BALLS]
    mask = {(x, y) for y in range(32) for x in range(32) if any(b[y][x] for b in org)}
    zone = {}
    for x, y in mask:
        votes = Counter(b[y][x] for b in org if b[y][x] in ORANGE)
        if votes:
            zone[x, y] = votes.most_common(1)[0][0]
    while len(zone) < len(mask):
        for x, y in mask - set(zone):
            nb = [zone[p] for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)) if p in zone]
            if nb:
                zone[x, y] = Counter(nb).most_common(1)[0][0]
    cx = sum(x for x, _ in mask) / len(mask)
    cy = sum(y for _, y in mask) / len(mask)
    r = math.sqrt(len(mask) / math.pi)
    ct, st = math.cos(TILT), math.sin(TILT)
    for ch, tiles in zip(BALL_WORD, BALLS):
        lines, aspect = STROKES[ch]
        hw = SPAN * aspect
        segs = [((-hw + 2 * hw * a[0], -SPAN + 2 * SPAN * a[1]), (-hw + 2 * hw * b[0], -SPAN + 2 * SPAN * b[1]))
                for ln in lines for a, b in zip(ln, ln[1:])]
        g = [[0] * 32 for _ in range(32)]
        for x, y in mask:
            hits = 0
            for sy in range(4):
                for sx in range(4):
                    dx, dy = (x + (sx + 0.5) / 4 - cx) / r, (y + (sy + 0.5) / 4 - cy) / r
                    q = dx * dx + dy * dy
                    if q >= 1:
                        continue
                    dz = math.sqrt(1 - q)
                    py, pz = dy * ct - dz * st, dy * st + dz * ct  # tilt about the x axis
                    lon, lat = math.atan2(dx, pz), math.asin(max(-1, min(1, py)))
                    if min(seg_dist(lon, lat, a, b) for a, b in segs) <= HALF:
                        hits += 1
            g[y][x] = BLUE_OF[zone[x, y]] if hits >= 7 else zone[x, y]
        for dy, row in enumerate(SHINE):
            for dx, c in enumerate(row):
                x, y = 10 + dx, 9 + dy
                if c == "r":
                    g[y][x] = 5 if g[y][x] in BLUE_OF.values() else 1
                elif c != ".":
                    g[y][x] = 0xB if c == "b" else 0xC
        for s, t in enumerate(tiles):
            for dy in range(2):
                for dx in range(2):
                    tt = ((t & ~0xF) | (t + dx) & 0xF) + dy * 16
                    px = [g[s // 2 * 16 + dy * 8 + y][s % 2 * 16 + dx * 8:s % 2 * 16 + dx * 8 + 8] for y in range(8)]
                    out[tt * 32:tt * 32 + 32] = font.planar(px)
    return bytes(out)
