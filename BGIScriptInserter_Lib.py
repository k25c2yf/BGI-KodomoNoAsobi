# -*- coding: utf-8 -*-
"""
BGIScriptInserter_Lib.py  —  孩子的遊戲／BGI BurikoCompiledScript 散檔回寫（自含）

用法（同舊 CLI）:
  python BGIScriptInserter_Lib.py <source> <txt> <out>

  source : 從 script.arc 抽出嘅章節檔（無副檔名）
           - DSC FORMAT 1.00 → 自動解壓，回寫後用原 key 再 DSC 壓縮，out 即遊戲散檔
           - BurikoCompiledScript 裸檔 → 只回寫，out 仍係裸檔
  txt    : ●XXXXXX●譯文（UTF-8／UTF-16；\\r = 換行）
  out    : 輸出散檔（建議無副檔名，放遊戲目錄同 EXE／script.arc 嗰層）

注意:
  - 原版 script.arc 唔使改；遊戲會優先讀散檔
  - 唔好重打整包 arc／唔好解壓重壓系統 entry（Framework／main…）
  - 僅標準庫；可單獨帶走本檔

可選環境變數:
  BGI_INSERTER_QUIET=1  減少壓縮過程輸出
"""
from __future__ import print_function

import os
import sys
import struct
from collections import Counter
import heapq

DSC_MAGIC = b"DSC FORMAT 1.00\x00"
BURIKO_MAGIC = b"BurikoCompiledScript"


# ---------------------------------------------------------------------------
# Write-back (from write_back_script.py)
# ---------------------------------------------------------------------------

def transcode(uni):
    out = []
    for ch in uni:
        try:
            ch.encode("utf-8")
        except Exception:
            out.append(u"·")
        else:
            out.append(ch)
    return (u"".join(out)).encode("utf-8")


