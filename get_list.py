#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档列表提取服务：从.doc或.docx文件提取文档项列表
"""

import os
import re
import logging
import traceback
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import argparse

from docx import Document
import subprocess

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("✅ 已加载.env环境变量文件")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ python-dotenv未安装，继续运行")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class DocumentItem(dict):
    """文档项模型 - 使用字典以简化"""
    def __init__(self, id: str, title: str, level: int = 1, type: str = "heading", parent_id: Optional[str] = None):
        super().__init__(
            id=id,
            title=title,
            level=level,
            type=type,
            parent_id=parent_id
        )

class DocumentListExtractor:
    """文档列表提取器"""
    
    def __init__(self):
        self.heading_patterns = [
            r'^([一二三四五六七八九十]+)[、．.]?\s*(.+)$',
            r'^(\d+(?:\.\d+)*)[、．.]?\s*(.+)$',
            r'^[（(]([一二三四五六七八九十]+)[）)]\s*(.+)$',
            r'^([A-Za-z]+)[、．.]?\s*(.+)$',
            r'^[（(](\d+)[）)]\s*(.+)$',
        ]
        logger.info("📋 文档列表提取器初始化完成")
    
    def extract_from_file_path(self, file_path: str) -> List[DocumentItem]:
        """从文件路径提取文档项列表"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext == '.doc':
            docx_path = self._convert_doc_to_docx(file_path)
            items = self._extract_from_docx(docx_path)
            # Clean up converted file
            if docx_path and os.path.exists(docx_path) and '_converted' in docx_path:
                os.remove(docx_path)
            return items
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def _convert_doc_to_docx(self, doc_path: str) -> str:
        """将.doc文件转换为.docx文件"""
        logger.info("🔄 开始DOC到DOCX转换...")
        
        # Create a temporary path for the converted file
        temp_dir = tempfile.gettempdir()
        base_name = Path(doc_path).stem
        docx_path = os.path.join(temp_dir, f"{base_name}_converted.docx")

        try:
            libreoffice_paths = [
                '/Applications/LibreOffice.app/Contents/MacOS/soffice',
                'libreoffice',
                'soffice',
            ]
            
            libreoffice_cmd = None
            for path in libreoffice_paths:
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        libreoffice_cmd = path
                        break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if not libreoffice_cmd:
                raise RuntimeError("LibreOffice未安装或不可用")
            
            if os.path.exists(docx_path):
                os.remove(docx_path)
            
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'docx',
                '--outdir', os.path.dirname(docx_path),
                doc_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                error_message = result.stderr or result.stdout
                raise RuntimeError(f"LibreOffice转换失败: {error_message}")
            
            # The output file will be in the same directory as the docx_path with .docx extension
            expected_docx_name = f"{Path(doc_path).stem}.docx"
            created_file_path = os.path.join(os.path.dirname(docx_path), expected_docx_name)

            if os.path.exists(created_file_path):
                # Move to the final desired path
                os.rename(created_file_path, docx_path)
                logger.info(f"✅ 转换成功: {docx_path}")
                return docx_path
            else:
                raise FileNotFoundError(f"转换后的文件未找到: {created_file_path}")
                
        except Exception as e:
            logger.error(f"❌ 转换过程中出错: {e}")
            raise RuntimeError(f"文件转换失败: {str(e)}")
    
    def _extract_from_docx(self, docx_path: str) -> List[DocumentItem]:
        """从docx文件提取文档项列表"""
        logger.info(f"📄 开始从docx文件提取文档项: {Path(docx_path).name}")
        
        try:
            doc = Document(docx_path)
            items = []
            item_counter = 0
            
            # 提取段落标题
            for para in doc.paragraphs:
                if para.text.strip():
                    item = self._process_paragraph(para, item_counter)
                    if item:
                        items.append(item)
                        item_counter += 1
            
            # 提取表格标题和内容
            for table_idx, table in enumerate(doc.tables):
                table_items = self._process_table(table, item_counter, table_idx)
                items.extend(table_items)
                item_counter += len(table_items)
            
            logger.info(f"✅ 成功提取 {len(items)} 个文档项")
            return items
            
        except Exception as e:
            logger.error(f"❌ 提取文档项失败: {e}")
            raise RuntimeError(f"文档解析失败: {str(e)}")
    
    def _process_paragraph(self, para, counter: int) -> Optional[DocumentItem]:
        """处理段落，识别标题和重要内容"""
        text = para.text.strip()
        if not text or len(text) < 2:
            return None
        
        style_name = para.style.name if para.style else ""
        is_heading = False
        level = 1
        
        # 检查标题样式
        if "Heading" in style_name or "标题" in style_name:
            is_heading = True
            level_match = re.search(r'(\d+)', style_name)
            if level_match:
                level = int(level_match.group(1))
        
        # 检查格式（加粗等）
        if para.runs:
            first_run = para.runs[0]
            if first_run.bold:
                is_heading = True
        
        # 通过文本模式识别编号标题
        title_info = self._extract_title_info(text)
        if title_info:
            is_heading = True
            level = title_info['level']
            text = title_info['title']
        
        # 过滤不重要的内容
        if not is_heading and len(text) < 5:
            return None
        
        if self._is_header_footer(text):
            return None
        
        return DocumentItem(
            id=str(counter + 1),
            title=text[:100],
            level=level,
            type="heading" if is_heading else "paragraph"
        )
    
    def _process_table(self, table, start_counter: int, table_idx: int) -> List[DocumentItem]:
        """处理表格，提取表格标题和重要行"""
        items = []
        counter = start_counter
        
        table_title = f"表格 {table_idx + 1}"
        
        if table.rows and table.rows[0].cells:
            first_row_text = " | ".join([cell.text.strip() for cell in table.rows[0].cells if cell.text.strip()])
            if first_row_text and len(first_row_text) > 5:
                table_title = first_row_text[:50] + "..." if len(first_row_text) > 50 else first_row_text
        
        items.append(
            DocumentItem(
                id=str(start_counter + len(items) + 1),
                title=f"表格 {table_idx + 1}",
                level=2,  # Example level for a table
                type="table"
            )
        )
        for row in table.rows:
            row_text = " | ".join([cell.text.strip() for cell in row.cells])
            if self._is_important_table_row(row_text):
                items.append(
                    DocumentItem(
                        id=str(start_counter + len(items) + 1),
                        title=row_text,
                        level=3,  # Example level for a row
                        type="table_row"
                    )
                )
        return items
    
    def _extract_title_info(self, text: str) -> Optional[Dict[str, Any]]:
        """提取标题信息（编号和级别）"""
        for pattern in self.heading_patterns:
            match = re.match(pattern, text.strip())
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    number_part = groups[0]
                    title_part = groups[1].strip()
                    level = self._calculate_level(number_part)
                    
                    return {
                        'number': number_part,
                        'title': title_part,
                        'level': level
                    }
        return None
    
    def _calculate_level(self, number_part: str) -> int:
        """根据编号计算层级"""
        if '.' in number_part:
            return len(number_part.split('.'))
        
        chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        if any(cn in number_part for cn in chinese_numbers):
            return 1
        
        if number_part.isdigit():
            num = int(number_part)
            if num <= 10:
                return 1
            elif num <= 100:
                return 2
            else:
                return 3
        
        return 1
    
    def _is_header_footer(self, text: str) -> bool:
        """判断是否为页眉页脚"""
        patterns = [
            r'第\s*\d+\s*页',
            r'共\s*\d+\s*页',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'^页\s*\d+',
            r'^\s*\d+\s*$',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return len(text) < 3 or text.isdigit()
    
    def _is_important_table_row(self, row_text: str) -> bool:
        """判断表格行是否重要"""
        if not row_text or len(row_text.strip()) < 5:
            return False
        
        keywords = [
            '小计', '合计', '总计', '汇总',
            '项目', '工程', '施工', '建设',
            '标准', '规范', '要求', '规定',
            '计划', '方案', '设计', '图纸',
            '质量', '安全', '进度', '费用'
        ]
        
        return any(keyword in row_text for keyword in keywords)

def run_get_list(file_path: str) -> List[Dict[str, Any]]:
    """
    AI tool to extract a structured list of items from a document (.doc or .docx).
    
    This function analyzes the document's structure, identifying headings, paragraphs, 
    and tables to create a hierarchical list of its contents.

    Args:
        file_path: The path to the document file.

    Returns:
        A list of dictionaries, where each dictionary represents an item in the document.
    """
    logger.info(f"🚀 Starting document list extraction for: {file_path}")
    
    try:
        extractor = DocumentListExtractor()
        items = extractor.extract_from_file_path(file_path)
        
        # Convert DocumentItem objects to plain dicts for the final output
        result_list = [dict(item) for item in items]
        
        logger.info(f"✅ Successfully extracted {len(result_list)} items from the document.")
        return result_list

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logger.error(f"❌ Processing failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during list extraction: {e}")
        logger.error(traceback.format_exc())
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract a structured list of items from a .doc or .docx file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file_path", help="Path to the document file.")
    parser.add_argument("--output-json", help="Optional. Path to save the output as a JSON file.", default=None)

    args = parser.parse_args()

    print("=" * 70)
    print("📄 Document List Extractor")
    print("=" * 70)
    print(f"▶️  Processing file: {args.file_path}")
    print("-" * 70)

    try:
        extracted_items = run_get_list(args.file_path)
        
        print(f"✅ Success! Extracted {len(extracted_items)} items.")

        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(extracted_items, f, ensure_ascii=False, indent=2)
            print(f"✅ Output saved to: {args.output_json}")
        else:
            print("\nExtracted Items:")
            for item in extracted_items:
                indent = "  " * (item.get('level', 1) - 1)
                print(f"{indent}- {item.get('title')}")
                
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        traceback.print_exc()

    print("=" * 70)
    print("✅ Process finished.")
    print("=" * 70) 