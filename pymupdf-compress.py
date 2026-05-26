#!/usr/bin/env python3
"""
Compresses PDF files in the current directory using PyMuPDF.

Requires: pip install pymupdf   (or: uv pip install pymupdf)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    import pymupdf
except ImportError:
    print("Error: PyMuPDF is not installed. Run: pip install pymupdf  (or: uv pip install pymupdf)", file=sys.stderr)
    sys.exit(1)


def compression_effort_type(value):
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: '{value}'")
    if ivalue < 0 or ivalue > 100:
        raise argparse.ArgumentTypeError(f"{ivalue} is not between 0 and 100")
    return ivalue


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compresses PDF files in the current directory using PyMuPDF."
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="compressed",
        help='Destination directory for compressed PDFs. Defaults to "compressed".',
    )
    parser.add_argument(
        "--mode", "-m",
        default="lossless",
        choices=["lossless", "aggressive"],
        help="Compression mode. 'lossless' (default) uses garbage collection, deflate, "
             "and object streams. 'aggressive' additionally subsets fonts and re-compresses images.",
    )
    parser.add_argument(
        "--compression-effort", "-e",
        type=compression_effort_type,
        default=0,
        help="Compression effort 0-100. 0 = auto, higher = more effort. Default: 0.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without compressing any files.",
    )
    return parser.parse_args()


def get_version():
    return getattr(pymupdf, "VersionBind", pymupdf.version)


def compress_lossless(doc, outfile, compression_effort):
    doc.save(
        outfile,
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        use_objstms=1,
        compression_effort=compression_effort,
    )


def compress_aggressive(doc, outfile, compression_effort):
    doc.subset_fonts()
    doc.rewrite_images()
    compress_lossless(doc, outfile, compression_effort)


def main():
    args = parse_args()
    version = get_version()

    pdf_files = sorted([f for f in Path(".").glob("*.pdf") if f.is_file()])
    if not pdf_files:
        print("No PDF files found in the current directory.")
        sys.exit(0)

    output_dir = Path(args.output_dir).resolve()
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    total = len(pdf_files)
    total_original_size = 0
    total_compressed_size = 0

    banner_sep = "-" * 40
    print()
    print(banner_sep)
    print("  PyMuPDF PDF Compressor v1.0")
    print(banner_sep)
    print(f"  PyMuPDF    : {version}")
    print(f"  Mode       : {args.mode}")
    print(f"  Output Dir : {output_dir}")
    print(banner_sep)
    print()

    now = datetime.now().astimezone()
    timestamp = now.isoformat(timespec="seconds")
    safe_timestamp = timestamp.replace(":", "")
    log_file = output_dir / f"log-{safe_timestamp}.txt"
    log_header_sep = "=" * 60

    log_header_lines = [
        log_header_sep,
        "  PyMuPDF PDF Compressor v1.0 - Log",
        log_header_sep,
        f"  Date        : {timestamp}",
        f"  PyMuPDF     : {version}",
        f"  Mode        : {args.mode}",
        f"  Output Dir  : {output_dir}",
        log_header_sep,
        "",
    ]

    if not args.dry_run:
        log_file.write_text("\n".join(log_header_lines) + "\n", encoding="utf-8")

    for i, pdf in enumerate(pdf_files, start=1):
        if args.dry_run:
            print(f"[{i}/{total}] {pdf.name} -> {output_dir / pdf.name}")
            continue

        print(f"[{i}/{total}] {pdf.name}... ", end="", flush=True)

        output_file = output_dir / pdf.name

        try:
            doc = pymupdf.open(str(pdf))

            if args.mode == "aggressive":
                compress_aggressive(doc, str(output_file), args.compression_effort)
            else:
                compress_lossless(doc, str(output_file), args.compression_effort)

            doc.close()
        except Exception as exc:
            print(file=sys.stderr)
            print(f"Error compressing '{pdf.name}': {exc}", file=sys.stderr)
            sys.exit(1)

        original_size = pdf.stat().st_size
        compressed_size = output_file.stat().st_size
        total_original_size += original_size
        total_compressed_size += compressed_size

        if original_size > 0:
            ratio = round((1 - compressed_size / original_size) * 100, 1)
        else:
            ratio = 0

        orig_mb = round(original_size / (1024 * 1024), 2)
        comp_mb = round(compressed_size / (1024 * 1024), 2)
        print(f"{orig_mb} MB -> {comp_mb} MB ({ratio}%)")

        log_entry_sep = "-" * 60
        log_entry_lines = [
            log_entry_sep,
            f"  [{i}/{total}] {pdf.name}",
            log_entry_sep,
            f"  {orig_mb} MB -> {comp_mb} MB ({ratio}%)",
            "",
        ]
        with log_file.open("a", encoding="utf-8") as lf:
            lf.write("\n".join(log_entry_lines) + "\n")

    print()
    if total_original_size > 0:
        total_ratio = round((1 - total_compressed_size / total_original_size) * 100, 1)
        total_orig_mb = round(total_original_size / (1024 * 1024), 2)
        total_comp_mb = round(total_compressed_size / (1024 * 1024), 2)
        print(
            f"  Total: {total} file(s)  |  {total_orig_mb} MB -> {total_comp_mb} MB  ({total_ratio}%)"
        )
    else:
        print(f"  Compressed files are in '{output_dir}'.")
    print(banner_sep)
    print()


if __name__ == "__main__":
    main()
