#!/usr/bin/env python3
import pandas as pd
import argparse
from pathlib import Path

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='View contents of a Parquet file')
    parser.add_argument('file', help='Path to the Parquet file')
    parser.add_argument('-n', '--rows', type=int, default=10, help='Number of rows to display (default: 10)')
    args = parser.parse_args()

    # Verify file exists
    parquet_path = Path(args.file)
    if not parquet_path.exists():
        print(f"Error: File not found: {parquet_path}")
        return 1

    # Read the parquet file
    df = pd.read_parquet(parquet_path)

    # Print basic information
    print(f"Total rows: {len(df):,}")
    print(f"\nFirst {args.rows} rows:")
    print(df.head(args.rows))
    print("\nData types:")
    print(df.dtypes)

    return 0

if __name__ == '__main__':
    exit(main()) 