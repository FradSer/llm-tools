# TMX to JSONL Converter

A command-line tool to convert TMX (Translation Memory eXchange) files to JSONL (JSON Lines) format.

## Features

- Streaming processing for large files
- Support for custom source and target languages
- Optional record limit
- Progress reporting for large files
- Error handling and reporting

## Installation

```bash
# Install dependencies
bun install
```

## Usage

```bash
bun run src/index.ts <input-file> <output-file> [options]
```

### Options

- `--limit N`: Only process N records
- `--source-lang LANG`: Source language code (default: en)
- `--target-lang LANG`: Target language code (default: zh_cn)

### Examples

```bash
# Basic usage
bun run src/index.ts input.tmx output.jsonl

# Convert only first 1000 records
bun run src/index.ts input.tmx output.jsonl --limit 1000

# Specify custom languages
bun run src/index.ts input.tmx output.jsonl --source-lang en --target-lang fr

# Build for production
bun run build
```

## Input Format

The tool accepts TMX (Translation Memory eXchange) files as input. The TMX file should follow the standard TMX 1.4b format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx11.dtd">
<tmx version="1.4">
  <header
    creationtool="XYZ Tool" 
    creationtoolversion="1.0"
    segtype="sentence"
    o-tmf="tmx"
    adminlang="en-us"
    srclang="en"
    datatype="plaintext">
  </header>
  <body>
    <tu>
      <tuv xml:lang="en">
        <seg>Source text in English</seg>
      </tuv>
      <tuv xml:lang="zh_cn">
        <seg>目标文本翻译</seg>
      </tuv>
    </tu>
    <!-- More translation units -->
  </body>
</tmx>
```

Each translation unit (`tu`) must contain:
- A source language segment (`tuv` with matching source language code)
- A target language segment (`tuv` with matching target language code)

## Output Format

The tool converts TMX records to JSONL format. Each line in the output file is a JSON object with the following structure:

```json
{"source": "English text", "target": "Translated text"}
```

## Development

```bash
# Run in development mode with watch
bun run dev

# Build for production
bun run build
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
