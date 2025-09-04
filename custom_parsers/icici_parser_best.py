import pdfplumber
import pandas as pd
import re

def parse(pdf_path: str) -> pd.DataFrame:
    with pdfplumber.open(pdf_path) as pdf:
        # Assuming the table starts on page 1.  Adjust if needed.
        first_page = pdf.pages[0]
        table = first_page.extract_table()

    # Clean up the extracted table
    cleaned_table = []
    for row in table:
        cleaned_row = [cell.strip() if isinstance(cell, str) else cell for cell in row]
        cleaned_table.append(cleaned_row)


    #Handle potential inconsistencies in the number of columns
    max_cols = max(len(row) for row in cleaned_table)
    for row in cleaned_table:
        while len(row) < max_cols:
            row.append('')


    #Identify header row (heuristic based on "Date" column presence)
    header_index = next((i for i, row in enumerate(cleaned_table) if "Date" in row), None)
    if header_index is None:
        raise ValueError("Could not find header row in PDF")
    header = cleaned_table[header_index]
    data_rows = cleaned_table[header_index + 1:]

    #Create DataFrame
    df = pd.DataFrame(data_rows, columns=header)

    #Clean numeric columns
    for col in ['Debit Amt', 'Credit Amt', 'Balance']:
        df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce') #Handle non-numeric values gracefully

    #Handle empty debit/credit cells
    df['Debit Amt'] = df['Debit Amt'].fillna(0)
    df['Credit Amt'] = df['Credit Amt'].fillna(0)

    return df