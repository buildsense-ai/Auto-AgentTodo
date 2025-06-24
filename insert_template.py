#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板插入服务：AI智能合并原始文档与模板JSON
"""

import os
import json
import logging
import traceback
import hashlib
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path
import argparse

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from openai import OpenAI
import fitz  # PyMuPDF
from docx import Document as DocxDocument

# 配置日志（优先配置）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载当前目录下的.env文件
    logger.info("✅ 已加载.env环境变量文件")
except ImportError:
    logger.warning("⚠️ python-dotenv未安装，将直接从系统环境变量读取配置")
except Exception as e:
    logger.warning(f"⚠️ 加载.env文件时出现问题: {e}")

def get_api_key() -> str:
    """获取OpenRouter API密钥"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        # 检查是否是测试模式
        test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"
        if test_mode:
            logger.warning("⚠️ 测试模式：使用模拟API密钥")
            return "test-api-key-for-testing"
        
        logger.error("❌ 未找到OPENROUTER_API_KEY")
        logger.error("请在.env文件中设置: OPENROUTER_API_KEY=your-api-key-here")
        logger.error("或设置系统环境变量: export OPENROUTER_API_KEY='your-api-key-here'")
        logger.error("或设置TEST_MODE=true进入测试模式")
        raise RuntimeError("缺少必需的API密钥配置")
    return api_key

# 确保输出目录存在
OUTPUT_DIR = "generated_docs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class DocumentExtractor:
    """文档内容提取器"""
    
    def __init__(self):
        logger.info("📄 文档提取器初始化完成")
    
    def extract_from_file_path(self, file_path: str) -> str:
        """从文件路径提取内容"""
        if not os.path.exists(file_path):
            raise ProcessingError(
                f"原始文档不存在: {file_path}",
                "FILE_NOT_FOUND",
                404
            )
        return self._extract_content(file_path)
    
    def _extract_content(self, file_path: str) -> str:
        """提取文档内容的核心方法"""
        logger.info(f"📄 开始提取文档内容: {Path(file_path).name}")
        
        content = ""
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.docx':
                doc = DocxDocument(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
                
                # 提取表格内容
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join([cell.text.strip() for cell in row.cells])
                        if row_text.strip():
                            content += f"\n表格行: {row_text}"
            
            elif file_ext == '.pdf':
                doc = fitz.open(file_path)
                for page in doc:
                    content += page.get_text()
                doc.close()
            
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            else:
                raise ProcessingError(
                    f"不支持的文件格式: {file_ext}",
                    "UNSUPPORTED_FORMAT",
                    422
                )
            
            if not content.strip():
                raise ProcessingError(
                    "文档内容为空",
                    "EMPTY_DOCUMENT",
                    422
                )
            
            logger.info(f"✅ 成功提取内容，长度: {len(content)} 字符")
            return content.strip()
            
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"❌ 提取文档内容失败: {e}")
            raise ProcessingError(
                f"文档内容提取失败: {str(e)}",
                "EXTRACTION_ERROR",
                500
            )

class ContentMerger:
    """内容智能合并器"""
    
    def __init__(self, api_key: str):
        """初始化AI客户端"""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = "google/gemini-2.5-pro-preview"
        logger.info("🧠 内容合并器初始化完成")
    
    def merge_content(self, template_json: Dict[str, str], original_content: str) -> Dict[str, str]:
        """使用AI智能合并模板JSON和原始内容"""
        logger.info("🧠 开始AI智能合并...")
        
        # 检查是否是测试模式
        test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"
        if test_mode or self.client.api_key == "test-api-key-for-testing":
            logger.warning("⚠️ 测试模式：使用模拟AI合并")
            return self._mock_merge_content(template_json, original_content)
        
        prompt = f"""
你是一个专业的文档处理AI助手。请根据提供的模板JSON结构和原始文档内容，进行智能合并。

模板JSON结构：
{json.dumps(template_json, ensure_ascii=False, indent=2)}

原始文档内容：
{original_content}

任务要求：
1. 分析模板JSON中每个章节的要求
2. 从原始文档内容中提取相关信息
3. 进行语义匹配和内容整合
4. 生成符合模板结构的内容

输出要求：
- 必须返回JSON格式
- 键名与模板JSON完全一致
- 值为根据原始内容智能生成的具体内容
- 如果原始内容中没有相关信息，请基于合理推测生成内容
- 每个章节内容应该完整、专业、符合实际

请直接返回JSON格式的结果，不要包含任何解释文字。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            
            if not response or not response.choices or not response.choices[0].message.content:
                raise ProcessingError(
                    "AI响应无效或为空",
                    "AI_NO_RESPONSE",
                    500
                )
            
            # 提取JSON内容
            response_content = response.choices[0].message.content.strip()
            json_str = self._extract_json_from_response(response_content)
            
            try:
                merged_content = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                logger.error(f"AI响应内容: {response_content}")
                raise ProcessingError(
                    f"AI返回的内容不是有效的JSON格式: {str(e)}",
                    "AI_INVALID_JSON",
                    422
                )
            
            # 验证合并结果
            if not isinstance(merged_content, dict):
                raise ProcessingError(
                    "AI返回的内容不是字典格式",
                    "AI_INVALID_FORMAT",
                    422
                )
            
            logger.info(f"✅ AI合并成功，生成 {len(merged_content)} 个章节")
            for key, value in merged_content.items():
                preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                logger.info(f"   📝 {key}: {preview}")
            
            return merged_content
            
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"❌ AI合并失败: {e}")
            raise ProcessingError(
                f"AI合并过程中发生错误: {str(e)}",
                "AI_MERGE_ERROR",
                500
            )
    
    def _mock_merge_content(self, template_json: Dict[str, str], original_content: str) -> Dict[str, str]:
        """模拟AI合并（测试模式）"""
        logger.info("🧪 模拟AI合并模式")
        
        merged_content = {}
        content_lines = original_content.split('\n')
        content_preview = ' '.join(content_lines[:5])[:200]
        
        for key, description in template_json.items():
            # 基于原始内容和模板描述生成简单的合并内容
            merged_content[key] = f"""根据原始文档内容生成的{key}章节：

