#!/usr/bin/env python3

"""
Parquet Cleaner Tool
This script cleans source data in Parquet files according to specific rules.
"""

import argparse
import pandas as pd
from pathlib import Path
import sys
import logging
import os
import time
import re
from typing import Tuple, List, Dict
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_progress(current: int, total: int) -> None:
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
    percentage = round((current / total) * 100) if total > 0 else 0
    progress_bar = f"[{'#' * (percentage // 2)}{' ' * (50 - percentage // 2)}]"
    progress = f"Progress: {current:,}/{total:,} records {progress_bar} {percentage}%"
    
    sys.stdout.write(f"\r{progress}")
    sys.stdout.flush()

def analyze_length_distribution(df: pd.DataFrame) -> Dict:
    """
    Analyze the distribution of text lengths in the source column
    
    Args:
        df: Input pandas DataFrame with 'source' column
        
    Returns:
        Dictionary with length distribution statistics
    """
    # Convert non-string values to empty strings for length calculation
    lengths = df['source'].apply(lambda x: len(x) if isinstance(x, str) else 0)
    
    # Calculate distribution metrics
    stats = {
        'min_length': lengths.min(),
        'max_length': lengths.max(),
        'mean_length': round(lengths.mean(), 2),
        'median_length': int(lengths.median()),
        'total_rows': len(df)
    }
    
    # Create length bins for histogram
    bins = [0, 5, 10, 15, 20, 30, 50, 100, 200, 500, 1000, int(lengths.max())]
    labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]
    
    # Count rows in each length bin
    hist_data = pd.cut(lengths, bins=bins, labels=labels, right=False).value_counts().sort_index()
    stats['length_histogram'] = {label: count for label, count in zip(hist_data.index, hist_data.values)}
    
    # Calculate potential removal counts at different thresholds
    thresholds = [5, 10, 15, 20, 30, 50]
    stats['removal_counts'] = {
        f"length < {t}": int(sum(lengths < t)) for t in thresholds
    }
    
    # Count dash-only rows
    stats['dash_only_count'] = int(sum(df['source'] == '-'))
    
    return stats

def clean_source(df: pd.DataFrame, min_length: int = 10) -> Tuple[pd.DataFrame, dict]:
    """
    Clean the source column according to specified rules
    
    Args:
        df: Input pandas DataFrame with 'source' column
        min_length: Minimum character length for source text to keep (default: 10)
        
    Returns:
        Tuple of (cleaned DataFrame, statistics dictionary)
    """
    total_rows = len(df)
    stats = {
        'total_rows': total_rows,
        'removed_dash': 0,
        'removed_short': 0,
        'cleaned_leading_dash': 0,
        'remaining_rows': 0
    }
    
    # Create a backup of original data
    df_cleaned = df.copy()
    
    # 1. Remove rows where source is exactly "-"
    dash_mask = df_cleaned['source'] == '-'
    stats['removed_dash'] = dash_mask.sum()
    
    # 2. Remove short phrases based on character length
    def is_short_phrase(text):
        if not isinstance(text, str):
            return False
        # Simply check text length
        return len(text) < min_length
    
    short_mask = df_cleaned['source'].apply(is_short_phrase)
    stats['removed_short'] = short_mask.sum()
    
    # Combine masks for removal
    remove_mask = dash_mask | short_mask
    
    # 3. For remaining rows, clean leading dash with space
    def clean_leading_dash(text):
        if not isinstance(text, str):
            return text
        if text.startswith('- '):
            return text[2:]
        return text
    
    # Only process rows we're keeping
    keep_mask = ~remove_mask
    df_to_clean = df_cleaned[keep_mask].copy()
    
    # Apply the cleaning function and count modifications
    original_sources = df_to_clean['source'].tolist()
    df_to_clean['source'] = df_to_clean['source'].apply(clean_leading_dash)
    
    # Count how many were changed
    stats['cleaned_leading_dash'] = sum(
        1 for orig, new in zip(original_sources, df_to_clean['source'].tolist())
        if orig != new
    )
    
    # Final cleaned dataframe with bad rows removed
    df_cleaned = df_to_clean
    stats['remaining_rows'] = len(df_cleaned)
    
    return df_cleaned, stats

