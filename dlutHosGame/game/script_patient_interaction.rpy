# 患者互动分支剧情脚本
# 包含三种初始选择后的详细分支和结局

# 定义角色
define patient = Character("患者", color="#a0a0ff")
define doctor = Character("[player_name]", color="#ffffff")
define system = Character("系统", color="#cccccc")

# 情况一分支 (您最初选择了【标准】，她问了费用)
label patient_branch_standard:
    patient "哦……好，好的……那我……我先过去问问……"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “好的，问清楚了再回来找我开单子。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "好的，问清楚了再回来找我开单子。"
            
        "【人性】 “别着急，慢慢来。如果费用有问题，我们再想别的办法。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "别着急，慢慢来。如果费用有问题，我们再想别的办法。"
            
        "【理性】 “请快一点，后面还有很多病人在等。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST * 1.5  # 更大理智消耗
            $ time_minutes -= R_TIME
            doctor "请快一点，后面还有很多病人在等。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

label patient_branch_standard_2:
    patient "哎，好的好的！谢谢您医生，太谢谢您了！"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “不客气，这是我应该做的。现在去缴费检查吧。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "不客气，这是我应该做的。现在去缴费检查吧。"
            
        "【人性】 “不用谢，看你放心了我就放心了。快去吧，早点检查完早点安心。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "不用谢，看你放心了我就放心了。快去吧，早点检查完早点安心。"
            
        "【理性】 “不用客气，我们尽快完成检查，这才是最重要的。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "不用客气，我们尽快完成检查，这才是最重要的。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

label patient_branch_standard_3:
    patient "治……治疗费用？医生，您的意思是……我真的得了什么重病吗？"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “请不要误解，我只是在陈述一种可能性。先做检查。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "请不要误解，我只是在陈述一种可能性。先做检查。"
            
        "【人性】 “对不起，是我说话太直接了，吓到你了。我不是说你得了重病，只是想说明检查的重要性。别怕。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN * 1.5  # 更大理智恢复
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "对不起，是我说话太直接了，吓到你了。我不是说你得了重病，只是想说明检查的重要性。别怕。"
            
        "【理性】 “现在讨论这个为时过早，一切等数据出来再说。请不要浪费时间在无端的猜测上。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST * 2  # 更大理智消耗
            $ time_minutes -= R_TIME
            doctor "现在讨论这个为时过早，一切等数据出来再说。请不要浪费时间在无端的猜测上。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

# 情况二分支 (您最初选择了【人性】，她寻求 reassurance)
label patient_branch_humane:
    patient "……所以，还是有可能是……不好的病，是吗？"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “任何可能性都存在，所以我们才需要检查来排除。请去缴费吧。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "任何可能性都存在，所以我们才需要检查来排除。请去缴费吧。"
            
        "【人性】 “别往坏处想，绝大多数人的检查结果都是好的。我们只是做最坏的打算，尽最大的努力。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "别往坏处想，绝大多数人的检查结果都是好的。我们只是做最坏的打算，尽最大的努力。"
            
        "【理性】 “是的，存在低概率的可能性。现在，我们需要通过检查将这个概率降到零。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "是的，存在低概率的可能性。现在，我们需要通过检查将这个概率降到零。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

label patient_branch_humane_2:
    patient "嗯！好！医生，我听您的！只要您说没事，我就放心了。"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “好的，那我们现在就开始检查流程吧。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "好的，那我们现在就开始检查流程吧。"
            
        "【人性】 “有你这份信任，我更有信心了。去吧，检查完告诉我结果。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN * 1.5  # 更大理智恢复
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "有你这份信任，我更有信心了。去吧，检查完告诉我结果。"
            
        "【理性】 “很好，医患间的信任能提高诊疗效率。请尽快完成检查。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "很好，医患间的信任能提高诊疗效率。请尽快完成检查。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

label patient_branch_humane_3:
    patient "……哦，对不起医生，是我说错话了……那……那就检查吧。"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “没关系，我们继续流程。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "没关系，我们继续流程。"
            
        "【人性】 “你没说错什么，只是我需要更客观的依据。别紧张。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "你没说错什么，只是我需要更客观的依据。别紧张。"
            
        "【理性】 “很好，我们达成了共识。请去检查。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "很好，我们达成了共识。请去检查。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

# 情况三分支 (您最初选择了【理性】，她害怕病情严重)
label patient_branch_rational:
    patient "……常规的啊……好，我知道了医生。那就……查吧。"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “嗯，去吧。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "嗯，去吧。"
            
        "【人性】 “检查结果出来后，不管怎么样，我都会跟你详细解释的。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "检查结果出来后，不管怎么样，我都会跟你详细解释的。"
            
        "【理性】 “是的，这是最标准的流程。尽快完成。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "是的，这是最标准的流程。尽快完成。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

label patient_branch_rational_2:
    patient "……嗯，嗯，谢谢医生，听您这么说我……我好多了。"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “不客气，去检查吧。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "不客气，去检查吧。"
            
        "【人性】 “这就对了。放轻松，没事的。我在。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN * 1.5  # 更大理智恢复
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "这就对了。放轻松，没事的。我在。"
            
        "【理性】 “良好的心态有助于后续的诊疗。请保持。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "良好的心态有助于后续的诊疗。请保持。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

label patient_branch_rational_3:
    patient "找……找问题？所以肯定是有问题的是不是？"
    
    menu:
        "您的最终选项是："
        
        "【标准】 “您误会了我的意思。‘找问题’是医生的工作语言，意思是‘进行诊断’。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST
            $ time_minutes -= R_TIME
            doctor "您误会了我的意思。'找问题'是医生的工作语言，意思是'进行诊断'。"
            
        "【人性】 “对不起对不起，是我用词不当，让你吓坏了！我的意思是，我们要‘排除’问题，证明你是健康的。我向你保证，现在没有任何证据表明你有问题。”":
            $ score += H_SCORE
            $ sanity += H_SANITY_GAIN * 2  # 更大理智恢复
            $ time_minutes -= H_TIME
            $ humane_count += 1
            doctor "对不起对不起，是我用词不当，让你吓坏了！我的意思是，我们要'排除'问题，证明你是健康的。我向你保证，现在没有任何证据表明你有问题。"
            
        "【理性】 “你的恐慌是非理性的。在没有数据之前，任何结论都是臆测。请立刻停止猜测，执行检查。”":
            $ score += R_SCORE
            $ sanity -= R_SANITY_COST * 2  # 更大理智消耗
            $ time_minutes -= R_TIME
            doctor "你的恐慌是非理性的。在没有数据之前，任何结论都是臆测。请立刻停止猜测，执行检查。"
    
    # 检查是否崩溃
    if sanity <= MELTDOWN_THRESHOLD:
        call meltdown
    else:
        jump patient_interaction_end

# 结束标签
label patient_interaction_end:
    # 这里可以添加一些后续剧情或返回主流程的代码
    system "患者互动环节结束。"
    return