#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试PDF文件用于演示比较功能
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os

def create_sample_pdf1():
    """创建第一个示例PDF"""
    filename = "sample_document_v1.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    
    # 添加标题
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Sample Document - Version 1")
    
    # 添加内容
    c.setFont("Helvetica", 12)
    y_pos = 700
    
    content = [
        "This is a sample PDF document for testing comparison tools.",
        "",
        "Contents:",
        "1. Introduction to PDF comparison",
        "2. Text-based differences",
        "3. Formatting changes",
        "4. Structural modifications",
        "",
        "Introduction:",
        "PDF comparison is essential for document version control.",
        "It helps identify changes between different versions of files.",
        "",
        "Key Benefits:",
        "- Track document revisions",
        "- Ensure accuracy in updates", 
        "- Maintain document integrity",
        "",
        "This document serves as version 1 for comparison testing."
    ]
    
    for line in content:
        c.drawString(100, y_pos, line)
        y_pos -= 20
    
    # 添加页脚
    c.setFont("Helvetica", 10)
    c.drawString(100, 50, "Document Version: 1.0 | Created: 2024-12-02")
    
    c.save()
    print(f"✅ 创建了 {filename}")
    return filename

def create_sample_pdf2():
    """创建第二个示例PDF（有修改）"""
    filename = "sample_document_v2.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    
    # 添加标题（稍有不同）
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Sample Document - Version 2 (Updated)")
    
    # 添加内容（有修改）
    c.setFont("Helvetica", 12)
    y_pos = 700
    
    content = [
        "This is a sample PDF document for testing comparison tools.",
        "",
        "Contents:",
        "1. Introduction to PDF comparison",
        "2. Text-based differences", 
        "3. Formatting changes",
        "4. Structural modifications",
        "5. New section added",  # 新增内容
        "",
        "Introduction:",
        "PDF comparison is essential for document version control and quality assurance.",  # 修改的行
        "It helps identify changes between different versions of files.",
        "",
        "Key Benefits:",
        "- Track document revisions systematically",  # 修改的行
        "- Ensure accuracy in updates",
        "- Maintain document integrity",
        "- Improve collaboration workflow",  # 新增行
        "",
        "New Features:",  # 新增段落
        "- Enhanced comparison algorithms",
        "- Better visualization of differences",
        "",
        "This document serves as version 2 for comparison testing."
    ]
    
    for line in content:
        c.drawString(100, y_pos, line)
        y_pos -= 20
    
    # 添加页脚（更新版本）
    c.setFont("Helvetica", 10)
    c.drawString(100, 50, "Document Version: 2.0 | Updated: 2024-12-02 | Status: Revised")
    
    c.save()
    print(f"✅ 创建了 {filename}")
    return filename

def create_sample_pdf3():
    """创建第三个示例PDF（视觉差异）"""
    filename = "sample_document_visual_diff.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    
    # 不同的布局和格式
    c.setFont("Helvetica-Bold", 18)  # 更大的字体
    c.drawString(150, 750, "Sample Document - Visual Variant")  # 不同位置
    
    # 添加边框
    c.rect(80, 600, 450, 120, stroke=1, fill=0)
    
    # 内容在框内
    c.setFont("Helvetica", 11)
    y_pos = 680
    
    content = [
        "This document demonstrates visual differences:",
        "• Different font sizes and positions",
        "• Added graphical elements (borders)", 
        "• Modified layout structure",
    ]
    
    for line in content:
        c.drawString(100, y_pos, line)
        y_pos -= 25
    
    # 添加一些图形元素
    c.circle(400, 400, 50, stroke=1, fill=0)
    c.drawString(375, 395, "Circle")
    
    # 不同的页脚位置
    c.setFont("Helvetica", 10)
    c.drawString(200, 100, "Version: Visual Diff | Layout: Modified")
    
    c.save()
    print(f"✅ 创建了 {filename}")
    return filename

def main():
    """创建所有测试PDF文件"""
    print("创建测试PDF文件...")
    
    try:
        pdf1 = create_sample_pdf1()
        pdf2 = create_sample_pdf2() 
        pdf3 = create_sample_pdf3()
        
        print(f"\n🎉 成功创建了3个测试PDF文件:")
        print(f"  📄 {pdf1} - 基础版本")
        print(f"  📄 {pdf2} - 文本修改版本") 
        print(f"  📄 {pdf3} - 视觉差异版本")
        
        print(f"\n使用示例:")
        print(f"  python simple_pdf_compare.py {pdf1} {pdf2}")
        print(f"  python simple_pdf_compare.py {pdf1} {pdf3}")
        
        return [pdf1, pdf2, pdf3]
        
    except Exception as e:
        print(f"❌ 创建PDF失败: {e}")
        print("请确保安装了reportlab: pip install reportlab")
        return None

if __name__ == "__main__":
    main()