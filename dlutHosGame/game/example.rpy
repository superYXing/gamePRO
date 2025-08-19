init -10 python:
    # 高优先级初始化TTS
    import os
    import sys
    
    # 强制将当前目录添加到路径
    game_dir = os.path.dirname(os.path.abspath(renpy.loader.transfn("day1.rpy")))
    if game_dir not in sys.path:
        sys.path.insert(0, game_dir)
    
    # 导入并直接初始化TTS
    import tts_module
    # 直接初始化TTS管理器
    BASE_URL = "https://yunwu.ai/v1"
    API_KEY = 
    MODEL = "tts-1"
    
    # 直接创建TTS管理器实例
    tts_module.manager = tts_module.TTSManager(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL
    )
    print("[TTS] 直接初始化TTS管理器完成")
    
    # 导入并直接创建AI管理器实例
    import ai_module
    ai_module.init_ai()
    # 创建全局引用，便于在脚本中使用
    ai_manager = ai_module.ai_manager
    print("[AI] AI对话管理器初始化完成")

init python:
    def speak_text_and_play(text, voice="alloy", speed=0.7, emotion=None):
        """生成TTS音频并使用Python API直接播放"""
        import tts_module
        if hasattr(tts_module, 'manager') and tts_module.manager:
            # 使用manager合成音频
            full_path = tts_module.manager.synthesize_to_file(text, voice)
            # 提取文件名并构建相对路径
            filename = os.path.basename(full_path)
            audio_path = "audio/tts/" + filename
            
            print(f"[TTS] 生成文件: {audio_path}")
            
            # 检查文件是否存在
            if os.path.exists(full_path):
                print(f"[TTS] 文件确认存在，使用Python API播放")
                # 使用Python API强制播放
                renpy.sound.play(audio_path, loop=False)
                return True
            else:
                print(f"[TTS] 文件不存在: {full_path}")
                return False
        else:
            print("[TTS] TTS管理器未初始化")
            return False
    
    def safe_ai_generate_response(messages, option_type):
        """安全地调用AI生成回应"""
        if ai_manager and hasattr(ai_manager, 'generate_response'):
            try:
                return ai_manager.generate_response(messages, option_type=option_type)
            except Exception as e:
                print(f"[AI] 生成回应时发生错误: {e}")
                return None
        else:
            print("[AI] AI管理器未初始化或不可用")
            return None
    
    def safe_ai_calculate_san(choice_type):
        """安全地调用AI计算SAN值"""
        if ai_manager and hasattr(ai_manager, 'calculate_san'):
            try:
                return ai_manager.calculate_san(choice_type)
            except Exception as e:
                print(f"[AI] 计算SAN值时发生错误: {e}")
                return -5  # 默认值
        else:
            print("[AI] AI管理器未初始化或不可用")
            return -5  # 默认值

