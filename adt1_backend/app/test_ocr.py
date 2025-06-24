from attachments import ocr_pdf 


pdf_path = "temp/attachments/Intimation Letter Signed.pdf" 

# Run OCR and print result
extracted_text = ocr_pdf(pdf_path)

print("\n🧾 Extracted Text from Attachment:")
print("=" * 50)
print(extracted_text)