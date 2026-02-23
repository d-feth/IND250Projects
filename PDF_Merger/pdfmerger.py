#!/usr/bin/env python3
"""
pdfmerger.py — PDF File Merger

Requires: PyPDF2
Install:  pip install PyPDF2

Usage:
  python pdfmerger.py filename
  python pdfmerger.py filename --extract-text
  python pdfmerger.py filename --dir /path/to/folder
"""

import os
import sys
import argparse
from PyPDF2 import PdfMerger, PdfReader


def print_usage_error_and_exit():
    print("Error: Merge file name not specified. Usage: python pdfmerger.py filename")
    sys.exit(1)


def list_pdf_files(directory: str):
    # Retrieve: Collect names of files in the directory
    try:
        names = os.listdir(directory)
    except OSError as e:
        print(f"Error: Could not read directory '{directory}': {e}")
        sys.exit(1)

    # Filter: .pdf only (case-insensitive)
    pdfs = [n for n in names if n.lower().endswith(".pdf") and os.path.isfile(os.path.join(directory, n))]

    # Sort: alphabetical
    pdfs.sort(key=lambda s: s.lower())
    return pdfs


def prompt_continue() -> bool:
    while True:
        answer = input("Continue (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def merge_pdfs(directory: str, output_pdf_path: str, pdf_files: list[str]) -> None:
    # Initialize: merger object
    merger = PdfMerger()

    output_basename = os.path.basename(output_pdf_path).lower()

    appended_any = False
    for name in pdf_files:
        # Be sure not to merge any file with the same name as the output file name
        if name.lower() == output_basename:
            continue

        full_path = os.path.join(directory, name)
        try:
            merger.append(full_path)
            appended_any = True
        except Exception as e:
            merger.close()
            print(f"Error: Failed to append '{name}': {e}")
            sys.exit(1)

    if not appended_any:
        merger.close()
        print("Error: No PDFs were merged (only output filename matched, or no readable PDFs).")
        sys.exit(1)

    # Export: save combined PDF
    try:
        with open(output_pdf_path, "wb") as f:
            merger.write(f)
    except OSError as e:
        print(f"Error: Could not write output file '{output_pdf_path}': {e}")
        sys.exit(1)
    finally:
        merger.close()


def extract_text_from_pdf(pdf_path: str, txt_path: str) -> None:
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error: Could not open merged PDF for text extraction: {e}")
        sys.exit(1)

    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        chunks.append(text)

    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(chunks))
    except OSError as e:
        print(f"Error: Could not write text file '{txt_path}': {e}")
        sys.exit(1)


def main():
    # Requirement #2: if name not specified, terminate with exact message
    if len(sys.argv) == 1:
        print_usage_error_and_exit()

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("filename", nargs="?", help="Output base name (merged file will be filename.pdf)")
    parser.add_argument("--dir", default=".", help="Directory to scan for PDFs (default: current directory)")
    parser.add_argument(
        "--extract-text",
        action="store_true",
        help="Bonus: extract all text from merged PDF into filename.txt",
    )
    args = parser.parse_args()

    if not args.filename:
        print_usage_error_and_exit()

    directory = args.dir
    output_pdf = f"{args.filename}.pdf"
    output_pdf_path = os.path.join(directory, output_pdf)

    # Steps 4–6: retrieve/filter/sort
    pdf_files = list_pdf_files(directory)

    # Step 7: report
    print(f"PDF files found: {len(pdf_files)}")
    print("List:")
    for n in pdf_files:
        print(n)

    # Step 8: prompt
    if not prompt_continue():
        print("Operation cancelled.")
        sys.exit(0)

    # Step 9–10: append/export
    merge_pdfs(directory, output_pdf_path, pdf_files)
    print(f"Merged PDF saved as: {output_pdf_path}")

    # Bonus: extract text to .txt
    if args.extract_text:
        txt_path = os.path.join(directory, f"{args.filename}.txt")
        extract_text_from_pdf(output_pdf_path, txt_path)
        print(f"Extracted text saved as: {txt_path}")


if __name__ == "__main__":
    main()