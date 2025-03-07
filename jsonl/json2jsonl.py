#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON to JSONL Converter

This script converts a JSON array file to JSONL (JSON Lines) format,
where each line contains one complete JSON object.
"""

import json
import argparse
import os
from pathlib import Path
import sys
from collections import OrderedDict


def validate_json_object(obj):
    """
    Validate that the JSON object has the expected fields.
    
    Args:
        obj (dict): JSON object to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = {'question', 'content', 'reasoning_content'}
    
    # Check if all required fields are present
    missing_fields = required_fields - set(obj.keys())
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Check if there are any unexpected fields
    unexpected_fields = set(obj.keys()) - required_fields
    if unexpected_fields:
        return False, f"Unexpected fields: {', '.join(unexpected_fields)}"
    
    return True, ""


def convert_json_to_jsonl(input_file, output_file, verbose=False, validate=True):
    """
    Convert JSON array file to JSONL format.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output JSONL file
        verbose (bool): Whether to print verbose output
        validate (bool): Whether to validate each JSON object
    
    Returns:
        int: Number of records processed
    """
    try:
        if verbose:
            print(f"Reading JSON from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Input JSON must be an array")
        
        total_records = len(data)
        if verbose:
            print(f"Found {total_records} records to process")
        
        # Validate input data format if required
        if validate:
            if verbose:
                print("Validating JSON objects...")
            
            for i, item in enumerate(data):
                is_valid, error_msg = validate_json_object(item)
                if not is_valid:
                    raise ValueError(f"Record {i+1} invalid: {error_msg}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, item in enumerate(data):
                # Use OrderedDict to ensure fields are always in the same order
                ordered_obj = OrderedDict([
                    ("question", item["question"]),
                    ("content", item["content"]),
                    ("reasoning_content", item["reasoning_content"])
                ])
                
                # Convert to JSON string without pretty-printing and without spaces
                json_str = json.dumps(ordered_obj, ensure_ascii=False, separators=(',', ':'))
                
                # Write a line with just the JSON object
                f.write(json_str + '\n')
                
                # Print progress if verbose
                if verbose and (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1}/{total_records} records ({(i + 1) / total_records:.1%})")
        
        if verbose:
            print(f"Conversion complete. Wrote {total_records} lines to {output_file}")
        
        return total_records
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {input_file}. {str(e)}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 0


def main():
    parser = argparse.ArgumentParser(description="Convert JSON array to JSONL format")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("output", help="Output JSONL file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation of JSON objects")
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        return 1
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Perform conversion
    records_processed = convert_json_to_jsonl(args.input, args.output, args.verbose, not args.no_validate)
    
    return 0 if records_processed > 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 