# dlutHosGame - 医院游戏（带TTS语音合成）

一个基于Ren'Py的互动视觉小说游戏，集成了讯飞语音合成(TTS)功能，支持实时朗读对话文本。

## 🎮 游戏特色

- **互动式医院故事**：沉浸式的医院环境体验
- **实时语音朗读**：集成讯飞TTS，自动朗读所有对话
- **智能文本处理**：自动清理Ren'Py标记，确保朗读内容清晰
- **音频文件保存**：生成的语音文件自动保存，可重复播放

## 🔧 技术栈

- **游戏引擎**：Ren'Py 8.4.1
- **语音合成**：讯飞开放平台 TTS API
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

### 3. 配置TTS API

1. 访问[讯飞开放平台](https://www.xfyun.cn/services/online_tts)注册账号
2. 创建语音合成应用，获取API凭证
3. 复制 `game/tts_config_template.rpy` 为 `game/tts_config.rpy`
4. 在 `tts_config.rpy` 中填入你的API凭证：

```python
TTS_APP_ID = "your_app_id_here"
TTS_API_KEY = "your_api_key_here"  
TTS_API_SECRET = "your_api_secret_here"
```

### 4. 运行游戏

1. 启动Ren'Py SDK
2. 选择项目文件夹
3. 点击"Launch Project"

## 🎯 TTS功能说明

### 自动语音朗读

- 游戏中所有对话都会自动触发TTS朗读
- 支持中英文混合文本
- 自动过滤Ren'Py文本标记（如颜色、粗体等）

### 音频文件管理

- 生成的语音文件保存在 `game/audio/tts/` 目录
- 文件命名格式：`tts_时间戳_文本哈希.wav`
- 支持WAV和MP3格式（需要ffmpeg）

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
- TTS客户端实现
- WebSocket通信
- 音频文件处理
- 错误处理和重试

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

- **API密钥保护**：真实的API凭证不会被提交到版本控制
- **配置模板**：使用模板文件避免意外泄露
- **测试文件**：包含真实密钥的测试文件已在`.gitignore`中排除

## 🐛 故障排除

### 常见问题

1. **TTS初始化失败**
   - 检查API凭证是否正确
   - 确认网络连接正常
   - 查看控制台错误信息

2. **音频文件未生成**
   - 检查 `game/audio/tts/` 目录权限
   - 确认TTS API调用成功
   - 查看磁盘空间是否充足

3. **WebSocket连接错误**
   - 检查防火墙设置
   - 确认讯飞服务状态
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

### v1.0.0 (2025-08-17)
- ✅ 初始版本发布
- ✅ 集成讯飞TTS API
- ✅ 实现自动语音朗读
- ✅ 支持音频文件保存
- ✅ 完整的错误处理机制
- ✅ 文本标记清理功能
