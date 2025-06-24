# 模板插入服务 (insert_template.py)

## 功能概述

模板插入服务是一个独立的FastAPI微服务，专门用于将原始文档内容与模板JSON进行AI智能合并，生成符合模板结构的docx文档。

## 核心功能

### `insert_temp` API端点

**作用：** 将原始文档内容与模板JSON进行AI智能合并，生成符合模板的docx文档。

**输入：**
```json
{
  "template_json": {
    "章节一": "工程概述",
    "章节二": "施工进度计划",
    "章节三": "质量控制措施"
  },
  "original_file_path": "original.docx"
}
```

**输出：**
```json
{
  "final_doc_path": "generated_docs/merged_document_20250120_143022.docx",
  "success": true,
  "message": "模板插入成功完成"
}
```

## 处理流程

### 双重AI处理机制

1. **文档内容提取**
   - 支持多种文档格式：.docx, .pdf, .txt, .md
   - 智能提取文本内容和表格数据
   - 保持原始内容的结构完整性

2. **AI智能合并**
   - 分析模板JSON中每个章节的要求
   - 从原始文档内容中提取相关信息
   - 进行语义匹配和内容整合
   - 生成符合模板结构的专业内容

3. **文档生成**
   - 使用python-docx生成标准docx文档
   - 自动添加目录和页码
   - 包含生成时间戳和格式验证
   - 确保文档格式规范

## 安装与运行

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 方式1: 使用.env文件（推荐）
# 复制配置模板
cp env_example.txt .env
# 编辑.env文件，填写您的API密钥
# OPENROUTER_API_KEY=your-actual-api-key-here

# 方式2: 直接设置环境变量
export OPENROUTER_API_KEY='your-api-key-here'
```

### 2. 启动服务

```bash
# 启动模板插入服务
python insert_template.py
```

服务将在以下地址启动：
- **API服务**: http://localhost:8001
- **API文档**: http://localhost:8001/docs
- **健康检查**: http://localhost:8001/health

### 3. 测试服务

```bash
# 运行测试脚本
python test_insert_template.py
```

## API使用示例

### Python客户端示例

```python
import requests

# API请求数据
request_data = {
    "template_json": {
        "项目概述": "项目基本信息介绍",
        "技术方案": "详细技术实施方案",
        "进度计划": "项目时间安排"
    },
    "original_file_path": "path/to/your/document.docx"
}

# 发送请求
response = requests.post(
    "http://localhost:8001/insert_temp",
    json=request_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"生成的文档路径: {result['final_doc_path']}")
else:
    print(f"请求失败: {response.text}")
```

### cURL示例

```bash
curl -X POST "http://localhost:8001/insert_temp" \
     -H "Content-Type: application/json" \
     -d '{
       "template_json": {
         "章节一": "工程概述",
         "章节二": "施工计划"
       },
       "original_file_path": "test_original.txt"
     }'
```

## 支持的文档格式

### 输入格式
- **.docx** - Microsoft Word文档
- **.pdf** - PDF文档（文本提取）
- **.txt** - 纯文本文件
- **.md** - Markdown文件

### 输出格式
- **.docx** - 标准Microsoft Word文档

## API端点详情

### POST /insert_temp
- **描述**: 模板插入处理
- **请求体**: InsertTemplateRequest
- **响应**: InsertTemplateResponse
- **超时**: 60秒

### GET /health
- **描述**: 健康检查
- **响应**: 服务状态信息

### GET /
- **描述**: 服务信息
- **响应**: API基本信息和可用端点

## 错误处理

服务包含完善的错误处理机制：

- **400** - 请求参数错误
- **404** - 文件不存在
- **500** - 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## 配置选项

### 环境变量
- `OPENROUTER_API_KEY`: OpenRouter API密钥（必需）
  - 可通过.env文件配置（推荐）
  - 也可通过系统环境变量设置

### 输出目录
- 默认输出目录: `generated_docs/`
- 文件命名格式: `merged_document_{timestamp}.docx`

## 技术特性

### AI模型
- 使用Google Gemini 2.5 Pro Preview模型
- 温度设置: 0.1（确保输出稳定性）
- 支持多语言内容处理

### 文档处理
- 智能段落分割和格式化
- 自动目录生成
- 页脚信息添加
- 文档完整性验证

### 性能优化
- 异步请求处理
- 智能内容缓存
- 错误重试机制

## 常见问题

### Q: 服务启动失败？
A: 请检查API密钥配置：
1. 确认.env文件中设置了`OPENROUTER_API_KEY=your-key`
2. 或确认系统环境变量已设置
3. 检查API密钥格式是否正确

### Q: 文档生成失败？
A: 请确认原始文档路径正确且文件格式受支持。

### Q: AI处理超时？
A: 对于大文档，处理可能需要更多时间，请耐心等待。

### Q: 生成的文档格式异常？
A: 服务包含自动格式验证，异常情况会在日志中报告。

## 日志信息

服务提供详细的日志信息：
- 📄 文档处理进度
- 🧠 AI处理状态
- ✅ 成功操作确认
- ❌ 错误信息记录

## 版本信息

- **版本**: 1.0.0
- **Python**: 3.8+
- **FastAPI**: 0.104.1+
- **依赖**: 见requirements.txt

## 技术支持

如遇问题，请检查：
1. 日志输出信息
2. API文档 (http://localhost:8001/docs)
3. 健康检查状态 (http://localhost:8001/health) 