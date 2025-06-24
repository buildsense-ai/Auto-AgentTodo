# AI文档生成器

AI驱动的Word文档生成器，支持从多种源文件自动提取数据并生成格式化文档。

## 🚀 新功能：图片附件处理

现在支持在Word模板中使用图片占位符，系统会自动将图片附加到文档末尾并生成引用。

### 功能特点

- ✅ **保持现有文本插入功能完整性** - 所有原有功能保持不变
- 🖼️ **图片占位符支持** - 使用 `{{image:键名}}` 格式
- 📎 **自动图片附件** - 图片统一附加到文档末尾
- 🔗 **智能引用生成** - 自动生成"（详见附件N）"引用
- 🧠 **AI图片分析** - 自动为图片生成描述性键名
- 📄 **多格式支持** - 支持PDF、PNG、JPG等多种图片来源

## 🧪 完整系统测试

### 快速测试

```bash
# 设置API密钥
export OPENROUTER_API_KEY="your-api-key-here"

# 运行完整系统测试
python main.py
```

### 测试内容

系统会自动进行以下测试：

1. **创建测试环境**
   - 生成包含图片占位符的测试模板
   - 创建测试图片文件
   - 生成测试数据

2. **功能测试**
   - 基本文档生成流程
   - 图片占位符处理
   - 图片附件自动附加
   - 错误处理和系统健壮性

3. **生成测试报告**
   - 详细的测试结果
   - 功能验证清单
   - 输出文件位置

### 测试输出

测试完成后，您将在 `test_outputs_YYYYMMDD_HHMMSS/` 目录中找到：

- `test_template_with_images.docx` - 测试模板
- `test_output_basic.docx` - 生成的文档
- `test_report.md` - 详细测试报告
- 各种测试图片文件

## 📖 使用指南

### 1. 在Word模板中添加图片占位符

```
详细的施工图纸请参考：{{image:shiGongTu}}
现场照片详见：{{image:xianChangZhaoPian}}
```

### 2. 上传包含图片的文件

- 支持PNG、JPG等图片文件
- 支持包含图片的PDF文件（系统会自动提取）

### 3. 系统自动处理

- AI分析图片内容并生成映射
- 占位符被替换为"（详见附件N）"
- 实际图片附加在文档末尾

## 🔧 环境要求

```bash
pip install -r requirements.txt
```

主要依赖：
- `openai` - AI接口
- `python-docx` - Word文档处理
- `PyMuPDF` - PDF处理
- `Pillow` - 图片处理
- `python-dotenv` - 环境变量管理

## 🌐 Web界面

```bash
# 启动Web界面
python main.py

# 或者明确指定
python app.py
```

## 🔑 API密钥设置

从 [OpenRouter](https://openrouter.ai/keys) 获取API密钥：

```bash
# 方式1：环境变量
export OPENROUTER_API_KEY="your-api-key-here"

# 方式2：.env文件
echo "OPENROUTER_API_KEY=your-api-key-here" > .env
```

## 🎯 使用示例

### 命令行模式

```bash
python main.py --cli
```

### Web界面模式

```bash
python main.py --web
```

### 完整系统测试

```bash
python main.py  # 默认运行测试
```

## 📋 项目结构

```
ai_docClassify/
├── main.py              # 主程序
├── app.py               # Web界面
├── prompt_utils.py      # AI提示工具
├── demo_specific_cases.py # 演示脚本
├── requirements.txt     # 依赖列表
├── templates/           # 模板文件
├── uploads/            # 上传文件
└── test_outputs_*/     # 测试输出
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ❌ 错误: 未找到 OPENROUTER_API_KEY 环境变量
   ```
   解决：设置正确的API密钥

2. **PIL不可用**
   ```
   ⚠️ PIL未安装，创建简单的测试图片文件
   ```
   解决：`pip install Pillow`

3. **LibreOffice未找到**
   ```
   ❌ 未找到LibreOffice，请确保已安装LibreOffice
   ```
   解决：安装LibreOffice用于DOC转换

## 🎉 测试成功标志

当您看到以下输出时，说明系统运行正常：

```
✅ 完整系统测试完成！
📁 测试结果保存在: test_outputs_20250120_143022/
📊 测试报告: test_outputs_20250120_143022/test_report.md
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## �� 许可证

MIT License 