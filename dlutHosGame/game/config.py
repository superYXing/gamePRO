"""
配置管理模块
统一管理环境变量和配置项
"""

import os
import sys

# 确保可以导入bundled的python-packages
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
    from dotenv import load_dotenv
except Exception as _e:
    load_dotenv = None

class Config:
    """配置管理类"""
    
    def __init__(self):
        self._load_env()
    
    def _load_env(self):
        """加载环境变量"""
        if load_dotenv is not None:
            # 尝试从当前目录加载.env文件
            env_path = os.path.join(_current_dir, '.env')
            if os.path.exists(env_path):
                load_dotenv(env_path)
            
            # 尝试从上级目录加载.env文件
            parent_env_path = os.path.join(os.path.dirname(_current_dir), '.env')
            if os.path.exists(parent_env_path):
                load_dotenv(parent_env_path)
    
    @property
    def api_key(self):
        """获取API密钥"""
        return os.getenv("OPENAI_API_KEY", os.getenv("API_KEY", "sk-0GszUjESD38HSUiSDFpMmRYHIeCdeunPhJ2eRLrwAT6pJZGJ"))
    
    @property
    def base_url(self):
        """获取API基础URL"""
        return os.getenv("OPENAI_BASE_URL", os.getenv("BASE_URL", "https://yunwu.ai/v1"))
    
    @property
    def model_name(self):
        """获取模型名称"""
        return os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    @property
    def tts_model(self):
        """获取TTS模型名称"""
        return os.getenv("OPENAI_TTS_MODEL", "tts-1")
    
    @property
    def tts_voice(self):
        """获取TTS语音类型"""
        return os.getenv("OPENAI_TTS_VOICE", "alloy")
    
    @property
    def debug_mode(self):
        """获取调试模式"""
        return os.getenv("GAME_DEBUG", "false").lower() == "true"

# 全局配置实例
config = Config()

# 向后兼容的变量
API_KEY = config.api_key
BASE_URL = config.base_url
MODEL_NAME = config.model_name
