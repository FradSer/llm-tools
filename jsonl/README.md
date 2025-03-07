# JSON and JSONL Conversion Tools

A set of command-line tools for converting JSON arrays to JSONL (JSON Lines) format, with support for both standard and template-based conversion for machine translation training data.

## Features

- High-performance JSON format conversion
- Two conversion modes:
  - Standard mode: Converts JSON arrays to JSONL with field validation
  - Template mode: Converts to chat-template format for translation training
- UTF-8 encoding support for multilingual data
- Detailed progress tracking and status updates
- Memory-efficient processing
- Strict field ordering for data format consistency
- Compact output format with no extra spaces

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd llm-tools
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv
```

3. Activate the virtual environment:

```bash
# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Standard JSON to JSONL Conversion (`json2jsonl.py`)

Converts JSON arrays to JSONL format with field validation and fixed field ordering.

#### Command-line Arguments

- `input`: Input JSON file path
- `output`: Output JSONL file path
- `-v, --verbose`: Enable detailed logging for progress tracking
- `--no-validate`: Skip JSON object field validation

#### Examples

Basic conversion:
```bash
python json2jsonl.py input.json output.jsonl
```

Using verbose mode with validation:
```bash
python json2jsonl.py input.json output.jsonl -v
```

Skip validation:
```bash
python json2jsonl.py input.json output.jsonl --no-validate
```

### Template-based Conversion for Translation Training (`json2jsonl4volcengine.py`)

Converts JSON arrays to a specialized JSONL format with chat templates for translation training.

#### Command-line Arguments

- `input`: Input JSON file path
- `output`: Output JSONL file path
- `-v, --verbose`: Enable detailed logging for progress tracking

#### Examples

```bash
python json2jsonl4volcengine.py input.json output.jsonl -v
```

#### Template Format

This tool converts each JSON record to a structured chat template format with a fixed system prompt for translation:

```json
{
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
      "content": "translation_content",
      "loss_weight": 1.0
    }
  ]
}
```

### Parquet to JSON Conversion

Please refer to the [Parquet Conversion Tool Documentation](parquet/README.md) for more information.

## Input Format

### Standard JSON to JSONL (`json2jsonl.py`)

The script expects a JSON array file where each object must contain exactly these fields:
- `question`: Question text (English)
- `content`: Content text (Chinese translation)
- `reasoning_content`: Translation reasoning process

For example:

```json
[
  {
    "question": "And I can't imagine how your father must feel.",
    "content": "真不敢想你父亲现在是什么心情。",
    "reasoning_content": "..."
  }
]
```

### Template-based Conversion (`json2jsonl4volcengine.py`)

The script expects a JSON array file where each object must contain at least:
- `question`: Original English text
- `content`: Chinese translation

Additional fields will be ignored.

## Output Format

### Standard JSON to JSONL (`json2jsonl.py`)

Each line in the output file is a complete JSON object with:
1. Fields strictly ordered as `question`, `content`, `reasoning_content`
2. No extra spaces or formatting
3. UTF-8 encoding for multilingual character support

Example:
```
{"question":"And I can't imagine how your father must feel.","content":"真不敢想你父亲现在是什么心情。","reasoning_content":"..."}
```

### Template-based Output (`json2jsonl4volcengine.py`)

Each line contains a complete chat template with system prompt, user query, and assistant response:

```
{"messages":[{"role":"system","content":"你是一个翻译助手..."},{"role":"user","content":"将「And I can't imagine how your father must feel.」翻译成中文"},{"role":"assistant","content":"真不敢想你父亲现在是什么心情。","loss_weight":1.0}]}
```

## Data Format Validation

### Standard JSON to JSONL (`json2jsonl.py`)
- Validates presence of all required fields
- Checks for unexpected fields
- Terminates with error if validation fails

### Template-based Conversion (`json2jsonl4volcengine.py`)
- Checks for required fields (`question` and `content`)
- Skips records with missing fields
- Continues processing remaining records

## Troubleshooting

If you receive an error message like "Error at line X, field 'questionreasoning_contentcontent'", it indicates that fields in the JSONL file have been incorrectly merged. Please use the latest version of the conversion tool to ensure clear field separation.

## Development

```bash
# Run tests (if available)
python -m pytest tests/

# Install in development mode
pip install -e .
```

Best practices:
- Use SSD storage for better I/O performance when processing large files
- Close other memory-intensive applications when processing large files
- Ensure consistent input file formatting

Troubleshooting guide:
1. ModuleNotFoundError:
   - Ensure the virtual environment is activated
   - Check for `(venv)` in the terminal prompt

2. Memory errors:
   - For very large files, consider processing in chunks
   - Increase system swap space if necessary

Requirements:
- Python 3.6+
- json (standard library)
- collections (standard library)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 