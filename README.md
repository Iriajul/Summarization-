# ADT-1 Form Processing API

This FastAPI application processes MCA ADT-1 forms (auditor appointment documents), extracts key information, handles attachments, and generates AI-powered summaries using Groq's LLaMA3 model.

---

## 🚀 Features

- **PDF Field Extraction**: Parses structured data from ADT-1 forms.
- **Attachment Handling**: 
  - Extracts embedded PDF/TXT attachments.
  - Performs OCR on scanned documents.
  - Classifies attachment types.
- **AI Summarization**: Generates summaries using Groq’s LLaMA3-70B model.
- **PDF Report Generation**: Creates downloadable summary reports.
- **Text Preprocessing**: Image enhancement and multiple OCR strategies.

---

## 📦 Requirements

- Python 3.9+
- Tesseract OCR installed system-wide
- [Groq API Key](https://console.groq.com/) (free tier available)

---

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Summarization-.git
cd adt1-processor

# Create virtual environment
python -m venv venv
# Activate virtual environment
source venv/bin/activate     # On Linux/macOS
venv\Scripts\activate        # On Windows

# Install dependencies
pip install -r requirements.txt

# Install Tesseract (Ubuntu example)
sudo apt install tesseract-ocr
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key_here

```

---

## 📁 Directory Structure (Auto-created at runtime)

```
adt1-processor/
├── temp/                  # Uploaded PDFs
├── temp/attachments/      # Extracted attachments
├── attachments_text/      # OCR results
└── debug_output/          # Preprocessed images
```

---

## ▶️ Usage

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

---

## 🔌 Endpoints

### 1. `POST /upload`
Upload an ADT-1 PDF. Returns structured company info, attachments, and summary.

### 2. `POST /download-summary-pdf`
Download the generated AI summary as a PDF report.

---

## 📤 Response Example

```json
{
  "extracted_data": {
    "company_name": "EXAMPLE LTD",
    "cin": "U12345MH2022PTC123456",
    "registered_office": "Mumbai, Maharashtra"
  },
  "attachments": [
    {
      "filename": "consent.pdf",
      "text": "Extracted text content...",
      "type": "text_pdf"
    }
  ],
  "summary": "Auditor appointment summary with attachment analysis..."
}
```

---

## 🗂️ Project Structure

```
adt1-processor/
├── app/
│   ├── attachments.py       # Attachment extraction and OCR logic
│   ├── extractor.py         # ADT-1 field parsing
│   ├── summarize.py         # AI-powered summarization
│   ├── models.py            # Pydantic data models
│   └── main.py              # FastAPI application
├── test_ocr.py              # Standalone OCR testing
├── requirements.txt         # Python dependencies
├── .env                     # API keys and config
└── README.md                # Documentation
```

---

## 🧠 Key Technologies

- **FastAPI** – Web framework
- **PyMuPDF (fitz)** – PDF parsing
- **Tesseract OCR** – Text extraction from scanned documents
- **OpenCV** – Image preprocessing
- **Groq API (LLaMA3-70B)** – AI summarization
- **FPDF** – PDF report generation

---

## 🛠️ Troubleshooting

### OCR Issues
- Confirm Tesseract is installed:
  ```bash
  tesseract --version
  ```
- Check `debug_output/` for processed image logs.

### Attachment Errors
- Ensure uploaded files are valid `.pdf` or `.txt`
- Verify file permissions in `temp/` directory

### API Errors
- Validate `GROQ_API_KEY` in your `.env` file
- Check [Groq service status](https://status.groq.com)

---

## 📃 License

MIT License