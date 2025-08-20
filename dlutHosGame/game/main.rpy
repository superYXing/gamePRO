init -10 python:
    # 高优先级初始化TTS
    import os
    import sys
    
    # 强制将当前目录添加到路径
    game_dir = os.path.dirname(os.path.abspath(renpy.loader.transfn("main.rpy")))
    if game_dir not in sys.path:
        sys.path.insert(0, game_dir)
    
    # 导入并直接初始化TTS
    import tts_module
    # 从统一配置读取 API 与模型参数
    try:
        from config import config as game_config
        _api_key = game_config.api_key
        _base_url = game_config.base_url
        _tts_model = game_config.tts_model
        _tts_voice = game_config.tts_voice
    except Exception:
        # 兜底（不建议，建议通过 .env 配置）
        _api_key = os.getenv("OPENAI_API_KEY", "")
        _base_url = os.getenv("OPENAI_BASE_URL", "https://yunwu.ai/v1")
        _tts_model = os.getenv("OPENAI_TTS_MODEL", "tts-1")
        _tts_voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
    
    # 直接创建TTS管理器实例（使用集中配置）
    tts_module.manager = tts_module.TTSManager(
        api_key=_api_key,
        base_url=_base_url,
        model=_tts_model,
        voice=_tts_voice
    )
    print("[TTS] 直接初始化TTS管理器完成")
init python:
    # 启动异步任务，返回一个“任务盒子”
    def spawn_async(fn, *args, **kwargs):
        box = {"done": False, "val": None}
        def _run():
            try:
                box["val"] = fn(*args, **kwargs)
            finally:
                box["done"] = True
        renpy.invoke_in_thread(_run)
        return box

    # 需要用结果时再阻塞等待
    def await_box(box):
        while not box["done"]:
            renpy.pause(0.05)
        return box["val"]

init python:
    # 导入并直接创建AI管理器实例
    import ai_module
    ai_module.init_ai()
    # 创建全局引用，便于在脚本中使用
    ai_manager = ai_module.ai_manager
    print("[AI] AI对话管理器初始化完成")
    
