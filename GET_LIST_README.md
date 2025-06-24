# 文档列表提取服务 (get_list.py)

## 概述

`get_list.py` 是一个基于 FastAPI 的微服务，专门用于从 .doc 或 .docx 文件中提取文档项列表，为 Dashboard 展示提供结构化数据。该服务通过解析文档结构，智能识别标题、表格和重要内容，并保持原有的层级关系。

## 主要功能

### 🔍 智能文档解析
- **多格式支持**: 同时支持 .doc 和 .docx 文件格式
- **自动转换**: 内置 LibreOffice 转换器，自动将 .doc 转换为 .docx
- **结构识别**: 智能识别文档标题、表格、段落等结构元素

### 📋 内容提取
- **标题提取**: 识别各级标题（基于样式和编号模式）
- **表格处理**: 提取表格标题和重要行数据
- **层级保持**: 维护原文档的层级结构和编号关系
- **过滤优化**: 自动过滤页眉页脚等无关内容

### 🌐 双端口支持
- **文件路径模式**: 适用于服务器本地文件处理
- **文件上传模式**: 适用于 Web 应用和分布式部署

## API 端点

### 1. POST `/get_list` - 文件路径方式

**请求格式:**
```json
{
    "file_path": "path/to/document.docx"
}
```

**响应格式:**
```json
{
    "items": [
        {
            "id": "1",
            "title": "项目概述",
            "level": 1,
            "type": "heading",
            "parent_id": null
        },
        {
            "id": "2",
            "title": "1.1 施工计划",
            "level": 2,
            "type": "heading",
            "parent_id": "1"
        }
    ],
    "total_count": 15,
    "success": true,
    "message": "文档列表提取成功",
    "processing_details": {
        "file_path": "path/to/document.docx",
        "extraction_time": "2025-01-20T10:30:00",
        "item_types": {"heading": 10, "table": 3, "paragraph": 2}
    }
}
```

### 2. POST `/get_list_upload` - 文件上传方式（推荐）

**请求**: 使用 multipart/form-data 上传文件

**响应**: 同上格式

### 3. GET `/health` - 健康检查

**响应:**
```json
{
    "status": "healthy",
    "service": "文档列表提取服务",
    "timestamp": "2025-01-20T10:30:00"
}
```

### 4. GET `/` - 服务信息

返回服务的详细信息，包括功能介绍、支持格式等。

## 安装和部署

### 环境要求

```bash
# Python 依赖
pip install fastapi uvicorn python-docx python-dotenv

# .doc 文件支持（可选）
# 需要安装 LibreOffice
# macOS: brew install libreoffice
# Ubuntu: sudo apt-get install libreoffice
# Windows: 下载安装 LibreOffice
```

### 启动服务

```bash
# 直接启动
python get_list.py

# 或使用 uvicorn
uvicorn get_list:app --host 0.0.0.0 --port 8002 --reload
```

### 访问地址

- **服务地址**: http://localhost:8002
- **API 文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/health

## 使用示例

### Python 客户端示例

```python
import requests

# 1. 文件路径方式
response = requests.post(
    "http://localhost:8002/get_list",
    json={"file_path": "document.docx"}
)
result = response.json()
print(f"提取到 {result['total_count']} 个项目")

# 2. 文件上传方式
with open("document.docx", "rb") as f:
    files = {"file": ("document.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = requests.post("http://localhost:8002/get_list_upload", files=files)
    result = response.json()
    
for item in result['items']:
    print(f"[{item['type']}] 级别{item['level']}: {item['title']}")
```

### curl 示例

```bash
# 文件路径方式
curl -X POST "http://localhost:8002/get_list" \
     -H "Content-Type: application/json" \
     -d '{"file_path": "document.docx"}'

# 文件上传方式
curl -X POST "http://localhost:8002/get_list_upload" \
     -F "file=@document.docx"
```

### JavaScript 示例

```javascript
// 文件上传方式
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8002/get_list_upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(`提取到 ${data.total_count} 个项目`);
    data.items.forEach(item => {
        console.log(`[${item.type}] ${item.title}`);
    });
});
```

## 文档结构识别

### 支持的标题模式

1. **中文数字编号**: 一、二、三、...
2. **阿拉伯数字编号**: 1、2、3、... 或 1.1、1.2、...
3. **中文序号**: （一）、（二）、（三）、...
4. **英文字母编号**: A、B、C、...
5. **括号数字**: （1）、（2）、（3）、...
6. **样式标题**: 基于 Word 标题样式识别

### 层级计算规则

- **多级编号**: 1.1.1 → 级别 3
- **中文数字**: 一、二、三 → 级别 1
- **阿拉伯数字**: 根据数字大小判断级别
- **样式标题**: 基于 Word 样式级别

### 表格处理

- 自动识别表格标题（通常为第一行）
- 提取包含重要关键词的数据行
- 保持表格与文档的层级关系

## 错误处理

### HTTP 状态码

| 状态码 | 含义 | 示例 |
|--------|------|------|
| 200 | 成功 | 文档解析成功 |
| 400 | 请求错误 | 缺少文件名 |
| 404 | 文件不存在 | 指定路径的文件不存在 |
| 422 | 格式不支持 | 上传了非 .doc/.docx 文件 |
| 500 | 服务器错误 | 文档解析失败、LibreOffice 不可用等 |

### 常见错误及解决方案

1. **LibreOffice 不可用**
   - 确保已安装 LibreOffice
   - 检查系统 PATH 配置

2. **文件格式不支持**
   - 确认文件扩展名为 .doc 或 .docx
   - 检查文件是否损坏

3. **内存不足**
   - 处理大文件时可能出现，建议分批处理

## 配置选项

### 环境变量

可以通过 .env 文件配置：

```bash
# .env 文件
SERVICE_PORT=8002
SERVICE_HOST=0.0.0.0
LOG_LEVEL=INFO
```

### 服务配置

```python
# 修改 get_list.py 中的配置
app = FastAPI(
    title="文档列表提取服务",
    description="从.doc或.docx文件提取文档项列表",
    version="1.0.0"
)
```

## 性能优化

### 处理大文件

- 使用临时文件避免内存溢出
- 自动清理临时文件
- 限制文件大小（可配置）

### 并发处理

- FastAPI 天然支持异步处理
- 可通过 uvicorn 配置工作进程数量

```bash
uvicorn get_list:app --workers 4
```

## 测试

### 运行测试

```bash
# 运行测试脚本
python test_get_list.py
```

### 测试内容

1. 健康检查测试
2. 根端点测试
3. 文件路径方式测试
4. 文件上传方式测试
5. 错误处理测试

## 集成指南

### 与 Dashboard 集成

```python
# Dashboard 代码示例
import requests

def get_document_items(file_path):
    """获取文档项目列表"""
    response = requests.post(
        "http://localhost:8002/get_list",
        json={"file_path": file_path}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['items']
    else:
        raise Exception(f"获取文档列表失败: {response.text}")

# 使用示例
items = get_document_items("project_docs.docx")
for item in items:
    print(f"{'  ' * (item['level']-1)}- {item['title']}")
```

### 与其他服务集成

该服务可以与 `insert_template.py` 等其他服务组合使用，形成完整的文档处理工作流。

## 许可证

MIT License

## 支持

如有问题或建议，请联系开发团队或提交 Issue。

---

**注意**: 该服务专注于文档结构提取，不使用 AI 技术，确保快速、稳定的处理性能。 