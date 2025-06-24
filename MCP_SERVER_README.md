# AI Document Processing MCP Server 🤖

A FastMCP-based server that provides AI-powered document processing tools for template insertion and document list extraction.

## Overview

This MCP (Model Context Protocol) server combines two powerful document processing tools:

1. **Template Insertion** - Intelligently merge documents with JSON templates using AI
2. **Document List Extraction** - Extract structured lists from Word documents (.doc/.docx)

## Features

### 🔄 Template Insertion Tool
- **AI-Powered Merging**: Uses advanced AI models to intelligently combine content
- **Multiple Format Support**: Works with .docx, .pdf, .txt, and .md files
- **Smart Content Mapping**: Automatically maps original content to template structure
- **Professional Output**: Generates well-formatted Word documents with proper styling

### 📋 Document List Extraction Tool
- **Smart Pattern Recognition**: Automatically detects headings, lists, and structured content
- **Multi-Level Hierarchy**: Preserves document structure and relationships
- **Table Processing**: Extracts important information from tables
- **Format Conversion**: Automatically converts .doc files to .docx for processing

## Installation

### Prerequisites
- Python 3.8 or higher
- LibreOffice (for .doc file conversion)

### Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `fastmcp`
- `openai`
- `python-docx`
- `PyMuPDF`
- `python-dotenv`

### Environment Setup
Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your-api-key-here
# OR for testing without API
TEST_MODE=true
```

## Usage

### Starting the Server

#### Option 1: Using the startup script (recommended)
```bash
python run_mcp_server.py
```

#### Option 2: Direct execution
```bash
python mcp_server.py
```

#### Option 3: Using FastMCP CLI
```bash
fastmcp run mcp_server.py
```

### Available Tools

#### 1. insert_template

Merge a document with a JSON template to generate a new Word document.

**Parameters:**
- `template_json_input`: Dictionary or file path containing the template JSON structure
- `original_file_path`: Path to the original document (.docx, .pdf, .txt)

**Returns:**
- File path of the generated .docx document

**Example Usage:**
```python
# Using dictionary input
template = {
    "项目概述": "项目的基本介绍和背景信息",
    "技术方案": "详细的技术实施方案",
    "实施计划": "项目实施的时间安排和里程碑"
}

result_path = insert_template(template, "original_document.pdf")
print(f"Generated document: {result_path}")

# Using JSON file input
result_path = insert_template("template.json", "original_document.docx")
```

#### 2. extract_document_list

Extract a structured list of items from Word documents.

**Parameters:**
- `file_path`: Path to the Word document (.doc or .docx)

**Returns:**
- List of dictionaries with document structure information

**Example Usage:**
```python
document_items = extract_document_list("document.docx")

for item in document_items:
    print(f"ID: {item['id']}")
    print(f"Title: {item['title']}")
    print(f"Level: {item['level']}")
    print(f"Type: {item['type']}")
    print("---")
```

**Sample Output:**
```json
[
    {
        "id": "item_0",
        "title": "1. 项目概述",
        "level": 1,
        "type": "heading",
        "parent_id": null
    },
    {
        "id": "item_1", 
        "title": "1.1 项目背景",
        "level": 2,
        "type": "heading",
        "parent_id": null
    },
    {
        "id": "table_0",
        "title": "表格 1",
        "level": 1,
        "type": "table",
        "parent_id": null
    }
]
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for AI processing | None | Yes (unless TEST_MODE=true) |
| `TEST_MODE` | Enable test mode with mock AI responses | false | No |

### Test Mode

When `TEST_MODE=true`, the server will:
- Use mock AI responses instead of real API calls
- Generate sample content for testing
- Skip API key validation

## Output

### Generated Documents
- Saved in `generated_docs/` directory
- Named with timestamp: `merged_document_YYYYMMDD_HHMMSS.docx`
- Include proper formatting, table of contents, and page numbers

### Document Structure
Generated documents include:
- Title page with generation timestamp
- Table of contents
- Structured content based on template
- Professional formatting and styling

## Error Handling

The server provides comprehensive error handling with specific error codes:

- `FILE_NOT_FOUND` (404): Original document not found
- `UNSUPPORTED_FORMAT` (422): Unsupported file format
- `EMPTY_DOCUMENT` (422): Document content is empty
- `AI_NO_RESPONSE` (500): AI service unavailable
- `AI_INVALID_JSON` (422): AI returned invalid JSON
- `DOCUMENT_GENERATION_ERROR` (500): Failed to generate output document

## Architecture

### Components

1. **DocumentExtractor**: Extracts content from various document formats
2. **ContentMerger**: Uses AI to intelligently merge content with templates
3. **DocumentGenerator**: Creates professionally formatted Word documents
4. **DocumentListExtractor**: Extracts structured lists from documents

### AI Integration

- Uses OpenRouter API with Google Gemini 2.5 Pro Preview model
- Intelligent content analysis and mapping
- Context-aware template filling
- Professional document generation

## Troubleshooting

### Common Issues

1. **LibreOffice Not Found**
   - Install LibreOffice for .doc file conversion
   - Ensure LibreOffice is in system PATH

2. **API Key Issues**
   - Verify OPENROUTER_API_KEY is set correctly
   - Use TEST_MODE=true for testing without API

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Document Processing Errors**
   - Ensure input files are not corrupted
   - Check file permissions
   - Verify supported file formats

### Debug Mode

Enable detailed logging by setting:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Development

### Project Structure
```
ai_docClassify/
├── mcp_server.py          # Main MCP server implementation
├── run_mcp_server.py      # Startup script
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── generated_docs/        # Output directory
└── templates/            # Sample templates
```

### Adding New Tools

To add new tools to the MCP server:

1. Define the tool function with proper type hints
2. Add the `@mcp.tool()` decorator
3. Include comprehensive docstring
4. Handle errors appropriately

Example:
```python
@mcp.tool()
def new_tool(input_param: str) -> str:
    """
    Description of what the tool does.
    
    Args:
        input_param: Description of the parameter
        
    Returns:
        Description of the return value
    """
    # Implementation here
    return result
```

## License

This project is part of the AI Document Classification system.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Ensure all dependencies are installed
4. Verify environment configuration

---

🚀 **Ready to process documents with AI-powered intelligence!** 