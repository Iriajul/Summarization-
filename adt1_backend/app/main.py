from fastapi import FastAPI, File, UploadFile
from app.extractor import extract_fields_from_pdf
from app.summarize import generate_summary
from app.attachments import extract_attachments
from app.models import ADT1Response, AttachmentInfo  # Fixed import path
from fastapi.responses import FileResponse
from fpdf import FPDF
import os
import uuid
import json
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ADT-1 Processor API",
    description="API for processing MCA ADT-1 auditor appointment forms",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "running", "version": "1.0.0"}

@app.post("/upload", response_model=ADT1Response)
async def upload_adt_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs("temp", exist_ok=True)
        pdf_path = f"temp/{file.filename}"
        logger.info(f"Processing file: {file.filename}")
        
        # Save uploaded file
        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)
            logger.info(f"Saved {len(content)} bytes to {pdf_path}")

        # Extract fields
        extracted_data = extract_fields_from_pdf(pdf_path)
        logger.info(f"Extracted data: {json.dumps(extracted_data, indent=2)}")
        
        # Save extracted data as JSON
        json_path = f"temp/{os.path.splitext(file.filename)[0]}_extracted.json"
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(extracted_data, jf, indent=2, ensure_ascii=False)
            logger.info(f"Saved extracted data to {json_path}")

        # Extract attachments
        attachments = extract_attachments(pdf_path)
        logger.info(f"Found {len(attachments)} attachments")
        
        # Create attachment info objects
        attachment_infos = [
            AttachmentInfo(
                filename=a["filename"], 
                text=a["text"], 
                type=a["type"]
            ) for a in attachments
        ]
        
        # Generate summary
        summary_data = {
            **extracted_data,
            "attachments": [a.dict() for a in attachment_infos]
        }
        summary = generate_summary(summary_data)
        logger.info("Generated summary successfully")
        
        return ADT1Response(
            extracted_data=extracted_data,
            attachments=attachment_infos,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return ADT1Response(
            extracted_data={"error": str(e)},
            attachments=[],
            summary="Processing failed due to an error"
        )

@app.post("/download-summary-pdf")
async def download_summary_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs("temp", exist_ok=True)
        pdf_path = f"temp/{file.filename}"
        logger.info(f"Processing PDF download for: {file.filename}")
        
        # Save uploaded file
        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)
            logger.info(f"Saved {len(content)} bytes to {pdf_path}")

        # Extract fields
        extracted_data = extract_fields_from_pdf(pdf_path)
        
        # Extract attachments
        attachments = extract_attachments(pdf_path)
        logger.info(f"Found {len(attachments)} attachments for summary PDF")
        
        # Generate summary
        summary_data = {
            **extracted_data,
            "attachments": [{"filename": a["filename"], "text": a["text"]} for a in attachments]
        }
        summary = generate_summary(summary_data)
        logger.info("Generated summary for PDF download")

        # Generate PDF
        summary_pdf_path = f"temp/summary_{uuid.uuid4().hex}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        
        # Handle special characters
        for line in summary.split('\n'):
            try:
                # Try UTF-8 first
                pdf.multi_cell(0, 10, line)
            except:
                try:
                    # Fallback to latin-1
                    pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
                except:
                    # Final fallback
                    pdf.multi_cell(0, 10, line.encode('utf-8', 'replace').decode('utf-8'))
        
        pdf.output(summary_pdf_path)
        logger.info(f"Generated summary PDF: {summary_pdf_path}")

        return FileResponse(
            summary_pdf_path,
            media_type="application/pdf",
            filename="auditor_appointment_summary.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating summary PDF: {str(e)}")
        return {"error": "Failed to generate summary PDF", "details": str(e)}