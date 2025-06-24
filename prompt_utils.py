#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI提示工具模块：AI文档生成器
包含用于生成AI提示的各种函数
"""

def get_template_analysis_prompt(template_representation: str) -> str:
    """
    (This function is currently not used as stage 1 is deterministic).
    Generates a prompt for the AI to analyze the template structure.
    """
    return f"""
Please analyze the following structured Word template content and identify all the fields that need to be filled.
The structure is represented as a JSON object where keys are unique cell identifiers (e.g., 'table_0_row_1_col_2') and values are the text content of those cells.

Template Structure:
{template_representation}

Your task is to return a JSON object containing the unique identifiers for cells that are placeholders for data.
The value for each key should be an empty string.

Example Output:
{{
  "table_0_row_0_col_1": "",
  "table_0_row_1_col_1": ""
}}
"""

def get_fill_data_prompt(template_structure: str, placeholders: str, input_data: str) -> str:
    """
    Generates a prompt for the AI to handle hybrid mapping: both template structure and placeholders.
    """
    return f"""
你是一个专业的混合模式文档填写助手。你需要同时处理三种任务：
1. **模板结构匹配**：将JSON数据映射到Word文档的表格单元格和段落结构中
2. **占位符匹配**：为特定的占位符找到对应的数据值
3. **图片引用处理**：处理图片占位符，确保图片能正确引用

---

**核心任务：生成统一的填充数据映射**

你将获得：
- **模板结构**：文档中所有单元格和段落的结构化表示
- **占位符列表**：从特定模式（如"项目名称："和"致____（监理单位）"）提取的占位符
- **输入数据**：需要映射的JSON数据（可能包含attachments_map图片信息）

你的输出应该是一个JSON对象，包含三种类型的映射：
- **结构映射**：键如"table_0_row_1_col_1"或"paragraph_3"，用于填充模板结构
- **占位符映射**：键如"label_项目名称"或"inline_监理单位"，用于替换占位符
- **图片映射**：如果输入数据包含attachments_map，直接将其包含在输出中

---

**重要原则：只填充确定的数据**

⚠️ **关键要求**：
- **只有在输入数据中找到明确对应的信息时，才输出该键值对**
- **如果找不到对应的数据，请完全省略该键，不要输出任何占位文本如"待填写"、"____"等**
- **宁可留空，也不要填入不确定的内容**

---

**映射规则**

### 1. 模板结构映射（保持原有逻辑）
- **排除规则**：如果单元格或段落文本中包含 **"（签字）"** 字样，**绝对不要**为其填充任何内容。
- 如果一个单元格的内容是"标签："（例如 `"项目名称："`），并且其右侧或下方的单元格为空，则应将数据填入那个空单元格
- 如果一个单元格包含下划线占位符但**不是特定的两种模式**，则直接替换该单元格内容
- 智能匹配：运用推理能力，如`project_leader`应映射到"项目负责人"相关的位置

### 2. 占位符映射（现有逻辑）
- 对于`label_*`类型的占位符（来自"项目名称："），找到语义匹配的数据
- 对于`inline_*`类型的占位符（来自"致____（监理单位）"），找到对应的值
- 占位符名称是提示性的，需要智能匹配到输入数据的字段
- **如果确实找不到匹配的数据，就不要输出这个键**

### 3. 图片映射（新增功能）
- 如果输入数据包含`attachments_map`字段，**必须**将其完整地包含在输出JSON中
- 这将确保图片信息能被正确传递到文档生成阶段
- 图片占位符`{{image:key}}`会在文档生成时被自动替换为"（详见附件N）"的格式

---

### 🧪 示例

**模板结构:**
```json
{{
  "table_0_row_0_col_0": "项目名称：",
  "table_0_row_0_col_1": "",
  "table_0_row_1_col_0": "负责人：",
  "table_0_row_1_col_1": "",
  "paragraph_0": "项目名称：{{label_项目名称}}",
  "paragraph_1": "致{{inline_监理单位}}（监理单位）",
  "paragraph_2": "施工图详见：{{image:shiGongTu}}"
}}
```

