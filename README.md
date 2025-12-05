# PDF比较工具 - 统一完整版

一个功能强大的PDF文件比较工具，支持多种比较方式和输出格式。

## 🌟 主要特性

- ✅ **文本内容比较** - 精确到页码和行号的文本差异检测
- ✅ **视觉外观比较** - 像素级的视觉差异检测（需要poppler）
- ✅ **结构分析比较** - 页数、表格等文档结构对比
- ✅ **元数据比较** - 文件属性和元信息对比
- ✅ **多种输出格式** - 命令行、HTML报告、JSON数据
- ✅ **智能检测** - 自动检测并使用可用的比较功能
- ✅ **详细定位** - 显示每个差异的具体页码、行号和上下文
- ✅ **灵活参数** - 通过命令行参数选择不同的比较方式

## 📦 安装依赖

### 基础功能（文本比较）
```bash
pip install PyMuPDF
```

### 完整功能（所有比较方式）
```bash
pip install PyMuPDF pdfplumber pdf2image Pillow numpy
```

### 视觉比较还需要安装poppler
**Windows:**
```bash
# 方法1: 使用conda
conda install -c conda-forge poppler

# 方法2: 手动安装
# 访问 https://github.com/oschwartz10612/poppler-windows/releases
# 下载并解压，将bin目录添加到PATH
```

**Linux:**
```bash
sudo apt-get install poppler-utils  # Ubuntu/Debian
```

**macOS:**
```bash
brew install poppler
```

### 一键安装脚本
```bash
python install_dependencies.py
```

## 🚀 快速开始

### 基本用法
```bash
# 快速文本比较
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf

# 显示详细差异位置
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf --detailed

# 使用所有可用的比较方法
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf --all
```

### 生成报告
```bash
# 生成HTML报告
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf --html report.html

# 保存JSON结果
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf --json result.json

# 同时生成HTML和JSON
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf --all --html report.html --json result.json
```

### 选择比较方法
```bash
# 只进行文本比较
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf -m text

# 文本和元数据比较
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf -m text metadata

# 视觉比较（需要poppler）
python pdf_comparer.py sample_document_v1.pdf sample_document_visual_diff.pdf -m visual

# 完整比较（结构、元数据、文本）
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf -m text structure metadata
```

## 📖 命令行参数

```
位置参数:
  pdf1                  第一个PDF文件路径
  pdf2                  第二个PDF文件路径

可选参数:
  -h, --help            显示帮助信息
  -m, --methods {text,visual,structure,metadata}
                        指定比较方法（可多选）
  --all                 使用所有可用的比较方法
  --detailed            显示详细的差异位置信息
  --html FILE           生成HTML报告到指定文件
  --json FILE           保存JSON结果到指定文件
  --dpi DPI             视觉比较的DPI（默认150）
  -q, --quiet           安静模式（减少输出）
```

## 💻 Python API使用

```python
from pdf_comparer import PDFComparer

# 创建比较器
comparer = PDFComparer(verbose=True)

# 执行比较
results = comparer.comprehensive_compare(
    'sample_document_v1.pdf', 
    'sample_document_v2.pdf',
    methods=['text_comparison', 'metadata_comparison']
)

# 打印结果
comparer.print_results(results, detailed=True)

# 生成报告
comparer.generate_html_report(results, 'report.html')
comparer.save_json(results, 'result.json')
```

### 单独使用各比较方法

```python
from pdf_comparer import PDFComparer

comparer = PDFComparer()

# 文本比较
text_result = comparer.compare_text('sample_document_v1.pdf', 'sample_document_v2.pdf', detailed=True)

# 获取详细差异位置
if 'detailed_differences' in text_result:
    for diff in text_result['detailed_differences']:
        print(f"{diff['type']}: 页{diff['page']} 行{diff['line']}")
        print(f"内容: {diff['content']}")
        print(f"上下文: {diff['context']}")

# 视觉比较
visual_result = comparer.compare_visual('sample_document_v1.pdf', 'sample_document_visual_diff.pdf', dpi=200)

# 结构分析
structure_result = comparer.compare_structure('sample_document_v1.pdf', 'sample_document_v2.pdf')

# 元数据比较
metadata_result = comparer.compare_metadata('sample_document_v1.pdf', 'sample_document_v2.pdf')
```

## 📊 输出示例

### 命令行输出
```
======================================================================
📊 PDF比较结果
======================================================================

📁 文件大小: ❌
   PDF1: 2,043 字节
   PDF2: 2,215 字节

📄 页面数量: ✅
   PDF1: 1 页
   PDF2: 1 页

📝 文本内容: ❌ 不同
   相似度: 83.15%
   添加行: 10
   删除行: 5
   总变化: 15

   📍 差异位置 (显示前10个):
   1. [删除] PDF1 页1 行1: Sample Document - Version 1
   2. [添加] PDF2 页1 行1: Sample Document - Version 2 (Updated)
   3. [添加] PDF2 页1 行8: 5. New section added
   ...

======================================================================
📋 结论: PDF文件存在差异
✅ 通过检查: 2/3
======================================================================
```