label day1_start:
    # 强制设置音频通道音量
    $ renpy.music.set_volume(2.0, channel="sound")
    $ renpy.music.set_volume(0.6, channel="voice") 
    $ renpy.music.set_volume(0.6, channel="music")
    $ print("[音频] 音频通道音量已设置")
    
    # 初始化SAN值
    $ san_value = 100
    
    # 患者案例介绍
    show hos_background:
        size (config.screen_width, config.screen_height)  # 全屏显示
        pos (0, 0)
    # 播放医院背景音乐
    play music "audio/bgm/amb_hospital.ogg" loop
    
    # 患者出场（只显示一次）
    show patient2 at center
    
    # 实时生成并播放旁白语音 - 使用Python API
    $ narrator_text = "您是大连医院的主治医生，现在需要处理第一位患者。"
    "[narrator_text]"
    $ print("[TTS播放] 开始播放旁白...")
    $ speak_success = speak_text_and_play(narrator_text, voice="alloy")
    if speak_success:
        $ renpy.pause(2.0)  # 等待播放完成
  
    # 实时生成并播放患者语音 - 使用Python API
    $ patient_text = "医生，我最近总是感觉很焦虑，晚上睡不着觉。"
    "患者：[patient_text]"
    $ print("[TTS播放] 开始播放患者语音...")
    $ speak_success = speak_text_and_play(patient_text, voice="nova")
    if speak_success:
        $ renpy.pause(2.0)  # 等待播放完成
    
    # 生成医生的三个选项
    menu:
        "理性分析":
            play sound "audio/sfx/sfx_buzz.ogg"
            $ ai_response = safe_ai_generate_response([
                {"role": "user", "content": "患者主诉：焦虑和失眠"}
            ], "理性")
            if not ai_response:
                $ ai_response = "根据您的症状描述，这可能是广泛性焦虑障碍的表现。建议您进行详细的心理评估。"
            $ san_change = safe_ai_calculate_san("理性")
            jump day1_choice_result
        "人性关怀":
            play sound "audio/sfx/sfx_warn.ogg"
            $ ai_response = safe_ai_generate_response([
                {"role": "user", "content": "患者主诉：焦虑和失眠"}
            ], "人性")
            if not ai_response:
                $ ai_response = "我理解您现在的困扰，焦虑确实会影响睡眠质量。让我们一起找到缓解的方法。"
            $ san_change = safe_ai_calculate_san("人性")
            jump day1_choice_result
        "普通建议":
            play sound "audio/sfx/sfx_chime.mp3"
            $ ai_response = safe_ai_generate_response([
                {"role": "user", "content": "患者主诉：焦虑和失眠"}
            ], "平淡")
            if not ai_response:
                $ ai_response = "焦虑和失眠是常见的问题。建议您保持规律作息，避免咖啡因。"
            $ san_change = safe_ai_calculate_san("平淡")
            jump day1_choice_result

label day1_choice_result:
    # 确保ai_response不为None
    if not ai_response:
        $ ai_response = "很抱歉，我需要更多信息来给您提供建议。"
    
    # 实时生成并播放医生回复的语音 - 使用Python API
    $ doctor_text = "医生：" + ai_response
    "[doctor_text]"
    $ print("[TTS播放] 开始播放医生回复...")
    $ speak_success = speak_text_and_play(ai_response, voice="onyx")
    if speak_success:
        $ renpy.pause(2.0)  # 医生回复通常较长，等待更久
    
    $ current_san = san_value + san_change
    $ san_value = current_san
    
    # 显示SAN值变化 - 使用Python API
    $ san_text = "SAN值变化：" + str(san_change) + "，当前SAN值：" + str(san_value)
    "[san_text]"
    $ print("[TTS播放] 开始播放SAN值变化...")
    $ speak_success = speak_text_and_play(san_text)
    if speak_success:
        $ renpy.pause(2.0)
    
    # 第二轮对话（移除不必要的场景切换）
    # 实时生成并播放旁白语音 - 使用Python API
    $ narrator_text2 = "患者似乎还有疑问，继续与您交流。"
    "[narrator_text2]"
    $ print("[TTS播放] 开始播放旁白...")
    $ speak_success = speak_text_and_play(narrator_text2, voice="alloy")
    if speak_success:
        $ renpy.pause(2.0)  # 等待播放完成
  
    # 实时生成并播放患者语音 - 使用Python API
    $ patient_text2 = "医生，我还有些担心，这种症状会不会影响我的工作？"
    "患者：[patient_text2]"
    $ print("[TTS播放] 开始播放患者语音...")
    $ speak_success = speak_text_and_play(patient_text2, voice="nova")
    if speak_success:
        $ renpy.pause(2.0)  # 等待播放完成
    
    # 生成医生的三个选项
    menu:
        "理性分析":
            play sound "audio/sfx/sfx_buzz.ogg"
            $ ai_response2 = safe_ai_generate_response([
                {"role": "user", "content": "患者担心症状对工作的影响"}
            ], "理性")
            if not ai_response2:
                $ ai_response2 = "根据医学研究，轻度焦虑通常不会严重影响工作能力，但失眠可能会降低注意力。建议您在治疗期间合理安排工作强度。"
            $ san_change2 = safe_ai_calculate_san("理性")
            jump day1_choice_result2
        "人性关怀":
            play sound "audio/sfx/sfx_warn.ogg"
            $ ai_response2 = safe_ai_generate_response([
                {"role": "user", "content": "患者担心症状对工作的影响"}
            ], "人性")
            if not ai_response2:
                $ ai_response2 = "我理解您的担心，工作确实很重要。我们会尽快帮您缓解症状，让您能正常工作。在治疗期间，您可以适当调整工作安排。"
            $ san_change2 = safe_ai_calculate_san("人性")
            jump day1_choice_result2
        "普通建议":
            play sound "audio/sfx/sfx_chime.mp3"
            $ ai_response2 = safe_ai_generate_response([
                {"role": "user", "content": "患者担心症状对工作的影响"}
            ], "平淡")
            if not ai_response2:
                $ ai_response2 = "症状可能会对工作产生一定影响，但通过治疗可以改善。建议您在工作时注意休息，避免过度劳累。"
            $ san_change2 = safe_ai_calculate_san("平淡")
            jump day1_choice_result2

