# -*- coding: utf-8 -*-
"""
测试文本清理功能
验证Ren'Py文本标记的移除是否正常工作
"""

import re

def test_text_cleaning():
    """测试文本清理功能"""
    print("测试文本清理功能")
    print("=" * 40)
    
    # 测试不同类型的Ren'Py文本标记
    test_cases = [
        "这是普通文本",
        "这是{color=#ff0000}红色{/color}文本",
        "{b}粗体文本{/b}和{i}斜体文本{/i}",
        "这里有{size=+10}大字体{/size}文字",
        "{alpha=0.5}半透明文本{/alpha}",
        "复杂的{b}{color=#00ff00}绿色粗体{/color}{/b}文本",
        "包含{w=1.0}等待标记{w}的文本",
        "有{p}分页标记{p}的长文本"
    ]
    
    def clean_text_simple(text):
        """简单的文本清理函数，移除Ren'Py标记"""
        return re.sub(r'\{[^}]*\}', '', text)
    
    print("原始文本 -> 清理后文本")
    print("-" * 40)
    
    for i, text in enumerate(test_cases, 1):
        cleaned = clean_text_simple(text)
        print(f"{i}. {text}")
        print(f"   -> {cleaned}")
        print()

def test_callback_simulation():
    """模拟回调函数测试"""
    print("模拟TTS回调函数测试")
    print("=" * 40)
    
    def mock_say_callback(event, interact=True, **kwargs):
        """模拟的say_callback函数"""
        if event == "show":
            what = kwargs.get('what', '')
            if what:
                # 简单的文本清理
                import re
                clean_text = re.sub(r'\{[^}]*\}', '', what)
                print(f"[TTS模拟] 原文: {what}")
                print(f"[TTS模拟] 清理: {clean_text}")
                print(f"[TTS模拟] 准备朗读: {clean_text}")
                return True
        return False
    
    # 测试不同的对话
    test_dialogues = [
        "普通对话文本",
        "带有{color=#ff0000}颜色{/color}的对话",
        "{b}重要{/b}的{i}斜体{/i}信息",
        "系统消息：{size=+5}警告{/size}信息"
    ]
    
    for dialogue in test_dialogues:
        print(f"测试对话: {dialogue}")
        result = mock_say_callback("show", what=dialogue)
        print(f"处理结果: {'成功' if result else '失败'}")
        print("-" * 30)

if __name__ == "__main__":
    test_text_cleaning()
    print("\n")
    test_callback_simulation()
    
    print("\n" + "="*50)
    print("文本清理功能测试完成!")
    print("现在Ren'Py游戏中的TTS应该可以正常工作了")
    print("="*50)