def open_txt(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16").splitlines()
    return raw.decode("utf-8-sig").splitlines()


def parse_bullet_line(line):
    if not line or line[0] != u"●":
        return None
    parts = line.split(u"●", 2)
    if len(parts) < 3 or not parts[1]:
        return None
    try:
        address = int(parts[1], 10)
    except ValueError:
        return None
    text = parts[2].replace(u"\\r", u"\n")
    return address, text


def write_back_bytes(sc_data, lines):
    """Append-UTF8 write-back on BurikoCompiledScript bytes. Returns new bytes."""
    if sc_data[:20] != BURIKO_MAGIC:
        raise ValueError("Not a BurikoCompiledScript")
    if len(sc_data) < 0x20:
        raise ValueError("File too small")
    header_size = struct.unpack_from("<L", sc_data, 0x1C)[0]
    offset = 0x1C + header_size
    if offset <= 0x1C or offset > len(sc_data):
        raise ValueError("Bad header size (code start=0x%X)" % offset)

    out = bytearray(sc_data)
    new_offset = len(out)
    text_to_file = bytearray()
    seen = {}
    patched = 0
    skipped = 0

    for line in lines:
        line = line.rstrip(u"\r\n")
        if line == u"":
            continue
        parsed = parse_bullet_line(line)
        if parsed is None:
            continue
        address, text = parsed
        if address < 0 or address + 4 > new_offset:
            print("Warn: address %d out of range (file=%d), skip" % (address, new_offset))
            skipped += 1
            continue
        text_utf8 = transcode(text) + b"\x00"
        if text_utf8 in seen:
            locate = seen[text_utf8] + new_offset - offset
        else:
            locate = len(text_to_file) + new_offset - offset
            seen[text_utf8] = len(text_to_file)
            text_to_file += text_utf8
        struct.pack_into("<L", out, address, locate)
        patched += 1

    out += text_to_file
    return bytes(out), patched, skipped, len(text_to_file)


# ---------------------------------------------------------------------------
# DSC decompress (GARbro DscDecoder port)
# ---------------------------------------------------------------------------

class HuffmanCode(object):
    __slots__ = ("code", "depth")

    def __init__(self, code=0, depth=0):
        self.code = code
        self.depth = depth

    def sort_key(self):
        return (self.depth, self.code)


class HuffmanNode(object):
    __slots__ = ("is_parent", "code", "left", "right")

    def __init__(self):
        self.is_parent = False
        self.code = 0
        self.left = 0
        self.right = 0


class DscDecoder(object):
    def __init__(self, data):
        if not data.startswith(b"DSC FORMAT 1.00"):
            raise ValueError("Not a DSC FORMAT 1.00 file")
        if len(data) < 0x220:
            raise ValueError("DSC too small")
        self.magic = struct.unpack("<H", data[0:2])[0] << 16
        self.key = struct.unpack("<I", data[16:20])[0]
        self.original_size = struct.unpack("<I", data[20:24])[0]
        self.dec_count = struct.unpack("<I", data[24:28])[0]
        self.data = data
        self.compressed = data[0x220:]
        self.byte_pos = 0
        self.bits_left = 0
        self.current_byte = 0

    def update_key(self):
        v0 = 20021 * (self.key & 0xFFFF)
        v1 = self.magic | (self.key >> 16)
        v1 = v1 * 20021 + self.key * 346
        v1 = (v1 + (v0 >> 16)) & 0xFFFF
        self.key = (v1 << 16) + (v0 & 0xFFFF) + 1
        return v1 & 0xFF

    def get_next_bit(self):
        if self.bits_left == 0:
            if self.byte_pos >= len(self.compressed):
                return -1
            self.current_byte = self.compressed[self.byte_pos]
            self.byte_pos += 1
            self.bits_left = 8
        bit = (self.current_byte >> 7) & 1
        self.current_byte = (self.current_byte << 1) & 0xFF
        self.bits_left -= 1
        return bit

    def get_bits(self, count):
        result = 0
        for _ in range(count):
            bit = self.get_next_bit()
            if bit < 0:
                return -1
            result = (result << 1) | bit
        return result

    def create_huffman_tree(self, hcodes, node_count):
        hnodes = [HuffmanNode() for _ in range(1023)]
        nodes_index = [[0] * 512 for _ in range(2)]
        next_node_index = 1
        depth_nodes = 1
        depth = 0
        child_index = 0
        nodes_index[0][0] = 0
        n = 0
        while n < node_count:
            huffman_nodes_index = child_index
            child_index ^= 1
            depth_existed_nodes = 0
            while n < node_count and hcodes[n].depth == depth:
                node = HuffmanNode()
                node.is_parent = False
                node.code = hcodes[n].code
                hnodes[nodes_index[huffman_nodes_index][depth_existed_nodes]] = node
                n += 1
                depth_existed_nodes += 1
            depth_nodes_to_create = depth_nodes - depth_existed_nodes
            for i in range(depth_nodes_to_create):
                node = HuffmanNode()
                node.is_parent = True
                node.left = next_node_index
                nodes_index[child_index][i * 2] = next_node_index
                next_node_index += 1
                node.right = next_node_index
                nodes_index[child_index][i * 2 + 1] = next_node_index
                next_node_index += 1
                hnodes[nodes_index[huffman_nodes_index][depth_existed_nodes + i]] = node
            depth += 1
            depth_nodes = depth_nodes_to_create * 2
        return hnodes

    def unpack(self):
        hcodes = []
        for i in range(512):
            src = self.data[0x20 + i]
            depth = (src - self.update_key()) & 0xFF
            if depth != 0:
                hcodes.append(HuffmanCode(i, depth))
        hcodes.sort(key=lambda c: c.sort_key())
        hnodes = self.create_huffman_tree(hcodes, len(hcodes))
        output = bytearray(self.original_size)
        dst = 0
        for _ in range(self.dec_count):
            node_index = 0
            while True:
                bit = self.get_next_bit()
                if bit < 0:
                    raise EOFError("Incomplete compressed stream")
                node = hnodes[node_index]
                if not node.is_parent:
                    break
                node_index = node.right if bit else node.left
                if not hnodes[node_index].is_parent:
                    break
            code = hnodes[node_index].code
            if code >= 256:
                offset = self.get_bits(12)
                if offset < 0:
                    break
                count = (code & 0xFF) + 2
                offset += 2
                src = dst - offset
                for _j in range(count):
                    output[dst] = output[src]
                    dst += 1
                    src += 1
            else:
                output[dst] = code & 0xFF
                dst += 1
        self.key = struct.unpack("<I", self.data[16:20])[0]
        return bytes(output[:dst]) if dst != self.original_size else bytes(output)

    def huffman_decompress(self):
        return self.unpack()


def dsc_decompress_bytes(data):
    dec = DscDecoder(data)
    out = dec.unpack()
    key = struct.unpack("<I", data[16:20])[0]
    return out, key


def dsc_key_from_bytes(data):
    if not data.startswith(b"DSC FORMAT 1.00"):
        raise ValueError("Not DSC")
    return struct.unpack("<I", data[16:20])[0]


# ---------------------------------------------------------------------------
# DSC compress (from dsc_compress.py / GARbro reverse)
# ---------------------------------------------------------------------------

def update_key(key, magic):
    v0 = 20021 * (key & 0xFFFF)
    v1 = magic | (key >> 16)
    v1 = v1 * 20021 + key * 346
    v1 = (v1 + (v0 >> 16)) & 0xFFFF
    new_key = (v1 << 16) + (v0 & 0xFFFF) + 1
    return new_key, v1 & 0xFF


def lz77_compress(data):
    symbols = []
    pos = 0
    while pos < len(data):
        best_length = 0
        best_offset = 0
        search_start = max(0, pos - 4097)
        for offset in range(pos - search_start, 1, -1):
            if offset < 2:
                continue
            match_pos = pos - offset
            length = 0
            while (length < 257 and
                   pos + length < len(data) and
                   data[match_pos + length] == data[pos + length]):
                length += 1
            if length > best_length:
                best_length = length
                best_offset = offset
        if best_length >= 3:
            code = 256 + (best_length - 2)
            symbols.append((code, best_offset))
            pos += best_length
        else:
            symbols.append((data[pos], None))
            pos += 1
    return symbols


def build_huffman_tree(symbols):
    freq = Counter()
    for symbol, _ in symbols:
        freq[symbol] += 1
    heap = []
    counter = 0
    for symbol, count in freq.items():
        heapq.heappush(heap, (count, counter, symbol, None, None))
        counter += 1
    while len(heap) > 1:
        freq1, id1, sym1, left1, right1 = heapq.heappop(heap)
        freq2, id2, sym2, left2, right2 = heapq.heappop(heap)
        parent = (freq1 + freq2, counter, None,
                  (freq1, id1, sym1, left1, right1),
                  (freq2, id2, sym2, left2, right2))
        heapq.heappush(heap, parent)
        counter += 1
    depths = [0] * 512

    def calculate_depths(node, depth=0):
        freq, node_id, symbol, left, right = node
        if symbol is not None:
            depths[symbol] = depth if depth > 0 else 1
        else:
            if left:
                calculate_depths(left, depth + 1)
            if right:
                calculate_depths(right, depth + 1)

    if heap:
        calculate_depths(heap[0])
    for symbol in freq.keys():
        if depths[symbol] == 0:
            depths[symbol] = 1
        elif depths[symbol] > 255:
            depths[symbol] = 255
    return depths


def assign_canonical_codes(depths):
    symbol_depths = [(i, depths[i]) for i in range(512) if depths[i] > 0]
    symbol_depths.sort(key=lambda x: (x[1], x[0]))
    codes = {}
    code = 0
    prev_depth = 0
    for symbol, depth in symbol_depths:
        if depth > prev_depth:
            code <<= (depth - prev_depth)
            prev_depth = depth
        codes[symbol] = (code, depth)
        code += 1
    return codes


def dsc_compress_bytes(input_data, key, quiet=False):
    magic = 0x53440000
    if not quiet:
        print("Compressing %d bytes..." % len(input_data))
    symbols = lz77_compress(input_data)
    if not quiet:
        print("  LZ77: %d symbols" % len(symbols))
    depths = build_huffman_tree(symbols)
    non_zero = sum(1 for d in depths if d > 0)
    if not quiet:
        print("  Huffman: %d codes" % non_zero)
    codes = assign_canonical_codes(depths)

    output = bytearray()
    output.extend(DSC_MAGIC)
    output.extend(struct.pack("<I", key))
    output.extend(struct.pack("<I", len(input_data)))
    output.extend(struct.pack("<I", len(symbols)))
    output.extend(b"\x00" * 4)

    temp_key = key
    for i in range(512):
        temp_key, enc_byte = update_key(temp_key, magic)
        encrypted_depth = (depths[i] + enc_byte) & 0xFF
        output.append(encrypted_depth)

    bit_buffer = 0
    bits_in_buffer = 0
    for symbol, offset in symbols:
        code, code_length = codes[symbol]
        for i in range(code_length):
            bit = (code >> (code_length - 1 - i)) & 1
            bit_buffer = (bit_buffer << 1) | bit
            bits_in_buffer += 1
            if bits_in_buffer == 8:
                output.append(bit_buffer)
                bit_buffer = 0
                bits_in_buffer = 0
        if symbol >= 256 and offset is not None:
            offset_bits = offset - 2
            for i in range(12):
                bit = (offset_bits >> (11 - i)) & 1
                bit_buffer = (bit_buffer << 1) | bit
                bits_in_buffer += 1
                if bits_in_buffer == 8:
                    output.append(bit_buffer)
                    bit_buffer = 0
                    bits_in_buffer = 0
    if bits_in_buffer > 0:
        bit_buffer <<= (8 - bits_in_buffer)
        output.append(bit_buffer)
    return bytes(output)


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def is_dsc(data):
    return data[:16] == DSC_MAGIC or data.startswith(b"DSC FORMAT 1.00")


def is_buriko(data):
    return data[:20] == BURIKO_MAGIC


def process(source_path, txt_path, out_path, quiet=False):
    try:
        src = open(source_path, "rb").read()
    except Exception as e:
        print("%s Error!\tCan't read: %s" % (source_path, e))
        return 1

    dsc_mode = False
    key = None
    if is_dsc(src):
        dsc_mode = True
        try:
            sc_data, key = dsc_decompress_bytes(src)
        except Exception as e:
            print("%s Error!\tDSC decompress failed: %s" % (source_path, e))
            return 1
        if not quiet:
            print("DSC in: key=0x%08X decompressed=%d" % (key, len(sc_data)))
    elif is_buriko(src):
        sc_data = src
        if not quiet:
            print("Raw BurikoCompiledScript in: %d bytes" % len(sc_data))
    else:
        print("%s Error!\tNot DSC and not BurikoCompiledScript!" % source_path)
        return 1

    try:
        lines = open_txt(txt_path)
    except Exception as e:
        print("%s Error!\t%s" % (txt_path, e))
        return 1

    try:
        written, patched, skipped, pool = write_back_bytes(sc_data, lines)
    except Exception as e:
        print("%s Error!\tWrite-back: %s" % (source_path, e))
        return 1

    if dsc_mode:
        try:
            out_bytes = dsc_compress_bytes(written, key, quiet=quiet)
        except Exception as e:
            print("Error!\tDSC compress failed: %s" % e)
            return 1
        if not quiet:
            print("DSC out: %d bytes (ratio %.1f%%)" % (
                len(out_bytes), 100.0 * len(out_bytes) / max(1, len(written))))
    else:
        out_bytes = written

    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    try:
        open(out_path, "wb").write(out_bytes)
    except Exception as e:
        print("Error!\tCan't write %s: %s" % (out_path, e))
        return 1

    mode = "DSC" if dsc_mode else "RAW"
    print("Finished! mode=%s patched=%d skipped=%d pool+=%d -> %s" % (
        mode, patched, skipped, pool, out_path))
    return 0


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    if len(argv) < 4:
        print("error\n")
        print(argv[0] + " <source> <txt> <out>")
        print("  source: JP chapter from arc (DSC or raw Buriko, no extension)")
        print("  txt:    translation ●addr●text UTF-8/UTF-16")
        print("  out:    loose file for game folder (no extension)")
        return 1
    quiet = os.environ.get("BGI_INSERTER_QUIET", "").strip() in ("1", "true", "yes")
    return process(argv[1], argv[2], argv[3], quiet=quiet)


if __name__ == "__main__":
    sys.exit(main())
