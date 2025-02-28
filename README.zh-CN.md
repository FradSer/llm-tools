# LLM 工具集 ![](https://img.shields.io/badge/A%20FRAD%20PRODUCT-WIP-yellow)

[![Twitter Follow](https://img.shields.io/twitter/follow/FradSer?style=social)](https://twitter.com/FradSer)

[English](README.md) | 简体中文

这是一个全面的工具集合，旨在简化大语言模型（LLM）应用的开发、处理和管理。这些工具采用现代技术和最佳实践构建，注重性能、可靠性和易用性。

## 工具列表

### 1. tmx2jsonl

一个高性能工具，用于将 TMX（Translation Memory eXchange）文件转换为 JSONL 格式，专为 LLM 训练数据准备优化。

- **技术栈**：Bun + TypeScript
- **状态**：可用 ✅
- **特点**：
  - 快速处理大型 TMX 文件
  - 内存高效的流式处理
  - 强大的错误处理
- [了解更多关于 tmx2jsonl](./tmx2jsonl/README.md)

### 2. jsonl2parquet

一个命令行工具，用于高效地将 JSONL 文件转换为 Parquet 格式，为机器学习工作流程优化。

- **技术栈**：Python
- **状态**：可用 ✅
- **特点**：
  - 高压缩比
  - 快速转换速度
  - 内存高效处理
- [了解更多关于 jsonl2parquet](./jsonl2parquet/README.md)

## 项目结构

```
llm-tools/
├── tmx2jsonl/        # TMX 转 JSONL 转换器
├── jsonl2parquet/    # JSONL 转 Parquet 转换器
└── ... (更多工具开发中)
```

## 技术栈

本项目利用现代技术实现最佳性能：

- **JavaScript/TypeScript 工具**：
  - Bun 运行时以获得最佳性能
  - TypeScript 提供类型安全和更好的开发体验
  - 现代 ES 模块和 async/await 模式
  
- **Python 工具**：
  - Python 3.8+ 确保与最新 ML 库的兼容性
  - pandas & pyarrow 用于高效数据处理
  - 类型提示以提高代码质量

## 快速开始

每个工具都有其独立的设置和使用说明。请参考各个工具的 README 获取具体详情：

- [tmx2jsonl 设置指南](./tmx2jsonl/README.md)
- [jsonl2parquet 设置指南](./jsonl2parquet/README.md)

## 参与贡献

我们热烈欢迎各种形式的贡献！以下是参与方式：

1. Fork 这个仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系与支持

- 如有 bug 报告或功能请求，请创建 issue
- 在 Twitter 上关注 [@FradSer](https://twitter.com/FradSer) 获取最新更新
- 如果您觉得这个项目有帮助，请给它点个星！ 