from pydantic import BaseModel
from typing import List, Dict, Optional

class AttachmentInfo(BaseModel):
    filename: str
    text: str
    type: str

class ADT1Response(BaseModel):
    extracted_data: Dict[str, str]
    attachments: List[AttachmentInfo]
    summary: str

class ADT1Fields(BaseModel):
    company_name: str = ""
    cin: str = ""
    registered_office: str = ""
    email: str = ""
    auditor_name: str = ""
    auditor_address: str = ""
    auditor_frn_or_membership: str = ""
    appointment_type: str = ""
    appointment_from: str = ""
    appointment_to: str = ""
    appointment_date: str = ""
    financial_year_count: str = ""
    agm_date: str = ""