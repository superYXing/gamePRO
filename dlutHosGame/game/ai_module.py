"""
AI功能模块，实现调用GPT-5-2025-08-07模型的接口
"""

import os
import sys
import json
from typing import Optional, Dict, Any

# 确保可以导入bundled的httpx
def get_current_dir():
    """Get current directory in a way that works in both Ren'Py and standalone environments"""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        try:
            import renpy
            return renpy.config.gamedir
        except (ImportError, AttributeError):
            return os.path.abspath('.')

_current_dir = get_current_dir()
_python_packages_dir = os.path.join(_current_dir, 'python-packages')
if os.path.exists(_python_packages_dir) and _python_packages_dir not in sys.path:
    sys.path.insert(0, _python_packages_dir)

try:
    import httpx
except Exception as _e:
    httpx = None

try:
    import openai
except Exception as _e:
    openai = None

# 导入配置模块
try:
    from config import config, API_KEY, BASE_URL, MODEL_NAME
except Exception as _e:
    # 如果配置模块不可用，使用传统方式
    try:
        from dotenv import load_dotenv
        if load_dotenv is not None:
            load_dotenv()
    except Exception:
        pass
    
    # 从环境变量读取API配置，提供默认值作为备用
    API_KEY = os.getenv("OPENAI_API_KEY", os.getenv("API_KEY", "sk-0GszUjESD38HSUiSDFpMmRYHIeCdeunPhJ2eRLrwAT6pJZGJ"))
    BASE_URL = os.getenv("OPENAI_BASE_URL", os.getenv("BASE_URL", "https://yunwu.ai/v1"))
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

class AIManager:
    """
    AI管理类，封装对GPT-5-2025-08-07模型的调用
    """
    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL):
        """
        初始化AI管理器
        
        Args:
            api_key (str): API密钥
            base_url (str): API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.san_value = 100  # 初始化SAN值为100
        self.san_history = []  # 记录SAN值变化历史
        # 存储患者对话历史
        self.patient_messages = []
        
        # 初始化 OpenAI 客户端
        if openai is not None:
            self.openai_client = openai.OpenAI(
                base_url=base_url,
                api_key=api_key
            )
        else:
            self.openai_client = None
        
        # 保留 httpx 客户端作为备用
        if httpx is not None:
            self.client = httpx.Client(timeout=120)
        else:
            self.client = None
    
    def generate_response(self, messages: list, temperature: float = 0.7, option_type: str = "理性") -> Optional[str]:
        """
        生成AI响应，根据选项类型调整prompt
        
        Args:
            messages (list): 对话历史
            temperature (float): 生成温度参数
            option_type (str): 选项类型（理性/人性/平淡）
            
        Returns:
            Optional[str]: 生成的响应文本，失败时返回None
        """
        # 根据选项类型调整prompt
        style_prompt = {
            "理性": "你是一个冷静、理性的医生，专注于医学事实和数据分析。回答字数在40字左右",
            "人性": "你是一个充满同理心的医生，关注患者的情感需求。回答字数在40字左右",
            "平淡": "你是一个普通医生，给出常规的医疗建议。回答字数在40字左右"
        }.get(option_type, "理性")
        
        # 添加风格提示到消息历史
        if not messages or messages[0].get('role') != 'system':
            messages.insert(0, {"role": "system", "content": style_prompt})
        
        try:
            # 优先使用 OpenAI 客户端
            if self.openai_client is not None:
                response = self.openai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=512
                )
                return response.choices[0].message.content
            else:
                # 备用方案：使用 httpx
                if self.client is None:
                    raise ImportError("Neither OpenAI nor httpx client is available")
                
                url = f"{self.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": MODEL_NAME,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 512
                }
                
                response = self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json().get('choices', [{}])[0].get('message', {}).get('content')
        except Exception as e:
            print(f"AI请求失败: {e}")
            return None
    
    def generate_patient_response(self, messages: list, patient_info: dict, conversation_context: str = "") -> Optional[str]:
        """
        生成患者AI响应，基于test_patient_ai_openai.py中的成功方法
        
        Args:
            messages (list): 对话历史
            patient_info (dict): 患者信息
            conversation_context (str): 对话上下文
            
        Returns:
            Optional[str]: 生成的患者响应文本，失败时返回None
        """
        # 设置患者AI的系统提示（与test_patient_ai_openai.py保持一致）
        patient_system_prompt = f"""你是患者{patient_info.get('name', '李秀兰')}，{patient_info.get('gender', '女')}，{patient_info.get('age', 39)}岁。