label day1_choice_result2:
    # 确保ai_response2不为None
    if not ai_response2:
        $ ai_response2 = "很抱歉，我需要更多信息来给您提供建议。"
    
    # 实时生成并播放医生回复的语音 - 使用Python API
    $ doctor_text2 = "医生：" + ai_response2
    $ print("[TTS播放] 开始播放医生回复...")
    $ speak_success = speak_text_and_play(ai_response2, voice="onyx")
    # 同时显示文本和播放音频
    "[doctor_text2]"
    if speak_success:
        $ renpy.pause(2.0)  # 医生回复通常较长，等待更久
    
    $ current_san = san_value + san_change2
    $ san_value = current_san
    
    # 显示SAN值变化 - 使用Python API
    $ san_text2 = "SAN值变化：" + str(san_change2) + "，当前SAN值：" + str(san_value)
    $ print("[TTS播放] 开始播放SAN值变化...")
    $ speak_success = speak_text_and_play(san_text2)
    # 同时显示文本和播放音频
    "[san_text2]"
    if speak_success:
        $ renpy.pause(2.0)
    
    # 第三轮对话（移除不必要的场景切换）
    # 实时生成并播放旁白语音 - 使用Python API
    $ narrator_text3 = "患者似乎还想了解更多关于治疗的信息。"
    $ print("[TTS播放] 开始播放旁白...")
    $ speak_success = speak_text_and_play(narrator_text3, voice="alloy")
    # 同时显示文本和播放音频
    "[narrator_text3]"
    if speak_success:
        $ renpy.pause(2.0)  # 等待播放完成
  
    # 实时生成并播放患者语音 - 使用Python API
    $ patient_text3 = "医生，这种治疗大概需要多长时间？我什么时候能感觉好一些？"
    $ print("[TTS播放] 开始播放患者语音...")
    $ speak_success = speak_text_and_play(patient_text3, voice="nova")
    # 同时显示文本和播放音频
    "患者：[patient_text3]"
    if speak_success:
        $ renpy.pause(4.0)  # 等待播放完成
    
    # 生成医生的三个选项
    menu:
        "理性分析":
            play sound "audio/sfx/sfx_buzz.ogg"
            $ ai_response3 = safe_ai_generate_response([
                {"role": "user", "content": "患者询问治疗时间和效果"}
            ], "理性")
            if not ai_response3:
                $ ai_response3 = "根据临床数据，轻度焦虑症的治疗周期通常为4-8周，症状缓解一般在2-3周内开始显现。但个体差异较大，需要定期评估调整治疗方案。"
            $ san_change3 = safe_ai_calculate_san("理性")
            jump day1_choice_result3
        "人性关怀":
            play sound "audio/sfx/sfx_warn.ogg"
            $ ai_response3 = safe_ai_generate_response([
                {"role": "user", "content": "患者询问治疗时间和效果"}
            ], "人性")
            if not ai_response3:
                $ ai_response3 = "每个人的情况不同，但大多数人在治疗2-3周后会开始感觉好转。治疗是一个循序渐进的过程，我们会一起努力，让您尽快恢复健康。"
            $ san_change3 = safe_ai_calculate_san("人性")
            jump day1_choice_result3
        "普通建议":
            play sound "audio/sfx/sfx_chime.mp3"
            $ ai_response3 = safe_ai_generate_response([
                {"role": "user", "content": "患者询问治疗时间和效果"}
            ], "平淡")
            if not ai_response3:
                $ ai_response3 = "治疗时间因人而异，通常需要几周到几个月不等。大多数患者在开始治疗后几周内会感受到改善。"
            $ san_change3 = safe_ai_calculate_san("平淡")
            jump day1_choice_result3

