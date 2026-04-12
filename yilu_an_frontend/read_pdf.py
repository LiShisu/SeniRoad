import pdfplumber

with pdfplumber.open('页面设计/老人端.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"=== Page {i+1} ===")
        text = page.extract_text()
        print(text)
        print()
