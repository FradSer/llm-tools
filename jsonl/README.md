# JSON and JSONL Conversion Tools

A set of command-line tools for converting JSON arrays to JSONL (JSON Lines) format, with support for both standard and template-based conversion for machine translation training data.

JSONL (JSON Lines) is a text-based format that stores structured data with each JSON object on a separate line. It's particularly well-suited for:

- Processing data streams one record at a time
- Log file management and analysis
- Machine learning training data preparation
- High-volume data processing with minimal memory requirements
- Integration with Unix-style text processing tools

These tools simplify the conversion process from JSON arrays to JSONL format, with specialized templates for machine translation tasks.

## Features

- High-performance JSON format conversion
- Multiple conversion modes:
  - Standard mode: Converts JSON arrays to JSONL with field validation
  - Template mode: Converts to chat-template format for translation training
  - Alpaca mode: Converts to Alpaca-style template for translation fine-tuning
  - Translation Template mode: Creates specialized templates with system prompts
- UTF-8 encoding support for multilingual data
- Detailed progress tracking and status updates
- Memory-efficient processing
- Strict field ordering for data format consistency
- Compact output format with no extra spaces
- Support for training/validation data splitting
- Optional inclusion of reasoning content

## JSONL Format Specification

JSONL (JSON Lines) is a text-based format for storing structured data with the following requirements:

1. **UTF-8 Encoding** - All files must use UTF-8 encoding.
2. **Each Line is a Valid JSON Value** - Every line in the file must contain a complete, valid JSON object.
3. **Line Separator is '\n'** - Lines are separated by newline characters. This also supports '\r\n' since surrounding whitespace is ignored when parsing JSON.

Additional conventions:

- File extension should be `.jsonl`
- Compressed JSONL files can use extensions like `.jsonl.gz` or `.jsonl.bz2`
- JSONL is ideal for:
  - Streaming data processing
  - Log files
  - Data that needs to be processed one record at a time
  - Working with Unix-style text processing tools and shell pipelines

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

### Alpaca Template Converter (`alpaca_template_converter.py`)

Converts JSON arrays to Alpaca-style JSONL format for translation fine-tuning.

#### Command-line Arguments

- `input`: Input JSON file path
- `output`: Output JSONL file path
- `-v, --verbose`: Enable detailed logging for progress tracking
- `--no-reasoning`: Exclude reasoning content from the output
- `--validation-split`: Fraction of data to use for validation (between 0.0 and 1.0)
- `--validation-output`: Output file for validation data
- `--random-seed`: Random seed for reproducible data splitting
- `--system-prompt`: Custom system prompt to use (optional)

#### Examples

Basic conversion:
```bash
python alpaca_template_converter.py input.json output.jsonl
```

With validation split:
```bash
python alpaca_template_converter.py input.json output.jsonl -v --validation-split 0.1 --validation-output validation.jsonl
```

#### Template Format

This tool converts each JSON record to an Alpaca-style format:

```json
{
  "instruction": "将「original_text」翻译成中文",
  "input": "",
  "output": "translated_content",
  "system": "system_prompt",
  "history": []
}
```

If reasoning content is included:
```json
{
  "instruction": "将「original_text」翻译成中文",
  "input": "",
  "output": "<think>reasoning_process</think>translated_content",
  "system": "system_prompt",
  "history": []
}
```

### Translation Template Converter (`translation_template_converter.py`)

Creates specialized templates with system prompts for translation training.

#### Command-line Arguments

- `input`: Input JSON file path
- `output`: Output JSONL file path
- `-v, --verbose`: Enable detailed logging for progress tracking
- `--no-reasoning`: Exclude reasoning content from the output
- `--validation-split`: Fraction of data to use for validation (between 0.0 and 1.0)
- `--validation-output`: Output file for validation data
- `--random-seed`: Random seed for reproducible data splitting

#### Examples

```bash
python translation_template_converter.py input.json output.jsonl
```

