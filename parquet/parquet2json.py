#!/usr/bin/env python3

"""
Parquet to JSON converter
This script converts Parquet files to a specific JSON format.
"""

import argparse
import pandas as pd
import json
from pathlib import Path
import sys
import logging
import os
import time
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_progress(current: int, total: int, file_size: int = 0, bytes_read: int = 0, sample_data: Optional[Dict[str, Any]] = None) -> None:
    """Update the progress bar"""
    now = time.time()
    if not hasattr(update_progress, 'last_update'):
        update_progress.last_update = 0
    
    # Update progress at most every 100ms
    if now - update_progress.last_update < 0.1:
        return
    
    update_progress.last_update = now
    
    # Clear the current line
    sys.stdout.write('\r\x1b[K')
    
    # Show progress
    progress = f"Progress: {current:,}/{total:,} records"
    if file_size:
        percentage = round((bytes_read / file_size) * 100)
        progress += f" [{percentage}%]"
    
    if sample_data and 'question' in sample_data:
        question = sample_data['question'][:30] + ('...' if len(str(sample_data['question'])) > 30 else '')
        progress += f" | Latest: {question}"
    
    sys.stdout.write(f"\r{progress}")
    sys.stdout.flush()

def read_parquet(input_path: str) -> pd.DataFrame:
    """
    Read a Parquet file into a pandas DataFrame
    
    Args:
        input_path: Path to the input Parquet file
        
    Returns:
        pandas DataFrame containing the data
    """
    try:
        logger.info(f"Reading Parquet file: {input_path}")
        # Get file size
        file_size = os.path.getsize(input_path)
        
        # Read the parquet file
        df = pd.read_parquet(input_path)
        total_rows = len(df)
        
        # Show progress
        update_progress(total_rows, total_rows, file_size, file_size)
        print()  # New line after progress bar
        
        return df
        
    except Exception as e:
        logger.error(f"Error reading Parquet file: {e}")
        raise

def convert_to_json_format(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert DataFrame to specific JSON format
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        List of dictionaries in the desired format
    """
    try:
        logger.info("Converting to JSON format")
        total_rows = len(df)
        result = []
        
        # Check if 'source' column exists (for compatibility with the example)
        question_col = 'source' if 'source' in df.columns else df.columns[0]
        
        for i, row in enumerate(df.itertuples()):
            # Extract the question from appropriate column
            question = getattr(row, question_col)
            
            # Create entry in the desired format
            entry = {
                "question": question,
                "is_answered": True
            }
            
            result.append(entry)
            
            # Update progress
            if i % 100 == 0 or i == total_rows - 1:
                update_progress(i + 1, total_rows, sample_data=entry)
        
        print()  # New line after progress
        return result
        
    except Exception as e:
        logger.error(f"Error converting to JSON format: {e}")
        raise

def save_to_json(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save data to JSON file
    
    Args:
        data: List of dictionaries to save
        output_path: Path where to save the JSON file
    """
    try:
        logger.info(f"Saving to JSON file: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info("Conversion completed successfully")
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Convert Parquet files to specific JSON format')
    parser.add_argument('input', help='Input Parquet file path')
    parser.add_argument('output', help='Output JSON file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--question-column', help='Column to use as question (defaults to "source")', default='source')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Read Parquet
        df = read_parquet(args.input)
        
        # If specified question column exists, rename it to make processing consistent
        if args.question_column != 'source' and args.question_column in df.columns:
            df = df.rename(columns={args.question_column: 'source'})
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON format
        json_data = convert_to_json_format(df)
        
        # Save to JSON file
        save_to_json(json_data, str(output_path))
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 