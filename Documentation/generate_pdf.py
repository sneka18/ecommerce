"""
Generates the Project_Documentation.pdf deliverable from the documentation text
using PyMuPDF (fitz).
"""
import sys
from pathlib import Path
import pymupdf as fitz

doc_dir = Path(__file__).resolve().parent
md_path = doc_dir / "Project_Documentation.md"
pdf_path = doc_dir / "Project_Documentation.pdf"

if not md_path.exists():
    print(f"Error: {md_path} does not exist.")
    sys.exit(1)

text_content = md_path.read_text(encoding="utf-8")
lines = text_content.splitlines()

doc = fitz.open()
PAGE_WIDTH = 595.0   # A4 width in points
PAGE_HEIGHT = 842.0  # A4 height in points
MARGIN_LEFT = 50.0
MARGIN_TOP = 50.0
MARGIN_BOTTOM = 50.0
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

current_page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
y = MARGIN_TOP

def check_new_page(required_space):
    global current_page, y
    if y + required_space > PAGE_HEIGHT - MARGIN_BOTTOM:
        current_page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        y = MARGIN_TOP

for line in lines:
    line_stripped = line.strip()

    # Title / Header 1
    if line_stripped.startswith("# "):
        title_text = line_stripped.replace("# ", "")
        check_new_page(40)
        current_page.draw_rect(
            fitz.Rect(MARGIN_LEFT - 10, y - 4, PAGE_WIDTH - MARGIN_LEFT + 10, y + 26),
            color=None,
            fill=(0.2, 0.22, 0.55)
        )
        current_page.insert_text(fitz.Point(MARGIN_LEFT, y + 16), title_text, fontsize=16, color=(1, 1, 1), fontname="helv")
        y += 36

    # Header 2
    elif line_stripped.startswith("## "):
        h2_text = line_stripped.replace("## ", "")
        check_new_page(30)
        current_page.insert_text(fitz.Point(MARGIN_LEFT, y + 14), h2_text, fontsize=13, color=(0.15, 0.2, 0.45), fontname="helv")
        current_page.draw_line(fitz.Point(MARGIN_LEFT, y + 18), fitz.Point(PAGE_WIDTH - MARGIN_LEFT, y + 18), color=(0.7, 0.75, 0.85), width=1)
        y += 26

    # Header 3
    elif line_stripped.startswith("### "):
        h3_text = line_stripped.replace("### ", "")
        check_new_page(22)
        current_page.insert_text(fitz.Point(MARGIN_LEFT, y + 12), h3_text, fontsize=11, color=(0.2, 0.25, 0.35), fontname="helv")
        y += 20

    # Header 4
    elif line_stripped.startswith("#### "):
        h4_text = line_stripped.replace("#### ", "")
        check_new_page(18)
        current_page.insert_text(fitz.Point(MARGIN_LEFT, y + 10), h4_text, fontsize=10, color=(0.3, 0.35, 0.45), fontname="helv")
        y += 16

    # Horizontal Rule
    elif line_stripped.startswith("---"):
        check_new_page(10)
        current_page.draw_line(fitz.Point(MARGIN_LEFT, y + 4), fitz.Point(PAGE_WIDTH - MARGIN_LEFT, y + 4), color=(0.8, 0.8, 0.8), width=0.5)
        y += 12

    # Empty Line
    elif not line_stripped:
        y += 6

    # Normal prose or bullet
    else:
        # Wrap long text
        words = line_stripped.split(" ")
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            # Roughly 95 characters per line on A4 with margin
            if len(test_line) > 85:
                current_line.pop()
                full_line = " ".join(current_line)
                check_new_page(14)
                current_page.insert_text(fitz.Point(MARGIN_LEFT, y + 10), full_line, fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv")
                y += 13
                current_line = [word]

        if current_line:
            full_line = " ".join(current_line)
            check_new_page(14)
            current_page.insert_text(fitz.Point(MARGIN_LEFT, y + 10), full_line, fontsize=9, color=(0.1, 0.1, 0.1), fontname="helv")
            y += 13

doc.save(str(pdf_path))
print(f"Successfully generated academic project PDF: {pdf_path} (Pages: {len(doc)})")

