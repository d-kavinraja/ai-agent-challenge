# run_parser_tests.py
import argparse
import importlib
import sys
import pandas as pd

def main():
    """
    Dynamically imports and tests a parser module.
    Exits with code 0 on success and 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Test runner for dynamically generated parsers.")
    parser.add_argument("--parser_module", required=True, help="The full module path of the parser to test.")
    parser.add_argument("--pdf_path", required=True, help="Path to the PDF file to parse.")
    parser.add_argument("--csv_path", required=True, help="Path to the ground truth CSV file.")
    args = parser.parse_args()

    try:
        # 1. Dynamically import the generated parser module
        print(f"Attempting to import module: {args.parser_module}")
        module = importlib.import_module(args.parser_module)
        
        # 2. Call the parse() function from the imported module
        print(f"Parsing PDF: {args.pdf_path}")
        generated_df = module.parse(args.pdf_path)
        
        # 3. Load the ground truth CSV, ensuring data types are consistent
        print(f"Loading expected CSV: {args.csv_path}")
        expected_df = pd.read_csv(args.csv_path)

        # 4. Perform a strict comparison using pandas testing utility
        # This checks shape, column names, dtypes, and values.
        pd.testing.assert_frame_equal(generated_df, expected_df)
        
        print("✅ Validation successful: DataFrame matches the expected CSV.")
        sys.exit(0) # Exit with success code

    except Exception as e:
        # Print the exception to stderr so the agent can capture it for self-correction.
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(1) # Exit with failure code

if __name__ == "__main__":
    main()