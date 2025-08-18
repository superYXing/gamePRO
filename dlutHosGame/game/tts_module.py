import os
import sys
import time
import hashlib
import subprocess
import platform
import tempfile

# Ensure bundled python-packages are importable (for httpx in Ren'Py/runtime)
def get_current_dir():
    """Get current directory in a way that works in both Ren'Py and standalone environments"""
    try:
        # First try __file__ (works in most Python environments)
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # Fallback for environments where __file__ is not defined
        try:
            # Try to use Ren'Py's game directory if available
            import renpy
            return renpy.config.gamedir
        except (ImportError, AttributeError):
            # Final fallback to current working directory
            return os.path.abspath('.')

_current_dir = get_current_dir()
_python_packages_dir = os.path.join(_current_dir, 'python-packages')
if os.path.exists(_python_packages_dir) and _python_packages_dir not in sys.path:
    sys.path.insert(0, _python_packages_dir)

try:
    import httpx
except Exception as _e:
    httpx = None

# TTS模块，用于在游戏对话时播放语音

class TTSManager:
    def __init__(self, api_key, base_url="https://yunwu.ai/v1", model="tts-1", voice="alloy"):
        """
        初始化TTS管理器
        
        Args:
            api_key (str): OpenAI API密钥
            base_url (str): API基础URL
            model (str): TTS模型名称
            voice (str): 语音类型
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.voice = voice
        self._renpy_context = None  # 存储 Ren'Py 上下文

    def set_renpy_context(self, renpy_module):
        """设置 Ren'Py 上下文（从外部传入）"""
        self._renpy_context = renpy_module
        print(f"[TTS配置] 已设置 Ren'Py 上下文: {renpy_module}")
        self.temp_dir = tempfile.gettempdir()

    def _ensure_audio_dir(self):
        """确保音频目录存在，使用适合 Ren'Py 的路径"""
        try:
            # 在 Ren'Py 环境中使用 config.gamedir
            if 'renpy' in sys.modules:
                renpy = sys.modules['renpy']
                game_dir = renpy.config.gamedir
            else:
                game_dir = _current_dir
            audio_dir = os.path.join(game_dir, 'audio', 'tts')
        except Exception:
            # 回退到全局目录
            audio_dir = os.path.join(_current_dir, 'audio', 'tts')
        os.makedirs(audio_dir, exist_ok=True)
        return audio_dir

    def _new_filename(self, text: str):
        ts = time.strftime("%Y%m%d_%H%M%S")
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
        audio_dir = self._ensure_audio_dir()
        return os.path.join(audio_dir, f"tts_{ts}_{text_hash}.ogg")

    def _normalize_base_url(self):
        b = (self.base_url or '').rstrip('/')
        # Ensure /v1 suffix for OpenAI-compatible endpoints
        if not b.endswith('/v1'):
            b = b + '/v1'
        return b

    def _get_renpy_context(self):
        """尝试获取 Ren'Py 上下文"""
        # 方法0: 检查是否已经设置了上下文
        if self._renpy_context is not None:
            print(f"[TTS调试] 使用已存储的 renpy 上下文: {self._renpy_context}")
            return self._renpy_context
        
        # 方法1: 尝试直接导入
        try:
            import renpy
            print(f"[TTS调试] 成功导入 renpy 模块: {renpy}")
            self._renpy_context = renpy  # 缓存上下文
            return renpy
        except ImportError:
            print("[TTS调试] 无法导入 renpy 模块")
        
        # 方法2: 检查全局变量中是否有 renpy
        if 'renpy' in globals():
            print("[TTS调试] 在 globals() 中找到 renpy")
            self._renpy_context = globals()['renpy']
            return globals()['renpy']
        
        # 方法3: 检查 builtins 中是否有 renpy
        try:
            import builtins
            if hasattr(builtins, 'renpy'):
                print("[TTS调试] 在 builtins 中找到 renpy")
                self._renpy_context = builtins.renpy
                return builtins.renpy
        except:
            pass
        
        print("[TTS调试] 所有方法都无法获取 renpy 上下文")
        return None

    def _play_audio(self, filename: str):
        """使用 Ren'Py 标准方式播放音频"""
        # 确保文件存在
        if not os.path.exists(filename):
            print(f"音频文件不存在: {filename}")
            return
        
        try:
            # 获取相对于游戏目录的路径
            try:
                import renpy
                base_dir = renpy.config.basedir
                print(f"[TTS调试] 获取到 renpy.config.basedir: {base_dir}")
            except (ImportError, AttributeError):
                base_dir = _current_dir
                print(f"[TTS调试] 使用默认目录: {base_dir}")
            
            rel_path = os.path.relpath(filename, base_dir)
            # 统一使用正斜杠，符合 Ren'Py 标准
            rel_path = rel_path.replace('\\', '/')
            
            print(f"[TTS音频] 播放文件: {rel_path}")
            
            # 检查 renpy 模块的可用属性
            try:
                import renpy
                print(f"[TTS调试] renpy 模块可用属性: {[attr for attr in dir(renpy) if not attr.startswith('_')]}")
                
                # 尝试使用不同的音频播放方法
                success = False
                
                # 方法1: 尝试 renpy.music
                if hasattr(renpy, 'music'):
                    try:
                        renpy.music.play(rel_path, channel="voice", loop=False, fadein=0.1)
                        print(f"✓ [TTS音频] 通过 renpy.music 播放成功: {rel_path}")
                        success = True
                    except Exception as e:
                        print(f"[TTS音频] renpy.music 播放失败: {e}")
                else:
                    print("[TTS调试] renpy.music 不可用")
                
                # 方法2: 尝试 renpy.sound
                if not success and hasattr(renpy, 'sound'):
                    try:
                        renpy.sound.play(rel_path, channel="voice", loop=False)
                        print(f"✓ [TTS音频] 通过 renpy.sound 播放成功: {rel_path}")
                        success = True
                    except Exception as e:
                        print(f"[TTS音频] renpy.sound 播放失败: {e}")
                else:
                    print("[TTS调试] renpy.sound 不可用")
                
                # 方法3: 尝试直接调用 renpy.play（如果存在）
                if not success and hasattr(renpy, 'play'):
                    try:
                        renpy.play(rel_path, channel="voice")
                        print(f"✓ [TTS音频] 通过 renpy.play 播放成功: {rel_path}")
                        success = True
                    except Exception as e:
                        print(f"[TTS音频] renpy.play 播放失败: {e}")
                else:
                    print("[TTS调试] renpy.play 不可用")
                
                # 方法4: 尝试通过 renpy.call_screen 或其他方式
                if not success:
                    print("[TTS调试] 所有 renpy 音频方法都不可用")
                    # 检查是否有其他可能的音频相关方法
                    audio_attrs = [attr for attr in dir(renpy) if 'audio' in attr.lower() or 'music' in attr.lower() or 'sound' in attr.lower() or 'play' in attr.lower()]
                    if audio_attrs:
                        print(f"[TTS调试] 发现可能的音频相关属性: {audio_attrs}")
                
                if success:
                    return
                    
            except ImportError:
                print("[TTS调试] 无法导入 renpy 模块")
                
        except Exception as e:
            print(f"[TTS音频] Ren'Py 播放失败: {e}")
        
        # 如果 Ren'Py 播放失败，使用系统播放器
        print("[警告] Ren'Py 播放失败，使用系统播放器")
        self._system_audio_fallback(filename)
    
    def _system_audio_fallback(self, filename: str):
        """系统音频播放回退方案"""
        print(f"[TTS音频] 使用系统播放器播放: {filename}")
        system = platform.system()
        if system == 'Windows':
            try:
                # 在Windows上静默播放音频文件
                subprocess.Popen(["cmd", "/c", "start", "/min", "", filename], shell=True)
                print("✓ [TTS音频] 系统播放器启动成功")
            except Exception:
                try:
                    subprocess.Popen(["wmplayer", "/close", filename], shell=True)
                    print("✓ [TTS音频] Windows Media Player 启动成功")
                except Exception as e:
                    print(f"✗ [TTS音频] 系统播放失败: {e}")
        elif system == 'Darwin':
            try:
                subprocess.Popen(["afplay", filename])
                print("✓ [TTS音频] macOS 播放成功")
            except Exception as e:
                print(f"✗ [TTS音频] macOS 播放失败: {e}")
        else:
            # Linux 和其他系统
            for player in ("paplay", "aplay", "mpg123", "play"):
                try:
                    subprocess.Popen([player, filename])
                    print(f"✓ [TTS音频] 使用 {player} 播放成功")
                    break
                except Exception:
                    continue
            else:
                print("✗ [TTS音频] 找不到可用的音频播放器")

    def synthesize_to_file(self, text: str, voice: str = None) -> str:
        """Synthesize speech to an MP3 file and return the file path.

        Works outside Ren'Py; does not attempt playback.
        """
        if not text:
            raise ValueError("text is empty")
        if httpx is None:
            raise ImportError("httpx is not available to perform HTTP requests")

        v = (voice or self.voice or "alloy").strip()
        url = self._normalize_base_url() + "/audio/speech"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "voice": v,
            "input": text.strip(),
            "response_format": "opus",
            "format": "opus",
        }

        outfile = self._new_filename(text)
        # Stream to file to avoid large memory usage
        with httpx.Client(timeout=120, trust_env=True) as client:
            with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                with open(outfile, "wb") as f:
                    for chunk in resp.iter_bytes():
                        if chunk:
                            f.write(chunk)

        return outfile
        
    def say_callback(self, who, what, **kwargs):
        """
        用于Ren'Py的say_callback函数
        当角色说话时会调用此函数，生成并播放TTS音频
        
        Args:
            who (str): 说话者
            what (str): 说的话
            **kwargs: 其他参数
        """
        try:
            outfile = self.synthesize_to_file(str(what))
            self._play_audio(outfile)
        except Exception as e:
            print(f"TTS错误: {e}")
            # 发生错误时不中断游戏流程
            pass

