import fitz
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path, dpi=400)
        debug_dir = os.path.join(os.path.dirname(__file__), "debug_output")
        os.makedirs(debug_dir, exist_ok=True)
        for i, img in enumerate(images):
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            for thresh_val in [127, 150, 160]:
                _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                sharpened = cv2.filter2D(thresh, -1, kernel)
                img_save_path = os.path.join(debug_dir, f"page_{i}_thresh{thresh_val}.png")
                cv2.imwrite(img_save_path, sharpened)
                ocr_result = pytesseract.image_to_string(sharpened, config='--psm 6')
                if ocr_result.strip():
                    text += ocr_result
                    break
            if not text.strip():
                text += pytesseract.image_to_string(gray)
    except Exception as e:
        text += f"\n[OCR failed: {e}]"

    # --- Save OCR text to attachments_text folder ---
    attachments_text_dir = os.path.join(os.path.dirname(__file__), "attachments_text")
    os.makedirs(attachments_text_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_save_path = os.path.join(attachments_text_dir, f"{base_name}.txt")
    with open(txt_save_path, "w", encoding="utf-8") as f:
        f.write(text)
    # --- End save ---

    return text

def extract_attachments(pdf_path: str, output_dir: str = "temp/attachments") -> list:
    attachments = []
    os.makedirs(output_dir, exist_ok=True)
    allowed_exts = [".pdf", ".txt"]  # Only allow PDF and text files
    with fitz.open(pdf_path) as doc:
        for i in range(doc.embfile_count()):
            try:
                info = doc.embfile_info(i)
                fname = info.get("filename", f"attachment_{i}")
                ext = os.path.splitext(fname)[1].lower()
                if ext not in allowed_exts:
                    continue  # Skip non-pdf/txt files
                fdata = doc.embfile_get(i)
                out_path = os.path.join(output_dir, fname)
                with open(out_path, "wb") as f:
                    f.write(fdata)

                # --- Attachment type/status detection ---
                text_content = ""
                attachment_type = ""
                if ext == ".pdf":
                    try:
                        with fitz.open(out_path) as adoc:
                            for page in adoc:
                                text_content += page.get_text()
                        if not text_content.strip():
                            # No extractable text, likely a scanned image
                            text_content = ocr_pdf(out_path)
                            attachment_type = "scanned_image_pdf" if text_content.strip() else "empty_pdf"
                        else:
                            attachment_type = "text_pdf"
                    except Exception:
                        # Not a valid PDF
                        text_content = ""
                        attachment_type = "invalid_pdf"
                elif ext == ".txt":
                    try:
                        with open(out_path, "r", encoding="utf-8", errors="ignore") as tf:
                            text_content = tf.read()
                        attachment_type = "text_txt"
                    except Exception:
                        text_content = ""
                        attachment_type = "invalid_txt"
                else:
                    text_content = ""
                    attachment_type = "unsupported"

                attachments.append({
                    "filename": fname,
                    "output_path": out_path,
                    "text": text_content[:1000],
                    "type": attachment_type
                })
            except Exception as e:
                attachments.append({
                    "filename": f"attachment_{i}",
                    "output_path": None,
                    "text": f"Could not extract attachment {i}: {e}",
                    "type": "extraction_error"
                })
    return attachments