### JSON输出结构
```json
{
  "files": {
    "pdf1": "sample_document_v1.pdf",
    "pdf2": "sample_document_v2.pdf"
  },
  "timestamp": "2025-12-05T14:30:00",
  "methods_used": ["text_comparison", "metadata_comparison"],
  "results": {
    "text_comparison": {
      "identical": false,
      "similarity": 0.8315,
      "statistics": {
        "lines_added": 10,
        "lines_removed": 5,
        "total_changes": 15
      },
      "detailed_differences": [
        {
          "type": "removed",
          "content": "Sample Document - Version 1",
          "page": 1,
          "line": 1,
          "file": "pdf1"
        }
      ]
    }
  },
  "summary": {
    "overall_identical": false,
    "checks_passed": 2,
    "checks_total": 3
  }
}
```

## 🎨 HTML报告特性

生成的HTML报告包含：
- 🎨 **现代化设计** - 渐变色标题、响应式布局
- 📊 **可视化指标** - 直观的数据展示卡片
- 📋 **详细表格** - 每个差异的完整位置信息
- 🔴🟢 **颜色区分** - 红色标记删除、绿色标记添加
- 📱 **响应式** - 适配不同屏幕尺寸

## 🔧 功能对比

| 比较方法 | 功能说明 | 依赖包 | 应用场景 |
|---------|---------|-------|---------|
| **文本比较** | 提取并对比文本内容，精确到行级 | PyMuPDF | 文档内容变更检测、版本控制 |
| **视觉比较** | 像素级图像对比 | pdf2image, numpy, poppler | 布局变化、图形元素检测 |
| **结构分析** | 页数、表格等结构元素对比 | pdfplumber | 文档结构完整性检查 |
| **元数据比较** | 文件属性、作者、创建时间等 | PyMuPDF | 文件来源和完整性验证 |

## 📁 项目文件结构

```
SpecCompare/
├── pdf_comparer.py           # 统一完整版工具（主文件）
├── install_dependencies.py   # 依赖安装脚本
├── create_test_pdfs.py       # 创建测试PDF文件
├── README.md                 # 本文档
├── sample_document_v1.pdf    # 测试文件1
├── sample_document_v2.pdf    # 测试文件2
└── sample_document_visual_diff.pdf  # 视觉差异测试文件
```

## 🎯 使用场景

1. **文档版本控制** - 追踪文档修改历史
2. **合同审查** - 对比合同不同版本的变化
3. **质量保证** - 验证PDF生成过程的一致性
4. **合规检查** - 确保文档未被篡改
5. **批量比较** - 自动化处理大量PDF文件
6. **报告审核** - 检查报告更新内容

## 💡 高级技巧

### 批量比较
```python
from pdf_comparer import PDFComparer
import os

comparer = PDFComparer(verbose=False)
base_file = "base.pdf"

for filename in os.listdir('.'):
    if filename.endswith('.pdf') and filename != base_file:
        results = comparer.comprehensive_compare(base_file, filename)
        if not results['summary']['overall_identical']:
            print(f"差异文件: {filename}")
            comparer.generate_html_report(results, f"{filename}_report.html")
```

### 筛选特定页的差异
```python
results = comparer.compare_text('sample_document_v1.pdf', 'sample_document_v2.pdf', detailed=True)

if 'detailed_differences' in results['results']['text_comparison']:
    diffs = results['results']['text_comparison']['detailed_differences']
    
    # 只看第5页的差异
    page5_diffs = [d for d in diffs if d['page'] == 5]
    print(f"第5页有 {len(page5_diffs)} 处差异")
```

### 自定义相似度阈值
```python
results = comparer.compare_text('sample_document_v1.pdf', 'sample_document_v2.pdf')
similarity = results.get('similarity', 0)

if similarity > 0.95:
    print("文档几乎相同")
elif similarity > 0.80:
    print("文档有轻微差异")
else:
    print("文档差异较大")
```

## 🐛 故障排除

### 问题：视觉比较不可用
**解决方案：**
1. 确保已安装 `pdf2image`: `pip install pdf2image`
2. 安装poppler（见上面的安装说明）
3. 运行 `python install_dependencies.py` 检查依赖状态

### 问题：中文显示乱码
**解决方案：**
- 确保PDF文件包含嵌入字体
- 使用支持中文的PDF阅读器查看结果
- HTML报告已设置UTF-8编码，应该正确显示

### 问题：大文件比较很慢
**解决方案：**
1. 降低视觉比较的DPI: `--dpi 100`
2. 只使用必要的比较方法: `-m text metadata`
3. 使用安静模式减少输出: `--quiet`

## 📝 退出代码

- `0` - 文件完全相同
- `1` - 发生错误
- `2` - 文件存在差异

可用于脚本自动化：
```bash
python pdf_comparer.py sample_document_v1.pdf sample_document_v2.pdf
if [ $? -eq 0 ]; then
    echo "文件相同"
else
    echo "文件不同或出错"
fi
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- PyMuPDF: https://pymupdf.readthedocs.io/
- pdfplumber: https://github.com/jsvine/pdfplumber
- pdf2image: https://github.com/Belval/pdf2image
- poppler: https://poppler.freedesktop.org/

---

**版本**: 3.0 - 统一完整版  
**更新日期**: 2025-12-05  
**作者**: PDF Compare Tool Team