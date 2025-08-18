# dlutHosGame - 医院游戏（带增强 TTS 语音合成）

一个基于 Ren'Py 的互动视觉小说游戏，内置增强 TTS 语音合成，支持 OpenAI 兼容 API，具备角色语音特色、智能情感识别和语速控制。

## 🎉 最新更新（2025-08-18）

✅ **TTS 功能完全重构**:
- 完全移除讯飞代码，仅使用 OpenAI TTS
- 支持情感和语速控制（6种情感 + 0.25x-4.0x语速）
- 每个角色都有专属语音特色
- 智能情感识别（根据对话内容自动调整）
- 使用 dotenv 安全管理 API 密钥

✅ **游戏中 TTS 已就绪**:
- 对话显示时自动播放 TTS
- 语法错误已修复，游戏可正常启动
- 所有测试脚本验证通过

## 🎮 游戏特色

- **互动式医院故事**：沉浸式的医院环境体验
- **实时语音朗读**：集成OpenAI兼容流式TTS（推荐）与讯飞TTS回退
- **智能文本处理**：自动清理Ren'Py标记，确保朗读内容清晰
- **音频文件保存**：生成的语音文件自动保存，可重复播放

## 🔧 技术栈

- **游戏引擎**：Ren'Py 8.4.1
- **语音合成**：OpenAI兼容 TTS API（如 yunwu.ai）；回退支持讯飞开放平台 TTS API
- **网络通信**：WebSocket客户端
- **音频格式**：WAV/MP3

## 📦 项目结构

```
dlutHosGame/
├── game/
│   ├── script_day1.rpy          # 主要游戏脚本
│   ├── tts_module.py            # TTS核心模块
│   ├── tts_config_template.rpy  # TTS配置模板
│   ├── core_systems.rpy         # 核心系统
│   ├── audio/
│   │   └── tts/                 # TTS生成的音频文件
│   ├── images/                  # 游戏图片资源
│   ├── gui/                     # UI资源
│   └── libs/                    # 第三方库
│       └── websocket/           # WebSocket客户端库
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 1. 环境要求

- **Ren'Py SDK**: 8.4.1或更高版本
- **Python**: 3.8+ (Ren'Py内置)
- **网络连接**: 用于TTS API调用

### 2. 下载安装

```bash
git clone https://github.com/your-username/dlutHosGame.git
cd dlutHosGame
```

### 3. 配置TTS（推荐：OpenAI兼容流式TTS）

1) 复制配置模板

- 复制 `game/tts_config_template.rpy` 为 `game/tts_config.rpy`

2) 设置系统环境变量（PowerShell 示例）

```powershell
$Env:OPENAI_BASE_URL = "https://api.yunwu.ai/v1"  # 或 https://api.openai.com/v1
$Env:OPENAI_API_KEY  = "sk-..."
$Env:OPENAI_TTS_MODEL = "gpt-4o-mini-tts"  # 或 tts-1 等
$Env:OPENAI_TTS_VOICE = "alloy"
```

3) 运行游戏：若OpenAI配置有效，将自动启用OpenAI TTS；否则尝试回退到讯飞环境变量：

- `XF_TTS_APP_ID`, `XF_TTS_API_KEY`, `XF_TTS_API_SECRET`

### 4. 运行游戏

1. 启动Ren'Py SDK
2. 选择项目文件夹
3. 点击"Launch Project"

## 🎯 TTS功能说明

### 自动语音朗读与格式

- 游戏中所有对话都会自动触发TTS朗读
- 支持中英文混合文本
- 自动过滤Ren'Py文本标记（如颜色、粗体等）

### 音频文件管理

- 生成的语音文件保存在 `game/audio/tts/` 目录
- 文件命名格式：`tts_时间戳_文本哈希.mp3`（OpenAI流式）或 `.wav/.mp3`（回退）
- 若需要WAV→MP3转换，建议安装 ffmpeg（回退路径使用）

### 调试功能

在游戏中按 `Shift + O` 打开控制台，可以看到TTS相关日志：

```
✓ TTS真实API初始化成功
[TTS游戏] 朗读: 欢迎回来，编号 D-001
TTS音频已保存: game/audio/tts/tts_xxxxx.wav
```

## 📋 开发说明

### 核心模块

#### `tts_module.py`
- OpenAI流式TTS实现：`client.audio.speech.create(...).stream_to_file(...)`
- 兼容回退讯飞WebSocket方案
- 音频文件管理与播放（Ren'Py优先，系统回退）

#### `script_day1.rpy`
- 游戏主脚本
- TTS回调函数
- 角色定义

#### `tts_config.rpy`
- TTS配置和初始化
- API凭证管理
- 开关控制

### 添加新角色

```python
define new_character = Character("角色名", what_color="#颜色值", callback=say_callback)
```

### 自定义TTS设置

在 `tts_module.py` 的 `BusinessArgs` 中可以修改语音参数：

```python
self.BusinessArgs = {
    "aue": "raw", 
    "auf": "audio/L16;rate=16000", 
    "vcn": "x4_yezi",  # 发音人
    "tte": "utf8"
}
```

可选发音人：
- `x4_yezi` - 叶子（女声）
- `x_xiaofeng` - 小峰（男声）
- `aisxping` - 小萍（女声）

## 🔒 安全说明

- 不要在仓库中硬编码任何API密钥
- 使用 `game/tts_config_template.rpy` 模板与系统环境变量
- `.gitignore` 已排除 `game/tts_config.rpy`、音频与测试脚本

## 🐛 故障排除

### 常见问题

1. **TTS初始化失败**
   - 确认已设置 `OPENAI_API_KEY`（或讯飞环境变量）
   - 检查 `OPENAI_BASE_URL` 是否可用（yunwu.ai 或官方OpenAI）
   - 若使用OpenAI流式，请安装 `openai` Python 包（由Ren'Py运行环境提供）

2. **音频文件未生成**
   - 检查 `game/audio/tts/` 目录权限
   - 确认TTS API调用成功
   - 查看磁盘空间是否充足

3. **WebSocket连接错误（仅讯飞回退）**
   - 检查防火墙设置与服务状态
   - 尝试重新初始化

### 日志文件

- `log.txt` - Ren'Py运行日志
- `errors.txt` - 错误信息
- `traceback.txt` - 详细错误追踪

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 开发规范

- 遵循Python PEP8编码规范
- 为新功能添加注释和文档
- 测试新功能确保稳定性
- 不要提交包含真实API密钥的文件

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Ren'Py](https://www.renpy.org/) - 强大的视觉小说引擎
- [讯飞开放平台](https://www.xfyun.cn/) - 提供优质的TTS服务
- [websocket-client](https://github.com/websocket-client/websocket-client) - WebSocket客户端库

## 📞 联系方式

- 项目主页：[GitHub Repository](https://github.com/your-username/dlutHosGame)
- 问题反馈：[Issues](https://github.com/your-username/dlutHosGame/issues)

---

**注意**：使用本项目前请确保你已获得讯飞开放平台的有效API凭证，并遵守相关服务条款。

## 🔄 更新日志

### v1.1.0 (2025-08-18)
- ✅ 新增 OpenAI 兼容流式TTS（yunwu.ai 等）
- ✅ 环境变量配置与安全指引
- ✅ 兼容回退至讯飞TTS
- ✅ 文档与模板更新
