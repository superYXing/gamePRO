# Day 1 脚本文件

# 定义回调函数用于TTS
init python:
    def say_callback(event, interact=True, **kwargs):
        # 当显示对话时触发TTS
        if event == "show":
            try:
                # 检查TTS是否启用
                if globals().get('TTS_ENABLED', False):
                    import tts_module
                    # 获取对话文本
                    what = kwargs.get('what', '')
                    if what:
                        # 清理文本，移除Ren'Py标记
                        try:
                            # 使用deny参数移除所有文本标记
                            clean_text = renpy.filter_text_tags(what, deny=True)
                        except:
                            # 如果filter_text_tags失败，使用简单的文本清理
                            import re
                            clean_text = re.sub(r'\{[^}]*\}', '', what)
                        
                        print(f"[TTS游戏] 朗读: {clean_text}")
                        # 调用TTS API
                        tts_module.speak_text(clean_text)
                    else:
                        print("[TTS游戏] 警告: 没有找到文本内容")
                else:
                    print("[TTS游戏] TTS功能已禁用")
            except Exception as e:
                # 记录错误但不影响游戏运行
                print(f"[TTS游戏] 错误: {e}")
                import traceback
                traceback.print_exc()

# 定义角色
define you = Character("YOU", what_color="#ffffff", callback=say_callback)
define sys = Character("SYS", what_color="#00ff00", callback=say_callback)
define a33 = Character("A-33", what_color="#ffcc00", callback=say_callback)
define b07 = Character("B-07", what_color="#ff99cc", callback=say_callback)

label day1_start:
    # 场 0｜INT. 医院走廊 – 早（开场）
    scene hospital_interior
    with fade
    play music "audio/bgm/amb_hospital.ogg" fadein 1.0
    call show_hud
    
    sys "欢迎回来，编号 D-001。目标：在工作周期内维持心智并完成必要诊疗。评分以效率为先。"
    
    you "又是同一段话……太阳穴在跳。"
    
    # 转到第一个病人
    jump day1_patient_A33

label day1_patient_A33:
    # 场 1｜INT. 急诊诊室 – 早｜病例 A-33（主场）
    scene hospital_office
    with dissolve
    # TODO: 显示A-33角色图像
    # show a33 at left
    # with dissolve
    
    sys "A-33：胸痛、气促。T 37.7。"
    
    a33 "医生，我胸口闷……是不是心脏病？"
    
    # 交互 1：起始问诊
    menu:
        "D1-1A（理性）：问诊 胸痛 起病时间":
            you "从什么时候开始？伴随出汗或放射痛吗？"
            a33 "半小时前突然，还喘不上气。"
            sys "优秀。核心信息优先。"
            call apply_action("rational")
            
        "D1-1B（人性）：安慰 患者 呼吸引导30秒":
            you "看着我，四拍吸、四拍停、四拍呼……再来。"
            a33 "好像不那么怕了。"
            sys "非流程交流，影响效率。"
            call apply_action("humane")
    
    # 交互 2：体征或压力史
    menu:
        "D1-2A（理性）：检查 生命体征 快速":
            you "血压？心率？血氧？"
            sys "BP 132/86，HR 112，SpO2 93%%。"
            sys "数据记录完成。"
            call apply_action("rational")
            
        "D1-2B（人性）：倾听 病史 最近压力事件":
            you "最近工作或睡眠有什么变化？"
            a33 "加班到凌晨，一想到评审就心慌。"
            sys "与当前诊断相关性低。"
            call apply_action("humane")
    
    # 交互 3：ECG 或自我短休
    menu:
        "D1-3A（理性）：开立 心电图 立即":
            you "先做心电图，马上回来。"
            sys "ECG 下达。评分提升。"
            call apply_action("rational")
            
        "D1-3B（人性·自护）：短休 自己 10秒放松肩颈":
            you "深呼吸……放松肩颈……"
            sys "脱岗记录。"
            call micro_rest()
    
    # 结果推进（根据进度 ≥2）
    if diagnosis_progress >= 2:
        sys "ECG 返回：窦性心动过速，无 ST 改变。"
        
        a33 "我是不是要住院？"
        
        # 交互 4：处理结果
        menu:
            "D1-4A（理性）：宣教 惊恐发作 呼吸训练+复诊":
                you "目前更倾向惊恐发作。给你呼吸训练卡，必要时复诊。"
                a33 "不是心脏病就好……"
                sys "明确处理。"
                call apply_action("rational")
                
            "D1-4B（人性）：陪伴 1分钟 确认家属联络":
                you "需要我帮你联系谁吗？我等你拨通。"
                a33 "……谢谢你。"
                sys "非必要时间占用。"
                call apply_action("humane")
    else:
        # 容错推进：若此前 progress < 2，SYS 插入一句「进度不足，建议加速」并强制触发一次理性补救：
        sys "进度不足，建议加速。"
        call apply_action("fill")
    
    # 场尾微恐效果
    scene hospital_interior
    with dissolve
    show ui_glitch at glitch_flicker
    pause 0.6
    you "灯在闪……还是我在闪？"
    hide ui_glitch
    
    # 转到下一个场景
    jump day1_water_station

