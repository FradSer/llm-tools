#!/usr/bin/env python3

"""
JSONL to Parquet converter
This script converts JSONL files to Parquet format.
"""

import argparse
import pandas as pd
from pathlib import Path
import sys
import logging
import os
import time
from typing import Optional, Dict, Any

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
    
    if sample_data and 'source' in sample_data and 'target' in sample_data:
        source = sample_data['source'][:30] + ('...' if len(str(sample_data['source'])) > 30 else '')
        target = sample_data['target'][:30] + ('...' if len(str(sample_data['target'])) > 30 else '')
        progress += f" | Latest: {source} => {target}"
    
    sys.stdout.write(f"\r{progress}")
    sys.stdout.flush()

def read_jsonl(input_path: str) -> pd.DataFrame:
    """
    Read a JSONL file into a pandas DataFrame
    
    Args:
        input_path: Path to the input JSONL file
        
    Returns:
        pandas DataFrame containing the data
    """
    try:
        logger.info(f"Reading JSONL file: {input_path}")
        # Get file size
        file_size = os.path.getsize(input_path)
        total_lines = sum(1 for _ in open(input_path, 'rb'))
        
        # Read the file with progress updates
        chunks = []
        bytes_read = 0
        for i, chunk in enumerate(pd.read_json(input_path, lines=True, chunksize=1000)):
            bytes_read = os.path.getsize(input_path) * (i * 1000) // total_lines
            chunks.append(chunk)
            if len(chunk) > 0:
                sample = chunk.iloc[-1].to_dict()
            else:
                sample = None
            update_progress(i * 1000, total_lines, file_size, bytes_read, sample)
        
        df = pd.concat(chunks)
        print()  # New line after progress bar
        return df
        
    except Exception as e:
        logger.error(f"Error reading JSONL file: {e}")
        raise

def convert_to_parquet(df: pd.DataFrame, output_path: str) -> None:
    """
    Convert DataFrame to Parquet format and save to file
    
    Args:
        df: Input pandas DataFrame
        output_path: Path where to save the Parquet file
    """
    try:
        logger.info(f"Converting to Parquet: {output_path}")
        total_rows = len(df)
        
        # Show initial progress
        update_progress(0, total_rows)
        
        # Convert to parquet with progress updates
        df.to_parquet(output_path, index=False)
        
        # Show final progress
        update_progress(total_rows, total_rows)
        print()  # New line after progress
        
        logger.info("Conversion completed successfully")
    except Exception as e:
        logger.error(f"Error converting to Parquet: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Convert JSONL files to Parquet format')
    parser.add_argument('input', help='Input JSONL file path')
    parser.add_argument('output', help='Output Parquet file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Read JSONL
        df = read_jsonl(args.input)
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to Parquet
        convert_to_parquet(df, str(output_path))
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 