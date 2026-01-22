from base64 import b64decode
from re import search, MULTILINE
from hashlib import sha512
from .palette import *
from math import ceil


def field_fill(fingerprint: bytes, field_size_x=17, field_size_y=9, max_fig=17):
    field = [[0] * field_size_x for i in range(field_size_y)]
    xs = x = field_size_x // 2
    ys = y = field_size_y // 2

    for byte in fingerprint:
        for j in range(4):
            x += 1 if byte & 1 else -1
            y += 1 if byte & 2 else -1
            x = max(0, min(x, field_size_x - 1))
            y = max(0, min(y, field_size_y - 1))
            if field[y][x] < max_fig - 2:
                field[y][x] += 1
            byte >>= 2
    
    field[ys][xs] = max_fig - 2
    field[y][x] = max_fig - 1
    return field


def field_color(field, data, fingerprint, mode='background', chars=" .o+=*BOX@%&#/^SE"):
    key_type = get_key_type(data)
    key_size = get_key_size(data)
    digest_type = get_digest_type(data)
    field_size_x = len(field[0])
    first_line = f'+--[{key_type} {key_size}]'
    first_line += '-' * (field_size_x - len(first_line) + 1) + '+'
    buf = [first_line]

    for i in field:
        line = "|"
        for j in i:
            line += str(chars[j])
        line += "|"
        buf.append(line)
    
    last_line = '+' + '-' * ((field_size_x - len(digest_type) - 2) // 2) + f'[{digest_type}]'
    last_line += '-' * (field_size_x - len(last_line) + 1) + '+'
    buf.append(last_line)

    if mode == 'background':
        colors = [BG_RED, BG_BLUE, BG_GREEN, BG_YELLOW, BG_MAGENTA, BG_CYAN, WHITE]
    
    if mode == 'foreground':
        colors = [RED, BLUE, GREEN, YELLOW, MAGENTA, CYAN, WHITE] 
    colors_index = list(get_colors(fingerprint))

    ans = []
    div = ceil(len(buf) / 4)
    for ind, val in enumerate(buf):
        if ind % div == 0:
            cur_color = f"{colors[colors_index[ind // div] % len(colors)]}"
        ans.append(BOLD)
        ans.append(cur_color)
        ans.append(val)
        ans.append(f"{RESET}\n")
    return ''.join(ans)


def get_colors(fingerprint: bytes):
    fingerprint = sha512(fingerprint).digest()
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    for byte in fingerprint:
        for j in range(2):
            c1 += 1 if byte & 1 else -1
            c2 += 1 if byte & 2 else -1            
            c3 += 1 if byte & 4 else -1
            c4 += 1 if byte & 8 else -1
            byte >>= 4
    
    return c1, c2, c3, c4


def parse_input(source):
    if (fingerprint := get_fingerprint_sha256(source)) is not None: 
        return fingerprint

    elif (fingerprint := get_fingerprint_md5(source)) is not None:
        return fingerprint

    else:
        raise ValueError("fingerprint was not found")


def get_fingerprint_sha256(data):
    if (fingerprint := search(r"SHA256:([a-zA-Z0-9+/]{43,44})(?=\s|$|=)", data)) is not None: 
        fingerprint = fingerprint.group(1)
        fingerprint += '=' * (-len(fingerprint) % 4)
        return b64decode(fingerprint)
    return None


def get_fingerprint_md5(data):
    if (fingerprint := search(r"(?:MD5:)?((?:[a-fA-F0-9]{2}:){15}[a-fA-F0-9]{2})(?=\s|$)", data)) is not None:
        fingerprint = fingerprint.group(1).replace(':', '')
        return bytes.fromhex(fingerprint)
    
    if (fingerprint := search(r"(?:MD5:)?((?:[a-fA-F0-9]{2}){16})(?=\s|$)", data)) is not None:
        fingerprint = fingerprint.group(1)
        return bytes.fromhex(fingerprint)

    return None


def get_key_type(data):
    if (type_key := search(r"\((\w+)\)", data)) is not None:
        return type_key.group(1)
    return ''


def get_digest_type(data):
    if get_fingerprint_md5(data):
        return "MD5"
    
    if get_fingerprint_sha256(data):
        return "SHA256"
    
    return ''


def get_key_size(data):
    if (size := search(r"^\d+\s", data, flags=MULTILINE)) is not None:
        return size.group()[:-1]
    return ''

