import re
from PIL import Image, ImageDraw

FIELD_SIZE_X = 32
FIELD_SIZE_Y = 32
BOX_SIZE = 25
IND = 2
MAX_FIG = 18


def fingerprint_check(fingerprint):
    if ':' in fingerprint:
        if (a := re.search(r"^(?:[\da-fA-F][\da-fA-F]:)+(?:[\da-fA-F][\da-fA-F])$", fingerprint)):
            fingerprint = a.group().replace(':', '')
        else:
            raise ValueError("Incorrect fingerprint: invalid format")

    if len(fingerprint) % 2 != 0:
        raise ValueError(f"Incorrect fingerprint: odd number of characters ({len(fingerprint)})")

    if not 24 <= len(fingerprint) <= 64:
        raise ValueError(f"Incorrect fingerprint: key must be 12-32 bytes ({len(fingerprint) // 2} given)")

    for i in fingerprint:
        if i not in 'abcdefABCDEF0123456789':
            raise ValueError(f"Incorrect fingerprint: invalid character ({i})")

    return fingerprint


def field_fill(fingerprint):
    field = [[0] * FIELD_SIZE_X for i in range(FIELD_SIZE_Y)]
    xs = x = FIELD_SIZE_X // 2
    ys = y = FIELD_SIZE_Y // 2

    for i in range(0, len(fingerprint), 2):
        byte = int(fingerprint[i:i + 2], 16)
        for j in range(4):
            x += 1 if byte & 1 else -1
            y += 1 if byte & 2 else -1
            x = max(0, min(x, FIELD_SIZE_X - 1))
            y = max(0, min(y, FIELD_SIZE_Y - 1))
            if field[y][x] < MAX_FIG:
                field[y][x] += 1
            byte >>= 2
    
    field[ys][xs] = 'S'
    field[y][x] = 'E'
    return field


def draw_rectangle(dr, x, y, color):
    dr.rectangle([x + IND, y + IND, x + BOX_SIZE - IND, y + BOX_SIZE - IND], fill=color)


def draw_triangle(dr, x, y, color):
    dr.polygon([(x + IND, y + BOX_SIZE - IND), (x + BOX_SIZE - IND, y + BOX_SIZE - IND), (x + ( BOX_SIZE - 2 * IND) // 2 + IND, y + IND)], fill=color)


def draw_ellipse(dr, x, y, color):
    dr.ellipse([x + IND, y + IND, x + BOX_SIZE - IND, y + BOX_SIZE - IND], fill=color)


def draw_X(dr, x, y, color):
    dr.line((x + IND * 3, y + IND, x + BOX_SIZE - IND * 3,   y + BOX_SIZE - IND), fill=color, width=2)
    dr.line((x + IND * 3, y + BOX_SIZE - IND, x + BOX_SIZE - IND * 3,   y + IND), fill=color, width=2)


def draw_S(dr, x, y, color):
    l, r = x + IND * 2, x + BOX_SIZE - IND * 2
    t, b = y + IND, y + BOX_SIZE - IND
    m = (t + b) // 2
    dr.rectangle((l, t, r, t + IND), fill=color)
    dr.rectangle((l, m - IND // 2, r, m + IND // 2), fill=color)
    dr.rectangle((l, b - IND, r, b), fill=color)
    dr.rectangle((l, t, l + IND, m), fill=color)
    dr.rectangle((r - IND, m, r, b), fill=color)


def draw_O(dr, x, y, color):
    dr.ellipse([x + IND * 2, y + IND, x + BOX_SIZE - IND * 2, y + BOX_SIZE - IND], outline=color, width=3)


def draw_F(dr, x, y, color):
    l = x + IND * 2
    r = x + BOX_SIZE - IND * 2
    t = y + IND 
    b = y + BOX_SIZE - IND
    mid = (t + b) // 2
    dr.rectangle((l, t, l + IND, b), fill=color)
    dr.rectangle((l, t, r, t + IND), fill=color)
    dr.rectangle((l, mid - IND // 2, r - IND * 2, mid + IND // 2), fill=color)


def draw_E(dr, x, y, color):
    l = x + IND * 2
    r = x + BOX_SIZE - IND * 2
    t = y + IND
    b = y + BOX_SIZE - IND
    mid = (t + b) // 2
    dr.rectangle((l, t, l + IND, b), fill=color)
    dr.rectangle((l, t, r, t + IND), fill=color)
    dr.rectangle((l, mid-IND // 2, r - IND * 2, mid + IND // 2), fill=color)
    dr.rectangle((l, b - IND, r, b), fill=color)


FIG = [draw_ellipse, draw_triangle, draw_rectangle, draw_O, draw_X, draw_F]
COLORS = ['blue', 'green', 'red']

def draw_figure(dr, n, x, y):
    if n == 0:
        return
    
    if n == 'S':
        draw_S(dr, x, y, 'black')
        return
    
    if n == 'E':
        draw_E(dr, x, y, 'black')
        return

    FIG[(n - 1) % len(FIG)](dr, x, y, COLORS[(n - 1) // len(FIG) % len(COLORS)])


def create_graphic_fingerprint(field):
    img = Image.new('RGB', (FIELD_SIZE_X * BOX_SIZE, FIELD_SIZE_Y * BOX_SIZE), 'white')
    dr = ImageDraw.Draw(img)
    x, y = 0, 0
    for i in range(FIELD_SIZE_Y):
        for j in range(FIELD_SIZE_X):
            dr.rectangle((x, y, x + BOX_SIZE - 1, y + BOX_SIZE - 1), fill="#EEEEEE" if (i + j) % 2 else '#FFFFFF')
            draw_figure(dr, field[i][j], x, y)
            x += BOX_SIZE
        x = 0
        y += BOX_SIZE 

    img.save("graphic_fingerprint.png")


fingerprint = fingerprint_check(input("Enter fingerprint:\n").strip())
field = field_fill(fingerprint)
create_graphic_fingerprint(field)
