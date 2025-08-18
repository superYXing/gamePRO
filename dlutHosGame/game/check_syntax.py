#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ren'Py语法验证脚本
检查脚本文件的语法是否正确
"""

import os
import re

def check_renpy_syntax():
    """检查Ren'Py脚本语法"""
    
    print("=== Ren'Py 语法检查 ===")
    
    files_to_check = [
        "game/script.rpy",
        "game/day1.rpy"
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            continue
            
        print(f"\n🔍 检查文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # 检查常见语法问题
        issues = []
        
        for i, line in enumerate(lines, 1):
            # 检查独立的try/except语句
            if re.match(r'^\s*try\s*:', line) and not re.search(r'python:', ''.join(lines[max(0,i-5):i])):
                issues.append(f"第{i}行: try语句需要在python代码块中")
            
            if re.match(r'^\s*except\s+', line) and not re.search(r'python:', ''.join(lines[max(0,i-5):i])):
                issues.append(f"第{i}行: except语句需要在python代码块中")
            
            # 检查独立的return语句
            if re.match(r'^\s*return\s*$', line):
                # 检查是否在label内
                in_label = False
                for j in range(max(0, i-10), i):
                    if re.match(r'^\s*label\s+', lines[j]):
                        in_label = True
                        break
                if not in_label:
                    issues.append(f"第{i}行: return语句必须在label内")
        
        if issues:
            print("❌ 发现语法问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 语法检查通过")

if __name__ == "__main__":
    check_renpy_syntax()
