import os
import sys
import shutil
import importlib.util
from pathlib import Path
import pandas as pd
import google.generativeai as genai

# -------------------- Gemini Config --------------------
# -------------------- Gemini Config --------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY not set. Please set it via environment variable.")
genai.configure(api_key=API_KEY)


# -------------------- Utils --------------------
def load_parser(module_path: Path):
    """Dynamically load a parser module from file path"""
    spec = importlib.util.spec_from_file_location("parser_module", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe for comparison"""
    df = df.fillna("").astype(str)
    df.columns = [c.strip() for c in df.columns]
    return df.reset_index(drop=True)

def score_parser(df_actual: pd.DataFrame, df_expected: pd.DataFrame) -> float:
    """Return similarity score (%) between two DataFrames"""
    min_len = min(len(df_actual), len(df_expected))
    df_actual = df_actual.head(min_len).reset_index(drop=True)
    df_expected = df_expected.head(min_len).reset_index(drop=True)

    matches = (df_actual == df_expected).sum().sum()
    total = df_expected.size
    return (matches / total) * 100 if total > 0 else 0.0

# -------------------- LLM Call --------------------
def generate_parser_with_llm(target: str, save_path: Path, feedback: str = ""):
    """Use Gemini to generate a custom parser file"""
    prompt = f"""
You are an AI agent that writes a Python parser for {target} bank statement PDFs.

Requirements:
- Create a function `parse(pdf_path: str) -> pd.DataFrame`
- Use `pdfplumber` to read the PDF
- Extract columns exactly as in results.csv: Date,Description,Debit Amt,Credit Amt,Balance
- Clean whitespace, handle empty debit/credit cells
- Return a pandas DataFrame with correct schema
- Do not include ```python fences in output

{feedback}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    code = response.text
    # Remove code fences if present
    code = code.replace("```python", "").replace("```", "").strip()

    save_path.write_text(code, encoding="utf-8")
    print(f"[Agent] Wrote {save_path} ({len(code)} chars)")

# -------------------- Main Agent --------------------
def run_agent(target: str, attempts: int = 5):
    data_dir = Path("data") / target
    parser_path = Path("custom_parsers") / f"{target}_parser.py"
    best_parser_path = Path("custom_parsers") / f"{target}_parser_best.py"
    csv_path = data_dir / "results.csv"
    pdf_path = data_dir / f"{target}_sample.pdf"

    df_expected = pd.read_csv(csv_path)

    best_score = -1
    feedback = ""

    for i in range(1, attempts + 1):
        print(f"\n[Agent] Attempt {i}/{attempts} — generating parser for '{target}'")

        if parser_path.exists():
            parser_path.unlink()

        generate_parser_with_llm(target, parser_path, feedback)

        try:
            parser = load_parser(parser_path)
            df_actual = parser.parse(str(pdf_path))
            score = score_parser(normalize(df_actual), normalize(df_expected))
            print(f"[Agent] Score for attempt {i}: {score:.2f}%")
        except Exception as e:
            print(f"[Agent] Parser crashed on attempt {i}: {e}")
            score = 0

        # update feedback for next attempt
        feedback = f"Previous attempt scored {score:.2f}%. Fix parsing issues and match results.csv exactly."

        if score > best_score:
            best_score = score
            shutil.copy(parser_path, best_parser_path)

    print(f"\n[Agent] ✅ Finished {attempts} attempts")
    print(f"[Agent] Best score: {best_score:.2f}%")
    print(f"[Agent] Best parser saved at {best_parser_path}")

# -------------------- CLI --------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Bank target name (e.g., icici)")
    parser.add_argument("--attempts", type=int, default=5, help="Number of retries")
    args = parser.parse_args()

    run_agent(args.target, args.attempts)
