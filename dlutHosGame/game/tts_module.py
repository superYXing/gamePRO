# -*- coding: utf-8 -*-
import os
import sys

# 添加libs目录到Python路径
libs_path = os.path.join(os.path.dirname(__file__), 'libs')
websocket_path = os.path.join(libs_path, 'websocket', 'websocket-client-1.8.0')
if os.path.exists(websocket_path):
    sys.path.insert(0, websocket_path)

import tempfile
import subprocess
import hashlib
import base64
import hmac
import json
import ssl
import threading
import time
from datetime import datetime
from urllib.parse import urlencode
# 使用email.utils替代wsgiref.handlers
from email.utils import formatdate
from time import mktime

# 导入websocket客户端
WebSocketApp = None
try:
    # 先尝试从本地websocket-client库导入
    websocket_client_path = os.path.join(os.path.dirname(__file__), 'libs', 'websocket', 'websocket-client-1.8.0', 'websocket')
    if os.path.exists(websocket_client_path):
        sys.path.insert(0, os.path.dirname(websocket_client_path))
        import websocket as ws_client
        if hasattr(ws_client, 'WebSocketApp'):
            WebSocketApp = ws_client.WebSocketApp
            print("Using local websocket-client library")
        else:
            # 尝试直接导入WebSocketApp
            from websocket import WebSocketApp
            print("Imported WebSocketApp from local library")
    else:
        # 回退到系统库
        from websocket import WebSocketApp
        print("Using system websocket library")
except ImportError as e:
    print(f"Warning: websocket-client library not found: {e}")
    WebSocketApp = None
except Exception as e:
    print(f"Error setting up WebSocket: {e}")
    WebSocketApp = None

# Status constants for TTS frames
STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2

