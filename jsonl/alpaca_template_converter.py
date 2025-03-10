#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Alpaca/QA JSON to Translation Template JSONL Converter

This script converts Alpaca format JSONL or JSON files to a specific JSONL template format
used for translation assistant training.

The script supports both:
- Standard JSON array format: A file containing a single JSON array of objects
- JSONL format: A file with one JSON object per line

The output format includes instruction, input, output, system, and history fields,
with the assistant message containing reasoning content in <think></think> tags.

The script also supports splitting data into training and validation sets.
"""

import json
import argparse
import os
import sys
import random
from collections import OrderedDict


def convert_to_translation_template_jsonl(input_file, output_file, verbose=False, include_reasoning=True,
                                     validation_split=0.0, validation_output_file=None, random_seed=None,
                                     system_prompt=None):
    """
    Convert Alpaca format JSON/JSONL files to a translation template JSONL format.
    
    Args:
        input_file (str): Path to input Alpaca JSON/JSONL file
        output_file (str): Path to output template JSONL file
        verbose (bool): Whether to print verbose output
        include_reasoning (bool): Whether to include reasoning content in assistant's message
        validation_split (float): Fraction of data to use as validation (0.0 to 1.0)
        validation_output_file (str): Path to validation output JSONL file (required if validation_split > 0)
        random_seed (int): Random seed for reproducible validation splits
        system_prompt (str): Custom system prompt to use (if None, default is used)
    
    Returns:
        tuple: (Number of training records processed, Number of validation records processed)
    """
    try:
        if verbose:
            print(f"Reading from {input_file}...")
        
        # Try to read the input file as a standard JSON array first
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if verbose:
                    print(f"Successfully loaded standard JSON array format")
        except json.JSONDecodeError:
            # If that fails, try to read as JSONL (one JSON object per line)
            data = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse line as JSON: {e}")
                        continue
            if verbose:
                print(f"Successfully loaded JSONL format")
        
        # If data is still empty after attempting both formats, raise an error
        if not data:
            raise ValueError(f"No valid data found in {input_file}")
        
        total_records = len(data)
        if verbose:
            print(f"Found {total_records} records to process")
        
        # Validate validation split parameters
        if validation_split > 0:
            if validation_split >= 1.0:
                raise ValueError("validation_split must be less than 1.0")
            if validation_output_file is None:
                raise ValueError("validation_output_file is required when validation_split > 0")
        
        # Set default system prompt if not provided
        if not system_prompt:
            system_prompt = "你是一个翻译助手，你不会回答输入的问题，只会将输入的英文翻译成中文。\n\n翻译要求：\n- 直接给出答案：必须只有翻译后的内容。\n- 准确性：必须准确传达原文的意思，不遗漏或歪曲信息。\n- 流畅性：在中文中应读起来自然，像本地人写的文本一样。\n- 文化适应性：应考虑中国人的文化背景，使用合适的表达和格式。\n- 主题专业性：判断原文的相关领域，根据相关领域有专业知识，确保术语使用正确。"
            
        # Split data into training and validation sets if needed
        train_data = data
        val_data = []
        
        if validation_split > 0:
            # Set random seed for reproducibility if provided
            if random_seed is not None:
                random.seed(random_seed)
            
            # Shuffle the data for random sampling
            indices = list(range(total_records))
            random.shuffle(indices)
            
            # Calculate the number of validation samples
            val_size = int(total_records * validation_split)
            train_size = total_records - val_size
            
            # Split the indices
            val_indices = set(indices[:val_size])
            
            # Split the data
            train_data = []
            val_data = []
            
            for i, item in enumerate(data):
                if i in val_indices:
                    val_data.append(item)
                else:
                    train_data.append(item)
                    
            if verbose:
                print(f"Split data into {train_size} training samples and {val_size} validation samples")
        
        # Process training data
        train_count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, item in enumerate(train_data):
                # Extract question/content or instruction/output based on format
                if "question" in item and "content" in item:
                    question = item["question"]
                    content = item["content"]
                    reasoning_content = item.get("reasoning_content", "")
                elif "instruction" in item and "output" in item:
                    question = item.get("input", "") if item.get("input") else item["instruction"]
                    content = item["output"]
                    reasoning_content = ""
                else:
                    print(f"Warning: Training record {i+1} has an unsupported format. Skipping.")
                    continue
                
                # Create template record
                record = {
                    "instruction": "将「${question}」翻译成中文".replace("${question}", question),
                    "input": "",
                    "output": content,
                    "system": system_prompt,
                    "history": []
                }
                
                # Add reasoning content if available and requested
                if include_reasoning and reasoning_content:
                    record["output"] = f"<think>{reasoning_content}</think>{content}"
                
                # Convert to JSON string without pretty-printing
                json_str = json.dumps(record, ensure_ascii=False, separators=(',', ':'))
                
                # Write a line with just the JSON object
                f.write(json_str + '\n')
                train_count += 1
                
                # Print progress if verbose
                if verbose and (train_count % 100 == 0):
                    print(f"Processed {train_count}/{len(train_data)} training records ({train_count / len(train_data):.1%})")
        
        # Process validation data if needed
        val_count = 0
        if validation_split > 0:
            with open(validation_output_file, 'w', encoding='utf-8') as f:
                for i, item in enumerate(val_data):
                    # Extract question/content or instruction/output based on format
                    if "question" in item and "content" in item:
                        question = item["question"]
                        content = item["content"]
                        reasoning_content = item.get("reasoning_content", "")
                    elif "instruction" in item and "output" in item:
                        question = item.get("input", "") if item.get("input") else item["instruction"]
                        content = item["output"]
                        reasoning_content = ""
                    else:
                        print(f"Warning: Validation record {i+1} has an unsupported format. Skipping.")
                        continue
                    
                    # Create template record
                    record = {
                        "instruction": "将「${question}」翻译成中文".replace("${question}", question),
                        "input": "",
                        "output": content,
                        "system": system_prompt,
                        "history": []
                    }
                    
                    # Add reasoning content if available and requested
                    if include_reasoning and reasoning_content:
                        record["output"] = f"<think>{reasoning_content}</think>{content}"
                    
                    # Convert to JSON string without pretty-printing
                    json_str = json.dumps(record, ensure_ascii=False, separators=(',', ':'))
                    
                    # Write a line with just the JSON object
                    f.write(json_str + '\n')
                    val_count += 1
                    
                    # Print progress if verbose
                    if verbose and (val_count % 100 == 0):
                        print(f"Processed {val_count}/{len(val_data)} validation records ({val_count / len(val_data):.1%})")
        
        if verbose:
            if validation_split > 0:
                print(f"Conversion complete. Wrote {train_count} training lines to {output_file}")
                print(f"Wrote {val_count} validation lines to {validation_output_file}")
            else:
                print(f"Conversion complete. Wrote {train_count} lines to {output_file}")
        
        return (train_count, val_count)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return (0, 0)


def main():
    parser = argparse.ArgumentParser(description="Convert Alpaca/QA JSON/JSONL format to translation template JSONL format")
    parser.add_argument("input", help="Input Alpaca/QA JSON/JSONL file path")
    parser.add_argument("output", help="Output template JSONL file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-reasoning", action="store_true", help="Exclude reasoning content from assistant's message")
    parser.add_argument("--validation-split", type=float, default=0.0, help="Fraction of data to use as validation (0.0 to 1.0)")
    parser.add_argument("--validation-output", help="Output JSONL file path for validation data")
    parser.add_argument("--random-seed", type=int, help="Random seed for reproducible validation splits")
    parser.add_argument("--system-prompt", help="Custom system prompt to use")
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        return 1
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ensure validation output directory exists if validation split is used
    if args.validation_split > 0:
        if args.validation_output is None:
            print("Error: --validation-output is required when --validation-split > 0", file=sys.stderr)
            return 1
        
        val_output_dir = os.path.dirname(args.validation_output)
        if val_output_dir and not os.path.exists(val_output_dir):
            os.makedirs(val_output_dir)
    
    # Perform conversion
    records_processed = convert_to_translation_template_jsonl(
        args.input, 
        args.output, 
        args.verbose,
        not args.no_reasoning,  # inverse of no-reasoning flag
        args.validation_split,
        args.validation_output,
        args.random_seed,
        args.system_prompt
    )
    
    return 0 if records_processed[0] > 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 