主要症状：{patient_info.get('symptoms', '头晕，起身偶有眼前发黑、心悸症状')}
既往病史：{patient_info.get('history', '无病史')}

性格与冲突点：性格急躁，对身体不适容忍度低，就医时因担忧病情，对医生问诊节奏、检查安排等易产生不满，
会急切打断医生，强调自己难受却没快速明确诊断，进而和医生起言语冲突，比如质疑医生能力、抱怨就医流程繁琐耽
误自己时间，凸显医患互动张力，为剧情添冲突。

你需要扮演这个患者，根据症状和医生的话语进行自然的回应。要表现出患者的担心、疑问和对治疗的关切。
回答要充满情绪色彩，字数控制在60字左右，体现患者的真实感受和疑问。{conversation_context}"""

        # 构建消息（与test_patient_ai_openai.py的方法一致）
        patient_messages = messages.copy()
        if not patient_messages or patient_messages[0].get('role') != 'system':
            patient_messages.insert(0, {"role": "system", "content": patient_system_prompt})
        else:
            patient_messages[0]["content"] = patient_system_prompt
        
        # 修正所有消息的角色为合法角色（system/user/assistant）
        normalized_messages = []
        for i, msg in enumerate(patient_messages):
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                # 保持 system 角色
                normalized_messages.append({"role": "system", "content": content})
            elif role in ["user", "doctor", "医生"]:
                # 医生的话转为 user 角色
                normalized_messages.append({"role": "user", "content": content})
            elif role in ["assistant", "patient", "患者"]:
                # 患者的话转为 assistant 角色
                normalized_messages.append({"role": "assistant", "content": content})
            else:
                # 未知角色默认为 user
                print(f"[警告] 未知角色 '{role}'，转换为 user")
                normalized_messages.append({"role": "user", "content": content})
        
        # 确保最后一条消息是医生的话（user角色）
        if normalized_messages and normalized_messages[-1].get("role") != "user":
            last = normalized_messages[-1]
            doc_text = last.get("content", "")
            # 替换最后一条消息为医生的话
            normalized_messages[-1] = {
                "role": "user",
                "content": f"医生：{doc_text}\n请按系统设定，以患者身份用约60字回应。"
            }
        elif normalized_messages and normalized_messages[-1].get("role") == "user":
            # 如果已经是user角色，确保格式正确
            last_content = normalized_messages[-1].get("content", "")
            if not last_content.startswith("医生："):
                normalized_messages[-1] = {
                    "role": "user", 
                    "content": f"医生：{last_content}\n请按系统设定，以患者身份用约60字回应。"
                }
        
        # 使用标准化后的消息
        patient_messages = normalized_messages
        
        # 调试信息
        debug_text = "\n\n".join(f"[{m.get('role','')}] {m.get('content','')}" for m in patient_messages)
        print("=== ChatCompletions final input ===\n" + debug_text)
        
        try:
            print(f"[AI患者模块] 正在生成患者回应...")
            
            # 优先使用 OpenAI 客户端
            if self.openai_client is not None:
                response = self.openai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=patient_messages,
                    temperature=0.8,
                    max_tokens=500
                )
                patient_response = response.choices[0].message.content.strip()
            else:
                # 备用方案：使用 httpx
                if self.client is None:
                    raise ImportError("Neither OpenAI nor httpx client is available")
                
                url = f"{self.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": MODEL_NAME,
                    "messages": patient_messages,
                    "temperature": 0.8,
                    "max_tokens": 500
                }
                
                response = self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                patient_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            print(f"[AI患者模块] 患者回应生成成功")
            
            # 添加医生和患者的消息到对话历史中
            for msg in messages:
                if msg not in self.patient_messages:
                    self.patient_messages.append(msg)
            self.patient_messages.append({"role": "assistant", "content": patient_response})
            
            return patient_response
            
        except Exception as e:
            print(f"[AI患者模块] 生成失败: {e}")
            return f"医生，我很担心我的{patient_info.get('symptoms', '症状')}，您能帮我看看吗？"
    
    def generate_simple_patient_response(self, doctor_message: str, patient_info: dict) -> Optional[str]:
        """
        生成患者AI响应的简化版本
        
        Args:
            doctor_message (str): 医生的消息
            patient_info (dict): 患者信息
            
        Returns:
            Optional[str]: 生成的患者响应文本，失败时返回None
        """
        # 设置患者AI的系统提示（与test_patient_ai_openai.py保持一致）
        patient_system_prompt = f"""你是患者{patient_info.get('name', '李秀兰')}，{patient_info.get('gender', '女')}，{patient_info.get('age', 39)}岁。