class TTSClient:
    def __init__(self, app_id, api_key, api_secret):
        # Check if credentials are provided
        if not app_id or not api_key or not api_secret:
            raise ValueError("TTS credentials not properly configured")
            
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.audio_data = bytearray()
        self.is_playing = False
        self.playback_thread = None

    def get_tts_url(self, text):
        """
        Generate TTS URL with authentication
        """
        class Ws_Param(object):
            def __init__(self, APPID, APIKey, APISecret, Text):
                self.APPID = APPID
                self.APIKey = APIKey
                self.APISecret = APISecret
                self.Text = Text

                # Common parameters
                self.CommonArgs = {"app_id": self.APPID}
                # Business parameters - can be customized for voice, speed, etc.
                self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x4_yezi", "tte": "utf8"}
                self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}

            def create_url(self):
                url = 'wss://tts-api.xfyun.cn/v2/tts'
                now = datetime.now()
                # 使用email.utils.formatdate替代wsgiref.handlers.format_date_time
                date = formatdate(timeval=None, localtime=False, usegmt=True)

                signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
                signature_origin += "date: " + date + "\n"
                signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
                
                signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
                signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

                authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                    self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
                authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
                
                v = {
                    "authorization": authorization,
                    "date": date,
                    "host": "ws-api.xfyun.cn"
                }
                
                url = url + '?' + urlencode(v)
                return url

        ws_param = Ws_Param(self.app_id, self.api_key, self.api_secret, text)
        return ws_param.create_url()

    def on_message(self, ws, message):
        """
        Handle incoming WebSocket messages
        """
        try:
            message = json.loads(message)
            code = message["code"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            
            if code != 0:
                errMsg = message["message"]
                print(f"TTS Error: {errMsg}, code: {code}")
                ws.close()
            else:
                # Append audio data
                self.audio_data.extend(audio)
                
                # If this is the last frame, save and play
                if status == 2:
                    ws.close()
                    self.save_and_play_audio()
                    
        except Exception as e:
            print(f"Error processing TTS message: {e}")

    def on_error(self, ws, error):
        """
        Handle WebSocket errors
        """
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code=None, close_msg=None):
        """
        Handle WebSocket closure
        """
        print("TTS WebSocket connection closed")

    def on_open(self, ws):
        """
        Handle WebSocket opening
        """
        def run(*args):
            d = {
                "common": {"app_id": self.app_id},
                "business": {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x4_yezi", "tte": "utf8"},
                "data": {"status": 2, "text": str(base64.b64encode(self.current_text.encode('utf-8')), "UTF8")}
            }
            d = json.dumps(d)
            ws.send(d)
            
        threading.Thread(target=run).start()

    def save_and_play_audio(self):
        """
        Save the audio data to a file and play it
        """
        if not self.audio_data:
            return
            
        # Create audio directory if it doesn't exist
        audio_dir = os.path.join(os.path.dirname(__file__), 'audio', 'tts')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate filename based on current time and text hash
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        text_hash = hashlib.md5(self.current_text.encode('utf-8')).hexdigest()[:8]
        
        # Save as MP3 format
        mp3_filename = os.path.join(audio_dir, f"tts_{timestamp}_{text_hash}.mp3")
        wav_filename = os.path.join(audio_dir, f"tts_{timestamp}_{text_hash}.wav")
        
        # First convert to WAV, then to MP3
        self.convert_to_wav(self.audio_data, wav_filename)
        
        # Convert WAV to MP3 if possible
        if self.convert_wav_to_mp3(wav_filename, mp3_filename):
            # Use MP3 file
            final_filename = mp3_filename
            # Clean up WAV file
            try:
                os.remove(wav_filename)
            except:
                pass
        else:
            # Use WAV file as fallback
            final_filename = wav_filename
        
        print(f"TTS音频已保存: {final_filename}")
        
        # Play the audio file
        self.play_audio(final_filename)
        
        # Clear audio data
        self.audio_data = bytearray()

    def convert_to_wav(self, raw_audio_data, output_filename):
        """
        Convert raw audio data to WAV format
        """
        try:
            import wave
            with wave.open(output_filename, 'wb') as wav_file:
                wav_file.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
                wav_file.writeframes(raw_audio_data)
            return True
        except Exception as e:
            print(f"Error converting to WAV: {e}")
            return False

    def convert_wav_to_mp3(self, wav_filename, mp3_filename):
        """
        Convert WAV file to MP3 format using ffmpeg or other tools
        """
        try:
            # Try using ffmpeg first
            result = subprocess.run([
                'ffmpeg', '-i', wav_filename, '-acodec', 'mp3', 
                '-ab', '128k', '-ac', '1', '-ar', '16000', 
                mp3_filename, '-y'  # -y to overwrite existing files
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                print(f"Successfully converted to MP3: {mp3_filename}")
                return True
            else:
                print(f"FFmpeg conversion failed: {result.stderr}")
                
        except FileNotFoundError:
            print("FFmpeg not found, trying alternative conversion...")
            
        # Try using Windows built-in tools or Python libraries as fallback
        try:
            # Alternative: use pydub if available
            from pydub import AudioSegment
            from pydub.utils import which
            
            # Load WAV file
            audio = AudioSegment.from_wav(wav_filename)
            
            # Export as MP3
            audio.export(mp3_filename, format="mp3", bitrate="128k")
            print(f"Successfully converted to MP3 using pydub: {mp3_filename}")
            return True
            
        except ImportError:
            print("pydub not available for MP3 conversion")
        except Exception as e:
            print(f"Error converting with pydub: {e}")
        
        print("MP3 conversion failed, will use WAV format")
        return False

    def play_audio(self, filename):
        """
        Play audio file using Ren'Py's audio system or system player
        """
        try:
            # Try to use Ren'Py's audio system if available
            try:
                import renpy
                # Convert to relative path for Ren'Py
                relative_path = os.path.relpath(filename, renpy.config.basedir)
                renpy.sound.play(relative_path, channel="voice")
                print(f"Playing TTS audio via Ren'Py: {relative_path}")
            except:
                # Fallback to system audio player
                self.play_with_system(filename)
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def play_with_system(self, filename):
        """
        Play audio using system player as fallback
        """
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Use Windows Media Player or built-in sound player
                subprocess.Popen(["powershell", "-c", f"(New-Object Media.SoundPlayer '{filename}').PlaySync()"], 
                               shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            elif system == "Darwin":  # macOS
                subprocess.run(["afplay", filename], check=True)
            elif system == "Linux":
                # Try common Linux audio players
                players = ["paplay", "aplay", "mpg123", "play"]
                for player in players:
                    try:
                        subprocess.run([player, filename], check=True)
                        break
                    except FileNotFoundError:
                        continue
            
            print(f"Playing TTS audio via system: {filename}")
        except Exception as e:
            print(f"Error playing audio with system player: {e}")

    def synthesize_and_play(self, text):
        """
        Synthesize text to speech and play it
        """
        if not text or self.is_playing:
            return
            
        self.current_text = text
        self.is_playing = True
        
        try:
            if WebSocketApp is None:
                raise Exception("WebSocketApp not available")
                
            url = self.get_tts_url(text)
            ws = WebSocketApp(url,
                            on_message=self.on_message,
                            on_error=self.on_error,
                            on_close=self.on_close)
            ws.on_open = self.on_open
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            print(f"Error in TTS synthesis: {e}")
        finally:
            self.is_playing = False

# Global TTS client instance
tts_client = None

def init_tts(app_id, api_key, api_secret):
    """
    Initialize the TTS client
    """
    global tts_client
    try:
        tts_client = TTSClient(app_id, api_key, api_secret)
        return True
    except ValueError as e:
        print(f"TTS API凭证无效，使用模拟模式: {e}")
        # 创建一个模拟TTS客户端
        tts_client = MockTTSClient()
        return False
    except Exception as e:
        print(f"Error initializing TTS: {e}")
        return False

class MockTTSClient:
    """
    Mock TTS client for testing when real API is not available
    """
    def __init__(self):
        self.is_playing = False
    
    def synthesize_and_play(self, text):
        """
        Mock synthesis - just print the text that would be spoken
        """
        if not text or self.is_playing:
            return
            
        self.is_playing = True
        try:
            print(f"[TTS模拟] 播放: {text}")
            # 模拟音频播放时间
            time.sleep(len(text) * 0.1)  # 大约每个字符0.1秒
        except Exception as e:
            print(f"Mock TTS error: {e}")
        finally:
            self.is_playing = False

def speak_text(text):
    """
    Speak the given text using TTS
    """
    global tts_client
    if tts_client and text:
        # Run in a separate thread to avoid blocking the game
        threading.Thread(target=tts_client.synthesize_and_play, args=(text,)).start()