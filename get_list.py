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
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

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

class DocumentItem:
    """文档项模型"""
    def __init__(self, id: str, title: str, level: int = 1, type: str = "heading", parent_id: Optional[str] = None):
        self.id = id
        self.title = title
        self.level = level
        self.type = type
        self.parent_id = parent_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "type": self.type,
            "parent_id": self.parent_id
        }

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
            return self._extract_from_docx(docx_path)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def _convert_doc_to_docx(self, doc_path: str) -> str:
        """将.doc文件转换为.docx文件"""
        logger.info("🔄 开始DOC到DOCX转换...")
        
        docx_path = doc_path.replace('.doc', '_converted.docx')
        
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
                '--outdir', os.path.dirname(doc_path),
                doc_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"LibreOffice转换失败")
            
            expected_docx = doc_path.replace('.doc', '.docx')
            if os.path.exists(expected_docx):
                if expected_docx != docx_path:
                    os.rename(expected_docx, docx_path)
                logger.info(f"✅ 转换成功: {docx_path}")
                return docx_path
            else:
                raise RuntimeError("转换后的文件未找到")
                
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
            logger.error(f"❌ 从docx文件提取失败: {e}")
            raise RuntimeError(f"文档内容提取失败: {str(e)}")
    
    def _process_paragraph(self, para, counter: int) -> Optional[DocumentItem]:
        """处理段落，提取标题信息"""
        text = para.text.strip()
        
        # 过滤页眉页脚等无关内容
        if self._is_header_footer(text):
            return None
        
        # 尝试匹配标题模式
        title_info = self._extract_title_info(text)
        if title_info:
            return DocumentItem(
                id=f"item_{counter}",
                title=title_info['title'],
                level=title_info['level'],
                type="heading"
            )
        
        # 如果是重要段落但不是标题，也包含进来
        if len(text) > 10 and len(text) < 200:
            return DocumentItem(
                id=f"item_{counter}",
                title=text,
                level=3,
                type="paragraph"
            )
        
        return None
    
    def _process_table(self, table, start_counter: int, table_idx: int) -> List[DocumentItem]:
        """处理表格，提取重要行"""
        items = []
        counter = start_counter
        
        for row_idx, row in enumerate(table.rows):
            row_text = " | ".join([cell.text.strip() for cell in row.cells])
            
            if self._is_important_table_row(row_text):
                items.append(DocumentItem(
                    id=f"table_{table_idx}_row_{row_idx}",
                    title=row_text,
                    level=2,
                    type="table_row",
                    parent_id=f"table_{table_idx}"
                ))
                counter += 1
        
        if items:
            # 添加表格标题
            table_title = DocumentItem(
                id=f"table_{table_idx}",
                title=f"表格 {table_idx + 1}",
                level=1,
                type="table"
            )
            return [table_title] + items
        
        return []
    
    def _extract_title_info(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取标题信息"""
        for pattern in self.heading_patterns:
            match = re.match(pattern, text)
            if match:
                number_part = match.group(1)
                title_part = match.group(2).strip()
                level = self._calculate_level(number_part)
                
                return {
                    'title': f"{number_part}. {title_part}",
                    'level': level,
                    'number': number_part
                }
        
        return None
    
    def _calculate_level(self, number_part: str) -> int:
        """根据编号计算层级"""
        if re.match(r'^\d+$', number_part):
            return 1
        elif re.match(r'^\d+\.\d+$', number_part):
            return 2
        elif re.match(r'^\d+\.\d+\.\d+$', number_part):
            return 3
        elif number_part in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
            return 1
        elif re.match(r'^[A-Za-z]$', number_part):
            return 2
        else:
            return 2
    
    def _is_header_footer(self, text: str) -> bool:
        """判断是否为页眉页脚"""
        header_footer_patterns = [
            r'第\s*\d+\s*页',
            r'共\s*\d+\s*页',
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'^页码',
            r'^第.*章$',
        ]
        
        for pattern in header_footer_patterns:
            if re.search(pattern, text):
                return True
        
        return len(text) < 5 or len(text) > 300
    
    def _is_important_table_row(self, row_text: str) -> bool:
        """判断表格行是否重要"""
        if not row_text.strip() or len(row_text) < 5:
            return False
        
        # 过滤明显的表头或分隔行
        if re.match(r'^[\s\-\|]+$', row_text):
            return False
        
        # 包含重要关键词的行
        important_keywords = ['项目', '内容', '要求', '标准', '规范', '方案', '措施']
        for keyword in important_keywords:
            if keyword in row_text:
                return True
        
        return len(row_text) > 10 and len(row_text) < 200

def extract_document_list(file_path: str) -> List[Dict[str, Any]]:
    """
    AI tool to extract a structured list of items from Word documents (.doc/.docx).
    
    This function processes Word documents and extracts headings, paragraphs, and table
    content to create a structured list suitable for dashboard display or further processing.

    Args:
        file_path: Path to the Word document file (.doc or .docx)

    Returns:
        A list of dictionaries containing document items with id, title, level, type, and parent_id
    """
    logger.info(f"🚀 Starting document list extraction from: {file_path}")
    
    try:
        extractor = DocumentListExtractor()
        items = extractor.extract_from_file_path(file_path)
        
        # Convert DocumentItem objects to dictionaries
        result = [item.to_dict() for item in items]
        
        logger.info(f"✅ Successfully extracted {len(result)} items from document")
        return result
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"❌ Invalid file format: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during extraction: {e}")
        logger.error(traceback.format_exc())
        raise RuntimeError(f"Document extraction failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract structured list from Word documents.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file_path", help="Path to the Word document file (.doc or .docx)")

    print("=" * 70)
    print("📋 Document List Extractor")
    print("=" * 70)

    args = parser.parse_args()

    print(f"\n▶️ Processing document:")
    print(f"   File: {args.file_path}")
    print("-" * 70)

    try:
        items = extract_document_list(args.file_path)
        
        print(f"\n✅ Successfully extracted {len(items)} items:")
        print("-" * 70)
        
        for i, item in enumerate(items, 1):
            indent = "  " * (item['level'] - 1)
            print(f"{i:2d}. {indent}[{item['type']}] {item['title']}")
        
        print(f"\n📊 Summary:")
        print(f"   Total items: {len(items)}")
        print(f"   Headings: {len([i for i in items if i['type'] == 'heading'])}")
        print(f"   Paragraphs: {len([i for i in items if i['type'] == 'paragraph'])}")
        print(f"   Tables: {len([i for i in items if i['type'] == 'table'])}")
        print(f"   Table rows: {len([i for i in items if i['type'] == 'table_row'])}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found.")
        print(f"   Details: {e}")
    except ValueError as e:
        print(f"\n❌ Error: Invalid file format.")
        print(f"   Details: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred.")
        traceback.print_exc()
    
    print("=" * 70)
    print("✅ Process finished.")
    print("=" * 70) 