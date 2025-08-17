# HUD界面文件

screen hud():
    # 显示当前天数、时间、理智值和分数
    frame:
        xalign 0.0
        yalign 0.0
        xpadding 10
        ypadding 10
        has vbox
        text "Day: [day] Run: [run_count]" size 20
        text "Time: [format_time(time_minutes)]" size 20
        text "Sanity: [sanity]/100" size 20
        text "Score: [score]" size 20

# 在游戏开始时显示HUD
label show_hud:
    show screen hud
    return