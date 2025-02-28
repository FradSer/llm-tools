# LLM 工具集 ![](https://img.shields.io/badge/A%20FRAD%20PRODUCT-WIP-yellow)

[![Twitter Follow](https://img.shields.io/twitter/follow/FradSer?style=social)](https://twitter.com/FradSer)

[English](README.md) | 简体中文

这个代码仓库包含了我在探索大语言模型（LLMs）过程中开发的一系列工具。这些工具使用 JavaScript（Bun/Node.js）和 Python 实现，主要聚焦于 LLM 开发和数据处理的各个方面。

## 工具列表

### 1. tmx2jsonl

一个将 TMX（Translation Memory eXchange）文件转换为 JSONL 格式的工具，使翻译数据更易于在 LLM 中使用。

- **技术栈**：Bun + TypeScript
- **状态**：可用
- [了解更多关于 tmx2jsonl](./tmx2jsonl/README.md)

## 项目结构

```
llm-tools/
├── tmx2jsonl/        # TMX 转 JSONL 转换器
└── ... (更多工具开发中)
```

## 技术栈

本项目使用以下技术：

- **JavaScript 环境**：
  - Bun（或 Node.js）用于 JavaScript/TypeScript 工具
  - TypeScript 用于类型安全
- **Python**：
  - Python 3.x 用于 Python 工具
  - 根据需要使用各种机器学习/自然语言处理库

## 快速开始

每个工具都有其独立的设置和使用说明。请参考各个工具目录中的 README 获取具体详情。

## 开发指南

### 环境要求

- Bun（或 Node.js）用于 JavaScript 工具
- Python 3.x 用于 Python 工具
- Git

### 开发环境设置

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/llm-tools.git
cd llm-tools
```

2. 按照各工具目录中的设置说明进行具体配置。

## 贡献指南

欢迎贡献！请随时提交 Pull Request。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

如果您有任何问题或建议，请随时提出 Issue。 