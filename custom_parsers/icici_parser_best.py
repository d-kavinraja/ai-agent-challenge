import pdfplumber
import pandas as pd
import re

def parse(pdf_path: str) -> pd.DataFrame:
    """
    Parses an ICICI bank statement PDF and returns a pandas DataFrame.
    """

    with pdfplumber.open(pdf_path) as pdf:
        # Assuming the table is on the first page for simplicity.  Adjust as needed for multi-page statements.
        first_page = pdf.pages[0]
        table = first_page.extract_table()

    # Clean up the extracted table data
    cleaned_table = []
    for row in table:
        cleaned_row = [cell.strip() if isinstance(cell, str) else cell for cell in row]
        cleaned_table.append(cleaned_row)


    #Data Cleaning and column identification.  This section is highly dependent on the specific format of your PDF.
    # You might need to adjust the regex patterns and column indices based on your PDF's structure.


    header_index = 0 #Find the header row index. This might need adjustment based on your PDF
    headers = cleaned_table[header_index]
    data_rows = cleaned_table[header_index+1:]

    #Handle potential inconsistencies in header names.
    header_map = {
        "Date": "Date",
        "Description": "Description",
        "Debit Amt": "Debit Amt",
        "Credit Amt": "Credit Amt",
        "Balance": "Balance"

    }
    
    #Remap headers if needed based on variations
    headers = [header_map.get(header, header) for header in headers]


    # Create a pandas DataFrame
    df = pd.DataFrame(data_rows, columns=headers)



    #Clean Numeric Columns
    numeric_cols = ["Debit Amt", "Credit Amt", "Balance"]
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    #Handle empty debit/credit cells
    df["Debit Amt"].fillna(0, inplace=True)
    df["Credit Amt"].fillna(0, inplace=True)



    return df