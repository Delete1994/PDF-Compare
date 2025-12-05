#!/usr/bin/env python3
"""
PDF比较工具 - 依赖包安装脚本

自动检测并安装所需的依赖包，并检查系统依赖（如poppler）。
"""

import subprocess
import sys
import os

def check_package(package_name):
    """检查Python包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装Python包"""
    print(f"正在安装 {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package_name} 安装失败")
        return False

def check_poppler():
    """检查poppler是否可用"""
    try:
        # 尝试导入pdf2image并测试poppler
        import pdf2image
        # 尝试查找poppler
        result = subprocess.run(
            ["where" if os.name == "nt" else "which", "pdftoppm"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, None
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("📦 PDF比较工具 - 依赖包安装检查")
    print("=" * 70)
    print()
    
    # 定义依赖包
    required_packages = {
        'PyMuPDF': 'fitz',  # 包名: 导入名
        'pdfplumber': 'pdfplumber',
        'pdf2image': 'pdf2image',
        'Pillow': 'PIL',
        'numpy': 'numpy'
    }
    
    # 检查并安装Python包
    print("🔍 检查Python依赖包...")
    print()
    
    missing_packages = []
    installed_packages = []
    
    for package_name, import_name in required_packages.items():
        status = check_package(import_name)
        if status:
            print(f"✅ {package_name:15} 已安装")
            installed_packages.append(package_name)
        else:
            print(f"❌ {package_name:15} 未安装")
            missing_packages.append(package_name)
    
    print()
    
    # 安装缺失的包
    if missing_packages:
        print(f"📥 发现 {len(missing_packages)} 个缺失的包，开始安装...")
        print()
        
        for package in missing_packages:
            install_package(package)
        
        print()
        print("=" * 70)
        print("✅ Python依赖包安装完成")
        print("=" * 70)
    else:
        print("✅ 所有Python依赖包都已安装")
    
    print()
    
    # 检查poppler
    print("🔍 检查系统依赖 (poppler)...")
    print()
    
    poppler_available, poppler_path = check_poppler()
    
    if poppler_available:
        print(f"✅ poppler 已安装")
        print(f"   路径: {poppler_path}")
    else:
        print("⚠️  poppler 未安装")
        print()
        print("   视觉比较功能需要poppler支持。安装方法:")
        print()
        if os.name == "nt":  # Windows
            print("   Windows:")
            print("   1. 使用conda: conda install -c conda-forge poppler")
            print("   2. 手动安装:")
            print("      - 访问: https://github.com/oschwartz10612/poppler-windows/releases")
            print("      - 下载并解压")
            print("      - 将bin目录添加到PATH环境变量")
        else:
            print("   Linux: sudo apt-get install poppler-utils")
            print("   macOS: brew install poppler")
    
    print()
    print("=" * 70)
    print("📊 功能可用性总结")
    print("=" * 70)
    print()
    
    # 功能可用性检查
    features = {
        "✅ 文本比较": check_package('fitz'),
        "✅ 结构分析": check_package('pdfplumber'),
        "✅ 元数据比较": check_package('fitz'),
        f"{'✅' if poppler_available else '❌'} 视觉比较": check_package('pdf2image') and poppler_available
    }
    
    for feature, available in features.items():
        status = "可用" if available else "不可用"
        print(f"{feature:20} - {status}")
    
    print()
    
    # 显示可用功能数量
    available_count = sum(1 for v in features.values() if v)
    total_count = len(features)
    
    if available_count == total_count:
        print(f"🎉 恭喜！所有功能 ({total_count}/{total_count}) 都可用")
    else:
        print(f"⚠️  {available_count}/{total_count} 个功能可用")
        if not poppler_available:
            print("   提示: 安装poppler可启用视觉比较功能")
    
    print()
    print("=" * 70)
    print("📖 使用说明")
    print("=" * 70)
    print()
    print("基本用法:")
    print("  python pdf_comparer.py file1.pdf file2.pdf")
    print()
    print("查看所有选项:")
    print("  python pdf_comparer.py --help")
    print()
    print("生成HTML报告:")
    print("  python pdf_comparer.py file1.pdf file2.pdf --html report.html")
    print()
    print("=" * 70)
    
    return 0 if available_count == total_count else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
