#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查day1.rpy的Ren'Py语法
"""

import re
import os

def check_renpy_syntax(file_path):
    """检查Ren'Py文件的基本语法问题"""
    
    print(f"=== 检查文件: {file_path} ===")
    
    if not os.path.exists(file_path):
        print("✗ 文件不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # 检查是否有裸露的try/except语句（不在python块中）
        if re.match(r'^\s*try:', line) and not in_python_block(lines, i-1):
            issues.append(f"第{i}行: 'try:' 语句不在python块中")
        
        if re.match(r'^\s*except:', line) and not in_python_block(lines, i-1):
            issues.append(f"第{i}行: 'except:' 语句不在python块中")
    
    if issues:
        print("发现语法问题:")
        for issue in issues:
            print(f"  ✗ {issue}")
        return False
    else:
        print("✓ 未发现明显的语法问题")
        return True

def in_python_block(lines, line_index):
    """检查指定行是否在python块中"""
    # 向上查找最近的python块开始
    for i in range(line_index, -1, -1):
        stripped = lines[i].strip()
        if stripped == "python:" or stripped.startswith("python:"):
            return True
        if stripped.startswith("label ") or stripped.startswith("menu:"):
            return False
    return False

def check_day1_structure():
    """检查day1.rpy的整体结构"""
    file_path = "day1.rpy"
    
    print("\n=== 检查day1.rpy结构 ===")
    
    if not os.path.exists(file_path):
        print("✗ day1.rpy文件不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查基本标签
    if "label day1_start:" in content:
        print("✓ 找到day1_start标签")
    else:
        print("✗ 未找到day1_start标签")
        return False
    
    if "label day1_choice_result:" in content:
        print("✓ 找到day1_choice_result标签")
    else:
        print("✗ 未找到day1_choice_result标签")
        return False
    
    # 检查TTS调用
    tts_calls = content.count("play_tts(")
    print(f"✓ 找到{tts_calls}个TTS调用")
    
    # 检查是否还有裸露的try/except
    bare_try = re.findall(r'^\s*try:', content, re.MULTILINE)
    bare_except = re.findall(r'^\s*except:', content, re.MULTILINE)
    
    if bare_try or bare_except:
        print(f"⚠ 可能还有裸露的try/except语句: try={len(bare_try)}, except={len(bare_except)}")
    else:
        print("✓ 未发现裸露的try/except语句")
    
    return True

if __name__ == "__main__":
    print("Day1.rpy语法检查工具")
    print("=" * 50)
    
    # 检查语法
    syntax_ok = check_renpy_syntax("day1.rpy")
    
    # 检查结构
    structure_ok = check_day1_structure()
    
    print("\n" + "=" * 50)
    if syntax_ok and structure_ok:
        print("🎉 检查完成，文件应该可以正常运行！")
    else:
        print("❌ 发现问题，需要进一步修复")
    
    print("\n修复摘要:")
    print("- 将所有try/except语句移到python块中")
    print("- 创建了play_tts()简化函数")
    print("- 使用renpy.music.play()代替play voice命令")
    print("- 所有TTS调用现在使用$ play_tts(text)格式")
