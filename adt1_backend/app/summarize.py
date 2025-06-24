import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_summary(data: dict) -> str:
    prompt = (
        "You are an AI assistant. Summarize the following company auditor appointment information in 3–5 lines.\n\n"
        "Always include the following details in the summary if available: company name, CIN, registered office, email, auditor name, auditor address, auditor FRN or membership number, appointment type, appointment dates, and AGM date.\n"
        "Format your output exactly like this (including bold filenames using double asterisks):\n\n"
        "Here is a summary of the company auditor appointment information:\n\n"
        "[Your 3-5 line summary here, mentioning all the above fields if present]\n\n"
        "Here are the summaries of the attached files:\n\n"
        "- **[filename]**: [summary of what it confirms, states, or contains]\n"
        "- **[filename]**: [summary...]\n"
        "- **[filename]**: [summary...]\n"
        "- **[filename]**: [summary...]\n\n"
        "If the attachment is a consent letter, board resolution, or intimation letter, mention any key dates, names, or approvals found in the text.\n"
        "If the attachment text is missing or unreadable, say so in the summary for that file.\n"
        "If you find any additional insight (such as a signed consent, unanimous board approval, or special notes), mention it in the summary.\n"
        "Be as detailed as possible in both the main summary and the attachment summaries. Include all relevant names, dates, and any notable observations. If there are multiple attachments, summarize each one in a separate bullet point.\n"
        "Here is the data:\n\n"
        + json.dumps(data, indent=2)
    )
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.1
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]