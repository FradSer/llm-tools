# JSONL to Parquet Converter

A simple command-line tool to convert JSONL (JSON Lines) files to Parquet format.

## Installation

1. Clone this repository

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Verify the installation:
```bash
python -c "import pandas as pd; import pyarrow; print('Installation successful!')"
```

## Usage

Basic usage:
```bash
python convert.py input.jsonl output.parquet
```

Enable verbose logging:
```bash
python convert.py input.jsonl output.parquet -v
```

### View Parquet Contents

To check the contents of a Parquet file, use the provided `view_parquet.py` script:

```bash
# View first 10 rows (default)
python view_parquet.py path/to/file.parquet

# View specific number of rows
python view_parquet.py path/to/file.parquet -n 5

# Show help
python view_parquet.py --help
```

The script will display:
- Total number of rows
- First N rows of data (default: 10)
- Column data types

### Arguments

- `input`: Path to the input JSONL file
- `output`: Path where the output Parquet file will be saved
- `-v, --verbose`: Enable verbose logging (optional)

### Example

First, create a sample JSONL file:
```bash
echo '{"source": "Hello", "target": "你好"}' > test.jsonl
echo '{"source": "World", "target": "世界"}' >> test.jsonl
```

Then convert it to Parquet:
```bash
python convert.py test.jsonl output.parquet
```

## Input Format

The input JSONL file should contain one JSON object per line. For example:

```json
{"source": "English text", "target": "Translated text"}
{"source": "Another English text", "target": "Another translated text"}
```

## Requirements

- Python 3.6+
- pandas >= 2.0.0
- pyarrow >= 14.0.1

## Troubleshooting

### Virtual Environment Issues

1. If you see "command not found: python3", try:
```bash
# On macOS (using Homebrew)
brew install python3

# On Ubuntu/Debian
sudo apt-get install python3
```

2. If you can't activate the virtual environment, make sure you're in the correct directory:
```bash
# Check current directory
pwd

# Should be in the project directory
cd path/to/jsonl2parquet
```

### Installation Issues

If you see an error like "Could not find a version that satisfies the requirement requirements.txt", make sure to use the `-r` flag with pip:

```bash
# Wrong
pip install requirements.txt

# Correct
pip install -r requirements.txt
```

### Common Problems

1. **ModuleNotFoundError**: Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)
2. **Permission Error**: Try running with `sudo` or check file permissions
3. **Memory Error**: For large files, try increasing your system's swap space 