#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的模板插入服务 v2.0
演示新的模块化架构和多种输入方式
"""

import requests
import json
import os
from pathlib import Path

# API服务地址
API_BASE_URL = "http://localhost:8001"

def test_file_path_mode():
    """测试文件路径模式（向后兼容）"""
    print("🧪 测试1: 文件路径模式（向后兼容）")
    print("=" * 50)
    
    # 创建测试用的模板JSON
    template_json = {
        "项目概述": "工程基本信息和背景介绍",
        "技术方案": "详细的技术实施方案和方法",
        "进度安排": "项目时间计划和里程碑",
        "质量保证": "质量控制措施和标准",
        "总结建议": "项目总结和后续建议"
    }
    
    # 创建测试文档
    original_file_path = "test_original_v2.txt"
    if not os.path.exists(original_file_path):
        create_comprehensive_test_document(original_file_path)
    
    # 准备API请求数据
    request_data = {
        "template_json": template_json,
        "original_file_path": original_file_path
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/insert_temp",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 文件路径模式测试成功!")
            print(f"   生成文档: {result['final_doc_path']}")
            print(f"   处理详情: {result.get('processing_details', {})}")
            return result['final_doc_path']
        else:
            print(f"❌ 测试失败! 状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_file_upload_mode():
    """测试文件上传模式（新功能）"""
    print("\n🧪 测试2: 文件上传模式（推荐方式）")
    print("=" * 50)
    
    # 模板JSON
    template_json = {
        "工程概述": "项目基本情况和目标",
        "设计方案": "详细设计方案和原理",
        "施工计划": "施工步骤和时间安排",
        "安全措施": "安全管理和风险控制",
        "验收标准": "项目验收标准和流程"
    }
    
    # 创建测试文档
    test_file_path = "test_upload_document.txt"
    create_comprehensive_test_document(test_file_path)
    
    try:
        # 准备文件上传
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            data = {'template_json': json.dumps(template_json, ensure_ascii=False)}
            
            response = requests.post(
                f"{API_BASE_URL}/insert_temp_upload",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 文件上传模式测试成功!")
            print(f"   生成文档: {result['final_doc_path']}")
            print(f"   原始文件名: {result.get('processing_details', {}).get('original_filename')}")
            print(f"   内容摘要: {result.get('processing_details', {}).get('content_summary')}")
            return result['final_doc_path']
        else:
            print(f"❌ 测试失败! 状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_error_handling():
    """测试错误处理机制"""
    print("\n🧪 测试3: 错误处理机制")
    print("=" * 50)
    
    # 测试无效JSON
    print("📋 测试无效JSON格式...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/insert_temp_upload",
            files={'file': ('test.txt', b'test content', 'text/plain')},
            data={'template_json': 'invalid json'},
            timeout=10
        )
        print(f"   状态码: {response.status_code} ({'✅ 正确' if response.status_code == 400 else '❌ 错误'})")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 测试空模板JSON
    print("📋 测试空模板JSON...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/insert_temp_upload",
            files={'file': ('test.txt', b'test content', 'text/plain')},
            data={'template_json': '{}'},
            timeout=10
        )
        print(f"   状态码: {response.status_code} ({'✅ 正确' if response.status_code == 400 else '❌ 错误'})")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 测试不存在的文件路径
    print("📋 测试不存在的文件路径...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/insert_temp",
            json={
                "template_json": {"test": "test"},
                "original_file_path": "/nonexistent/file.txt"
            },
            timeout=10
        )
        print(f"   状态码: {response.status_code} ({'✅ 正确' if response.status_code == 404 else '❌ 错误'})")
    except Exception as e:
        print(f"   异常: {e}")

def test_download_functionality(file_path: str):
    """测试文件下载功能"""
    if not file_path:
        print("\n⚠️ 跳过下载测试 - 没有生成的文件")
        return
    
    print("\n🧪 测试4: 文件下载功能")
    print("=" * 50)
    
    filename = Path(file_path).name
    
    try:
        response = requests.get(f"{API_BASE_URL}/download/{filename}", timeout=10)
        
        if response.status_code == 200:
            print("✅ 文件下载测试成功!")
            print(f"   文件大小: {len(response.content)} 字节")
            print(f"   内容类型: {response.headers.get('content-type')}")
        else:
            print(f"❌ 下载失败! 状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 下载请求失败: {e}")

def test_service_info():
    """测试服务信息获取"""
    print("\n🧪 测试5: 服务信息获取")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            info = response.json()
            print("✅ 服务信息获取成功!")
            print(f"   版本: {info.get('version')}")
            print(f"   AI模型: {info.get('ai_model')}")
            print("   主要特性:")
            for feature in info.get('features', []):
                print(f"     - {feature}")
            print("   支持的格式:")
            formats = info.get('supported_formats', {})
            print(f"     输入: {formats.get('input', [])}")
            print(f"     输出: {formats.get('output', [])}")
        else:
            print(f"❌ 获取服务信息失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def create_comprehensive_test_document(file_path: str):
    """创建更全面的测试文档"""
    print(f"📝 创建测试文档: {file_path}")
    
    content = """
