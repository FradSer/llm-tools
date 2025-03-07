# Parquet Tools Suite

A collection of high-performance command-line tools for working with Parquet files, including conversion, viewing, and cleaning utilities.

## Features

- Fast and memory-efficient operations
- Progress tracking with detailed status updates
- Support for different column mappings
- UTF-8 encoding support for multilingual data
- Multiple utilities for different Parquet operations

## Tools Included

1. **parquet2json.py**: Convert Parquet files to JSON format
2. **jsonl2parquet.py**: Convert JSONL files to Parquet format
3. **view_parquet.py**: Quick viewer for Parquet file contents
4. **clean_parquet.py**: Clean and process Parquet files

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd parquet-tools
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

5. Verify installation:
```bash
python -c "import pandas as pd; import pyarrow; print('Installation successful!')"
```

## Usage

### 1. View Parquet File (view_parquet.py)

Quick inspection of Parquet file contents:

```bash
python view_parquet.py input.parquet [-n ROWS]
```

Options:
- `-n, --rows`: Number of rows to display (default: 10)

### 2. Parquet to JSON Conversion (parquet2json.py)

Convert Parquet files to JSON format:

```bash
python parquet2json.py input.parquet output.json [-v] [--question-column COLUMN]
```

Options:
- `-v, --verbose`: Enable verbose logging
- `--question-column`: Specify source column (default: "source")

### 3. JSONL to Parquet Conversion (jsonl2parquet.py)

Convert JSONL files to Parquet format:

```bash
python jsonl2parquet.py input.jsonl output.parquet
```

### 4. Clean Parquet Files (clean_parquet.py)

Process and clean Parquet files:

```bash
python clean_parquet.py input.parquet output.parquet
```

## Input/Output Formats

### Parquet to JSON
Input: Parquet file with specified column structure
Output:
```json
[
  {
    "question": "What is the capital of France?",
    "is_answered": true
  }
]
```

### JSONL to Parquet
Input: JSONL file with consistent schema
Output: Optimized Parquet file

## Development

Best Practices:
- Use SSD storage for better I/O performance
- Close other memory-intensive applications when processing large files
- Ensure consistent schema in input files

Requirements:
- Python 3.6+
- pandas >= 2.0.0
- pandas-stubs >= 2.0.0
- pyarrow >= 14.0.1

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.