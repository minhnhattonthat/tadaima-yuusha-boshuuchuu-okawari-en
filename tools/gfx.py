"""Graphics text redrawn in English at build time (docs/re/graphics.md G1, G2). Called by insert.apply on the unpacked blocks.

buttons(): block 002, 28 buttons of 32x16 (4x2 tiles, 4 to a sheet row of 16 tiles). Inside the border (x 2-29, y 2-13) the ground is
index 11, ink 15, shadow 1 to the right. English from fonts/spleen-5x8.bdf with a 3-px t, centred.
title(): block 794, the title menu しなりおモード / ぱーてぃーモード / つづきをする. Tiles 0x325-0x36F of BG2 (VRAM tile 0x300 = block
tile 0), one per cell of a 14x6 box (tilemap read off a PPU dump, work/qa/ppu_title); cells showing the shared blank tile 0x365 can't
take ink. Line n draws in index n+1 (the menu lights a line by its palette entry), ground 4, no shadow; English in fonts/vwf.txt.
"""
import font

BUTTONS = [  # JP per sheet row; None keeps the art (PASS, SOS! and the frame pieces are already Latin or not text)
    ["Move", "Magic", "Orb", "Items"],  # 移動 魔法 オーブ 道具 (turn menu)
    ["Rest", "Map", "Status", None],  # 休憩 地図 状態 PASS (X menu)
    ["Attack", "Magic", "Orb", "Items"],  # 攻撃 魔法 オーブ 道具 (battle)
    ["Guard", "Run", "Auto", None],  # 防御 逃げる オート SOS!
    [None, None, None, "Yes"],  # frame, hand, arrow, はい
    ["Stats", "Equip", "Magic", "No"],  # 能力値 装備 魔法 いいえ (status menu)
    ["Quest", "Town", "Hero", "Shops"],  # クエスト 街 勇者 施設 (map menu)
]
NARROW = {"t": [0x40, 0x40, 0xE0, 0x40, 0x40, 0x40, 0x60, 0], }  # 3 px wide, so Status and Attack fit 28 px
GROUND, INK, SHADOW = 11, 15, 1

TITLE = ["Scenario Mode", "Party Mode", "Continue"]  # しなりおモード ぱーてぃーモード つづきをする
TITLE_ROWS = [(9, 0x25, 13), (9, 0x32, 13), (9, 0x3F, 13), (9, 0x4C, 14), (9, 0x5A, 11), (10, 0x66, 10)]  # per box row: first col, block tile, count
TITLE_COL0, TITLE_W, TITLE_X = 9, 14, 8  # box cols 9-22; text starts 8 px in, past the blank cell of the last row


def unplanar(t):
    return [[sum((t[(p >> 1) * 16 + y * 2 + (p & 1)] >> (7 - x) & 1) << p for p in range(4)) for x in range(8)] for y in range(8)]


def get(sheet, tile):
    return unplanar(sheet[tile * 32:tile * 32 + 32])


def put(sheet, tile, px):
    sheet[tile * 32:tile * 32 + 32] = font.planar(px)


def glyphs():
    """{char: (rows, ink width)}"""
    return {c: (rows, adv - 1) for c, (rows, adv) in font.small().items()} | {c: (rows, 3) for c, rows in NARROW.items()}


def button_px(word):
    """28x12 interior: index rows."""
    g = glyphs()
    width = sum(g[c][1] for c in word) + len(word)  # a gap after each glyph, the last one holds the shadow
    assert width <= 28, (word, width)
    px = [[GROUND] * 28 for _ in range(12)]
    pen = (28 - width + 1) // 2
    for c in word:
        rows, w = g[c]
        for y, r in enumerate(rows):
            for x in range(w):
                if r >> (7 - x) & 1:
                    px[y + 2][pen + x] = INK
                    if px[y + 2][pen + x + 1] == GROUND:
                        px[y + 2][pen + x + 1] = SHADOW
        pen += w + 1
    return px


def buttons(sheet):
    out = bytearray(sheet)
    for r, row in enumerate(BUTTONS):
        for c, word in enumerate(row):
            if not word:
                continue
            first = r * 32 + c * 4
            grid = [[0] * 32 for _ in range(16)]
            for ty in range(2):
                for tx in range(4):
                    for y, line in enumerate(get(out, first + ty * 16 + tx)):
                        grid[ty * 8 + y][tx * 8:tx * 8 + 8] = line
            for y, line in enumerate(button_px(word)):
                grid[y + 2][2:30] = line
            for ty in range(2):
                for tx in range(4):
                    put(out, first + ty * 16 + tx, [grid[ty * 8 + y][tx * 8:tx * 8 + 8] for y in range(8)])
    return bytes(out)


def title(sheet):
    out = bytearray(sheet)
    g = font.load()
    cells = {}
    for y, (col, tile, n) in enumerate(TITLE_ROWS):
        for k in range(n):
            cells[y, col - TITLE_COL0 + k] = tile + k
    px = [[4] * (TITLE_W * 8) for _ in range(len(TITLE_ROWS) * 8)]
    for n, line in enumerate(TITLE):
        pen = TITLE_X
        for c in line:
            rows, adv = g[c]
            for y, r in enumerate(rows):
                for x in range(8):
                    if r >> (7 - x) & 1:
                        yy, xx = 16 * n + 2 + y, pen + x
                        assert (yy // 8, xx // 8) in cells, (line, "ink on a cell with no tile of its own")
                        px[yy][xx] = n + 1
            pen += adv
    for (cy, cx), tile in cells.items():
        put(out, tile, [px[cy * 8 + y][cx * 8:cx * 8 + 8] for y in range(8)])
    return bytes(out)