智慧城市物联网平台建设项目技术方案

项目背景：
随着城市化进程的加快，传统城市管理方式已无法满足现代化管理需求。
本项目旨在构建一个全面的智慧城市物联网平台，整合各类城市资源，
提升城市管理效率和市民生活质量。

技术架构：
1. 感知层：部署各类传感器和IoT设备
   - 环境监测传感器（PM2.5、噪音、温湿度等）
   - 交通流量监测设备
   - 市政设施状态监测器
   - 视频监控系统

2. 网络层：构建高可靠通信网络
   - 5G无线通信网络
   - 光纤骨干网络
   - LoRaWAN物联网专网
   - 边缘计算节点

3. 平台层：核心数据处理平台
   - 大数据处理引擎（Hadoop、Spark）
   - 实时流处理系统（Kafka、Storm）
   - 人工智能分析平台（TensorFlow、PyTorch）
   - 区块链数据安全保障

4. 应用层：各类智慧应用
   - 智慧交通管理系统
   - 环境质量监测预警
   - 公共安全应急响应
   - 市政设施智能运维

实施计划：
第一阶段（6个月）：基础设施建设
- 完成核心机房建设
- 部署基础网络设施
- 安装重点区域传感器设备
- 搭建数据处理平台

第二阶段（9个月）：系统集成开发
- 开发核心业务应用
- 完成系统集成测试
- 建立运维管理体系
- 培训技术运维人员

第三阶段（3个月）：试运行优化
- 开展系统试运行
- 收集用户反馈意见
- 优化系统性能表现
- 完善安全防护机制

质量保证措施：
1. 技术质量保证
   - 采用业界成熟技术标准
   - 建立代码审查机制
   - 实施全面测试策略
   - 建立技术文档体系

2. 项目质量管理
   - 严格按照PMBOK标准执行
   - 建立质量检查点制度
   - 定期开展项目评审
   - 持续改进项目流程

3. 数据安全保障
   - 实施多层次安全防护
   - 建立数据备份机制
   - 加强访问权限控制
   - 定期安全风险评估

预期效果：
通过本项目的实施，预期能够实现：
- 城市管理效率提升30%以上
- 环境监测精度提高50%
- 交通拥堵情况改善20%
- 公共安全响应时间缩短40%
- 市政设施故障预警准确率达到95%

项目团队：
项目经理：张华（PMP认证，10年项目管理经验）
技术总监：李明（架构师，15年技术研发经验）
AI算法专家：王芳（博士，专注机器学习5年）
网络工程师：赵军（CCIE认证，8年网络建设经验）
测试经理：陈丽（ISTQB认证，6年测试管理经验）

总投资：8500万元人民币
建设周期：18个月
维护期：5年

本项目将为城市数字化转型奠定坚实基础，
为建设现代化智慧城市贡献重要力量。
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    
    print(f"✅ 测试文档创建完成，大小: {len(content)} 字符")

def main():
    """主函数"""
    print("🚀 模板插入服务 v2.0 综合测试")
    print("=" * 60)
    
    # 检查服务状态
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务未正常运行")
            print("请确保:")
            print("1. 配置了.env文件或环境变量 OPENROUTER_API_KEY")
            print("2. 启动服务: python insert_template.py")
            return
    except:
        print("❌ 无法连接到服务")
        print("请确保:")
        print("1. 配置了.env文件或环境变量 OPENROUTER_API_KEY")
        print("2. 启动服务: python insert_template.py")
        return
    
    print("✅ 服务连接正常，开始测试...\n")
    
    # 运行各项测试
    generated_file1 = test_file_path_mode()
    generated_file2 = test_file_upload_mode()
    test_error_handling()
    test_download_functionality(generated_file1 or generated_file2)
    test_service_info()
    
    print("\n" + "=" * 60)
    print("🎯 测试完成!")
    print(f"📖 查看API文档: {API_BASE_URL}/docs")
    print("📊 主要改进:")
    print("   ✅ 模块化架构 - 提取器、合并器、生成器分离")
    print("   ✅ 多种输入方式 - 文件路径 + 文件上传")
    print("   ✅ 精确异常处理 - 400/422/404/500状态码")
    print("   ✅ 详细处理信息 - 生成统计和验证结果")
    print("   ✅ 文件下载支持 - 便于分布式部署")

if __name__ == "__main__":
    main() 