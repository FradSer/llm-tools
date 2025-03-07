#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON to Template JSONL Converter

This script converts a JSON array file to a specific JSONL template format used for
translation assistant data with system, user, and assistant messages.
"""

import json
import argparse
import os
import sys
from collections import OrderedDict


def convert_json_to_template_jsonl(input_file, output_file, verbose=False):
    """
    Convert JSON array file to JSONL format with a specific template structure.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output JSONL file
        verbose (bool): Whether to print verbose output
    
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
        
        # The template structure for each record
        template = {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个翻译助手，你不会回答输入的问题，只会将输入的英文翻译成中文。\n\n翻译要求：\n- 直接给出答案：必须只有翻译后的内容。\n- 准确性：必须准确传达原文的意思，不遗漏或歪曲信息。\n- 流畅性：在中文中应读起来自然，像本地人写的文本一样。\n- 文化适应性：应考虑中国人的文化背景，使用合适的表达和格式。\n- 主题专业性：判断原文的相关领域，根据相关领域有专业知识，确保术语使用正确。"
                },
                {
                    "role": "user",
                    "content": "${question}"
                },
                {
                    "role": "assistant",
                    "content": "",
                    "loss_weight": 1.0
                }
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, item in enumerate(data):
                if "question" not in item or "content" not in item:
                    print(f"Warning: Record {i+1} missing required 'question' or 'content' field. Skipping.")
                    continue
                
                # Create a deep copy of the template for each record
                record = json.loads(json.dumps(template))
                
                # Replace the question placeholder
                record["messages"][1]["content"] = record["messages"][1]["content"].replace("${question}", item["question"])
                
                # Set the assistant content to the translated content
                record["messages"][2]["content"] = item["content"]
                
                # Convert to JSON string without pretty-printing and without spaces
                json_str = json.dumps(record, ensure_ascii=False, separators=(',', ':'))
                
                # Write a line with just the JSON object
                f.write(json_str + '\n')
                
                # Print progress if verbose
                if verbose and (i + 1) % 100 == 0:
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
    parser = argparse.ArgumentParser(description="Convert JSON array to template-based JSONL format")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("output", help="Output JSONL file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
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
    records_processed = convert_json_to_template_jsonl(args.input, args.output, args.verbose)
    
    return 0 if records_processed > 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 