label day1_water_station:
    # 场 2｜EXT. 走廊饮水处 – 午（茶水间事件）
    if humane_count > 0:
        sys "记录：人性行为提升了 Sanity。该指标不计入评分。"
    
    # 交互 5：不停留 or 微休
    menu:
        "D1-5A（理性）：继续巡诊 无停留":
            you "下一位。"
            sys "良好时间管理。"
            call apply_action("rational")
            
        "D1-5B（人性）：热水 捧杯20秒 闭眼":
            you "热气裹着呼吸……好了点。"
            sys "与诊疗无关。"
            call apply_action("humane")
    
    # 转到第三个病人
    jump day1_patient_B07

label day1_patient_B07:
    # 场 3｜INT. 急诊诊室 – 下午｜病例 B-07（轻量）
    sys "B-07：头晕站不稳。"
    
    # 镜头：隔壁躺椅上青年低声抽气。
    # TODO: 添加视觉效果
    
    # 交互 6：流程评估 or 建立连接
    menu:
        "D1-6A（理性）：评估 直立试验 立即":
            you "先别动，我测躺位与站位血压。"
            sys "疑体位性低血压。"
            call apply_action("rational")
            
        "D1-6B（人性）：同理 握手 “我在”":
            you "我在。慢慢讲。"
            # TODO: 显示B-07角色
            # show b07
            "B-07" "刚考完试……脑子嗡。"
            sys "非必要接触。"
            call apply_action("humane")
    
    # 转到日终总结
    jump day1_summary

label day1_summary:
    # 场 4｜INT. 走廊 – 傍晚（日终结算或崩溃）
    # 检查是否崩溃
    if sanity <= END_DAY_THRESHOLD:
        # 分支 B｜崩溃回滚（日终 <=15）
        hide screen hud
        play sound "audio/sfx/sfx_warn.ogg"
        scene black with hpunch
        sys "心智判定：失败。理性最优 ≠ 生存最优。循环回滚。"
        $ run_count += 1
        jump loop_reset
    else:
        # 分支 A｜正常日终（sanity > 15 且未在过程中崩溃）
        # 计算评级
        $ final_grade = get_grade(score)
        sys "Day 1 结束。效率评分：[final_grade]（依据总分）。心智阈值：稳定（[sanity]/100）。"
        you "我还撑得住……明天，试试新的平衡。"
        # TODO: 返回地图/第二天
        scene black with fade
        "第一天结束。"
        return

# 微恐效果变换
transform glitch_flicker:
    alpha 0.3
    linear 0.1 alpha 0.4
    repeat