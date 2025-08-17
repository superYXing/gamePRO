# TTS配置文件模板

# TTS设置
init python:
    # 讯飞API配置 - 请填入你的实际凭证
    # 获取方式：https://www.xfyun.cn/services/online_tts
    TTS_APP_ID = "YOUR_APP_ID_HERE"
    TTS_API_KEY = "YOUR_API_KEY_HERE"  
    TTS_API_SECRET = "YOUR_API_SECRET_HERE"
    
    # TTS启用开关
    TTS_ENABLED = True  # 启用TTS进行测试
    
    # 初始化TTS模块（如果启用）
    if TTS_ENABLED:
        try:
            import tts_module
            # 初始化TTS客户端
            success = tts_module.init_tts(TTS_APP_ID, TTS_API_KEY, TTS_API_SECRET)
            if success:
                print("✓ TTS真实API初始化成功")
            else:
                print("⚠ TTS使用模拟模式")
        except Exception as e:
            print(f"✗ TTS初始化失败: {e}")
            TTS_ENABLED = False

# 定义TTS切换动作
init python:
    class ToggleTTS(Action):
        def __call__(self):
            global TTS_ENABLED
            TTS_ENABLED = not TTS_ENABLED
            
            # 如果启用TTS，初始化模块
            if TTS_ENABLED:
                try:
                    import tts_module
                    if not tts_module.init_tts(TTS_APP_ID, TTS_API_KEY, TTS_API_SECRET):
                        print("使用TTS模拟模式")
                except Exception as e:
                    print("TTS初始化失败: ", e)
                    TTS_ENABLED = False
            
            # 返回当前状态以更新界面
            return TTS_ENABLED
            
        def get_selected(self):
            return TTS_ENABLED
