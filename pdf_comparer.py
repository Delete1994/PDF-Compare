#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF比较工具 - 统一完整版
整合所有功能，支持命令行参数选择不同比较模式

功能特性:
- 文本内容比较（精确到页码和行号）
- 视觉外观比较（需要poppler）
- 结构分析比较
- 元数据比较
- 多种输出格式（命令行/HTML/JSON）
- 自动检测可用功能
- 批量比较支持

作者: PDF Compare Tool
版本: 3.0 - 统一完整版
日期: 2025-12-05
"""

import os
import sys
import json
import argparse
import difflib
import hashlib
import subprocess
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pdf2image import convert_from_path
    import numpy as np
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


class PDFComparer:
    """统一的PDF比较器 - 集成所有功能"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.capabilities = self._check_capabilities()
    
    def _check_capabilities(self) -> Dict[str, bool]:
        """检查系统可用功能"""
        caps = {
            'text_comparison': HAS_PYMUPDF,
            'visual_comparison': HAS_PDF2IMAGE and self._check_poppler(),
            'structure_analysis': HAS_PDFPLUMBER,
            'metadata_comparison': HAS_PYMUPDF,
        }
        
        if self.verbose:
            print("🔍 系统功能检测:")
            for feature, available in caps.items():
                status = "✅" if available else "❌"
                print(f"  {status} {feature}")
        
        return caps
    
    def _check_poppler(self) -> bool:
        """检查poppler是否可用"""
        try:
            subprocess.run(['pdftoppm', '-h'], 
                          capture_output=True, 
                          timeout=5)
            return True
        except:
            return False
    
    # ==================== 文本比较 ====================
    
    def compare_text(self, pdf1_path: str, pdf2_path: str, 
                    detailed: bool = True) -> Dict:
        """
        文本内容比较
        
        Args:
            pdf1_path: PDF文件1路径
            pdf2_path: PDF文件2路径
            detailed: 是否包含详细位置信息
        
        Returns:
            比较结果字典
        """
        if not self.capabilities['text_comparison']:
            return {'error': '文本比较功能不可用，需要安装PyMuPDF'}
        
        if self.verbose:
            print("📝 正在进行文本比较...")
        
        try:
            # 按页提取文本
            pages1 = self._extract_text_by_page(pdf1_path)
            pages2 = self._extract_text_by_page(pdf2_path)
            
            text1 = '\n'.join(pages1)
            text2 = '\n'.join(pages2)
            
            # 基本比较
            lines1 = text1.splitlines()
            lines2 = text2.splitlines()
            
            diff_lines = list(difflib.unified_diff(
                lines1, lines2,
                fromfile=os.path.basename(pdf1_path),
                tofile=os.path.basename(pdf2_path),
                lineterm=''
            ))
            
            # 统计
            added = len([l for l in diff_lines if l.startswith('+') and not l.startswith('+++')])
            removed = len([l for l in diff_lines if l.startswith('-') and not l.startswith('---')])
            similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
            
            result = {
                'method': 'text_comparison',
                'identical': text1 == text2,
                'similarity': similarity,
                'statistics': {
                    'lines_added': added,
                    'lines_removed': removed,
                    'total_changes': added + removed,
                    'char_count1': len(text1),
                    'char_count2': len(text2),
                    'line_count1': len(lines1),
                    'line_count2': len(lines2),
                }
            }
            
            # 详细位置信息
            if detailed and diff_lines:
                result['detailed_differences'] = self._extract_detailed_positions(
                    diff_lines, lines1, lines2, pages1, pages2
                )
            else:
                result['diff_preview'] = diff_lines[:20]
            
            return result
            
        except Exception as e:
            return {'error': f'文本比较失败: {str(e)}'}
    
    def _extract_text_by_page(self, pdf_path: str) -> List[str]:
        """按页提取PDF文本"""
        doc = fitz.open(pdf_path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return pages
    
    def _extract_detailed_positions(self, diff_lines: List[str], 
                                   lines1: List[str], lines2: List[str],
                                   pages1: List[str], pages2: List[str]) -> List[Dict]:
        """提取差异的详细位置信息"""
        differences = []
        current_line1 = 0
        current_line2 = 0
        
        import re
        for line in diff_lines:
            if line.startswith('@@'):
                match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if match:
                    current_line1 = int(match.group(1)) - 1
                    current_line2 = int(match.group(3)) - 1
                continue
            
            if line.startswith('---') or line.startswith('+++'):
                continue
            
            if line.startswith('-'):
                page_num, line_in_page = self._find_page_for_line(current_line1, pages1)
                differences.append({
                    'type': 'removed',
                    'content': line[1:],
                    'page': page_num,
                    'line': current_line1 + 1,
                    'line_in_page': line_in_page,
                    'file': 'pdf1',
                    'context': self._get_context(lines1, current_line1)
                })
                current_line1 += 1
            
            elif line.startswith('+'):
                page_num, line_in_page = self._find_page_for_line(current_line2, pages2)
                differences.append({
                    'type': 'added',
                    'content': line[1:],
                    'page': page_num,
                    'line': current_line2 + 1,
                    'line_in_page': line_in_page,
                    'file': 'pdf2',
                    'context': self._get_context(lines2, current_line2)
                })
                current_line2 += 1
            
            else:
                current_line1 += 1
                current_line2 += 1
        
        return differences
    
    def _find_page_for_line(self, line_num: int, pages: List[str]) -> Tuple[int, int]:
        """找到行号所在的页码和页内行号"""
        current_line = 0
        for page_idx, page_text in enumerate(pages):
            page_lines = page_text.splitlines()
            if current_line + len(page_lines) >= line_num:
                return (page_idx + 1, line_num - current_line)
            current_line += len(page_lines)
        return (len(pages), 0)
    
    def _get_context(self, lines: List[str], line_num: int, 
                    context_size: int = 2) -> Dict:
        """获取上下文"""
        return {
            'before': lines[max(0, line_num - context_size):line_num],
            'after': lines[line_num + 1:min(len(lines), line_num + 1 + context_size)]
        }
    
    # ==================== 视觉比较 ====================
    
    def compare_visual(self, pdf1_path: str, pdf2_path: str, 
                      dpi: int = 150) -> Dict:
        """
        视觉外观比较
        
        Args:
            pdf1_path: PDF文件1路径
            pdf2_path: PDF文件2路径
            dpi: 转换图像的DPI（越高越精确但越慢）
        
        Returns:
            比较结果字典
        """
        if not self.capabilities['visual_comparison']:
            return {'error': '视觉比较不可用，需要安装pdf2image和poppler'}
        
        if self.verbose:
            print(f"🖼️  正在进行视觉比较 (DPI={dpi})...")
        
        try:
            images1 = convert_from_path(pdf1_path, dpi=dpi)
            images2 = convert_from_path(pdf2_path, dpi=dpi)
            
            if len(images1) != len(images2):
                return {
                    'method': 'visual_comparison',
                    'identical': False,
                    'error': f'页数不同: {len(images1)} vs {len(images2)}'
                }
            
            page_similarities = []
            for i, (img1, img2) in enumerate(zip(images1, images2)):
                if img1.size != img2.size:
                    img2 = img2.resize(img1.size)
                
                arr1 = np.array(img1)
                arr2 = np.array(img2)
                
                diff_pixels = np.count_nonzero(arr1 != arr2)
                total_pixels = arr1.size
                similarity = 1 - (diff_pixels / total_pixels)
                
                page_similarities.append({
                    'page': i + 1,
                    'similarity': similarity,
                    'different_pixels': diff_pixels,
                    'total_pixels': total_pixels
                })
            
            overall_similarity = sum(p['similarity'] for p in page_similarities) / len(page_similarities)
            
            return {
                'method': 'visual_comparison',
                'identical': overall_similarity > 0.999,
                'overall_similarity': overall_similarity,
                'page_count': len(images1),
                'page_similarities': page_similarities
            }
            
        except Exception as e:
            return {'error': f'视觉比较失败: {str(e)}'}
    
    # ==================== 结构分析 ====================
    
    def compare_structure(self, pdf1_path: str, pdf2_path: str) -> Dict:
        """
        结构比较（页数、表格等）
        
        Args:
            pdf1_path: PDF文件1路径
            pdf2_path: PDF文件2路径
        
        Returns:
            比较结果字典
        """
        if not self.capabilities['structure_analysis']:
            return {'error': '结构分析不可用，需要安装pdfplumber'}
        
        if self.verbose:
            print("📊 正在进行结构分析...")
        
        try:
            with pdfplumber.open(pdf1_path) as pdf1, pdfplumber.open(pdf2_path) as pdf2:
                result = {
                    'method': 'structure_comparison',
                    'page_count': {
                        'pdf1': len(pdf1.pages),
                        'pdf2': len(pdf2.pages),
                        'identical': len(pdf1.pages) == len(pdf2.pages)
                    }
                }
                
                # 表格分析
                tables_info = []
                max_pages = min(len(pdf1.pages), len(pdf2.pages))
                
                for i in range(max_pages):
                    tables1 = pdf1.pages[i].extract_tables()
                    tables2 = pdf2.pages[i].extract_tables()
                    
                    tables_info.append({
                        'page': i + 1,
                        'tables_pdf1': len(tables1) if tables1 else 0,
                        'tables_pdf2': len(tables2) if tables2 else 0,
                        'identical': len(tables1 or []) == len(tables2 or [])
                    })
                
                result['tables'] = tables_info
                result['identical'] = (
                    result['page_count']['identical'] and
                    all(t['identical'] for t in tables_info)
                )
                
                return result
                
        except Exception as e:
            return {'error': f'结构分析失败: {str(e)}'}
    
    # ==================== 元数据比较 ====================
    
    def compare_metadata(self, pdf1_path: str, pdf2_path: str) -> Dict:
        """
        元数据比较
        
        Args:
            pdf1_path: PDF文件1路径
            pdf2_path: PDF文件2路径
        
        Returns:
            比较结果字典
        """
        if not self.capabilities['metadata_comparison']:
            return {'error': '元数据比较不可用，需要安装PyMuPDF'}
        
        if self.verbose:
            print("🏷️  正在比较元数据...")
        
        try:
            doc1 = fitz.open(pdf1_path)
            doc2 = fitz.open(pdf2_path)
            
            # 文件哈希
            hash1 = self._calculate_hash(pdf1_path)
            hash2 = self._calculate_hash(pdf2_path)
            
            # 元数据
            metadata1 = doc1.metadata
            metadata2 = doc2.metadata
            
            metadata_comparison = {}
            all_keys = set(metadata1.keys()) | set(metadata2.keys())
            
            for key in all_keys:
                val1 = metadata1.get(key, '')
                val2 = metadata2.get(key, '')
                metadata_comparison[key] = {
                    'pdf1': val1,
                    'pdf2': val2,
                    'identical': val1 == val2
                }
            
            doc1.close()
            doc2.close()
            
            return {
                'method': 'metadata_comparison',
                'file_hash': {
                    'pdf1': hash1,
                    'pdf2': hash2,
                    'identical': hash1 == hash2
                },
                'metadata': metadata_comparison,
                'identical': all(m['identical'] for m in metadata_comparison.values())
            }
            
        except Exception as e:
            return {'error': f'元数据比较失败: {str(e)}'}
    
    def _calculate_hash(self, filepath: str) -> str:
        """计算文件哈希"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    # ==================== 基本信息比较 ====================
    
    def compare_basic_info(self, pdf1_path: str, pdf2_path: str) -> Dict:
        """基本信息比较（文件大小等）"""
        try:
            size1 = os.path.getsize(pdf1_path)
            size2 = os.path.getsize(pdf2_path)
            
            result = {
                'method': 'basic_info',
                'file_size': {
                    'pdf1': size1,
                    'pdf2': size2,
                    'identical': size1 == size2
                }
            }
            
            # 如果有PyMuPDF，添加页数信息
            if HAS_PYMUPDF:
                doc1 = fitz.open(pdf1_path)
                doc2 = fitz.open(pdf2_path)
                result['page_count'] = {
                    'pdf1': len(doc1),
                    'pdf2': len(doc2),
                    'identical': len(doc1) == len(doc2)
                }
                doc1.close()
                doc2.close()
            
            return result
            
        except Exception as e:
            return {'error': f'基本信息比较失败: {str(e)}'}
    
    # ==================== 综合比较 ====================
    
    def comprehensive_compare(self, pdf1_path: str, pdf2_path: str,
                            methods: Optional[List[str]] = None) -> Dict:
        """
        综合比较
        
        Args:
            pdf1_path: PDF文件1路径
            pdf2_path: PDF文件2路径
            methods: 要使用的方法列表，None表示使用所有可用方法
        
        Returns:
            完整的比较结果字典
        """
        if self.verbose:
            print("\n" + "=" * 70)
            print("🔍 开始综合PDF比较")
            print("=" * 70)
            print(f"文件1: {pdf1_path}")
            print(f"文件2: {pdf2_path}")
        
        # 检查文件存在
        if not os.path.exists(pdf1_path):
            return {'error': f'文件不存在: {pdf1_path}'}
        if not os.path.exists(pdf2_path):
            return {'error': f'文件不存在: {pdf2_path}'}
        
        # 确定要使用的方法
        if methods is None:
            methods = [k for k, v in self.capabilities.items() if v]
        
        if self.verbose:
            print(f"使用方法: {', '.join(methods)}\n")
        
        results = {
            'files': {
                'pdf1': pdf1_path,
                'pdf2': pdf2_path
            },
            'timestamp': datetime.now().isoformat(),
            'methods_used': methods,
            'results': {}
        }
        
        # 基本信息（总是执行）
        results['results']['basic_info'] = self.compare_basic_info(pdf1_path, pdf2_path)
        
        # 执行各种比较
        if 'text_comparison' in methods:
            results['results']['text_comparison'] = self.compare_text(pdf1_path, pdf2_path)
        
        if 'visual_comparison' in methods:
            results['results']['visual_comparison'] = self.compare_visual(pdf1_path, pdf2_path)
        
        if 'structure_analysis' in methods:
            results['results']['structure_analysis'] = self.compare_structure(pdf1_path, pdf2_path)
        
        if 'metadata_comparison' in methods:
            results['results']['metadata_comparison'] = self.compare_metadata(pdf1_path, pdf2_path)
        
        # 计算总体结果
        identical_checks = []
        for result in results['results'].values():
            if 'error' not in result and 'identical' in result:
                identical_checks.append(result['identical'])
        
        results['summary'] = {
            'overall_identical': all(identical_checks) if identical_checks else False,
            'checks_passed': sum(identical_checks) if identical_checks else 0,
            'checks_total': len(identical_checks),
            'has_errors': any('error' in r for r in results['results'].values())
        }
        
        return results
    
    # ==================== 输出格式化 ====================
    
    def print_results(self, results: Dict, detailed: bool = False):
        """打印比较结果到控制台"""
        print("\n" + "=" * 70)
        print("📊 PDF比较结果")
        print("=" * 70)
        
        if 'error' in results:
            print(f"❌ 错误: {results['error']}")
            return
        
        # 基本信息
        if 'basic_info' in results.get('results', {}):
            info = results['results']['basic_info']
            if 'file_size' in info:
                fs = info['file_size']
                status = "✅" if fs['identical'] else "❌"
                print(f"\n📁 文件大小: {status}")
                print(f"   PDF1: {fs['pdf1']:,} 字节")
                print(f"   PDF2: {fs['pdf2']:,} 字节")
            
            if 'page_count' in info:
                pc = info['page_count']
                status = "✅" if pc['identical'] else "❌"
                print(f"\n📄 页面数量: {status}")
                print(f"   PDF1: {pc['pdf1']} 页")
                print(f"   PDF2: {pc['pdf2']} 页")
        
        # 文本比较
        if 'text_comparison' in results.get('results', {}):
            text = results['results']['text_comparison']
            if 'error' not in text:
                status = "✅ 相同" if text['identical'] else "❌ 不同"
                print(f"\n📝 文本内容: {status}")
                
                if not text['identical']:
                    print(f"   相似度: {text['similarity']:.2%}")
                    stats = text['statistics']
                    print(f"   添加行: {stats['lines_added']}")
                    print(f"   删除行: {stats['lines_removed']}")
                    print(f"   总变化: {stats['total_changes']}")
                    
                    # 详细差异
                    if detailed and 'detailed_differences' in text:
                        diffs = text['detailed_differences']
                        print(f"\n   📍 差异位置 (显示前10个):")
                        for idx, diff in enumerate(diffs[:10], 1):
                            dtype = "删除" if diff['type'] == 'removed' else "添加"
                            file_label = "PDF1" if diff['file'] == 'pdf1' else "PDF2"
                            content = diff['content'][:60]
                            if len(diff['content']) > 60:
                                content += '...'
                            print(f"   {idx}. [{dtype}] {file_label} 页{diff['page']} 行{diff['line']}: {content}")
                        
                        if len(diffs) > 10:
                            print(f"   ... 还有 {len(diffs) - 10} 处差异")
        
        # 视觉比较
        if 'visual_comparison' in results.get('results', {}):
            visual = results['results']['visual_comparison']
            if 'error' not in visual:
                status = "✅ 相同" if visual['identical'] else "❌ 不同"
                print(f"\n🖼️  视觉外观: {status}")
                print(f"   相似度: {visual['overall_similarity']:.2%}")
                print(f"   页数: {visual['page_count']}")
        
        # 结构分析
        if 'structure_analysis' in results.get('results', {}):
            struct = results['results']['structure_analysis']
            if 'error' not in struct:
                status = "✅ 相同" if struct['identical'] else "❌ 不同"
                print(f"\n📊 文档结构: {status}")
        
        # 元数据
        if 'metadata_comparison' in results.get('results', {}):
            meta = results['results']['metadata_comparison']
            if 'error' not in meta:
                status = "✅ 相同" if meta['identical'] else "❌ 不同"
                print(f"\n🏷️  元数据: {status}")
                if 'file_hash' in meta:
                    hash_status = "✅" if meta['file_hash']['identical'] else "❌"
                    print(f"   文件哈希: {hash_status}")
        
        # 总结
        if 'summary' in results:
            summary = results['summary']
            print("\n" + "=" * 70)
            if summary['overall_identical']:
                print("🎉 结论: PDF文件完全相同")
            else:
                print("📋 结论: PDF文件存在差异")
            print(f"✅ 通过检查: {summary['checks_passed']}/{summary['checks_total']}")
            print("=" * 70)
    
    def generate_html_report(self, results: Dict, output_path: str):
        """生成HTML格式报告"""
        if 'error' in results:
            print(f"❌ 无法生成报告: {results['error']}")
            return
        
        html = self._build_html_report(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        if self.verbose:
            print(f"✅ HTML报告已生成: {output_path}")
    
    def _build_html_report(self, results: Dict) -> str:
        """构建HTML报告内容"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PDF比较报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0; opacity: 0.9; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; }
        .section h2 { margin-top: 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .status-same { color: #4caf50; font-weight: bold; }
        .status-diff { color: #f44336; font-weight: bold; }
        .status-error { color: #ff9800; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin-top: 15px; background: white; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #667eea; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr.removed { background-color: #ffebee; }
        tr.added { background-color: #e8f5e9; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; padding: 10px 15px; background: white; border-radius: 5px; border-left: 4px solid #667eea; }
        .metric-label { font-size: 0.9em; color: #666; }
        .metric-value { font-size: 1.5em; font-weight: bold; color: #333; }
        .summary { background: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 5px solid #2196f3; }
        .diff-context { font-size: 0.85em; color: #666; font-style: italic; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 PDF比较报告</h1>
            <p>生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>文件1: """ + results['files']['pdf1'] + """</p>
            <p>文件2: """ + results['files']['pdf2'] + """</p>
        </div>
"""
        
        # 添加各部分内容
        for method, result in results.get('results', {}).items():
            html += self._format_result_section(method, result)
        
        # 添加总结
        if 'summary' in results:
            summary = results['summary']
            html += """
        <div class="summary">
            <h2>📋 总结</h2>
"""
            if summary['overall_identical']:
                html += """            <p class="status-same">✅ 两个PDF文件完全相同</p>"""
            else:
                html += """            <p class="status-diff">❌ 两个PDF文件存在差异</p>"""
            
            html += f"""
            <div class="metric">
                <div class="metric-label">通过检查</div>
                <div class="metric-value">{summary['checks_passed']}/{summary['checks_total']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">使用方法</div>
                <div class="metric-value">{len(results['methods_used'])}</div>
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def _format_result_section(self, method: str, result: Dict) -> str:
        """格式化单个结果部分"""
        if 'error' in result:
            return f"""
        <div class="section">
            <h2>{method.replace('_', ' ').title()}</h2>
            <p class="status-error">⚠️ {result['error']}</p>
        </div>
"""
        
        title = method.replace('_', ' ').title()
        status_class = 'status-same' if result.get('identical', False) else 'status-diff'
        status_text = '✅ 相同' if result.get('identical', False) else '❌ 不同'
        
        html = f"""
        <div class="section">
            <h2>{title}</h2>
            <p class="{status_class}">{status_text}</p>
"""
        
        # 根据方法类型添加详细信息
        if method == 'text_comparison' and 'statistics' in result:
            stats = result['statistics']
            html += f"""
            <div class="metric">
                <div class="metric-label">相似度</div>
                <div class="metric-value">{result.get('similarity', 0):.1%}</div>
            </div>
            <div class="metric">
                <div class="metric-label">添加行数</div>
                <div class="metric-value">{stats['lines_added']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">删除行数</div>
                <div class="metric-value">{stats['lines_removed']}</div>
            </div>
"""
            
            # 添加详细差异表格
            if 'detailed_differences' in result:
                html += self._format_differences_table(result['detailed_differences'])
        
        elif method == 'visual_comparison' and 'overall_similarity' in result:
            html += f"""
            <div class="metric">
                <div class="metric-label">视觉相似度</div>
                <div class="metric-value">{result['overall_similarity']:.1%}</div>
            </div>
            <div class="metric">
                <div class="metric-label">页数</div>
                <div class="metric-value">{result['page_count']}</div>
            </div>
"""
        
        html += """
        </div>
"""
        return html
    
    def _format_differences_table(self, differences: List[Dict]) -> str:
        """格式化差异表格"""
        html = """
            <h3>详细差异位置</h3>
            <table>
                <tr>
                    <th>序号</th>
                    <th>类型</th>
                    <th>文件</th>
                    <th>页码</th>
                    <th>行号</th>
                    <th>内容</th>
                </tr>
"""
        
        for idx, diff in enumerate(differences[:50], 1):  # 限制50个
            row_class = 'removed' if diff['type'] == 'removed' else 'added'
            diff_type = '删除' if diff['type'] == 'removed' else '添加'
            content = diff['content'][:100]
            if len(diff['content']) > 100:
                content += '...'
            content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            html += f"""
                <tr class="{row_class}">
                    <td>{idx}</td>
                    <td><strong>{diff_type}</strong></td>
                    <td>{diff['file'].upper()}</td>
                    <td>{diff['page']}</td>
                    <td>{diff['line']}</td>
                    <td style="font-family: monospace;">{content}</td>
                </tr>
"""
        
        if len(differences) > 50:
            html += f"""
                <tr>
                    <td colspan="6" style="text-align: center; color: #999;">
                        还有 {len(differences) - 50} 处差异未显示
                    </td>
                </tr>
"""
        
        html += """
            </table>
"""
        return html
    
    def save_json(self, results: Dict, output_path: str):
        """保存JSON格式结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"✅ JSON结果已保存: {output_path}")


# ==================== 命令行接口 ====================

def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='PDF比较工具 - 统一完整版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速文本比较
  python pdf_comparer.py file1.pdf file2.pdf
  
  # 完整比较（所有方法）
  python pdf_comparer.py file1.pdf file2.pdf --all
  
  # 只进行文本和元数据比较
  python pdf_comparer.py file1.pdf file2.pdf -m text metadata
  
  # 生成HTML报告
  python pdf_comparer.py file1.pdf file2.pdf --html report.html
  
  # 保存JSON结果
  python pdf_comparer.py file1.pdf file2.pdf --json result.json
  
  # 详细模式（显示所有差异位置）
  python pdf_comparer.py file1.pdf file2.pdf --detailed
        """
    )
    
    parser.add_argument('pdf1', help='第一个PDF文件路径')
    parser.add_argument('pdf2', help='第二个PDF文件路径')
    
    parser.add_argument('-m', '--methods', nargs='+',
                       choices=['text', 'visual', 'structure', 'metadata'],
                       help='指定比较方法（可多选）')
    
    parser.add_argument('--all', action='store_true',
                       help='使用所有可用的比较方法')
    
    parser.add_argument('--detailed', action='store_true',
                       help='显示详细的差异位置信息')
    
    parser.add_argument('--html', metavar='FILE',
                       help='生成HTML报告到指定文件')
    
    parser.add_argument('--json', metavar='FILE',
                       help='保存JSON结果到指定文件')
    
    parser.add_argument('--dpi', type=int, default=150,
                       help='视觉比较的DPI（默认150）')
    
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='安静模式（减少输出）')
    
    args = parser.parse_args()
    
    # 创建比较器
    comparer = PDFComparer(verbose=not args.quiet)
    
    # 确定使用的方法
    methods = None
    if args.methods:
        method_map = {
            'text': 'text_comparison',
            'visual': 'visual_comparison',
            'structure': 'structure_analysis',
            'metadata': 'metadata_comparison'
        }
        methods = [method_map[m] for m in args.methods]
    elif args.all:
        methods = None  # 使用所有可用方法
    else:
        # 默认只使用文本比较
        methods = ['text_comparison'] if comparer.capabilities['text_comparison'] else None
    
    # 执行比较
    results = comparer.comprehensive_compare(args.pdf1, args.pdf2, methods)
    
    # 输出结果
    comparer.print_results(results, detailed=args.detailed)
    
    # 生成HTML报告
    if args.html:
        comparer.generate_html_report(results, args.html)
    
    # 保存JSON
    if args.json:
        comparer.save_json(results, args.json)
    
    # 返回退出码
    if 'error' in results:
        return 1
    elif results.get('summary', {}).get('overall_identical', False):
        return 0
    else:
        return 2


if __name__ == '__main__':
    sys.exit(main())