label day1_choice_result3:
    # 确保ai_response3不为None
    if not ai_response3:
        $ ai_response3 = "很抱歉，我需要更多信息来给您提供建议。"
    
    # 实时生成并播放医生回复的语音 - 使用Python API
    $ doctor_text3 = "医生：" + ai_response3
    $ print("[TTS播放] 开始播放医生回复...")
    $ speak_success = speak_text_and_play(ai_response3, voice="onyx")
    # 同时显示文本和播放音频
    "[doctor_text3]"
    if speak_success:
        $ renpy.pause(2.0)  # 医生回复通常较长，等待更久
    
    $ current_san = san_value + san_change3
    $ san_value = current_san
    
    # 显示SAN值变化 - 使用Python API
    $ san_text3 = "SAN值变化：" + str(san_change3) + "，当前SAN值：" + str(san_value)
    $ print("[TTS播放] 开始播放SAN值变化...")
    $ speak_success = speak_text_and_play(san_text3)
    # 同时显示文本和播放音频
    "[san_text3]"
    if speak_success:
        $ renpy.pause(2.0)
    
    # 询问满意度 - 使用Python API
    $ question_text = "您是否满意这个回答？"
    $ print("[TTS播放] 开始播放询问...")
    $ speak_success = speak_text_and_play(question_text)
    # 同时显示文本和播放音频
    "[question_text]"
    if speak_success:
        $ renpy.pause(2.0)
    
    menu:
        "是的":
            $ thanks_text = "谢谢医生，我明白了。"
            $ print("[TTS播放] 开始播放感谢...")
            $ speak_success = speak_text_and_play(thanks_text)
            # 同时显示文本和播放音频
            "患者：[thanks_text]"
            if speak_success:
                $ renpy.pause(2.0)
            jump day1_end
        "不太满意":
            $ question_text = "医生，您能详细解释一下吗？"
            $ print("[TTS播放] 开始播放询问...")
            $ speak_success = speak_text_and_play(question_text)
            # 同时显示文本和播放音频
            "患者：[question_text]"
            if speak_success:
                $ renpy.pause(2.0)
            jump day1_end

label day1_end:
    # 总结当前SAN值
    $ final_san_text = f"今日诊疗结束。您的最终SAN值为：{san_value}"
    $ print("[TTS播放] 开始播放总结...")
    $ speak_success = speak_text_and_play(final_san_text)
    # 同时显示文本和播放音频
    "[final_san_text]"
    if speak_success:
        $ renpy.pause(2.0)
    
    # 显示结束画面
    scene black with fade
    "第一天的诊疗到此结束。"
    
    # 返回主菜单或者跳转到下一天
    return