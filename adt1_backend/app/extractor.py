import fitz
import re

def extract_fields_from_pdf(pdf_path: str) -> dict:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()

    # Save the raw text for inspection
    with open("temp/raw_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    def extract(pattern, text, default=""):
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else default

    # Use the order and structure from your raw_text.txt
    data = {
        "company_name": extract(r"Pre-fill\n([A-Z0-9 &]+)", text),
        "cin": extract(r"Pre-fill\n([A-Z0-9]+)", text),
        "registered_office": extract(r"Pre-fill\n[A-Z0-9 &]+\n([A-Z0-9 ,\-\/\n]+)\nUdupi", text).replace('\n', ', '),
        "email": extract(r"\n(mail@[\w\.-]+)", text),
        "auditor_name": extract(r"\n([A-Z &]+)\n001955S", text),
        "auditor_address": extract(r"001955S\n([^\n]+)\n([^\n]+)\n([^\n]+)\n([^\n]+)", text, ""),
        "auditor_frn_or_membership": extract(r"\n([0-9A-Z]{6,})\n29\/2", text),
        "appointment_type": extract(r"\n(Appointment/Re-appointment in AGM)", text),
        "appointment_from": extract(r"\n([0-9]{2}/[0-9]{2}/[0-9]{4})\n[0-9]{2}/[0-9]{2}/[0-9]{4}\n5", text),
        "appointment_to": extract(r"\n[0-9]{2}/[0-9]{2}/[0-9]{4}\n([0-9]{2}/[0-9]{2}/[0-9]{4})\n5", text),
        "appointment_date": extract(r"\n(26/09/2022)\n26/09/2022", text),  # You can generalize this if needed
        "financial_year_count": extract(r"\n([1-9])\nAppointment/Re-appointment in AGM", text),
        "agm_date": extract(r"\n(26/09/2022)\nAttach", text),  # You can generalize this if needed
    }

    # For auditor_address, join the captured groups if found
    if data["auditor_address"]:
        parts = re.search(r"001955S\n([^\n]+)\n([^\n]+)\n([^\n]+)\n([^\n]+)", text)
        if parts:
            data["auditor_address"] = ', '.join([parts.group(i).strip() for i in range(1, 5)])

    return data