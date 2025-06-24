#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模板插入服务的示例脚本
演示如何调用insert_temp API端点
"""

import requests
import json
import os
from pathlib import Path

# API服务地址
API_BASE_URL = "http://localhost:8001"

def test_insert_template_api():
    """测试模板插入API"""
    print("🧪 开始测试模板插入API")
    print("=" * 50)
    
    # 1. 创建测试用的模板JSON
    template_json = {
        "章节一": "工程概述",
        "章节二": "施工进度计划", 
        "章节三": "质量控制措施",
        "章节四": "安全管理方案",
        "章节五": "环保措施",
        "章节六": "总结与建议"
    }
    
    # 2. 创建测试用的原始文档（如果不存在）
    original_file_path = "test_original.txt"
    if not os.path.exists(original_file_path):
        create_test_original_document(original_file_path)
    
    # 3. 准备API请求数据
    request_data = {
        "template_json": template_json,
        "original_file_path": original_file_path
    }
    
    print("📋 请求数据:")
    print(f"   模板章节: {list(template_json.keys())}")
    print(f"   原始文档: {original_file_path}")
    print()
    
    try:
        # 4. 发送API请求
        print("🌐 发送API请求...")
        response = requests.post(
            f"{API_BASE_URL}/insert_temp",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60秒超时
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功!")
            print(f"   生成文档路径: {result['final_doc_path']}")
            print(f"   处理状态: {result['success']}")
            print(f"   消息: {result['message']}")
            
            # 检查生成的文档是否存在
            if os.path.exists(result['final_doc_path']):
                file_size = os.path.getsize(result['final_doc_path'])
                print(f"   文档大小: {file_size} 字节")
                print("📄 文档生成成功!")
            else:
                print("⚠️ 警告: 生成的文档文件不存在")
                
        else:
            print(f"❌ API调用失败!")
            print(f"   状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        print("请确保模板插入服务正在运行 (python insert_template.py)")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def create_test_original_document(file_path: str):
    """创建测试用的原始文档"""
    print(f"📝 创建测试原始文档: {file_path}")
    
    content = """
建筑工程项目报告

项目名称：AI智能办公楼建设项目
项目地址：北京市朝阳区科技园区
建设单位：科技发展有限公司
设计单位：建筑设计院
监理单位：工程监理公司

工程概况：
本项目为一栋12层的智能办公楼，总建筑面积约15000平方米。
采用框架结构，地下1层，地上12层。
项目预算总投资8000万元，计划工期18个月。

施工进度安排：
第一阶段（1-3个月）：基础工程施工
- 土方开挖及基坑支护
- 基础混凝土浇筑
- 地下室结构施工

第二阶段（4-12个月）：主体结构施工
- 框架结构施工
- 楼板混凝土浇筑
- 外墙装饰施工

第三阶段（13-18个月）：装修及设备安装
- 内部装修工程
- 机电设备安装
- 智能化系统集成

质量管理：
严格按照国家建筑工程质量验收标准执行。
建立三级质量检查制度。
关键工序实行样板引路制度。

安全管理：
制定完善的安全生产管理制度。
定期开展安全教育培训。
配备专职安全员进行现场监督。

环保措施：
施工现场实行封闭管理。
设置车辆冲洗设施。
采用低噪音施工工艺。
建筑垃圾分类处理。

技术创新：
采用BIM技术进行施工管理。
使用预制装配式构件。
应用绿色建筑技术。

项目团队：
项目经理：张工程师
技术负责人：李工程师  
质量负责人：王工程师
安全负责人：赵工程师

总结：
本项目将严格按照设计要求和施工规范执行，
确保工程质量，按期完成建设任务，
为业主提供高质量的建筑产品。
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    
    print(f"✅ 测试文档创建完成，大小: {len(content)} 字符")

def test_api_health():
    """测试API健康状态"""
    print("🏥 检查API服务健康状态...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ API服务运行正常")
            print(f"   服务: {result.get('service', 'N/A')}")
            print(f"   状态: {result.get('status', 'N/A')}")
        else:
            print(f"⚠️ API服务响应异常: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ 无法连接到API服务")
        print("请先启动模板插入服务: python insert_template.py")
        return False
    
    return True

def show_api_info():
    """显示API信息"""
    print("📖 获取API信息...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("📋 API服务信息:")
            print(f"   名称: {result.get('message', 'N/A')}")
            print(f"   版本: {result.get('version', 'N/A')}")
            print(f"   描述: {result.get('description', 'N/A')}")
            print("   可用端点:")
            endpoints = result.get('endpoints', {})
            for endpoint, desc in endpoints.items():
                print(f"     - {endpoint}: {desc}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取API信息失败: {e}")

def main():
    """主函数"""
    print("🚀 模板插入服务测试工具")
    print("=" * 60)
    
    # 1. 检查API服务状态
    if not test_api_health():
        return
    
    print()
    
    # 2. 显示API信息
    show_api_info()
    
    print()
    
    # 3. 运行主要测试
    test_insert_template_api()
    
    print()
    print("🎯 测试完成!")
    print(f"📖 查看API文档: {API_BASE_URL}/docs")

if __name__ == "__main__":
    main() 