#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for AI Document Processing MCP Server
"""

import os
import sys
import json
from pathlib import Path

def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing AI Document Processing MCP Server")
    print("=" * 50)
    
    try:
        # Set test mode
        os.environ["TEST_MODE"] = "true"
        
        # Import the server
        print("📦 Importing MCP server...")
        from mcp_server import insert_template, extract_document_list
        print("✅ MCP server imported successfully")
        
        # Test 1: Template insertion with sample data
        print("\n🔄 Testing template insertion...")
        
        # Create a sample template
        sample_template = {
            "项目概述": "项目的基本介绍和背景信息，包括项目目标、范围和重要性。",
            "技术方案": "详细的技术实施方案，包括技术选型、架构设计和实施步骤。",
            "实施计划": "项目实施的时间安排和里程碑，包括各阶段的任务分配。",
            "风险评估": "项目风险分析和应对措施，确保项目顺利进行。"
        }
        
        # Check if sample files exist
        sample_files = ["template_test.doc", "templates/template_test.doc"]
        sample_file = None
        
        for file_path in sample_files:
            if os.path.exists(file_path):
                sample_file = file_path
                break
        
        if sample_file:
            print(f"   Using sample file: {sample_file}")
            try:
                result_path = insert_template(sample_template, sample_file)
                print(f"✅ Template insertion successful!")
                print(f"   Generated file: {result_path}")
                
                if os.path.exists(result_path):
                    file_size = os.path.getsize(result_path)
                    print(f"   File size: {file_size} bytes")
                else:
                    print("⚠️ Generated file not found")
                    
            except Exception as e:
                print(f"❌ Template insertion failed: {e}")
        else:
            print("⚠️ No sample files found for template insertion test")
        
        # Test 2: Document list extraction
        print("\n📋 Testing document list extraction...")
        
        if sample_file:
            try:
                document_items = extract_document_list(sample_file)
                print(f"✅ Document list extraction successful!")
                print(f"   Extracted {len(document_items)} items")
                
                # Show sample items
                for i, item in enumerate(document_items[:3], 1):
                    print(f"   {i}. [{item['type']}] {item['title'][:50]}...")
                
                if len(document_items) > 3:
                    print(f"   ... and {len(document_items) - 3} more items")
                    
            except Exception as e:
                print(f"❌ Document list extraction failed: {e}")
        else:
            print("⚠️ No sample files found for document list extraction test")
        
        print("\n✅ MCP server tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

def check_sample_files():
    """Check for available sample files"""
    print("\n📁 Checking for sample files...")
    
    sample_locations = [
        "template_test.doc",
        "templates/template_test.doc", 
        "templates/template_test2.doc",
        "templates/1-04施工组织设计报审表（章）_doc_ca6e1ffa.doc"
    ]
    
    found_files = []
    for file_path in sample_locations:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            found_files.append((file_path, file_size))
            print(f"   ✅ {file_path} ({file_size} bytes)")
        else:
            print(f"   ❌ {file_path} (not found)")
    
    return found_files

if __name__ == "__main__":
    print("🤖 AI Document Processing MCP Server Test")
    print("=" * 60)
    
    # Check environment
    print("🔍 Checking environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Working directory: {os.getcwd()}")
    
    # Check sample files
    sample_files = check_sample_files()
    
    if not sample_files:
        print("\n⚠️ No sample files found!")
        print("   You can create sample files for testing or use existing documents.")
    
    # Run tests
    test_mcp_server()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!") 