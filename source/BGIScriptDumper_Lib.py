# -*- coding: utf-8 -*-
# BGIScriptDumper_Lib (improved): works for both scenario chapters and
# library-type BGI scripts (Custom, Product, Framework, macro_*).
# Output format is identical to BGIScriptDumper-jp.py: ●address●text, UTF-16.
import sys, struct, unicodedata

def is_text_part(part):
    try:
        t = part.decode('cp932')
    except UnicodeDecodeError:
        return False
    return not any(ord(c) < 0x20 and c not in '\r\n\t' for c in t)

def has_japanese(t):
    # FIX: keep any string containing non-ASCII (full-width) text, even if it
    # starts with half-width chars such as "(" or "01see_01：..."; skip
    # labels/function names that start with "_" (e.g. __ビクッ, _SetGF).
    if t.startswith('_'):
        return False
    return any(ord(c) > 0x7e for c in t)

def dump(SC, include_ascii=False):
    data = open(SC, 'rb').read()
    if not data.startswith(b'BurikoCompiledScript'):
        print(SC + " Error!\tNot a script file!"); return False
    # code start = 0x1C + header size
    offset = 0x1C + struct.unpack_from('<I', data, 0x1C)[0]

    # 1) find where the trailing string pool begins: walk back from EOF over
    #    NUL-terminated printable strings until we hit code bytes.
    parts = data[offset:].split(b'\x00')
    pos = len(data)
    for part in reversed(parts):
        start = pos - len(part)
        if part and not is_text_part(part):
            break
        pos = start - 1          # skip the NUL before this part
    tail = pos + 1

    # 2) pool start = smallest push-string (03) operand pointing into the tail
    ops = []
    for p in range(offset, len(data) - 8, 4):
        if data[p:p+4] == b'\x03\x00\x00\x00':
            v = struct.unpack_from('<I', data, p + 4)[0]
            ops.append((p + 4, v))
    valid = [v for _, v in ops if tail <= offset + v < len(data)
             and data[offset + v - 1] == 0]
    if not valid:
        print(SC + "\tno strings."); open(SC + ".txt", 'w', encoding='utf-16').close(); return True
    pool = offset + min(valid)

    n = 0
    with open(SC + ".txt", 'w', 1, "UTF_16") as out:
        for address, v in ops:
            a = offset + v
            if address >= pool or not (pool <= a < len(data)) or data[a-1] != 0:
                continue
            raw = data[a:data.find(b'\x00', a)]
            # Shift-JIS first (identical to the -jp dumper, e.g. 〜),
            # cp932 as fallback so lines with ①②, ～ etc. are not dropped
            try:
                t = raw.decode('shift_jis')
            except UnicodeDecodeError:
                try:
                    t = raw.decode('cp932')
                except UnicodeDecodeError:
                    continue
            if not t:
                continue
            # FIX: multi-line dialogue (e.g. two speakers at once) -> escape the
            # line break so one ●ID● line is kept; the inserter must turn "\\n" back into a newline
            t = t.replace('\r', '\\r').replace('\n', '\\n')
            if include_ascii or has_japanese(t):
                out.write('●' + '%.6d' % address + '●' + t + '\n'); n += 1
    print(SC + "\t%d lines. Finished!" % n)
    return True

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--all']
    if not args:
        print("usage: " + sys.argv[0] + " [--all] <script> [script ...]"); sys.exit(1)
    for f in args:
        dump(f, '--all' in sys.argv)
