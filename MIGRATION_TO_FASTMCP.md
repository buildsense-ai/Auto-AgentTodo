# Migration to FastMCP 🚀

This document outlines the migration from standalone Python scripts to a unified FastMCP server.

## Overview

The refactoring consolidates two separate tools into a single MCP (Model Context Protocol) server:
- `insert_template.py` → `@mcp.tool()` decorator
- `get_list.py` → `@mcp.tool()` decorator

## Changes Summary

### Before (Separate Scripts)
```
ai_docClassify/
├── insert_template.py      # Standalone script
├── get_list.py            # Standalone script
├── test_insert_template.py
└── test_get_list.py
```

### After (Unified MCP Server)
```
ai_docClassify/
├── mcp_server.py          # Unified FastMCP server
├── run_mcp_server.py      # Startup script
├── test_mcp_server.py     # Unified test script
└── MCP_SERVER_README.md   # Comprehensive documentation
```

## Key Benefits

### 1. Unified Interface
- **Before**: Two separate command-line scripts
- **After**: Single MCP server with multiple tools

### 2. Better Integration
- **Before**: Manual script execution
- **After**: MCP protocol support for AI assistants

### 3. Improved Error Handling
- **Before**: Basic error messages
- **After**: Structured error codes and comprehensive logging

### 4. Enhanced Testability
- **Before**: Separate test files
- **After**: Unified test framework with mock mode

## Function Mapping

### Template Insertion

#### Before (`insert_template.py`)
```python
def run_template_insertion(template_json_input, original_file_path):
    # Implementation
    return final_doc_path

# Command line usage
if __name__ == "__main__":
    # argparse setup
    result = run_template_insertion(args.template, args.document)
```

#### After (`mcp_server.py`)
```python
@mcp.tool()
def insert_template(template_json_input: Union[str, Dict[str, str]], 
                   original_file_path: str) -> str:
    """AI tool to merge a document with a JSON template..."""
    # Same core logic, enhanced error handling
    return output_path
```

### Document List Extraction

#### Before (`get_list.py`)
```python
def extract_document_list(file_path: str) -> List[Dict[str, Any]]:
    # Implementation
    return result

# Command line usage
if __name__ == "__main__":
    # argparse setup
    items = extract_document_list(args.file_path)
```

#### After (`mcp_server.py`)
```python
@mcp.tool()
def extract_document_list(file_path: str) -> List[Dict[str, Any]]:
    """AI tool to extract a structured list from Word documents..."""
    # Same core logic, enhanced error handling
    return result
```

## Architecture Improvements

### 1. Component Organization
- **DocumentExtractor**: Handles content extraction from various formats
- **ContentMerger**: AI-powered content merging with templates
- **DocumentGenerator**: Professional document generation
- **DocumentListExtractor**: Structured list extraction from documents

### 2. Error Handling
```python
class ProcessingError(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
```

### 3. Test Mode Support
```python
# Enable test mode for development
os.environ["TEST_MODE"] = "true"

# Mock AI responses when in test mode
def _mock_merge_content(self, template_json, original_content):
    # Generate sample content for testing
```

## Usage Changes

### Before (Command Line)
```bash
# Template insertion
python insert_template.py template.json document.pdf

# Document list extraction  
python get_list.py document.docx
```

### After (MCP Server)
```bash
# Start the server
python run_mcp_server.py
# or
fastmcp run mcp_server.py

# Use tools through MCP protocol
# Tools: insert_template, extract_document_list
```

### Testing
```bash
# Before
python test_insert_template.py
python test_get_list.py

# After
python test_mcp_server.py
```

## Configuration

### Environment Variables
```env
# Required for production
OPENROUTER_API_KEY=your-api-key-here

# Optional for testing
TEST_MODE=true
```

### Dependencies
```txt
# Added to requirements.txt
fastmcp
```

## Migration Checklist

- [x] ✅ Consolidate `insert_template.py` functionality into MCP tools
- [x] ✅ Consolidate `get_list.py` functionality into MCP tools  
- [x] ✅ Create unified `mcp_server.py` with FastMCP
- [x] ✅ Add comprehensive error handling
- [x] ✅ Implement test mode for development
- [x] ✅ Create startup script `run_mcp_server.py`
- [x] ✅ Create unified test script `test_mcp_server.py`
- [x] ✅ Update requirements.txt with FastMCP
- [x] ✅ Create detailed documentation

## Backward Compatibility

The original scripts (`insert_template.py` and `get_list.py`) remain functional but are superseded by the MCP server implementation. The core functionality is preserved with the following enhancements:

1. **Same Input/Output**: Functions accept the same parameters and return the same results
2. **Enhanced Error Messages**: More detailed error information with error codes
3. **Better Logging**: Comprehensive logging with timestamps and context
4. **Test Mode**: Ability to run without API keys for development

## Next Steps

1. **Install FastMCP**: `pip install -r requirements.txt`
2. **Configure Environment**: Set up `.env` file with API keys
3. **Test the Server**: Run `python test_mcp_server.py` 
4. **Start the Server**: Run `python run_mcp_server.py`
5. **Integrate with AI Tools**: Use MCP protocol to access the tools

## Support

For issues with the migration:
1. Check the `MCP_SERVER_README.md` for detailed usage instructions
2. Run the test script to verify functionality
3. Enable test mode for development without API keys
4. Review error logs for specific error codes and messages

---

🎉 **Migration Complete!** The system is now powered by FastMCP for better integration and enhanced functionality. 