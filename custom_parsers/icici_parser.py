import pdfplumber
import pandas as pd
import re

def parse(pdf_path: str) -> pd.DataFrame:
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

    # Extract data section (adjust regex if needed based on PDF structure)
    data_section = re.search(r"Date\s*Description\s*Debit Amt\s*Credit Amt\s*Balance.*?(?=\n\n|$)", text, re.DOTALL).group(0)

    lines = data_section.splitlines()
    header = [re.sub(r'\s+', ' ', line).strip() for line in lines[:1]][0].split()
    data = [re.sub(r'\s+', ' ', line).strip().split() for line in lines[1:]]

    #Handle inconsistent spacing and missing values
    cleaned_data = []
    for row in data:
      if len(row) < 5:
        row.extend([''] * (5 - len(row)))
      cleaned_data.append(row)

    df = pd.DataFrame(cleaned_data, columns=header)

    #Clean and convert data types
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    df['Debit Amt'] = df['Debit Amt'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', 0).astype(float)
    df['Credit Amt'] = df['Credit Amt'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', 0).astype(float)
    df['Balance'] = df['Balance'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', 0).astype(float)


    return df