init python:
    import threading
    import time
    
    # 音频播放线程管理
    audio_threads = []
    current_audio_thread = None
    
    def cleanup_finished_threads():
        """清理已完成的音频线程"""
        global audio_threads
        audio_threads = [t for t in audio_threads if t.is_alive()]
    
    def stop_current_audio():
        """停止当前播放的音频"""
        global current_audio_thread
        if current_audio_thread and current_audio_thread.is_alive():
            # 停止当前音频播放
            renpy.sound.stop()
            print("[TTS线程] 停止当前音频播放")
    
    def speak_text_and_play(text, voice="alloy", speed=0.7, emotion=None):
        """异步生成TTS音频并播放，不阻塞界面"""
        import tts_module
        
        def audio_worker():
            try:
                if hasattr(tts_module, 'manager') and tts_module.manager:
                    # 使用manager合成音频
                    full_path = tts_module.manager.synthesize_to_file(text, voice)
                    # 提取文件名并构建相对路径
                    filename = os.path.basename(full_path)
                    audio_path = "audio/tts/" + filename
                    
                    print(f"[TTS线程] 生成文件: {audio_path}")
                    
                    # 检查文件是否存在
                    if os.path.exists(full_path):
                        print(f"[TTS线程] 文件确认存在，异步播放")
                        # 使用Ren'Py API异步播放
                        renpy.sound.play(audio_path, loop=False)
                    else:
                        print(f"[TTS线程] 文件不存在: {full_path}")
                else:
                    print("[TTS线程] TTS管理器未初始化")
            except Exception as e:
                print(f"[TTS线程] 播放音频时发生错误: {e}")
        
        # 停止当前播放的音频
        stop_current_audio()
        
        # 创建新的音频线程
        global current_audio_thread, audio_threads
        current_audio_thread = threading.Thread(target=audio_worker, daemon=True)
        current_audio_thread.start()
        audio_threads.append(current_audio_thread)
        
        # 清理已完成的线程
        cleanup_finished_threads()
        
        print(f"[TTS主线程] 音频播放线程已启动，继续显示字幕")
        return True
    
    def safe_ai_generate_response(messages, option_type):
        """异步安全地调用AI生成回应"""
        import ai_module
        import threading
        import time
        
        # 用于存储结果的容器
        result_container = {"response": None, "finished": False, "error": None}
        
        def ai_worker():
            """AI生成工作线程"""
            try:
                # 确保AI管理器已正确初始化
                if ai_module.ai_manager and hasattr(ai_module.ai_manager, 'generate_response'):
                    response = ai_module.ai_manager.generate_response(messages, option_type=option_type)
                    result_container["response"] = response
                else:
                    result_container["error"] = "AI管理器未初始化或不可用"
            except Exception as e:
                result_container["error"] = f"生成回应时发生错误: {e}"
            finally:
                result_container["finished"] = True
        
        # 启动AI生成线程
        ai_thread = threading.Thread(target=ai_worker, daemon=True)
        ai_thread.start()
        
        # 显示生成进度提示
        print(f"[AI异步] 正在生成{option_type}类型的回应...")
        
        # 等待结果，但不阻塞太久
        max_wait_time = 30  # 最大等待30秒
        wait_interval = 0.1  # 每0.1秒检查一次
        waited_time = 0
        
        while not result_container["finished"] and waited_time < max_wait_time:
            time.sleep(wait_interval)
            waited_time += wait_interval
            
            # 每2秒显示一次进度
            if int(waited_time * 5) % 10 == 0:
                dots = "." * (int(waited_time / 2) % 4)
                print(f"[AI异步] {option_type}生成中{dots}")
        
        # 检查结果
        if result_container["finished"]:
            if result_container["error"]:
                print(f"[AI异步] {result_container['error']}")
                return None
            else:
                print(f"[AI异步] {option_type}类型回应生成完成")
                return result_container["response"]
        else:
            print(f"[AI异步] {option_type}生成超时，将使用默认回应")
            return None
    
    def safe_ai_generate_multiple_responses(prompts_and_types):
        """并行生成多个AI回应以提升性能"""
        import threading
        import time
        
        results = {}
        threads = []
        
        def generate_single_response(prompt_data, option_type, result_dict):
            """单个回应生成函数"""
            response = safe_ai_generate_response(prompt_data, option_type)
            result_dict[option_type] = response
        
        # 启动所有生成线程
        for prompt_data, option_type in prompts_and_types:
            thread = threading.Thread(
                target=generate_single_response, 
                args=(prompt_data, option_type, results),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        print(f"[AI并行] 启动{len(threads)}个AI生成线程...")
        
        # 等待所有线程完成
        max_wait_time = 35  # 最大等待35秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            alive_threads = [t for t in threads if t.is_alive()]
            if not alive_threads:
                print("[AI并行] 所有AI回应生成完成")
                break
            time.sleep(0.5)  # 每0.5秒检查一次
            if int((time.time() - start_time) * 2) % 4 == 0:
                print(f"[AI并行] 还有{len(alive_threads)}个回应正在生成...")
        
        return results
    
    def safe_ai_calculate_san(choice_type):
        """安全地调用AI计算SAN值"""
        # 确保AI管理器已正确初始化
        import ai_module
        if ai_module.ai_manager and hasattr(ai_module.ai_manager, 'calculate_san'):
            try:
                return ai_module.ai_manager.calculate_san(choice_type)
            except Exception as e:
                print(f"[AI] 计算SAN值时发生错误: {e}")
                return -5  # 默认值
        else:
            print("[AI] AI管理器未初始化或不可用")
            return -5  # 默认值
    
    def safe_ai_generate_patient_response(messages, patient_info, conversation_context=""):
        """异步安全地调用AI生成患者回应"""
        import ai_module
        import threading
        import time
        
        # 用于存储结果的容器
        result_container = {"response": None, "finished": False, "error": None}
        
        def patient_ai_worker():
            """患者AI生成工作线程"""
            try:
                # 确保AI管理器已正确初始化
                if ai_module.ai_manager and hasattr(ai_module.ai_manager, 'generate_patient_response'):
                    response = ai_module.ai_manager.generate_patient_response(messages, patient_info, conversation_context)
                    result_container["response"] = response
                else:
                    result_container["error"] = "AI管理器未初始化或不可用"
            except Exception as e:
                result_container["error"] = f"生成患者回应时发生错误: {e}"
            finally:
                result_container["finished"] = True
        
        # 启动患者AI生成线程
        patient_ai_thread = threading.Thread(target=patient_ai_worker, daemon=True)
        patient_ai_thread.start()
        
        # 显示生成进度提示
        print(f"[患者AI异步] 正在生成患者回应...")
        
        # 等待结果，但不阻塞太久
        max_wait_time = 25  # 最大等待25秒
        wait_interval = 0.2  # 每0.2秒检查一次
        waited_time = 0
        
        while not result_container["finished"] and waited_time < max_wait_time:
            time.sleep(wait_interval)
            waited_time += wait_interval
            
            # 每2秒显示一次进度
            if int(waited_time * 5) % 10 == 0:
                dots = "." * (int(waited_time / 2) % 4)
                print(f"[患者AI异步] 生成中{dots}")
        
        # 检查结果
        if result_container["finished"]:
            if result_container["error"]:
                print(f"[患者AI异步] {result_container['error']}")
                return None
            else:
                print(f"[患者AI异步] 患者回应生成完成")
                return result_container["response"]
        else:
            print(f"[患者AI异步] 患者回应生成超时，将使用默认回应")
            return None

label day1_start:
    # 强制设置音频通道音量
    $ renpy.music.set_volume(2.0, channel="sound")
    $ renpy.music.set_volume(0.6, channel="voice") 
    $ renpy.music.set_volume(0.6, channel="music")
    $ print("[音频] 音频通道音量已设置")
    
    # 初始化SAN值
    $ san_value = 100
    
    # 设置患者信息
    $ patient_info = {
        "name": "李秀兰",
        "gender": "女",
        "age": 39,
        "symptoms": "头晕，起身偶有眼前发黑、心悸症状",
        "history": "无病史"
    }
    
    # 初始化对话历史
    $ conversation_history = []
    
    # 患者案例介绍
    show hos_background:
        size (config.screen_width, config.screen_height)  # 全屏显示
        pos (0, 0)
    # 播放医院背景音乐
    play music "audio/bgm/amb_hospital.ogg" loop
    
    # 开场介绍第一段 - 同时显示和播放TTS
    $ intro_text1 = "在AI时代，医生面临着前所未有的挑战。"
    $ speak_text_and_play(intro_text1, voice="shimmer")
    "[intro_text1]"
    
    # 开场介绍第二段 - 同时显示和播放TTS
    $ intro_text2 = "你将扮演一位被困在无尽工作循环中的医生，在每一次诊疗中寻找理性与人性的平衡。"
    $ speak_text_and_play(intro_text2, voice="shimmer")
    "[intro_text2]"
    
    # 开场介绍第三段 - 同时显示和播放TTS
    $ intro_text3 = "点击开始游戏，开启你的医生之旅"
    $ speak_text_and_play(intro_text3, voice="shimmer")
    "[intro_text3]"
    
    # 显示bg5.png，全屏
    show bg5:
        size (config.screen_width, config.screen_height)
        pos (0, 0)
    with dissolve

    # 实时生成并播放旁白语音 - 使用异步播放
    $ narrator_text = f"患者{patient_info['name']}，{patient_info['gender']}，{patient_info['age']}岁，前来就诊。"
    $ speak_text_and_play(narrator_text, voice="shimmer")
    "[narrator_text]"
    $ print("[TTS播放] 开始播放旁白...")
  
    # 让患者AI生成第一句话
    $ print("[患者AI] 正在生成患者初始主诉...")
    
    # ✅ 新增：先在后台启动生成（此时已经开始联网生成了）
    $ task_pf = spawn_async(
        safe_ai_generate_patient_response,
        [{"role": "user", "content": f"你是患者{patient_info['name']}，现在来到医院看病。请根据你的症状（{patient_info['symptoms']}）向医生主诉你的不适，表达你的担忧。"}],
        patient_info,
        "这是你第一次向医生描述症状"
    )

    # 显示bg2.png，全屏
    show bg2:
        size (config.screen_width, config.screen_height)
        pos (0, 0)
    with dissolve
    # 这一行台词会立即显示；同时后台已在生成AI文本
    "患者紧皱眉头，似乎在组织语言描述自己的不适。"

    # ✅ 替换：把原来的同步调用替换为等待后台结果
    $ patient_first_message = await_box(task_pf)
    
    
    # 实时生成并播放患者语音 - 使用异步播放
    $ print("[TTS播放] 开始播放患者语音...")
    $ speak_text_and_play(patient_first_message, voice="nova")
    "患者：[patient_first_message]"
    
    # 记录对话历史
    $ conversation_history.append({"role": "patient", "content": patient_first_message})
    
    # 构建医生AI的对话上下文
    $ doctor_context = f"患者{patient_info['name']}主诉：{patient_first_message}"
    
    # 让AI并行生成三个不同风格的回应选项
    $ print("[AI并行] 正在生成第一轮医生回应选项...")
    
    # ✅ 新增：先在后台启动生成（此时已经开始联网生成了）
    $ task_dr1 = spawn_async(
        safe_ai_generate_multiple_responses,
    [
            ([{"role": "user", "content": f"患者{patient_info['name']}（{patient_info['gender']}，{patient_info['age']}岁）说：'{patient_first_message}'。请生成一个理性、专业的医生回应，控制在40字以内，要询问更多症状细节。"}], "理性"),
            ([{"role": "user", "content": f"患者{patient_info['name']}（{patient_info['gender']}，{patient_info['age']}岁）说：'{patient_first_message}'。请生成一个温暖、关怀的医生回应，控制在40字以内，安抚患者并询问症状。"}], "人性"),
            ([{"role": "user", "content": f"患者{patient_info['name']}（{patient_info['gender']}，{patient_info['age']}岁）说：'{patient_first_message}'。请生成一个简单、直接的医生回应，控制在40字以内。"}], "中性")
    ]
    )

    # 这一行台词会立即显示；同时后台已在生成AI文本
    "您在脑海中快速思考着几种不同的回应方式"

    # ✅ 替换：把原来的同步调用替换为等待后台结果
    $ ai_responses = await_box(task_dr1)
    $ option1 = ai_responses.get("理性")
    $ option2 = ai_responses.get("人性") 
    $ option3 = ai_responses.get("中性")
    

    
    # 生成医生的三个选项
    menu:
        "[option1]":
            play sound "audio/sfx/sfx_buzz.ogg"
            $ ai_response = option1
            $ response_type = "理性"
            $ san_change = safe_ai_calculate_san("理性")
            jump day1_choice_result
        "[option2]":
            play sound "audio/sfx/sfx_warn.ogg"
            $ ai_response = option2
            $ response_type = "人性"
            $ san_change = safe_ai_calculate_san("人性")
            jump day1_choice_result
        "[option3]":
            play sound "audio/sfx/sfx_chime.mp3"
            $ ai_response = option3
            $ response_type = "中性"
            $ san_change = safe_ai_calculate_san("中性")
            jump day1_choice_result

label day1_choice_result:
    # 确保ai_response不为None
    if not ai_response:
        $ ai_response = "很抱歉，我需要更多信息来给您提供建议。"
    
    # 记录医生的回应到对话历史
    $ conversation_history.append({"role": "doctor", "content": ai_response})
    
    # 实时生成并播放医生回复的语音 - 使用异步播放
    $ doctor_text = "医生：" + ai_response
    $ print("[TTS播放] 开始播放医生回复...")
    $ speak_text_and_play(ai_response, voice="echo")
    "[doctor_text]"
    
    $ current_san = san_value + san_change
    $ san_value = current_san
    
    # 让患者AI根据医生的回复生成下一个回应
    $ print("[患者AI] 正在生成患者第二轮回应...")

    # ✅ 新增：先在后台启动生成（此时已经开始联网生成了）
    $ task_ps = spawn_async(
        safe_ai_generate_patient_response,
        conversation_history[-2:],            # 使用最近的对话历史
        patient_info, 
        "你需要根据医生的话继续交流，可能询问更多细节、表达担忧或寻求更多信息。"
    )

    # 这一行台词会立即显示；同时后台已在生成AI文本
    "患者仔细听着您的询问，眼神中透露出担忧和期待"

    # ✅ 替换：把原来的同步调用替换为等待后台结果
    $ patient_second_message = await_box(task_ps)

    

    # 第二轮对话 - 旁白
    $ narrator_text2 = f"{patient_info['name']}继续与您交流她的担忧。"
    $ print("[TTS播放] 开始播放旁白...")
    $ speak_text_and_play(narrator_text2, voice="shimmer")
    "[narrator_text2]"
  
    # 实时生成并播放患者语音 - 使用异步播放
    $ print("[TTS播放] 开始播放患者语音...")
    $ speak_text_and_play(patient_second_message, voice="nova")
    "患者：[patient_second_message]"
    
    # 记录患者的第二轮回应
    $ conversation_history.append({"role": "patient", "content": patient_second_message})
    
    # 让AI并行生成第二轮回应选项
    $ print("[AI并行] 正在生成第二轮医生回应选项...")
    
    # ✅ 新增：先在后台启动生成（此时已经开始联网生成了）
    $ task_dr2 = spawn_async(
        safe_ai_generate_multiple_responses,
    [
            ([{"role": "user", "content": f"患者{patient_info['name']}刚才说：'{patient_second_message}'。请生成一个理性、专业的医生回应，控制在40字以内。"}], "理性"),
            ([{"role": "user", "content": f"患者{patient_info['name']}刚才说：'{patient_second_message}'。请生成一个温暖、关怀的医生回应，控制在40字以内。"}], "人性"),
            ([{"role": "user", "content": f"患者{patient_info['name']}刚才说：'{patient_second_message}'。请生成一个简单、直接的医生回应，控制在40字以内。"}], "中性")
    ]
    )

    # 这一行台词会立即显示；同时后台已在生成AI文本
    "您看着患者期待的眼神，思考着下一步该如何询问"

    # ✅ 替换：把原来的同步调用替换为等待后台结果
    $ ai_responses2 = await_box(task_dr2)
    $ option2_1 = ai_responses2.get("理性")
    $ option2_2 = ai_responses2.get("人性")
    $ option2_3 = ai_responses2.get("中性")
    
    
    # 生成医生的三个选项
    menu:
        "[option2_1]":
            play sound "audio/sfx/sfx_buzz.ogg"
            $ ai_response2 = option2_1
            $ response_type2 = "理性"
            $ san_change2 = safe_ai_calculate_san("理性")
            jump day1_choice_result2
        "[option2_2]":
            play sound "audio/sfx/sfx_warn.ogg"
            $ ai_response2 = option2_2
            $ response_type2 = "人性"
            $ san_change2 = safe_ai_calculate_san("人性")
            jump day1_choice_result2
        "[option2_3]":
            play sound "audio/sfx/sfx_chime.mp3"
            $ ai_response2 = option2_3
            $ response_type2 = "中性"
            $ san_change2 = safe_ai_calculate_san("中性")
            jump day1_choice_result2

label day1_choice_result2:
    # 确保ai_response2不为None
    if not ai_response2:
        $ ai_response2 = "很抱歉，我需要更多信息来给您提供建议。"
    
    # 记录医生的第二轮回应到对话历史
    $ conversation_history.append({"role": "doctor", "content": ai_response2})
    
    # 实时生成并播放医生回复的语音 - 使用异步播放
    $ doctor_text2 = "医生：" + ai_response2
    $ print("[TTS播放] 开始播放医生回复...")
    $ speak_text_and_play(ai_response2, voice="echo")
    "[doctor_text2]"
    
    $ current_san = san_value + san_change2
    $ san_value = current_san
    
    # 让患者AI根据医生的第二轮回复生成第三个回应
    $ print("[患者AI] 正在生成患者第三轮回应...")
    $ patient_third_message = safe_ai_generate_patient_response(
        conversation_history[-2:],  # 使用最近的对话历史
        patient_info, 
        f"医生刚才回答：{ai_response2}。你可能想了解更多治疗信息、费用、时间等，或者表达其他担忧。"
    )
    
   

    # 第三轮对话 - 旁白
    $ narrator_text3 = f"{patient_info['name']}还想了解更多关于治疗的信息。"
    $ print("[TTS播放] 开始播放旁白...")
    $ speak_text_and_play(narrator_text3, voice="shimmer")
    "[narrator_text3]"
  
    # 实时生成并播放患者语音 - 使用异步播放
    $ print("[TTS播放] 开始播放患者语音...")
    $ speak_text_and_play(patient_third_message, voice="nova")
    "患者：[patient_third_message]"
    
    # 记录患者的第三轮回应
    $ conversation_history.append({"role": "patient", "content": patient_third_message})
    
    # 让AI并行生成第三轮回应选项
    $ print("[AI并行] 正在生成第三轮医生回应选项...")
    $ ai_prompts3 = [
        ([{"role": "user", "content": f"患者{patient_info['name']}刚才说：'{patient_third_message}'。请生成一个理性、专业的医生回应，控制在40字以内。"}], "理性"),
        ([{"role": "user", "content": f"患者{patient_info['name']}刚才说：'{patient_third_message}'。请生成一个温暖、关怀的医生回应，控制在40字以内。"}], "人性"),
        ([{"role": "user", "content": f"患者{patient_info['name']}刚才说：'{patient_third_message}'。请生成一个简单、直接的医生回应，控制在40字以内。"}], "中性")
    ]
    $ ai_responses3 = safe_ai_generate_multiple_responses(ai_prompts3)
    $ option3_1 = ai_responses3.get("理性")
    $ option3_2 = ai_responses3.get("人性")
    $ option3_3 = ai_responses3.get("中性")
    
    # 为选项设置默认值
    if not option3_1:
        $ option3_1 = f"根据您的症状，建议先做相关检查确诊，然后制定治疗方案。"
    if not option3_2:
        $ option3_2 = f"{patient_info['name']}，不要太担心，我们会帮您找到最合适的治疗方法。"
    if not option3_3:
        $ option3_3 = f"需要综合评估病情后才能确定具体的治疗计划。"
    
    # 生成医生的三个选项
    menu:
        "[option3_1]":
            play sound "audio/sfx/sfx_buzz.ogg"
            $ ai_response3 = option3_1
            $ response_type3 = "理性"
            $ san_change3 = safe_ai_calculate_san("理性")
            jump day1_choice_result3
        "[option3_2]":
            play sound "audio/sfx/sfx_warn.ogg"
            $ ai_response3 = option3_2
            $ response_type3 = "人性"
            $ san_change3 = safe_ai_calculate_san("人性")
            jump day1_choice_result3
        "[option3_3]":
            play sound "audio/sfx/sfx_chime.mp3"
            $ ai_response3 = option3_3
            $ response_type3 = "中性"
            $ san_change3 = safe_ai_calculate_san("中性")
            jump day1_choice_result3


    
label day1_choice_result3:
    # 确保ai_response3不为None
    if not ai_response3:
        $ ai_response3 = "很抱歉，我需要更多信息来给您提供建议。"
    
    # 记录医生的第三轮回应到对话历史
    $ conversation_history.append({"role": "doctor", "content": ai_response3})
    
    # 实时生成并播放医生回复的语音 - 使用异步播放
    $ doctor_text3 = "医生：" + ai_response3
    $ print("[TTS播放] 开始播放医生回复...")
    $ speak_text_and_play(ai_response3, voice="echo")
    "[doctor_text3]"
    
    $ current_san = san_value + san_change3
    $ san_value = current_san
    
    # 让患者AI生成最终的满意度回应
    $ print("[患者AI] 正在生成患者满意度回应...")
    $ patient_satisfaction_message = safe_ai_generate_patient_response(
        conversation_history[-2:],  # 使用最近的对话历史
        patient_info, 
        f"医生最后说：{ai_response3}。请表达你对整个诊疗过程的感受，可能是满意、感谢，或者还有疑问。要自然地结束对话。"
    )
    
   
    
    # 播放患者的最终回应
    $ print("[TTS播放] 开始播放患者最终回应...")
    $ speak_text_and_play(patient_satisfaction_message, voice="nova")
    "患者：[patient_satisfaction_message]"
    
    jump day1_end

label day1_end:
    # 显示bg4.png，全屏
    show bg4:
        size (config.screen_width, config.screen_height)
        pos (0, 0)
    with dissolve
    # 总结当前SAN值和对话情况
    $ final_san_text = f"今日诊疗结束。患者{patient_info['name']}的诊疗完成，您的最终SAN值为：{san_value}"
    $ print("[TTS播放] 开始播放总结...")
    $ speak_text_and_play(final_san_text, voice="shimmer")
    "[final_san_text]"
    
    # 显示对话总结
    $ dialogue_summary = f"本次诊疗中，您与患者{patient_info['name']}进行了深入的交流，了解了她的症状并给出了专业建议。"
    "[dialogue_summary]"
    
    # 显示结束画面
    show black:
        size (config.screen_width, config.screen_height)
        pos (0, 0)
    with fade
    "第一天的AI对话诊疗到此结束。"
    
    # 返回主菜单或者跳转到下一天
    return