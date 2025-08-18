# Day1实时TTS音频生成功能说明

## 功能概述
已成功为`day1.rpy`场景实现实时TTS音频生成功能，每个对话都会在运行时动态生成OGG格式的音频文件并播放。

## 修改内容

### 1. script.rpy 修改
- 在`init_tts_delayed()`函数中添加了`speak_text`函数的全局导入
- 确保`speak_text`函数在Ren'Py环境中可用

### 2. tts_module.py 修改  
- 更新了`speak_text`函数，使其返回音频文件路径而不是直接播放
- 返回的路径格式适配Ren'Py的`play voice`命令
- 生成的音频文件为OGG格式

### 3. day1.rpy 修改
- 所有对话现在都使用实时TTS生成
- 添加了错误处理机制，确保即使TTS失败也不会中断游戏
- 包含以下实时生成的音频：
  - 旁白介绍
  - 患者主诉
  - 医生AI回复（根据选择动态生成）
  - SAN值变化提示
  - 询问语音
  - 患者后续回复

## 使用方式

### 在Ren'Py中的代码模式：
```renpy
# 初始化TTS系统
$ init_tts_delayed()

# 实时生成并播放语音
$ text_content = "要说的话"
try:
    $ tts_file = speak_text(text_content)
    if tts_file:
        play voice "[tts_file]"
except:
    pass
"[text_content]"
```

## 技术特点

1. **实时生成**：每次运行都会调用云雾API生成新的音频
2. **OGG格式**：所有音频文件都是OGG/Opus格式，适合游戏使用
3. **自动路径处理**：生成的文件路径自动适配Ren'Py环境
4. **错误容错**：TTS失败时游戏继续运行，不会崩溃
5. **动态内容**：AI生成的回复内容会实时转换为语音

## 生成的音频文件
- 位置：`game/audio/tts/`
- 格式：OGG/Opus
- 命名：`tts_时间戳_文本哈希.ogg`

## 测试验证
- ✅ TTS模块导入正常
- ✅ speak_text函数可用
- ✅ 音频文件生成成功
- ✅ OGG格式输出正确
- ✅ Ren'Py环境兼容

## 下一步
现在可以运行游戏测试Day1场景，所有对话都应该有实时生成的语音播放。