**占位符列表:**
```json
[
  "label_项目名称",
  "inline_监理单位"
]
```

**输入数据:**
```json
{{
  "project_name": "古建筑保护修缮工程",  
  "project_leader": "张三",
  "supervision_company": "广州建设监理公司",
  "attachments_map": {{
    "shiGongTu": "uploads/construction_drawing.png",
    "xianChangZhaoPian": "uploads/site_photo.jpg"
  }}
}}
```

**输出结果:**
```json
{{
  "table_0_row_0_col_1": "古建筑保护修缮工程",
  "table_0_row_1_col_1": "张三",
  "label_项目名称": "古建筑保护修缮工程",
  "inline_监理单位": "广州建设监理公司",
  "attachments_map": {{
    "shiGongTu": "uploads/construction_drawing.png",
    "xianChangZhaoPian": "uploads/site_photo.jpg"
  }}
}}
```

---

现在请根据下方的数据进行混合映射：

**模板结构:**
```json
{template_structure}
```

**占位符列表:**
```json
{placeholders}
```

**输入数据:**
```json
{input_data}
```

**重要要求:**
- **所有生成的内容必须使用中文**
- 输出统一的JSON对象，包含所有类型的映射
- 对占位符进行智能语义匹配
- 保持原有的模板结构填充逻辑
- **如果输入数据包含attachments_map，必须完整包含在输出中**
- **重要：如果找不到对应数据，完全省略该键，不要填入"待填写"等占位文本**
- 只输出最终的JSON对象，不要包含解释说明或Markdown格式
"""

def get_multimodal_extraction_prompt(fields_to_extract: str) -> str:
    """
    Generates a prompt for the AI to extract structured data from multimodal inputs.
    """
    
    return f"""
你是一个高度智能的AI助手，负责从各种来源（包括文本和图像）中提取结构化信息来填写表单。

你的目标是基于提供的内容填充一个JSON对象。仔细分析所有文本和图像。

**需要提取的信息架构:**
你的最终输出必须是一个JSON对象。以下是你需要提取的字段。尽量填写尽可能多的字段。如果找不到某个字段的信息，请在最终JSON中省略该字段。

```json
{fields_to_extract}
```

**特别注意 - 图像处理指令:**
对于 `attachments_map` 字段，你必须返回一个**JSON对象**（不是数组），其中：
- **键**: 是对图像内容的简短中文描述，用拼音或英文表示（例如：'shiGongTu', 'sunHuaiZhaoPian', 'xianChangTu'）
- **值**: 是对应的图像文件路径（在提供的文本内容中会显示）

示例格式：
```json
{{
  "attachments_map": {{
    "shiGongTu": "uploads/construction_drawing.png",
    "sunHuaiZhaoPian": "uploads/damage_photo.jpg",
    "xianChangTu": "uploads/site_photo.png"
  }}
}}
```

**操作指令:**
1. **分析所有输入:** 审查从文档中提取的文本和所有图像的内容。
2. **综合信息:** 将所有来源的信息组合起来获得最完整的图像。例如，图像可能显示文本中描述的损伤。
3. **处理图像:** 当你发现相关图像时，为每个图像创建一个描述性的键名，并将其文件路径作为值添加到 `attachments_map` 对象中。文件路径会在文本内容中以"附加图像 (文件路径: ...)"的格式提供给你。
4. **智能分类:** 根据图像内容给出合适的中文描述键名，如：
   - 施工图纸 → 'shiGongTu'
   - 损坏照片 → 'sunHuaiZhaoPian' 
   - 现场照片 → 'xianChangZhaoPian'
   - 设计图纸 → 'sheJiTu'
5. **输出JSON:** **只返回一个有效的JSON对象**，包含提取的数据。**所有提取的文本内容和描述必须使用中文**。不要包含任何其他文本、解释或markdown格式。

现在，分析以下内容并生成JSON对象。
""" 