With validation split:
```bash
python translation_template_converter.py input.json output.jsonl --validation-split 0.2 --validation-output val.jsonl
```

#### Template Format

This tool creates a chat template format with a detailed system prompt:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个翻译助手，你不会回答输入的问题，只会将输入的英文翻译成中文。\n\n翻译要求：\n- 直接给出答案：必须只有翻译后的内容。\n- 准确性：必须准确传达原文的意思，不遗漏或歪曲信息。\n- 流畅性：在中文中应读起来自然，像本地人写的文本一样。\n- 文化适应性：应考虑中国人的文化背景，使用合适的表达和格式。\n- 主题专业性：判断原文的相关领域，根据相关领域有专业知识，确保术语使用正确。"
    },
    {
      "role": "user",
      "content": "将「original_text」翻译成中文"
    },
    {
      "role": "assistant",
      "content": "translated_content"
    }
  ]
}
```

### Parquet to JSON Conversion

Please refer to the [Parquet Conversion Tool Documentation](parquet/README.md) for more information.

## Input Format

### For All Converters

The scripts expect a JSON array file where each object contains either:

**Format 1: Question/Content**
- `question`: Original text (typically English)
- `content`: Translated text (typically Chinese)
- `reasoning_content`: Translation reasoning process (optional)

**Format 2: Instruction/Output**
- `instruction`: The instruction text
- `input`: Input text (can be empty)
- `output`: The output content

Example:

```json
[
  {
    "question": "And I can't imagine how your father must feel.",
    "content": "真不敢想你父亲现在是什么心情。",
    "reasoning_content": "..."
  }
]
```

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

### Alpaca Template Output (`alpaca_template_converter.py`)

Each line contains a complete Alpaca-style record:

```
{"instruction":"将「And I can't imagine how your father must feel.」翻译成中文","input":"","output":"真不敢想你父亲现在是什么心情。","system":"system_prompt_text","history":[]}
```

### Translation Template Output (`translation_template_converter.py`)

Each line contains a complete chat template:

```
{"messages":[{"role":"system","content":"你是一个翻译助手..."},{"role":"user","content":"将「And I can't imagine how your father must feel.」翻译成中文"},{"role":"assistant","content":"真不敢想你父亲现在是什么心情。"}]}
```

## Data Format Validation

Each converter validates the input data according to its specific requirements. Records with missing required fields will be skipped with warnings.

## Training/Validation Split

Both `alpaca_template_converter.py` and `translation_template_converter.py` support:
- Splitting data into training and validation sets
- Specifying validation split ratios
- Setting random seeds for reproducible results
- Outputting validation data to separate files

## Troubleshooting

If you receive an error message like "Error at line X, field 'questionreasoning_contentcontent'", it indicates that fields in the JSONL file have been incorrectly merged. Please use the latest version of the conversion tool to ensure clear field separation.

## Opening JSONL Files

JSONL files are plain text files that can be opened with any text editor, but specialized tools provide better functionality for large files:

### Windows
1. **Text Editors**: Visual Studio Code, Notepad++, or GitHub Atom
2. **Command Line**: Use PowerShell commands like `Get-Content` to view or process JSONL files
3. **Programming**: Python with libraries like `pandas` or `json` module

### macOS
1. **Text Editors**: Visual Studio Code, TextEdit, or GitHub Atom
2. **Command Line**: Use `cat`, `less`, or `head` commands to view JSONL files
3. **Programming**: Python with appropriate libraries

### Linux
1. **Text Editors**: Visual Studio Code, Vim, Emacs, or Nano
2. **Command Line**: Leverage Unix tools like `jq` for JSON processing, or `cat`, `head`, and `grep` for viewing and searching
3. **Shell Processing**: Process records with tools like `awk` or `sed`

For large files, consider using specialized JSON viewers or stream processing tools to avoid memory limitations.

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
- pandas>=1.3.0
- pyarrow>=7.0.0
- pytest>=7.0.0 (development)
- black>=22.3.0 (development)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 