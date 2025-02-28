# JSONL to Parquet Converter

A high-performance command-line tool to convert JSONL (JSON Lines) files to Parquet format, optimized for machine learning workflows.

## Features

- Fast and memory-efficient conversion
- Automatic schema inference
- Progress tracking with verbose mode
- Support for large files through streaming
- Built-in Parquet viewer utility

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd jsonl2parquet
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python -c "import pandas as pd; import pyarrow; print('Installation successful!')"
```

## Usage

### Options

- `-v, --verbose`: Enable verbose logging for progress tracking
- `-n, --rows N`: Number of rows to display in viewer (default: 10)
- `--help`: Display help information

### Examples

Basic conversion:
```bash
python convert.py input.jsonl output.parquet
```

View Parquet file contents:
```bash
# View first 10 rows (default)
python view_parquet.py data.parquet

# View specific number of rows
python view_parquet.py data.parquet -n 5
```

## Input Format

JSONL files should contain one valid JSON object per line:

```jsonl
{"source": "Hello world", "target": "你好世界"}
{"source": "How are you?", "target": "你好吗？"}
```

## Output Format

The tool converts JSONL to Parquet format, which offers:
- Efficient columnar storage
- Schema enforcement
- Built-in compression
- Fast data retrieval

Sample Parquet file structure:
- Total row count
- Schema information
- Column data types
- Compressed data blocks

## Development

```bash
# Run tests
python -m pytest tests/

# Build distribution
python setup.py sdist bdist_wheel

# Install in development mode
pip install -e .
```

Best Practices for Development:
- Use SSD storage for better I/O performance
- Close other memory-intensive applications
- Consider using pypy for better performance
- Validate JSONL format before conversion
- Ensure consistent schema across records
- Back up data before conversion

Troubleshooting Development Issues:
1. ModuleNotFoundError:
   - Ensure virtual environment is activated
   - Check for `(venv)` in terminal prompt

2. Memory Errors:
   - Increase system swap space
   - Process file in smaller chunks

Requirements:
- Python 3.6+
- pandas >= 2.0.0
- pyarrow >= 14.0.1

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.