主要症状：{patient_info.get('symptoms', '头晕，起身偶有眼前发黑、心悸症状')}
既往病史：{patient_info.get('history', '无病史')}

性格与冲突点：性格急躁，对身体不适容忍度低，就医时因担忧病情，对医生问诊节奏、检查安排等易产生不满，
会急切打断医生，强调自己难受却没快速明确诊断，进而和医生起言语冲突，比如质疑医生能力、抱怨就医流程繁琐耽
误自己时间，凸显医患互动张力，为剧情添冲突。

你需要扮演这个患者，根据症状和医生的话语进行自然的回应。要表现出患者的担心、疑问和对治疗的关切。
回答要充满情绪色彩，字数控制在60字左右，体现患者的真实感受和疑问。"""

        # 构建消息（与test_patient_ai_openai.py的方法一致）
        messages = [
            {"role": "system", "content": patient_system_prompt},
            {"role": "user", "content": f"医生：{doctor_message}\n请按系统设定，以患者身份用约60字回应。"}
        ]
        
        try:
            print(f"[AI患者模块] 正在生成患者回应...")
            
            # 优先使用 OpenAI 客户端
            if self.openai_client is not None:
                response = self.openai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=200
                )
                patient_response = response.choices[0].message.content.strip()
            else:
                # 备用方案：使用 httpx
                if self.client is None:
                    raise ImportError("Neither OpenAI nor httpx client is available")
                
                url = f"{self.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": MODEL_NAME,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 200
                }
                
                response = self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                patient_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            print(f"[AI患者模块] 患者回应生成成功")
            
            # 添加医生和患者的消息到对话历史中
            self.patient_messages.append({"role": "user", "content": f"医生：{doctor_message}"})
            self.patient_messages.append({"role": "assistant", "content": patient_response})
            
            return patient_response
            
        except Exception as e:
            print(f"[AI患者模块] 生成失败: {e}")
            return f"医生，我很担心我的{patient_info.get('symptoms', '症状')}，您能帮我看看吗？"
    
    def calculate_san(self, choice_type: str) -> int:
        """
        简单的SAN值计算算法
        
        Args:
            choice_type (str): 选择的选项类型
            
        Returns:
            int: SAN值变化量
        """
        san_changes = {
            "理性": -5,  # 理性选择减少SAN值
            "人性": -2,  # 人性选择小幅减少SAN值
            "中性": -10  # 平淡选择大幅减少SAN值
        }
        
        change = san_changes.get(choice_type, -5)
        self.san_value = max(0, min(100, self.san_value + change))
        self.san_history.append((choice_type, change, self.san_value))
        return change

# 全局AI管理器实例
ai_manager = None

def init_ai():
    """
    初始化AI模块
    """
    global ai_manager
    try:
        ai_manager = AIManager()
    except Exception as e:
        print(f"AI初始化失败: {e}")
        ai_manager = None

# ... 其他相关功能可根据需求扩展 ...

def test_ai():
    """简单的AI测试接口"""
    print("测试AI接口...")
    
    try:
        # 创建AI管理器
        manager = AIManager()
        print("✓ AI管理器创建成功")
        
        # 发送测试消息
        test_message = [{"role": "user", "content": "你好，这是一个测试"}]
        response = manager.generate_response(test_message)
        
        if response:
            print("✓ AI回复成功:")
            print(f"  {response}")
            return True
        else:
            print("✗ AI回复失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_ai()