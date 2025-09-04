import pandas as pd
from pathlib import Path
import importlib.util

def load_parser(module_path: Path):
    spec = importlib.util.spec_from_file_location("bank_parser", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Ensure column order and string types
    cols = ["Date", "Description", "Debit Amt", "Credit Amt", "Balance"]
    df = df[cols]
    for c in cols:
        df[c] = df[c].fillna("").astype(str).str.strip()
    return df

def test_icici_equals_csv():
    target = "icici"
    module_path = Path("custom_parsers") / f"{target}_parser.py"
    assert module_path.exists(), f"{module_path} does not exist. Run agent.py first."
    parser = load_parser(module_path)
    pdf_path = Path("data")/target/f"{target}_sample.pdf"
    csv_path = Path("data")/target/"results.csv"
    df_expected = pd.read_csv(csv_path)
    # Parse PDF (if missing, allow developer to drop a CSV with same name for quick test)
    if not pdf_path.exists() and (csv_path).exists():
        df_actual = pd.read_csv(csv_path)
    else:
        df_actual = parser.parse(str(pdf_path))
    assert normalize(df_actual).equals(normalize(df_expected)), "Parsed DataFrame != expected CSV"
