#!/usr/bin/env python3
"""Copy the news-image entry (entry.png) to the grading output directory.

Stdlib only. The image is copied byte-for-byte; the copy is verified
afterwards by size and SHA-256 so a truncated write can never pass silently.
"""

import hashlib
import os
import shutil
import sys

SOURCE = "entry.png"
MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), SOURCE)

    if not os.path.isfile(source):
        print(f"error: {SOURCE} not found next to {__file__}", file=sys.stderr)
        return 1

    with open(source, "rb") as handle:
        magic = handle.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        print("error: entry.png is not a PNG file", file=sys.stderr)
        return 1

    size = os.path.getsize(source)
    if size > MAX_BYTES:
        print(f"error: entry.png is {size} bytes, over the {MAX_BYTES} limit",
              file=sys.stderr)
        return 1

    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        print(f"error: output path {out_dir} exists and is not a directory",
              file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, SOURCE)

    # Never clobber the entry itself: refuse if the output resolves to
    # the same file as the source (e.g. MAKEFUN_OUTPUT_DIR pointing
    # at the repo directory).
    if os.path.abspath(destination) == os.path.abspath(source):
        print("error: output directory is the source directory; "
              "refusing to copy entry.png onto itself", file=sys.stderr)
        return 1

    shutil.copyfile(source, destination)

    copied_size = os.path.getsize(destination)
    if copied_size != size:
        print(f"error: copied size {copied_size} != source size {size}",
              file=sys.stderr)
        return 1

    source_hash = sha256_of(source)
    copied_hash = sha256_of(destination)
    if copied_hash != source_hash:
        print("error: SHA-256 mismatch after copy", file=sys.stderr)
        return 1

    print(f"copied {SOURCE}: {size} bytes, sha256 {source_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