def sample_data(df: pd.DataFrame, target_size: int = 20000) -> Tuple[pd.DataFrame, dict]:
    """
    Sample data from specific length ranges to create a balanced dataset
    
    Args:
        df: Input pandas DataFrame with 'source' column
        target_size: Target size of the sampled dataset
        
    Returns:
        Tuple of (sampled DataFrame, statistics dictionary)
    """
    # Calculate source text lengths
    df['length'] = df['source'].apply(lambda x: len(x) if isinstance(x, str) else 0)
    
    # Define the length ranges to sample from
    ranges = [
        (30, 49),   # 短句子
        (50, 99),   # 中等长度
        (100, 199), # 长句子
        (200, 499)  # 非常长的句子
    ]
    
    # Define sampling weights for each range (can be adjusted)
    # Current weights: 30%, 40%, 25%, 5%
    weights = [0.30, 0.40, 0.25, 0.05]
    
    # Calculate number of samples for each range
    sample_counts = [int(target_size * weight) for weight in weights]
    
    # Adjust the last count to ensure we get exactly target_size samples
    sample_counts[-1] += target_size - sum(sample_counts)
    
    # Store statistics
    stats = {
        'original_size': len(df),
        'target_size': target_size,
        'actual_size': 0,
        'ranges': {}
    }
    
    sampled_dfs = []
    for i, ((min_len, max_len), count) in enumerate(zip(ranges, sample_counts)):
        # Filter data for this range
        range_mask = (df['length'] >= min_len) & (df['length'] <= max_len)
        range_df = df[range_mask]
        
        # Calculate available samples in this range
        available = len(range_df)
        
        # Adjust sample count if not enough data
        actual_count = min(count, available)
        
        # Sample data
        if actual_count > 0:
            if actual_count < available:
                range_sample = range_df.sample(actual_count, random_state=42)
            else:
                range_sample = range_df
                
            sampled_dfs.append(range_sample)
            
            # Store statistics for this range
            stats['ranges'][f"{min_len}-{max_len}"] = {
                'available': available,
                'requested': count,
                'sampled': actual_count
            }
        else:
            stats['ranges'][f"{min_len}-{max_len}"] = {
                'available': available,
                'requested': count,
                'sampled': 0
            }
    
    # Combine all sampled data
    if sampled_dfs:
        sampled_df = pd.concat(sampled_dfs)
        stats['actual_size'] = len(sampled_df)
        
        # Remove the length column we added
        sampled_df = sampled_df.drop(columns=['length'])
        
        return sampled_df, stats
    else:
        return pd.DataFrame(columns=df.columns), stats

def print_length_distribution(stats: Dict) -> None:
    """
    Print the length distribution statistics in a readable format
    
    Args:
        stats: Dictionary with length distribution statistics
    """
    print("\n===== 句子长度分布分析 =====")
    print(f"总行数: {stats['total_rows']:,}")
    print(f"最短句子长度: {stats['min_length']}")
    print(f"最长句子长度: {stats['max_length']}")
    print(f"平均句子长度: {stats['mean_length']}")
    print(f"中位数句子长度: {stats['median_length']}")
    print(f"只包含破折号 '-' 的行数: {stats['dash_only_count']:,}")
    
    print("\n不同长度句子的数量:")
    for length_range, count in stats['length_histogram'].items():
        percentage = (count / stats['total_rows']) * 100
        print(f"  {length_range} 字符: {count:,} 行 ({percentage:.2f}%)")
    
    print("\n不同阈值下将被移除的行数:")
    for threshold, count in stats['removal_counts'].items():
        percentage = (count / stats['total_rows']) * 100
        print(f"  {threshold}: {count:,} 行 ({percentage:.2f}%)")

def print_sampling_stats(stats: Dict) -> None:
    """
    Print sampling statistics in a readable format
    
    Args:
        stats: Dictionary with sampling statistics
    """
    print("\n===== 抽样统计 =====")
    print(f"原始数据集大小: {stats['original_size']:,}")
    print(f"目标抽样大小: {stats['target_size']:,}")
    print(f"实际抽样大小: {stats['actual_size']:,}")
    
    print("\n各长度区间抽样情况:")
    for range_name, range_stats in stats['ranges'].items():
        available = range_stats['available']
        requested = range_stats['requested']
        sampled = range_stats['sampled']
        
        print(f"  {range_name} 字符区间:")
        print(f"    可用数据: {available:,} 行")
        print(f"    计划抽样: {requested:,} 行")
        print(f"    实际抽样: {sampled:,} 行")
        if available > 0:
            print(f"    抽样比例: {sampled/available*100:.2f}%")

