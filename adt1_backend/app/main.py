from fastapi import FastAPI, File, UploadFile
from app.extractor import extract_fields_from_pdf
from app.summarize import generate_summary
from app.attachments import extract_attachments
from .models import ADT1Response, AttachmentInfo
from fastapi.responses import FileResponse
from fpdf import FPDF
import os
import uuid  # For unique filenames
import json

app = FastAPI()

@app.post("/upload", response_model=ADT1Response)
async def upload_adt_pdf(file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)
    pdf_path = f"temp/{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    extracted_data = extract_fields_from_pdf(pdf_path)
    # Save extracted data as JSON
    json_path = f"temp/{os.path.splitext(file.filename)[0]}_extracted.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(extracted_data, jf, indent=2, ensure_ascii=False)

    attachments = extract_attachments(pdf_path)
    # Pass all info (filename, text, type)
    attachment_infos = [
        AttachmentInfo(filename=a["filename"], text=a["text"], type=a["type"])
        for a in attachments
    ]
    summary = generate_summary({
        **extracted_data,
        "attachments": [a.dict() for a in attachment_infos]
    })

    return ADT1Response(
        extracted_data=extracted_data,
        attachments=attachment_infos,
        summary=summary
    )

@app.post("/download-summary-pdf")
async def download_summary_pdf(file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)
    pdf_path = f"temp/{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    extracted_data = extract_fields_from_pdf(pdf_path)
    attachments = extract_attachments(pdf_path)
    attachment_summaries = [
        {"filename": a["filename"], "text": a["text"]} for a in attachments
    ]
    summary = generate_summary({
        **extracted_data,
        "attachments": attachment_summaries
    })

    # Generate PDF with a unique filename
    summary_pdf_path = f"temp/summary_{uuid.uuid4().hex}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in summary.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(summary_pdf_path)

    return FileResponse(summary_pdf_path, media_type="application/pdf", filename="summary.pdf")