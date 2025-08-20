# 游戏的脚本可置于此文件中。

# 图像定义
image room = "images/room.png"
image file = "images/file.png"

# TTS 初始化与回调函数定义 - 延迟初始化避免冲突
init python:
    import re
    import sys, os
    
    # TTS 配置（延迟初始化）
    TTS_ENABLED = False
    TTS_INITIALIZED = False
    
    # AI 配置
    ai_manager = None
    
    def init_tts_delayed():
        """延迟初始化TTS，在游戏完全启动后调用"""
        global TTS_ENABLED, TTS_INITIALIZED
        if TTS_INITIALIZED:
            return
        
        # 获取当前目录的 Ren'Py 兼容方法
        import renpy
        _current_dir = renpy.config.gamedir
        
        _python_packages_dir = os.path.join(_current_dir, 'python-packages')
        if os.path.exists(_python_packages_dir) and _python_packages_dir not in sys.path:
            sys.path.insert(0, _python_packages_dir)
        
        import tts_module
        # 从统一配置读取
        try:
            from config import config as game_config
            _api_key = game_config.api_key
            _base_url = game_config.base_url
            _model = game_config.tts_model
            _voice = game_config.tts_voice
        except Exception:
            _api_key = os.getenv("OPENAI_API_KEY", "")
            _base_url = os.getenv("OPENAI_BASE_URL", "https://yunwu.ai/v1")
            _model = os.getenv("OPENAI_TTS_MODEL", "tts-1")
            _voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
        
        tts_module.init_tts(api_key=_api_key, base_url=_base_url, model=_model, voice=_voice)
        
        # 传递 Ren'Py 上下文给 TTS 管理器
        import renpy
        if hasattr(tts_module, 'tts_manager') and tts_module.tts_manager:
            tts_module.tts_manager.set_renpy_context(renpy)
            print("[TTS配置] 已传递 Ren'Py 上下文给 TTS 管理器")
        
        print("[TTS配置] 初始化完成 (HTTP 模式)")
        
        # 初始化 AI 模块
        import ai_module
        ai_module.init_ai()
        # 将 ai_manager 添加到全局命名空间
        global ai_manager
        ai_manager = ai_module.ai_manager
        if ai_manager:
            print("[AI配置] AI 模块初始化完成")
        else:
            print("[AI配置] AI 模块初始化失败")
        
        TTS_ENABLED = True
        TTS_INITIALIZED = True
        
        # 测试 Ren'Py 音频系统
        test_renpy_audio()
        
        # 测试一个简单的 TTS 合成
        print("[TTS测试] 开始测试音频合成...")
        test_text = "TTS系统测试"
        if hasattr(tts_module, 'tts_manager') and tts_module.tts_manager:
            test_file = tts_module.tts_manager.synthesize_to_file(test_text)
            print(f"[TTS测试] 合成完成: {test_file}")
            # 立即尝试播放测试文件
            tts_module.tts_manager._play_audio(test_file)
            print("[TTS测试] 播放测试完成")
        
        TTS_ENABLED = True
        TTS_INITIALIZED = True
    
    def clean_text_simple(text):
        """安全的文本清理函数"""
        if not text:
            return ""
        # 移除 Ren'Py 的文本标记
        cleaned = re.sub(r'\{[^}]*\}', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
# 在 script.rpy 中，将 ToggleTTS 类改为简单函数
init python:
    def ToggleTTS():
        """切换TTS开关的简单函数"""
        global TTS_ENABLED
        TTS_ENABLED = not TTS_ENABLED
        if TTS_ENABLED:
            renpy.notify("TTS语音已启用")
        else:
            renpy.notify("TTS语音已禁用")
        return True
            
    def say_callback(event, interact=True, **kwargs):
        # 延迟初始化 TTS（首次调用时）
        if not globals().get('TTS_INITIALIZED', False):
            init_tts_delayed()
            
        # 当显示对话时触发TTS
        if event == "show":
            # 检查TTS是否启用
            if globals().get('TTS_ENABLED', False):
                import tts_module
                # 获取对话文本
                what = kwargs.get('what', '')
                if what:
                    # 使用安全的文本清理
                    clean_text = clean_text_simple(what)
                    
                    # 获取角色信息，用于确定语音特色
                    who = kwargs.get('who', '')
                    emotion = None
                    speed = 0.7
                    voice = None
                    
                    # 根据角色设置语音特色
                    if who == "艾琳" or who == "e":
                        voice = "nova"  # 活泼年轻女声
                        emotion = "happy"
                        speed = 0.7
                    else:
                        voice = "alloy"  # 默认中性
                    
                    # 分析对话内容，调整情感
                    if "！" in clean_text or "?" in clean_text:
                        emotion = "excited"
                        speed = min(speed * 1.2, 1.5)
                    elif "..." in clean_text or "……" in clean_text:
                        emotion = "whisper"
                        speed = max(speed * 0.8, 0.7)
                    
                    print(f"[TTS游戏] {who}: {clean_text} (情感:{emotion}, 语速:{speed}x, 语音:{voice})")
                    # 调用TTS API
                    tts_module.speak_text(clean_text, emotion=emotion, speed=speed, voice=voice)
                else:
                    print("[TTS游戏] 警告: 没有找到文本内容")
            else:
                print("[TTS游戏] TTS功能已禁用")
            
    def test_renpy_audio():
        """测试 Ren'Py 音频系统是否可用"""
        print("=== Ren'Py 音频系统检测 ===")
        
        # 检查音频系统是否可用
        import renpy
        print(f"  - renpy 模块: 可用")
        print(f"  - renpy.music: {hasattr(renpy, 'music')}")
        print(f"  - renpy.sound: {hasattr(renpy, 'sound')}")
        
        # 测试音频通道
        print("  - 可用音频通道:")
        channels = ["master", "music", "sound", "voice"]
        for ch in channels:
            if hasattr(renpy.audio, 'get_channel'):
                channel_obj = renpy.audio.get_channel(ch)
                print(f"    * {ch}: 可用")
            else:
                print(f"    * {ch}: 未知")
                
        print("=== 检测完成 ===")
    
   

# 声明此游戏使用的角色。颜色参数可使角色姓名着色。

define e = Character("艾琳")

# 游戏在此开始。

# 主游戏标签 - 跳转到day1
label start:

    # 播放医院背景音乐
    play music "audio/bgm/amb_hospital.ogg" loop  # TODO: 替换为实际的医院场景BGM
    # 显示游戏开始封面
    scene black with fade
    show room:
        size (config.screen_width, config.screen_height)  # 全屏显示
        pos (0, 0)
    with dissolve

    "欢迎来到《完美医生》"
    
    # 跳转到day1
    jump day1_start
    
    # 此处为游戏结尾
    return