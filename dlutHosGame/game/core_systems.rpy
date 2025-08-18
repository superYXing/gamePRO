# 核心系统文件 - 变量、常量和核心函数

# 初始化游戏变量
default player_name = "医生"  # 玩家角色名称
default day = 1
default run_count = 1
default time_minutes = 480  # 08:00 (480分钟) - 16:00 (960分钟)
default sanity = 80
default score = 0
default diagnosis_progress = 0
default humane_count = 0

# 定义角色
define you = Character("[player_name]", color="#ffffff")
define system = Character("系统", color="#cccccc")

# 基础数值常量 (Day1适用)
# 理性动作
define R_SCORE = 10
define R_SANITY_COST = 6
define R_TIME = 3

# 人性动作
define H_SCORE = -2
define H_SANITY_GAIN = 8
define H_TIME = 5

# 微休息
define MICRO_REST_SANITY = 12
define MICRO_REST_TIME = 8
define MICRO_REST_SCORE = -4

# 崩溃判断阈值
define MELTDOWN_THRESHOLD = 0
define END_DAY_THRESHOLD = 15

# 评分等级
define GRADE_S = 90
define GRADE_A = 70
define GRADE_B = 50
# 低于50为C级

# HUD显示函数
init python:
    def format_time(minutes):
        # 将分钟转换为HH:MM格式
        hours = minutes // 60
        mins = minutes % 60
        return "{:02d}:{:02d}".format(hours, mins)
    
    def get_grade(total_score):
        # 根据总分获取评级
        if total_score >= GRADE_S:
            return "S"
        elif total_score >= GRADE_A:
            return "A"
        elif total_score >= GRADE_B:
            return "B"
        else:
            return "C"
    
    def speak_system_message(message):
        # 为系统消息触发TTS
        try:
            import tts_module
            tts_module.speak_text(message)
        except:
            # 如果TTS模块不可用，则静默失败
            pass

# 应用动作效果的公共函数
label apply_action(action_type):
    if action_type == "rational":
        $ score += R_SCORE
        $ sanity -= R_SANITY_COST
        $ time_minutes -= R_TIME
        $ diagnosis_progress += 1
        play sound "audio/sfx/sfx_chime.ogg"
        # TODO: 显示HUD分数增加提示
    elif action_type == "humane":
        $ score += H_SCORE
        $ sanity += H_SANITY_GAIN
        $ time_minutes -= H_TIME
        $ humane_count += 1
        play sound "audio/sfx/sfx_buzz.ogg"
        # TODO: 显示HUD理智值增加提示
    elif action_type == "fill":
        # 进度不足时的自动理性补救
        $ score += R_SCORE
        $ sanity -= R_SANITY_COST
        $ time_minutes -= R_TIME
        $ diagnosis_progress += 1
        play sound "audio/sfx/sfx_chime.ogg"
        # TODO: 显示HUD分数增加提示
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
        
    return

# 微休息函数
label micro_rest():
    $ score += MICRO_REST_SCORE
    $ sanity += MICRO_REST_SANITY
    $ time_minutes -= MICRO_REST_TIME
    play sound "audio/sfx/sfx_buzz.ogg"
    # TODO: 显示HUD理智值增加提示
    
    # 检查理智值是否过低需要警告
    if sanity <= 20:
        play sound "audio/sfx/sfx_warn.ogg"
        # TODO: 可能需要添加视觉效果
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    
    return

# 崩溃处理
label meltdown:
    hide screen hud
    play sound "audio/sfx/sfx_warn.ogg"
    scene black with hpunch
    "SYS" "心智判定：失败。理性最优 ≠ 生存最优。循环回滚。"
    # 触发TTS
    $ speak_system_message("心智判定：失败。理性最优 ≠ 生存最优。循环回滚。")
    $ run_count += 1
    jump loop_reset

# 循环重置
label loop_reset:
    # 重置变量
    $ time_minutes = 480
    $ sanity = 80
    $ score = 0
    $ diagnosis_progress = 0
    $ humane_count = 0
    # 重新开始第一天
    jump day1_start

# 根据分数获取评级
label grade_by_score:
    return get_grade(score)