# 全局TTS管理器实例
tts_manager = None

def init_tts(api_key, base_url="https://yunwu.ai/v1", model="tts-1", voice="alloy"):
    """
    初始化TTS模块
    
    Args:
        api_key (str): OpenAI API密钥
        base_url (str): API基础URL
        model (str): TTS模型名称
        voice (str): 语音类型
    """
    global tts_manager
    tts_manager = TTSManager(api_key, base_url, model, voice)

def say_callback(who, what, **kwargs):
    """
    Ren'Py say_callback函数
    """
    if tts_manager:
        tts_manager.say_callback(who, what, **kwargs)
    # 如果未初始化TTS管理器，则不执行任何操作

def speak_text(text, emotion=None, speed=0.8, voice="alloy"):
    """
    文本转语音函数，适配script.rpy中的调用方式
    返回生成的音频文件路径，而不是直接播放
    
    Args:
        text (str): 要转换为语音的文本
        emotion (str): 情感类型（当前实现中未使用）
        speed (float): 语速（当前实现中未使用）
        voice (str): 语音类型
    
    Returns:
        str: 生成的音频文件路径，如果失败则返回None
    """
    global tts_manager
    if tts_manager and text:
        # 保存原始语音设置
        original_voice = tts_manager.voice
        try:
            if voice:
                tts_manager.voice = voice
            outfile = tts_manager.synthesize_to_file(text)
            # 返回相对路径，适合Ren'Py使用
            if outfile and os.path.exists(outfile):
                # 将绝对路径转换为相对于game目录的路径
                try:
                    if 'renpy' in sys.modules:
                        renpy = sys.modules['renpy']
                        game_dir = renpy.config.gamedir
                    else:
                        game_dir = _current_dir
                    rel_path = os.path.relpath(outfile, game_dir)
                    return rel_path.replace('\\', '/')  # 使用正斜杠
                except:
                    return outfile  # 如果转换失败，返回绝对路径
            return None
        except Exception as e:
            print(f"[TTS错误] speak_text失败: {e}")
            return None
        finally:
            tts_manager.voice = original_voice
    # 如果未初始化TTS管理器，则返回None
    return None

def test_tts():
    """简单的TTS文件生成测试"""
    print("=== TTS文件生成测试 ===")
    
    try:
        # 创建TTS管理器
        manager = TTSManager(
            api_key="sk-0GszUjESD38HSUiSDFpMmRYHIeCdeunPhJ2eRLrwAT6pJZGJ",
            base_url="https://yunwu.ai/v1"
        )
        print("✓ TTS管理器创建成功")
        
        # 测试文件生成
        test_text = "这是一个TTS测试，音频文件生成功能正常"
        print(f"开始生成音频: {test_text}")
        
        import time
        start_time = time.time()
        
        output_file = manager.synthesize_to_file(test_text)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ 音频文件生成成功: {output_file}")
        print(f"✓ 生成耗时: {duration:.2f}秒")
        
        # 检查文件是否存在
        import os
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ 文件确认存在，大小: {file_size} 字节")
            print(f"✓ 文件路径: {output_file}")
        else:
            print("✗ 文件不存在")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"✗ 测试失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_tts()