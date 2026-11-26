"""make.fun entry: World news of 26 November 2026 in one image.

Copies the entry image (entry.png, next to this file) byte-for-byte
into the output directory: $MAKEFUN_OUTPUT_DIR when set, else /output.
Before copying it validates the PNG signature; after copying it checks
the copy matches the source in size and SHA-256. Standard library only.
"""
import hashlib
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"entry image missing: {SOURCE}")
    if SOURCE.stat().st_size == 0:
        raise SystemExit(f"entry image is empty: {SOURCE}")
    if SOURCE.stat().st_size > 1024 * 1024:
        raise SystemExit(
            f"entry image over the 1 MiB limit: {SOURCE.stat().st_size} bytes")
    with open(SOURCE, "rb") as f:
        signature = f.read(len(PNG_SIGNATURE))
    if signature != PNG_SIGNATURE:
        raise SystemExit(f"{SOURCE} is not a PNG file (bad signature)")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(SOURCE, dest)
    with open(dest, "rb") as f:
        dest_signature = f.read(len(PNG_SIGNATURE))
    if dest_signature != PNG_SIGNATURE:
        raise SystemExit(f"{dest} is not a PNG file after copy (bad signature)")
    src_size = SOURCE.stat().st_size
    dst_size = dest.stat().st_size
    if dst_size != src_size:
        raise SystemExit(
            f"size mismatch after copy: source {src_size} bytes, "
            f"copy {dst_size} bytes")
    src_hash = sha256_of(SOURCE)
    dst_hash = sha256_of(dest)
    if dst_hash != src_hash:
        raise SystemExit(
            f"SHA-256 mismatch after copy: source {src_hash}, copy {dst_hash}")
    print(f"copied {SOURCE} -> {dest} ({dst_size} bytes, sha256 {dst_hash})")


if __name__ == "__main__":
    main()
