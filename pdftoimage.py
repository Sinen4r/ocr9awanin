# pip install pymupdf
import fitz  # PyMuPDF
from pathlib import Path
from typing import Iterable, Optional
from tqdm import tqdm

def convert_pdf_to_images(
    pdf_path: str,
    out_dir: str = "pdf_images",
    dpi: int = 200,
    fmt: str = "png",
    pages: Optional[Iterable[int]] = None,  # 0-based page indices; None = all
    prefix: Optional[str] = None,
):
    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    try:
        # Scale factor from DPI (default pixmap is 72 dpi)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        page_indices = pages if pages is not None else range(len(doc))
        base = prefix if prefix else pdf_path.stem

        saved = []
        for i in tqdm(page_indices):
            page = doc.load_page(i)  # zero-based
            pix = page.get_pixmap(matrix=mat, alpha=False,colorspace=fitz.csGRAY)
            out_file = out_dir / f"{base}_page-{i+1:03d}.{fmt.lower()}"
            pix.save(out_file.as_posix())
            saved.append(out_file.as_posix())

        print(f"Saved {len(saved)} image(s) to: {out_dir.resolve()}")
        return saved
    finally:
        doc.close()

if __name__ == "__main__":
    # Example usage
    # python script.py  (when run directly)
    convert_pdf_to_images("COCArabe.pdf", out_dir="COCArabe", dpi=200, fmt="png")
