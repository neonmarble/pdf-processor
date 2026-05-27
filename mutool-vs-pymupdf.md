# PDF Compression: mutool vs pymupdf Findings

## The Problem

`mutool clean` barely compresses PDFs containing **Flate-compressed raw pixel images** (0.1–0.6% reduction on affected files), while achieving excellent compression on **JPEG-compressed images** (72–93%).

## Root Cause

`mutool clean`'s image recompression pipeline (`--color-lossy-image-recompress-method jpeg` + `--color-lossy-image-subsample-dpi`) **only operates during subsampling**. It cannot convert Flate/RGB pixel data to JPEG — it only re-encodes images it actually downsamples. Flate images are passed through untouched regardless of the preset DPI.

This was confirmed by running `mutool clean` with the most aggressive settings (`--recompress-images-when always` + `jpeg:50` quality) — the Flate images remained identical in dimensions and encoding.

## Comparison Results

| Method | 01.pdf | 02.pdf | 03.pdf | 04.pdf | 05.pdf | 06.pdf | TOTAL |
|--------|--------|--------|--------|--------|--------|--------|-------|
| Original | 9.18MB | 0.46MB | 0.35MB | 3.47MB | 0.21MB | 11.92MB | 25.59MB |
| mutool lossless | 0.1% | 28.6% | 26.4% | 0.4% | 1.4% | 0.1% | 1.0% |
| mutool aggressive/screen | 0.6% | 58.1% | 48.0% | 3.3% | 25.9% | **93.3%** | 46.0% |
| pymupdf lossless | 0.1% | 28.3% | 25.9% | 0.3% | 0.6% | 0.1% | 1.0% |
| pymupdf aggressive | **85.1%** | 51.2% | 38.8% | **80.9%** | 10.9% | 0.1% | 43.1% |

## Why They're Complementary

| Image encoding | mutool | pymupdf (`rewrite_images()`) |
|----------------|--------|------|
| **Flate (raw RGB pixels)** | Cannot re-encode — passes through unchanged | Decompresses and re-encodes as JPEG — massive savings |
| **DCT (JPEG)** | Subsamples and recompresses at lower quality — massive savings | Already JPEG — passes through with minimal savings |
| **CCITTFax** | No effect | No effect |

### `01.pdf` image detail (8.9 MB Flate → 1.2 MB DCT via pymupdf)

| Image | Original (Flate) | pymupdf (DCT) | Reduction |
|-------|-----------------|---------------|-----------|
| 1350×1800 | 2,669 KB | 208 KB | 92% |
| 1280×960 | 1,230 KB | 131 KB | 89% |
| 960×1280 (×5) | 833–1,399 KB | 119–159 KB each | 85–89% each |
| 1284×2604 | 300 KB | 122 KB | 59% |

## Effective DPI Analysis

For `mutool clean`, the effective DPI of images on the page determines whether subsampling triggers:

| Page | Image | Pixel dims | Render size (pts) | Effective DPI |
|------|-------|-----------|-------------------|---------------|
| 3 | photo | 960×1280 | 542.7×711.2 | ~128 |
| 4 | photo | 960×1280 | 521.0×634.9 | ~133 |
| 5 | photo | 1350×1800 | 301.6×383.2 | ~330 |
| 5 | hidden | 1284×2604 | 0.63×1.00 | ~146K |
| 9 | photo | 1280×960 | 528.5×367.2 | ~174 |

At the **ebook (150 DPI)** preset, the page 3/4 images at ~128–133 DPI are *below* the threshold, so no downsampling occurs. Even at **screen (72 DPI)**, `mutool` still won't re-encode Flate images.

## Conclusion

- **mutool** excels at downsampling already-JPEG images for screen/ebook/printer output
- **pymupdf** excels at converting Flate (raw pixel) images to JPEG
- Neither tool alone handles both edge cases well
- **Optimal strategy**: chain both tools (pymupdf aggressive → mutool aggressive) or run both and keep the smaller result