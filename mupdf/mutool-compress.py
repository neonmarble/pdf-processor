#!/usr/bin/env python3
"""
Compresses PDF files in the current directory using mutool clean.

Requires: mutool (from MuPDF) installed and on PATH.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


PRESETS = {
    "screen": {"dpi": 72, "description": "Screen quality (72 DPI)"},
    "ebook": {"dpi": 150, "description": "eBook quality (150 DPI)"},
    "printer": {"dpi": 300, "description": "Printer quality (300 DPI)"},
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compresses PDF files in the current directory using mutool clean."
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
             "and object streams. 'aggressive' additionally subs fonts and "
             "re-compresses/downsamples images.",
    )
    parser.add_argument(
        "--preset", "-p",
        default="ebook",
        choices=list(PRESETS.keys()),
        help="Image quality preset for aggressive mode: screen (72 DPI), "
             "ebook (150 DPI, default), printer (300 DPI).",
    )
    parser.add_argument(
        "--mutool-exe", "-x",
        default="mutool",
        help='Path to the mutool executable. Defaults to "mutool".',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without compressing any files.",
    )
    return parser.parse_args()


def locate_mutool(mutool_exe):
    mutool_path = shutil.which(mutool_exe)
    if mutool_path:
        return Path(mutool_path)

    p = Path(mutool_exe)
    if p.is_file():
        return p.resolve()

    raise FileNotFoundError(f"mutool executable not found: {mutool_exe}")


def get_mutool_version(mutool_path):
    result = subprocess.run(
        [str(mutool_path), "-v"],
        capture_output=True,
        text=True,
        check=True,
    )
    version_output = result.stderr.strip() or result.stdout.strip()
    version_line = version_output.splitlines()[0]
    return version_line.replace("mutool version ", "")


def build_clean_cmd(mutool_path, mode, preset, input_file, output_file):
    cmd = [str(mutool_path), "clean"]

    cmd.append("-gggg")
    cmd.append("-z")
    cmd.append("-f")
    cmd.append("-i")
    cmd.append("-s")
    cmd.append("-Z")

    if mode == "lossless":
        cmd.append("-t")
    else:
        cmd.append("-t")
        cmd.append("-S")

        dpi = PRESETS[preset]["dpi"]

        cmd.extend([
            "--color-lossy-image-subsample-dpi", str(dpi),
            "--color-lossy-image-subsample-method", "bicubic",
            "--color-lossy-image-recompress-method", "jpeg",
            "--gray-lossy-image-subsample-dpi", str(dpi),
            "--gray-lossy-image-subsample-method", "bicubic",
            "--gray-lossy-image-recompress-method", "jpeg",
        ])

    cmd.extend([str(input_file), str(output_file)])

    return cmd


def main():
    args = parse_args()

    try:
        mutool_path = locate_mutool(args.mutool_exe)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        mutool_version = get_mutool_version(mutool_path)
    except Exception as exc:
        print(f"Error detecting mutool version: {exc}", file=sys.stderr)
        sys.exit(1)

    mutool_exe_name = mutool_path.stem

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
    print("  mutool PDF Compressor v1.0")
    print(banner_sep)
    print(f"  mutool     : {mutool_version} ({mutool_exe_name})")
    print(f"  Mode       : {args.mode}")
    if args.mode == "aggressive":
        print(f"  Preset     : {args.preset} ({PRESETS[args.preset]['description']})")
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
        "  mutool PDF Compressor v1.0 - Log",
        log_header_sep,
        f"  Date        : {timestamp}",
        f"  mutool      : {mutool_version} ({mutool_exe_name})",
        f"  Mode        : {args.mode}",
    ]
    if args.mode == "aggressive":
        log_header_lines.append(f"  Preset      : {args.preset} ({PRESETS[args.preset]['description']})")
    log_header_lines.extend([
        f"  Output Dir  : {output_dir}",
        log_header_sep,
        "",
    ])

    if not args.dry_run:
        log_file.write_text("\n".join(log_header_lines) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="mutool-compress-", ignore_cleanup_errors=True) as _td:
        temp_dir = Path(_td)

        for i, pdf in enumerate(pdf_files, start=1):
            if args.dry_run:
                print(f"[{i}/{total}] {pdf.name} -> {output_dir / pdf.name}")
                continue

            print(f"[{i}/{total}] {pdf.name}... ", end="", flush=True)

            output_file = output_dir / pdf.name
            temp_output = temp_dir / f"compressed_{pdf.name}"

            cmd = build_clean_cmd(mutool_path, args.mode, args.preset, pdf, temp_output)

            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    print(
                        f"\nmutool clean failed on '{pdf.name}' (exit code: {result.returncode}).\n{result.stdout}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            except Exception as exc:
                print(f"\nError compressing '{pdf.name}': {exc}", file=sys.stderr)
                sys.exit(1)

            shutil.move(str(temp_output), str(output_file))

            mutool_output = result.stdout.strip() if result.stdout else ""
            if mutool_output:
                log_entry_sep = "-" * 60
                log_entry_lines = [
                    log_entry_sep,
                    f"  [{i}/{total}] {pdf.name}",
                    log_entry_sep,
                    mutool_output,
                    "",
                ]
                with log_file.open("a", encoding="utf-8") as lf:
                    lf.write("\n".join(log_entry_lines) + "\n")

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