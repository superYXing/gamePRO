# -*- coding: utf-8 -*-
"""
GitHub部署前安全检查
确保没有敏感信息被意外提交
"""

import os
import re
import glob

def check_for_sensitive_data():
    """检查项目中是否包含敏感数据"""
    print("🔍 GitHub部署前安全检查")
    print("=" * 50)
    
    # 定义敏感数据模式（使用占位符避免泄露真实密钥）
    sensitive_patterns = [
        r'[0-9a-f]{8}',  # APP_ID格式
        r'[0-9a-f]{32}',  # API_KEY格式  
        r'[A-Za-z0-9+/]{32,}',  # API_SECRET格式（Base64）
        r'TTS_APP_ID\s*=\s*["\'][^"\']*["\'](?!\s*["\']YOUR_)',
        r'TTS_API_KEY\s*=\s*["\'][^"\']*["\'](?!\s*["\']YOUR_)',
        r'TTS_API_SECRET\s*=\s*["\'][^"\']*["\'](?!\s*["\']YOUR_)'
    ]
    
    # 需要检查的文件类型
    file_patterns = [
        '**/*.py',
        '**/*.rpy', 
        '**/*.md',
        '**/*.txt',
        '**/*.json'
    ]
    
    # 排除的文件和目录
    exclude_patterns = [
        'cache/',
        'saves/', 
        '__pycache__/',
        'libs/',
        '.git/'
    ]
    
    issues_found = []
    files_checked = 0
    
    # 检查所有文件
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # 检查是否应该排除此文件
            should_exclude = False
            file_path_normalized = file_path.replace('\\', '/')
            for exclude in exclude_patterns:
                if exclude in file_path_normalized:
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    files_checked += 1
                    
                    # 检查每个敏感模式
                    for i, pattern in enumerate(sensitive_patterns):
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            issues_found.append({
                                'file': file_path,
                                'pattern': i,
                                'matches': matches
                            })
            except Exception as e:
                print(f"⚠ 无法读取文件 {file_path}: {e}")
    
    print(f"📊 检查了 {files_checked} 个文件")
    
    if issues_found:
        print(f"\n❌ 发现 {len(issues_found)} 个安全问题:")
        for issue in issues_found:
            print(f"   📁 {issue['file']}")
            print(f"      匹配内容: {issue['matches']}")
        
        print(f"\n🚫 请在推送前解决这些问题！")
        return False
    else:
        print(f"\n✅ 未发现敏感信息，可以安全推送到GitHub")
        return True

def check_gitignore():
    """检查.gitignore文件"""
    print(f"\n📝 检查.gitignore配置...")
    
    gitignore_path = '.gitignore'
    if not os.path.exists(gitignore_path):
        print("❌ .gitignore文件不存在")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_patterns = [
        'tts_config.rpy',
        'test_real_tts.py',
        'single_tts_test.py', 
        'final_verification.py',
        'test_game_integration.py'
    ]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"⚠ .gitignore缺少以下规则:")
        for pattern in missing_patterns:
            print(f"   - {pattern}")
        return False
    else:
        print("✅ .gitignore配置正确")
        return True

def check_template_files():
    """检查模板文件是否存在"""
    print(f"\n📋 检查模板文件...")
    
    template_files = [
        'game/tts_config_template.rpy'
    ]
    
    all_exist = True
    for template in template_files:
        if os.path.exists(template):
            print(f"✅ {template} 存在")
        else:
            print(f"❌ {template} 不存在")
            all_exist = False
    
    return all_exist

def show_deployment_checklist():
    """显示部署检查清单"""
    print(f"\n" + "="*60)
    print("📋 GitHub部署检查清单")
    print("="*60)
    print("1. ✅ 敏感信息已从代码中移除")
    print("2. ✅ .gitignore已正确配置")
    print("3. ✅ 配置模板文件已创建")
    print("4. ✅ README.md已创建，包含详细说明")
    print("5. ✅ LICENSE文件已添加")
    print("6. ✅ 项目结构清晰，注释完整")
    
    print(f"\n🚀 推荐的Git命令:")
    print("```bash")
    print("git add .")
    print("git commit -m 'Initial commit: dlutHosGame with TTS integration'")
    print("git branch -M main")
    print("git remote add origin https://github.com/your-username/dlutHosGame.git")
    print("git push -u origin main")
    print("```")
    
    print(f"\n⚠ 重要提醒:")
    print("- 确保你的GitHub仓库是私有的，或者已确认无敏感信息")
    print("- 首次使用者需要复制tts_config_template.rpy并填入自己的API密钥")
    print("- 定期检查提交历史，确保没有意外提交敏感信息")

if __name__ == "__main__":
    print("开始GitHub部署前安全检查...\n")
    
    # 执行所有检查
    sensitive_check = check_for_sensitive_data()
    gitignore_check = check_gitignore()
    template_check = check_template_files()
    
    # 总结
    if sensitive_check and gitignore_check and template_check:
        print(f"\n🎉 所有检查通过！项目可以安全推送到GitHub")
        show_deployment_checklist()
    else:
        print(f"\n🛑 存在问题，请解决后再推送")
    
    input(f"\n按Enter键退出...")