{description}

基于原始文档的相关信息：
{content_preview}

本章节内容已根据模板要求进行智能整合，确保符合工程文档的标准格式和要求。具体内容包括项目的基本情况、技术要求、实施方案等关键信息。

注：此内容由测试模式生成，实际应用中将使用真实AI进行智能合并。"""
        
        logger.info(f"✅ 模拟合并完成，生成 {len(merged_content)} 个章节")
        return merged_content
    
    def _extract_json_from_response(self, response_content: str) -> str:
        """从AI响应中提取JSON内容"""
        # 尝试提取JSON
        if "```json" in response_content:
            start = response_content.find("```json") + 7
            end = response_content.find("```", start)
            if end != -1:
                return response_content[start:end].strip()
            else:
                return response_content[response_content.find("```json") + 7:].strip()
        elif response_content.startswith("{") and response_content.endswith("}"):
            return response_content
        else:
            # 查找JSON对象
            start_idx = response_content.find("{")
            if start_idx != -1:
                brace_count = 0
                for i, char in enumerate(response_content[start_idx:], start_idx):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            return response_content[start_idx:i+1]
                brace_count = 0
                for i, char in enumerate(response_content[start_idx:], start_idx):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            return response_content[start_idx:i+1]
            return response_content

class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self):
        logger.info("📄 文档生成器初始化完成")
    
    def generate_docx(self, merged_content: Dict[str, str], output_path: str) -> Dict[str, Any]:
        """生成最终的docx文档"""
        logger.info("📄 开始生成docx文档...")
        
        try:
            doc = Document()
            
            # 设置文档标题
            title = doc.add_heading('AI智能合并文档', 0)
            title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
            # 添加生成时间
            timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            time_para = doc.add_paragraph(f'生成时间: {timestamp}')
            time_para.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
            
            doc.add_page_break()
            
            # 添加目录标题
            doc.add_heading('目录', level=1)
            
            # 生成目录
            for i, section_title in enumerate(merged_content.keys(), 1):
                toc_para = doc.add_paragraph(f"{i}. {section_title}")
                toc_para.style = 'List Number'
            
            doc.add_page_break()
            
            # 添加正文内容
            for i, (section_title, section_content) in enumerate(merged_content.items(), 1):
                # 添加章节标题
                heading = doc.add_heading(f"{i}. {section_title}", level=1)
                
                # 添加章节内容
                if isinstance(section_content, str):
                    # 处理多段落内容
                    paragraphs = section_content.split('\n\n')
                    for para_text in paragraphs:
                        if para_text.strip():
                            para = doc.add_paragraph(para_text.strip())
                            para.style = 'Normal'
                elif isinstance(section_content, list):
                    # 处理列表内容
                    for item in section_content:
                        para = doc.add_paragraph(str(item))
                        para.style = 'List Bullet'
                else:
                    # 其他类型转为字符串
                    para = doc.add_paragraph(str(section_content))
                    para.style = 'Normal'
                
                # 添加章节间距
                doc.add_paragraph()
            
            # 添加页脚
            footer_section = doc.sections[0]
            footer = footer_section.footer
            footer_para = footer.paragraphs[0]
            footer_para.text = "本文档由AI智能合并系统自动生成"
            footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
            # 保存文档
            doc.save(output_path)
            logger.info(f"✅ 成功生成docx文档: {output_path}")
            
            # 验证文档并返回统计信息
            validation_info = self._validate_docx(output_path)
            
            return {
                "sections_count": len(merged_content),
                "file_size": os.path.getsize(output_path),
                "validation": validation_info
            }
            
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"❌ 生成docx文档失败: {e}")
            raise ProcessingError(
                f"文档生成失败: {str(e)}",
                "DOCUMENT_GENERATION_ERROR",
                500
            )
    
    def _validate_docx(self, file_path: str) -> Dict[str, Any]:
        """验证生成的docx文档"""
        try:
            # 尝试打开文档进行验证
            doc = Document(file_path)
            paragraph_count = len(doc.paragraphs)
            table_count = len(doc.tables)
            
            if paragraph_count == 0:
                raise ProcessingError(
                    "生成的文档为空",
                    "EMPTY_GENERATED_DOCUMENT",
                    500
                )
            
            validation_info = {
                "paragraph_count": paragraph_count,
                "table_count": table_count,
                "is_valid": True
            }
            
            logger.info(f"✅ 文档验证通过，包含 {paragraph_count} 个段落")
            return validation_info
            
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"❌ 文档验证失败: {e}")
            raise ProcessingError(
                f"生成的文档格式有误: {str(e)}",
                "DOCUMENT_VALIDATION_ERROR",
                500
            )

class TemplateInserter:
    """模板插入调度器 - 协调各个组件"""
    
    def __init__(self, api_key: str):
        """初始化各个组件"""
        self.extractor = DocumentExtractor()
        self.merger = ContentMerger(api_key)
        self.generator = DocumentGenerator()
        logger.info("🤖 模板插入调度器初始化完成")
    
    def process_from_file_path(self, template_json: Dict[str, str], original_file_path: str) -> Dict[str, Any]:
        """从文件路径处理模板插入（向后兼容）"""
        logger.info("🚀 开始文件路径模式的模板插入处理...")
        
        # 1. 提取原始文档内容
        original_content = self.extractor.extract_from_file_path(original_file_path)
        
        # 2. AI智能合并
        merged_content = self.merger.merge_content(template_json, original_content)
        
        # 3. 生成输出文件路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"merged_document_{timestamp}.docx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 4. 生成docx文档
        generation_info = self.generator.generate_docx(merged_content, output_path)
        
        logger.info(f"✅ 模板插入处理完成: {output_path}")
        return {
            "final_doc_path": output_path,
            "generation_info": generation_info,
            "content_summary": {key: len(str(value)) for key, value in merged_content.items()}
        }

def run_template_insertion(template_json_input: Union[str, Dict[str, str]], original_file_path: str) -> str:
    """
    AI tool to merge a document with a JSON template to generate a new docx file.
    
    It uses an AI model to intelligently merge content from the original document 
    (e.g., .docx, .pdf, .txt) into the structure defined by the JSON template.

    Args:
        template_json_input: A dictionary or file path for the template JSON.
        original_file_path: The path to the original document file.

    Returns:
        The file path of the generated .docx document.
    """
    logger.info("🚀 Starting template insertion process...")
    
    try:
        # Load template json if a path is provided
        if isinstance(template_json_input, str):
            if not os.path.exists(template_json_input):
                raise FileNotFoundError(f"Template JSON file not found: {template_json_input}")
            with open(template_json_input, 'r', encoding='utf-8') as f:
                template_json = json.load(f)
        else:
            template_json = template_json_input

        # Get API key and initialize inserter
        api_key = get_api_key()
        inserter = TemplateInserter(api_key)

        # Process and get result
        result = inserter.process_from_file_path(template_json, original_file_path)
        
        final_doc_path = result["final_doc_path"]
        logger.info(f"✅ Template insertion process completed successfully. Document saved at: {final_doc_path}")
        
        return final_doc_path

    except (ProcessingError, FileNotFoundError) as e:
        logger.error(f"❌ Processing failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during template insertion: {e}")
        logger.error(traceback.format_exc())
        raise ProcessingError(f"An unexpected error occurred: {str(e)}", "UNEXPECTED_ERROR", 500)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI-powered document generation from a template.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("template_json_path", help="Path to the template JSON file.")
    parser.add_argument("original_file_path", help="Path to the original document file (.docx, .pdf, .txt).")

    print("=" * 70)
    print("🤖 AI Document Template Inserter")
    print("=" * 70)
    
    # 检查API密钥配置
    try:
        api_key = get_api_key()
        logger.info(f"✅ API key found (length: {len(api_key)}).")
    except Exception as e:
        logger.error(f"❌ Critical Error: {e}")
        print("\nConfiguration Help:")
        print("1. Create a file named .env in the same directory.")
        print("2. Add this line to it: OPENROUTER_API_KEY=your-api-key-here")
        print("\nAlternatively, set a system environment variable.")
        exit(1)

    args = parser.parse_args()

    print(f"\n▶️ Starting process with:")
    print(f"   Template: {args.template_json_path}")
    print(f"   Original Document: {args.original_file_path}")
    print("-" * 70)

    try:
        output_file = run_template_insertion(
            template_json_input=args.template_json_path,
            original_file_path=args.original_file_path
        )
        print(f"\n✅ Success! Generated document saved at:")
        print(f"   -> {output_file}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found.")
        print(f"   Details: {e}")
    except ProcessingError as e:
        print(f"\n❌ Error during processing: {e.error_code}")
        print(f"   Details: {e.message}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred.")
        traceback.print_exc()
    
    print("=" * 70)
    print("✅ Process finished.")
    print("=" * 70) 