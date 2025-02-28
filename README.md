# LLM Tools Collection ![](https://img.shields.io/badge/A%20FRAD%20PRODUCT-WIP-yellow)

[![Twitter Follow](https://img.shields.io/twitter/follow/FradSer?style=social)](https://twitter.com/FradSer)

English | [简体中文](README.zh-CN.md)

A comprehensive collection of tools designed to streamline the development, processing, and management of Large Language Model (LLM) applications. These tools are built with modern technologies and best practices, focusing on performance, reliability, and ease of use.

## Tools

### 1. tmx2jsonl

A high-performance tool for converting TMX (Translation Memory eXchange) files to JSONL format, optimized for LLM training data preparation.

- **Technology**: Bun + TypeScript
- **Status**: Available ✅
- **Features**:
  - Fast processing of large TMX files
  - Memory-efficient streaming
  - Robust error handling
- [Learn more about tmx2jsonl](./tmx2jsonl/README.md)

### 2. jsonl2parquet

A command-line tool for efficient conversion of JSONL files to Parquet format, optimized for machine learning workflows.

- **Technology**: Python
- **Status**: Available ✅
- **Features**:
  - High compression ratio
  - Fast conversion speed
  - Memory-efficient processing
- [Learn more about jsonl2parquet](./jsonl2parquet/README.md)

## Project Structure

```
llm-tools/
├── tmx2jsonl/        # TMX to JSONL converter
├── jsonl2parquet/    # JSONL to Parquet converter
└── ... (more tools coming soon)
```

## Technology Stack

This project leverages modern technologies for optimal performance:

- **JavaScript/TypeScript Tools**:
  - Bun runtime for maximum performance
  - TypeScript for type safety and better developer experience
  - Modern ES modules and async/await patterns
  
- **Python Tools**:
  - Python 3.8+ for compatibility with latest ML libraries
  - pandas & pyarrow for efficient data processing
  - Type hints for better code quality

## Getting Started

Each tool has its own setup and usage instructions. Please refer to the individual tool's README for specific details:

- [tmx2jsonl Setup Guide](./tmx2jsonl/README.md)
- [jsonl2parquet Setup Guide](./jsonl2parquet/README.md)

## Contributing

Contributions are warmly welcomed! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact & Support

- Create an issue for bug reports or feature requests
- Follow [@FradSer](https://twitter.com/FradSer) on Twitter for updates
- Star this repo if you find it helpful! 