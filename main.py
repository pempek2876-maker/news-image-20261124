# news-image-20261124 — "Sum up 24 November's world news in one image"
# Draws an illustrated newspaper front page (1024x1024 PNG) with Python stdlib only.
# Deterministic: no network, no time, no randomness; two runs write identical bytes.
# Output: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png)
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette (newsprint) ----
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 30, 30)
GREEN = (30, 122, 52)
NAVY = (31, 58, 95)
SKY = (220, 233, 242)
GRAY = (107, 101, 88)
LIGHT = (232, 226, 210)
WHITE = (255, 255, 255)
BALL = (204, 214, 74)   # tennis-ball yellow-green
GOLD = (201, 162, 39)

# ---- 5x7 bitmap font (rows top->bottom, '#' = on). Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            for x in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill(x0, y0, x1, y0 + t, c)
        self.fill(x0, y1 - t, x1, y1, c)
        self.fill(x0, y0, x0 + t, y1, c)
        self.fill(x1 - t, y0, x1, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            for a in range(-(t // 2), t // 2 + 1):
                for b in range(-(t // 2), t // 2 + 1):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x += sx
            if e2 < dx:
                err += dx; y += sy

    def circle(self, cx, cy, r, c, filled=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.set(x, y, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(x, y, c)

    def polyline(self, pts, c, t=2):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            self.line(x0, y0, x1, y1, c, t)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for r, row in enumerate(glyph):
                for col, bit in enumerate(row):
                    if bit == '1':
                        self.fill(cx + col * scale, y + r * scale,
                                  cx + (col + 1) * scale, y + (r + 1) * scale,
                                  color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        return self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def paragraph(self, x, y, s, scale, color, max_w, leading=None):
        lh = leading if leading is not None else 7 * scale + 4
        for ln in wrap_text(s, scale, max_w):
            self.text(x, y, ln, scale, color)
            y += lh
        return y


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- layout ----
M = 24            # outer margin
CW = W - 2 * M    # 976 content width


def draw_masthead(cv):
    cv.text_center(W // 2, 20, "THE WORLD TODAY", 6, INK)
    cv.fill(M, 74, W - M, 77, INK)
    cv.fill(M, 80, W - M, 82, INK)


def draw_date_band(cv):
    cv.fill(M, 90, W - M, 132, RED)
    cv.text_center(W // 2, 97, "TUESDAY, 24 NOVEMBER 2026", 4, WHITE)


def draw_hero(cv):
    x0, y0, x1, y1 = M, 142, W - M, 536
    cv.rect(x0, y0, x1, y1, INK, 2)
    cv.fill(x0 + 2, y0 + 2, x1 - 2, y1 - 2, SKY)
    # faint grid
    for gy in range(y0 + 60, y1 - 90, 44):
        cv.fill(x0 + 2, gy, x1 - 2, gy + 1, (200, 214, 226))
    # market chart: Friday plunge (red) then Monday/Tuesday rebound (green),
    # kept clear of the headline box (x40..560, y158..330)
    plunge = [(580, 300), (640, 350), (720, 400)]
    rebound = [(720, 400), (800, 330), (880, 260), (960, 200)]
    cv.polyline(plunge, RED, 4)
    cv.polyline(rebound, GREEN, 4)
    for (px, py) in plunge + rebound[1:]:
        cv.circle(px, py, 5, INK, filled=True)
        cv.circle(px, py, 3, WHITE, filled=True)
    # Tokyo skyline silhouette along the bottom
    base = y1 - 2
    buildings = [
        (48, 150, 60, 96), (112, 130, 46, 120), (162, 170, 58, 82),
        (224, 120, 52, 130), (280, 150, 60, 100), (344, 110, 48, 140),
        (396, 160, 56, 90), (456, 125, 50, 125), (510, 145, 62, 105),
        (576, 115, 46, 135), (626, 155, 58, 95), (688, 120, 52, 130),
        (744, 150, 60, 100), (808, 130, 48, 120), (860, 160, 56, 90),
        (920, 125, 52, 125),
    ]
    for (bx, bh, bw, _h) in buildings:
        top = base - bh
        cv.fill(bx, top, bx + bw, base, NAVY)
        # lit windows
        for wy in range(top + 12, base - 10, 22):
            for wx in range(bx + 8, bx + bw - 8, 18):
                if (wx + wy) % 36 < 18:
                    cv.fill(wx, wy, wx + 7, wy + 9, (250, 214, 120))
    # Tokyo Tower spire
    tx = 950
    cv.line(tx, base - 210, tx - 26, base, RED, 4)
    cv.line(tx, base - 210, tx + 26, base, RED, 4)
    cv.line(tx - 14, base - 120, tx + 14, base - 120, RED, 3)
    cv.circle(tx, base - 214, 5, RED, filled=True)
    # chart labels (drawn after the skyline, in clear sky beside the plunge)
    cv.text(566, 250, "FRI: -5.06%", 2, RED)
    cv.text(566, 268, "56,437", 2, RED)
    cv.text(720, 146, "FUTURES +3%", 2, GREEN)
    cv.text(720, 164, "TUE OPEN", 2, GREEN)
    # headline box (paper, top-left)
    bx0, by0, bx1, by1 = 40, 158, 560, 330
    cv.fill(bx0, by0, bx1, by1, PAPER)
    cv.rect(bx0, by0, bx1, by1, INK, 2)
    cv.fill(bx0, by0, bx0 + 8, by1, RED)
    cv.text(bx0 + 22, by0 + 16, "TOKYO REOPENS", 5, RED)
    cv.text(bx0 + 22, by0 + 58, "AFTER THE ROUT", 5, INK)
    cv.text(bx0 + 22, by0 + 108, "NIKKEI FUTURES POINT NEAR +3% AS", 2, INK)
    cv.text(bx0 + 22, by0 + 126, "THE EXCHANGE REOPENS AFTER ITS", 2, INK)
    cv.text(bx0 + 22, by0 + 144, "HOLIDAY AND FRIDAY'S PLUNGE.", 2, INK)


def draw_hero_sub(cv):
    # strip under the hero: Monday's Wall Street rebound, labelled as Monday
    y = 544
    cv.text(M, y, "MONDAY: S&P +4.7%, NASDAQ +6.5%, DOW +3.0%, NVIDIA +30% AS HUANG RETURNS", 2, INK)


def draw_panel(cv, x0, tag, tag_color, headline, sub, art):
    y0, y1 = 566, 768
    x1 = x0 + 317
    cv.rect(x0, y0, x1, y1, INK, 2)
    cv.fill(x0 + 2, y0 + 2, x1 - 2, y0 + 26, tag_color)
    cv.text(x0 + 10, y0 + 6, tag, 2, WHITE)
    art(cv, x0, y0 + 32)
    yy = y0 + 102
    for ln in headline:
        cv.text(x0 + 12, yy, ln, 3, INK)
        yy += 24
    sub_lines = wrap_text(sub, 2, x1 - x0 - 24)
    assert len(sub_lines) <= 3, f"panel sub overflows: {sub_lines}"
    cv.paragraph(x0 + 12, yy + 2, sub, 2, GRAY, x1 - x0 - 24, leading=16)


def art_globe(cv, x0, y):
    cx, cy, r = x0 + 52, y + 36, 34
    cv.circle(cx, cy, r, NAVY, filled=False)
    cv.circle(cx, cy, r - 2, SKY, filled=True)
    cv.circle(cx, cy, r, NAVY, filled=False)
    # meridians
    for dx in (-18, 0, 18):
        for k in range(-r, r + 1, 2):
            xx = cx + dx * (1 - (k / r) ** 2) ** 0.5 if abs(k) < r else cx
            cv.set(int(xx), cy + k, NAVY)
    for k in (-14, 0, 14):
        for a in range(-r, r + 1, 2):
            xx = cx + a
            yy = cy + k * (1 - (a / r) ** 2) ** 0.5 if abs(a) < r else cy
            cv.set(xx, int(yy), NAVY)
    # land blobs
    cv.circle(cx - 10, cy - 8, 8, GREEN, filled=True)
    cv.circle(cx + 12, cy + 10, 9, GREEN, filled=True)
    cv.circle(cx + 14, cy - 14, 5, GREEN, filled=True)
    # crack: no deal
    cv.line(cx - 6, cy - 30, cx + 2, cy - 6, RED, 3)
    cv.line(cx + 2, cy - 6, cx - 8, cy + 12, RED, 3)
    cv.line(cx - 8, cy + 12, cx + 4, cy + 30, RED, 3)


def art_bars(cv, x0, y):
    bx, base = x0 + 22, y + 64
    heights = [20, 38, 56]
    for i, hh in enumerate(heights):
        x = bx + i * 34
        cv.fill(x, base - hh, x + 24, base, NAVY if i < 2 else GREEN)
    cv.line(bx - 6, base, bx + 108, base, INK, 2)


def art_ball(cv, x0, y):
    cx, cy, r = x0 + 52, y + 36, 34
    cv.circle(cx, cy, r, BALL, filled=True)
    cv.circle(cx, cy, r, INK, filled=False)
    # curved seams
    for k in range(-r, r + 1, 2):
        off = int(10 * (1 - (k / r) ** 2) ** 0.5)
        cv.set(cx - r + 8 + (off // 2), cy + k, WHITE)
        cv.set(cx + r - 8 - (off // 2), cy + k, WHITE)
    cv.line(cx - 20, cy - 28, cx - 8, cy + 28, INK, 2)
    cv.line(cx + 20, cy - 28, cx + 8, cy + 28, INK, 2)


def draw_panels(cv):
    draw_panel(cv, M, "CLIMATE - ANTALYA", RED,
               ["COP31: NO DEAL,", "NO SURRENDER"],
               "ERDOGAN: 'ALL IS NOT LOST' - 46 DECISIONS ADOPTED, TALKS GO ON.",
               art_globe)
    draw_panel(cv, M + 329, "TECH - SEOUL", NAVY,
               ["KOREA CHIP", "EXPORTS +294%"],
               "SEMICONDUCTOR SHIPMENTS SURGE IN THE FIRST 20 DAYS OF NOVEMBER.",
               art_bars)
    draw_panel(cv, M + 658, "SPORT - TURKU", GREEN,
               ["SINNER UNDER", "THE KNIFE TODAY"],
               "KNEE SURGERY TODAY IN FINLAND; 3-4 MONTHS OUT, MELBOURNE IN DOUBT.",
               art_ball)


# ---- briefs, ticker, footer ----
BRIEFS_LEFT = [
    "KYIV - 11 KILLED IN OVERNIGHT STRIKES ON THE KYIV REGION",
    "KINSHASA - CONGO HALTS COBALT EXPORTS AGAIN FROM 30 NOV",
    "NEW YORK - CROWDSTRIKE TO BUY ZSCALER IN A $43.9B DEAL",
    "WASHINGTON - US IN TALKS TO TRAIN SYRIAN FORCES IN DEMINING",
]
BRIEFS_RIGHT = [
    "NEW DELHI - INDIA WEIGHS ABOUT 20% DUTIES ON RICE EXPORTS",
    "JERUSALEM - SETTLER VIOLENCE SHADOWS ISRAEL GOVERNMENT TALKS",
    "WASHINGTON - DEMOCRATS CLINCH 258 HOUSE SEATS, MOST SINCE 1992",
    "LONDON - 12,000 EVACUATED FROM A DON TOLIVER CONCERT",
]


def draw_briefs(cv):
    cv.text(M, 780, "ALSO IN THE NEWS", 3, INK)
    cv.fill(M, 806, W - M, 808, INK)
    for col, items in ((M, BRIEFS_LEFT), (M + 500, BRIEFS_RIGHT)):
        y = 814
        for item in items:
            cv.fill(col, y + 2, col + 8, y + 10, RED)
            cv.paragraph(col + 16, y, item, 2, INK, 460, leading=18)
            y += 40


def draw_ticker(cv):
    cv.fill(M, 980, W - M, 1012, INK)
    cv.text(M + 12, 989,
            "OIL: WTI -4.5% TO $80.17, BRENT -3.5% TO $89.37 AS TRUMP GIVES IRAN TALKS TIME",
            2, WHITE)


def draw_footer(cv):
    cv.text_center(W // 2, 1016, "SOURCES: REUTERS, AP, AAP, ASIA DAILY", 1, GRAY)


def build():
    cv = Canvas()
    draw_masthead(cv)
    draw_date_band(cv)
    draw_hero(cv)
    draw_hero_sub(cv)
    draw_panels(cv)
    draw_briefs(cv)
    draw_ticker(cv)
    draw_footer(cv)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(build(), path)
    import hashlib
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(f"wrote {path} {size} bytes sha256={digest}")


if __name__ == "__main__":
    main()