def main():
    parser = argparse.ArgumentParser(description='Clean source data in Parquet files')
    parser.add_argument('input', help='Input Parquet file path')
    parser.add_argument('output', nargs='?', help='Output cleaned Parquet file path')
    parser.add_argument('-l', '--min-length', type=int, default=10, 
                       help='Minimum character length for source text (default: 10)')
    parser.add_argument('-d', '--dry-run', action='store_true',
                       help='Only analyze the data without performing cleaning or saving')
    parser.add_argument('-s', '--sample', action='store_true',
                       help='Sample data from specific length ranges')
    parser.add_argument('--sample-size', type=int, default=20000,
                       help='Target size for sampled dataset (default: 20000)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # In dry-run mode, output path is optional
    if not args.dry_run and not args.sample and not args.output:
        logger.error("Output path is required when not in dry-run mode")
        sys.exit(1)
    
    try:
        # Verify input file exists
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            sys.exit(1)
        
        # Read Parquet file
        logger.info(f"Reading Parquet file: {args.input}")
        df = pd.read_parquet(args.input)
        
        # Ensure 'source' column exists
        if 'source' not in df.columns:
            logger.error("Input file does not contain a 'source' column")
            sys.exit(1)
        
        # Dry-run mode: only analyze length distribution
        if args.dry_run:
            logger.info("Running in dry-run mode, analyzing data distribution...")
            
            # Analyze length distribution
            length_stats = analyze_length_distribution(df)
            
            # Display distribution results
            print_length_distribution(length_stats)
            
            # Show example cleaning with current threshold
            sample_size = min(10, len(df))
            logger.info(f"\nExample cleaning (sample of {sample_size} rows with current min_length={args.min_length}):")
            
            sample_df = df.sample(sample_size).copy()
            cleaned_sample, _ = clean_source(sample_df, args.min_length)
            
            removed_indices = set(sample_df.index) - set(cleaned_sample.index)
            
            for idx, row in sample_df.iterrows():
                source = row['source']
                status = "会被删除" if idx in removed_indices else "会被保留"
                
                # Clean leading dash if needed
                if isinstance(source, str) and source.startswith('- '):
                    cleaned = source[2:]
                    print(f"原文 ({len(source)}字符): '{source}'")
                    print(f"清理后 ({len(cleaned)}字符): '{cleaned}'")
                    print(f"状态: {status}\n")
                else:
                    print(f"原文 ({len(source) if isinstance(source, str) else 0}字符): '{source}'")
                    print(f"状态: {status}\n")
            
            logger.info("Dry run completed. No files were modified.")
        
        # Sample mode: sample from length ranges
        elif args.sample:
            logger.info(f"Running in sampling mode, targeting {args.sample_size} records...")
            
            # First clean the data
            logger.info(f"First cleaning data (minimum length: {args.min_length} characters)...")
            df_cleaned, clean_stats = clean_source(df, args.min_length)
            
            # Then sample the data
            logger.info(f"Sampling from cleaned data...")
            df_sampled, sample_stats = sample_data(df_cleaned, args.sample_size)
            
            # Print statistics
            print_sampling_stats(sample_stats)
            
            # If output path is provided, save the sampled data
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                logger.info(f"Saving sampled data to: {args.output}")
                df_sampled.to_parquet(str(output_path), index=False)
                logger.info(f"Saved {len(df_sampled):,} records to {args.output}")
            else:
                logger.info("No output path provided. Sampled data not saved.")
        
        # Normal mode: clean and save data
        else:
            # Clean the data
            logger.info(f"Cleaning source data (minimum length: {args.min_length} characters)...")
            total_rows = len(df)
            update_progress(0, total_rows)
            
            df_cleaned, stats = clean_source(df, args.min_length)
            
            update_progress(total_rows, total_rows)
            print()  # New line after progress
            
            # Create output directory if it doesn't exist
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save cleaned data
            logger.info(f"Saving cleaned data to: {args.output}")
            df_cleaned.to_parquet(str(output_path), index=False)
            
            # Print statistics
            logger.info("Cleaning completed. Statistics:")
            logger.info(f"Total rows processed: {stats['total_rows']:,}")
            logger.info(f"Rows with just '-' removed: {stats['removed_dash']:,}")
            logger.info(f"Short phrases removed (< {args.min_length} chars): {stats['removed_short']:,}")
            logger.info(f"Leading dash cleaned: {stats['cleaned_leading_dash']:,}")
            logger.info(f"Remaining rows: {stats['remaining_rows']:,}")
            logger.info(f"Reduction: {stats['total_rows'] - stats['remaining_rows']:,} rows ({(stats['total_rows'] - stats['remaining_rows']) / stats['total_rows'] * 100:.2f}%)")
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 