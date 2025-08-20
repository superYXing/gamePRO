# 《完美医生》- AI 医患对话体验（Ren'Py + 实时TTS）

《完美医生》是一款基于 Ren'Py 的互动视觉小说式医学体验项目，集成了 AI 医患对话（医生/患者均可由 AI 驱动）与实时 TTS 语音合成。项目支持 OpenAI 兼容 API（如 yunwu.ai），通过 .env + config.py 统一管理密钥与模型配置，可直接在 Ren'Py 中运行体验。

## 🎉 最新更新（2025-08-19）

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

✅ **AI 对话增强**:
- 患者 AI 会基于医生发言上下文生成回应（角色校正：仅使用 system/user/assistant）
- 统一角色规范，避免 Chat Completions 500 错误
- 支持并行生成多种医生回复风格（理性/人性/中性）

## 🎮 游戏特色

- **互动式医院故事**：沉浸式的医院环境体验
- **实时语音朗读**：集成 OpenAI 兼容 TTS（yunwu.ai 等）
- **智能文本处理**：自动清理Ren'Py标记，确保朗读内容清晰
- **音频文件保存**：生成的语音文件自动保存，可重复播放
- **AI 医患对话**：医生选项由 AI 生成，患者由 AI 连贯回应

## 🔧 技术栈

- **游戏引擎**：Ren'Py 8.4.1
- **语音合成**：OpenAI 兼容 TTS API（yunwu.ai）
- **网络通信**：WebSocket客户端
- **音频格式**：WAV/MP3
- **AI 对话**：Chat Completions（gpt-4o-mini，示例）

## 📁 项目结构

```
《完美医生》/
├── game/                 # 游戏主目录
│   ├── audio/            # 音频文件
│   ├── images/           # 图像资源
│   ├── python-packages/  # Python 第三方包
│   ├── config.py         # 统一配置（从 .env 读取）
│   └── *.rpy             # 游戏脚本文件
├── test/                 # 测试脚本
└── README.md             # 项目说明文档
```

## 🚀 快速开始

### 克隆仓库

```bash
git clone https://github.com/your-username/PerfectDoctor.git
cd PerfectDoctor
```

### 配置 API/模型（集中化）

项目提供统一的 `game/config.py` 配置模块，并通过 `.env` 管理敏感信息（推荐）。

1) 复制根目录或 `game/` 目录下的 `.env.example` 为 `.env`

2) 编辑 `.env`：

```
# OpenAI 兼容 API
OPENAI_BASE_URL=https://yunwu.ai/v1
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# TTS 配置
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy

# 对话模型
MODEL_NAME=gpt-4o-mini
```

3) 不要在 .rpy 或 .py 中硬编码密钥；`day1.rpy`、`script.rpy`、`ai_module.py` 均已改为从 `config.py` 读取。

提示：`.env` 已在 `.gitignore` 中忽略，避免泄露密钥。
1) 复制根目录或 `game/` 目录下的 `.env.example` 为 `.env`

2) 编辑 `.env`：

```
# OpenAI 兼容 API
OPENAI_BASE_URL=https://yunwu.ai/v1
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# TTS 配置
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
- `game/test_env_config.py`: 验证 .env 与 config.py 生效
- `game/test_ai_integration.py`: 端到端 AI 对话集成测试

# 对话模型
MODEL_NAME=gpt-4o-mini
```

## ❓ 常见问题（FAQ）

- Q: 第二轮开始报 500？
	- A: 确保传入 Chat Completions 的消息仅包含 `system/user/assistant` 三种角色。本项目已在 `ai_module.py` 中进行角色标准化与末条 user 校正。
- Q: TTS 无声或卡顿？
	- A: 检查音量通道（music/sound/voice），确认音频文件已生成到 `game/audio/tts/`。
- Q: 密钥未生效？
	- A: 确认 `.env` 位置（根目录或 game/），并确保未提交到版本库；`config.py` 会自动加载。

3) 代码中不要硬编码密钥。Ren'Py 脚本 `day1.rpy`、`script.rpy` 与 `ai_module.py` 已改为自动从 `config.py` 读取。

提示：`.env` 已在 `.gitignore` 中忽略，避免泄露密钥。

### 运行游戏

在 Ren'Py 启动器中选择项目并点击 "启动"。

## 🧪 测试

项目包含多个测试脚本：

- `test_tts_api.py`: 测试 TTS API 连接
- `test/test_ai_manager.py`: 测试 AI 管理器
- `quick_ai_test.py`: 快速 AI 测试

## 🛠️ 构建

使用 Ren'Py 启动器的 "构建" 功能生成发布版本。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

## 📞 联系方式

- 项目主页：[GitHub Repository](https://github.com/your-username/PerfectDoctor)
- 问题反馈：[Issues](https://github.com/your-username/PerfectDoctor/issues)

---

**注意**：请遵守所使用 OpenAI 兼容服务的相关条款与配额限制。

## 🔄 更新日志

### v1.2.0 (2025-08-19)
- ✅ 集中化配置（config.py + .env），移除硬编码密钥
- ✅ AI 患者对话角色标准化，避免 500 错误
- ✅ README 重构，补充快速上手与 FAQ

### v1.1.0 (2025-08-18)
- ✅ 新增 OpenAI 兼容 TTS（yunwu.ai 等）
- ✅ 环境变量配置与安全指引
- ✅ 文档与模板更新
