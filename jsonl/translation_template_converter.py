#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON to Template JSONL Converter with Reasoning

This script converts a JSON array file to a specific JSONL template format used for
translation assistant data with system, user, and assistant messages.

By default, the assistant message will include reasoning content in <think></think> tags,
but this behavior can be controlled with the --no-reasoning flag or the include_reasoning parameter.

The script also supports splitting data into training and validation sets with the validation_split parameter.
"""

import json
import argparse
import os
import sys
import random
from collections import OrderedDict


def convert_json_to_template_jsonl_with_reasoning(input_file, output_file, verbose=False, include_reasoning=True, validation_split=0.0, validation_output_file=None, random_seed=None):
    """
    Convert JSON array file to JSONL format with a specific template structure
    that includes reasoning content in <think></think> tags.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output JSONL file
        verbose (bool): Whether to print verbose output
        include_reasoning (bool): Whether to include reasoning content in assistant's message
        validation_split (float): Fraction of data to use as validation (0.0 to 1.0)
        validation_output_file (str): Path to validation output JSONL file (required if validation_split > 0)
        random_seed (int): Random seed for reproducible validation splits
    
    Returns:
        tuple: (Number of training records processed, Number of validation records processed)
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
        
        # Validate validation split parameters
        if validation_split > 0:
            if validation_split >= 1.0:
                raise ValueError("validation_split must be less than 1.0")
            if validation_output_file is None:
                raise ValueError("validation_output_file is required when validation_split > 0")
        
        # The template structure for each record
        template = {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个翻译助手，你不会回答输入的问题，只会将输入的英文翻译成中文。\n\n翻译要求：\n- 直接给出答案：必须只有翻译后的内容。\n- 准确性：必须准确传达原文的意思，不遗漏或歪曲信息。\n- 流畅性：在中文中应读起来自然，像本地人写的文本一样。\n- 文化适应性：应考虑中国人的文化背景，使用合适的表达和格式。\n- 主题专业性：判断原文的相关领域，根据相关领域有专业知识，确保术语使用正确。"
                },
                {
                    "role": "user",
                    "content": "将「${question}」翻译成中文"
                },
                {
                    "role": "assistant",
                    "content": "",
                }
            ]
        }
        
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
                if "question" not in item or "content" not in item:
                    print(f"Warning: Training record {i+1} missing required 'question' or 'content' field. Skipping.")
                    continue
                
                if "reasoning_content" not in item:
                    print(f"Warning: Training record {i+1} missing 'reasoning_content' field. Using empty reasoning.")
                    reasoning_content = ""
                else:
                    reasoning_content = item["reasoning_content"]
                
                # Create a deep copy of the template for each record
                record = json.loads(json.dumps(template))
                
                # Replace the question placeholder
                record["messages"][1]["content"] = record["messages"][1]["content"].replace("${question}", item["question"])
                
                # Set the assistant content based on include_reasoning parameter
                if include_reasoning:
                    record["messages"][2]["content"] = f"<think>{reasoning_content}</think>{item['content']}"
                else:
                    record["messages"][2]["content"] = item['content']
                
                # Convert to JSON string without pretty-printing and without spaces
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
                    if "question" not in item or "content" not in item:
                        print(f"Warning: Validation record {i+1} missing required 'question' or 'content' field. Skipping.")
                        continue
                    
                    if "reasoning_content" not in item:
                        print(f"Warning: Validation record {i+1} missing 'reasoning_content' field. Using empty reasoning.")
                        reasoning_content = ""
                    else:
                        reasoning_content = item["reasoning_content"]
                    
                    # Create a deep copy of the template for each record
                    record = json.loads(json.dumps(template))
                    
                    # Replace the question placeholder
                    record["messages"][1]["content"] = record["messages"][1]["content"].replace("${question}", item["question"])
                    
                    # Set the assistant content based on include_reasoning parameter
                    if include_reasoning:
                        record["messages"][2]["content"] = f"<think>{reasoning_content}</think>{item['content']}"
                    else:
                        record["messages"][2]["content"] = item['content']
                    
                    # Convert to JSON string without pretty-printing and without spaces
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
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {input_file}. {str(e)}", file=sys.stderr)
        return (0, 0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return (0, 0)


def main():
    parser = argparse.ArgumentParser(description="Convert JSON array to template-based JSONL format with reasoning")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("output", help="Output JSONL file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-reasoning", action="store_true", help="Exclude reasoning content from assistant's message")
    parser.add_argument("--validation-split", type=float, default=0.0, help="Fraction of data to use as validation (0.0 to 1.0)")
    parser.add_argument("--validation-output", help="Output JSONL file path for validation data")
    parser.add_argument("--random-seed", type=int, help="Random seed for reproducible validation splits")
    
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
    records_processed = convert_json_to_template_jsonl_with_reasoning(
        args.input, 
        args.output, 
        args.verbose,
        not args.no_reasoning,  # inverse of no-reasoning flag
        args.validation_split,
        args.validation_output,
        args.random_seed
    )
    
    return 0 if records_processed[0] > 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 