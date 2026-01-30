import requests
import os

PDFCO_API_KEY = os.getenv("PDFCO_API_KEY")

def convertir_a_pdf_pdfco(docx_path):
    pdf_path = docx_path.replace(".docx", ".pdf")

    with open(docx_path, "rb") as f:
        response = requests.post(
            "https://api.pdf.co/v1/pdf/convert/from/doc",
            headers={
                "x-api-key": PDFCO_API_KEY
            },
            files={
                "file": f
            }
        )

    result = response.json()

    if not result.get("url"):
        raise Exception(f"Error PDF.co: {result}")

    pdf_url = result["url"]

    pdf_data = requests.get(pdf_url).content

    with open(pdf_path, "wb") as f:
        f.write(pdf_data)

    return pdf_path
