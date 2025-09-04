import pdfplumber
import pandas as pd
import re

def parse(pdf_path: str) -> pd.DataFrame:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()

    # Extract data using regular expressions.  Adjust these if needed based on your PDF's formatting.
    lines = text.splitlines()
    data = []
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line or "Statement Summary" in cleaned_line or "Balance" in cleaned_line or "Page" in cleaned_line:
            continue  #Skip header, footer and summary lines

        match = re.match(r"(\d{2}/\d{2}/\d{4})\s*([^\d]+)\s*(\d+\.?\d*|\s*)\s*(\d+\.?\d*|\s*)\s*(\d+\.?\d*)", cleaned_line)
        if match:
            date, description, debit, credit, balance = match.groups()
            debit = debit.strip() if debit else ''
            credit = credit.strip() if credit else ''
            data.append([date, description.strip(), debit, credit, balance])

    df = pd.DataFrame(data, columns=["Date", "Description", "Debit Amt", "Credit Amt", "Balance"])

    # Convert numeric columns to numeric, handling potential errors
    for col in ["Debit Amt", "Credit Amt", "Balance"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df