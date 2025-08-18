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
        
        try:
            # 获取当前目录的 Ren'Py 兼容方法
            try:
                # 在 Ren'Py 环境中使用 config.gamedir
                import renpy
                _current_dir = renpy.config.gamedir
            except (ImportError, AttributeError):
                # 回退到当前工作目录
                _current_dir = os.getcwd()
            
            _python_packages_dir = os.path.join(_current_dir, 'python-packages')
            if os.path.exists(_python_packages_dir) and _python_packages_dir not in sys.path:
                sys.path.insert(0, _python_packages_dir)
            
            import tts_module
            # 明文配置（按需修改）
            API_KEY = "sk-0GszUjESD38HSUiSDFpMmRYHIeCdeunPhJ2eRLrwAT6pJZGJ"
            BASE_URL = "https://yunwu.ai/v1"
            MODEL = "tts-1"
            DEFAULT_VOICE = "alloy"
            
            tts_module.init_tts(api_key=API_KEY, base_url=BASE_URL, model=MODEL, voice=DEFAULT_VOICE)
            
            # 传递 Ren'Py 上下文给 TTS 管理器
            try:
                import renpy
                tts_module.tts_manager.set_renpy_context(renpy)
                print("[TTS配置] 已传递 Ren'Py 上下文给 TTS 管理器")
            except Exception:
                print(f"[TTS配置] 传递 Ren'Py 上下文失败")
            
            print("[TTS配置] 初始化完成 (HTTP 模式)")
            
            # 初始化 AI 模块
            try:
                import ai_module
                ai_module.init_ai()
                # 将 ai_manager 添加到全局命名空间
                global ai_manager
                ai_manager = ai_module.ai_manager
                if ai_manager:
                    print("[AI配置] AI 模块初始化完成")
                else:
                    print("[AI配置] AI 模块初始化失败")
            except Exception:
                print(f"[AI配置] AI 模块初始化出错")
                ai_manager = None
            
            TTS_ENABLED = True
            TTS_INITIALIZED = True
            
            # 测试 Ren'Py 音频系统
            test_renpy_audio()
            
            # 测试一个简单的 TTS 合成
            try:
                print("[TTS测试] 开始测试音频合成...")
                test_text = "TTS系统测试"
                test_file = tts_module.tts_manager.synthesize_to_file(test_text)
                print(f"[TTS测试] 合成完成: {test_file}")
                
                # 立即尝试播放测试文件
                tts_module.tts_manager._play_audio(test_file)
                print("[TTS测试] 播放测试完成")
            except Exception:
                print(f"[TTS测试] 测试失败")
            
            TTS_ENABLED = True
            TTS_INITIALIZED = True
        except Exception:
            print(f"[TTS配置] 初始化失败")
            TTS_ENABLED = False
            TTS_INITIALIZED = True
    
    def clean_text_simple(text):
        """安全的文本清理函数"""
        if not text:
            return ""
        # 移除 Ren'Py 的文本标记
        cleaned = re.sub(r'\{[^}]*\}', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def test_renpy_audio():
        """测试 Ren'Py 音频系统是否可用"""
        try:
            import renpy
            print(f"=== Ren'Py 音频系统检测 ===")
            print(f"  - renpy.sound 可用: {hasattr(renpy, 'sound')}")
            print(f"  - renpy.music 可用: {hasattr(renpy, 'music')}")
            if hasattr(renpy, 'sound'):
                print(f"  - renpy.sound.play 可用: {hasattr(renpy.sound, 'play')}")
            if hasattr(renpy, 'music'):
                print(f"  - renpy.music.play 可用: {hasattr(renpy.music, 'play')}")
            print(f"  - 游戏基础目录: {renpy.config.basedir}")
            print(f"  - 游戏目录: {renpy.config.gamedir}")
        except Exception:
            print(f"[音频检测] 发生错误")

# TTS 控制动作
init python:
    class ToggleTTS(renpy.Action):
        """切换TTS开关状态的动作类"""
        
        def __call__(self):
            """执行TTS开关切换"""
            global TTS_ENABLED
            TTS_ENABLED = not TTS_ENABLED
            
            if TTS_ENABLED:
                print("[TTS设置] TTS已启用")
                renpy.notify("TTS语音已启用")
            else:
                print("[TTS设置] TTS已禁用")
                renpy.notify("TTS语音已禁用")
            
            return True
        
        def get_selected(self):
            """返回当前TTS是否启用"""
            global TTS_ENABLED
            return TTS_ENABLED
        
        def get_sensitive(self):
            """返回按钮是否可用"""
            return True
            
    def say_callback(event, interact=True, **kwargs):
        # 延迟初始化 TTS（首次调用时）
        if not globals().get('TTS_INITIALIZED', False):
            init_tts_delayed()
            
        # 当显示对话时触发TTS
        if event == "show":
            try:
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
            except Exception:
                # 记录错误但不影响游戏运行
                print(f"[TTS游戏] 发生错误")
                import traceback
                traceback.print_exc()
            
            # 测试音频通道
            try:
                print("  - 可用音频通道:")
                channels = ["master", "music", "sound", "voice"]
                for ch in channels:
                    try:
                        # 检查通道是否存在（不播放任何内容）
                        if hasattr(renpy.audio, 'get_channel'):
                            channel_obj = renpy.audio.get_channel(ch)
                            print(f"    * {ch}: 可用")
                        else:
                            print(f"    * {ch}: 未知")
                    except Exception:
                        print(f"    * {ch}: 不可用")
            except Exception:
                print(f"  - 音频通道检测失败")
                
            print("=== 检测完成 ===")
        except Exception:
            print(f"Ren'Py 音频系统检测失败")
    
   

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

    "欢迎来到大连医院模拟器"
    
    "点击开始游戏"
    
    # 跳转到day1
    jump day1_start
    
    # 此处为游戏结尾
    return