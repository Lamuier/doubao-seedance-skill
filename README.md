# Seedance 视频生成 API

调用火山引擎 Seedance 视频生成模型，支持文生视频、图生视频、首尾帧视频等功能。

## 环境配置

1. 安装依赖：
   ```bash
   pip install requests python-dotenv
   ```

2. 配置环境变量：
   ```
   VOLCENGINE_API_KEY=你的火山引擎API Key
   ```

## 快速使用

```bash
python seedance_api.py "一只小猫打哈欠"
```

## 支持的模型

| 名称 | Model ID | 说明 |
|------|----------|------|
| 1.5-pro (默认) | `doubao-seedance-1-5-pro-251215` | 最新，支持有声视频 |
| 1.0-pro | `doubao-seedance-1-0-pro-250121` | |
| 1.0-pro-fast | `doubao-seedance-1-0-pro-fast-250121` | 快速模式 |
| 1.0-lite-t2v | `doubao-seedance-1-0-lite-t2v-241118` | 文生视频 |
| 1.0-lite-i2v | `doubao-seedance-1-0-lite-i2v-241118` | 图生视频 |

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| prompt | 视频描述 | 必填 |
| -m, --model | 模型版本 | 1.5-pro |
| -d, --duration | 视频时长(秒) 2-12 | 5 |
| -r, --ratio | 宽高比 | 16:9 |
| -s, --resolution | 分辨率 | 720p |
| -o, --output-dir | 输出目录 | output |
| -i, --image | 图生视频：参考图片 URL | - |
| --first-frame | 首尾帧视频：首帧图片 URL | - |
| --last-frame | 首尾帧视频：尾帧图片 URL | - |
| --no-audio | 不生成音频 | - |
| --seed | 随机种子 | - |
| --fixed | 固定摄像头 | - |
| --watermark | 添加水印 | - |

## 使用示例

```bash
# 默认 1.5-pro 模型
python seedance_api.py "一只小猫打哈欠"

# 指定时长和分辨率
python seedance_api.py "一只小猫打哈欠" -d 10 -s 1080p

# 使用 1.0-lite 模型
python seedance_api.py "一只小猫打哈欠" -m 1.0-lite-t2v

# 图生视频
python seedance_api.py "小猫奔跑" -i "https://example.com/cat.jpg"

# 首尾帧视频
python seedance_api.py "过渡动画" --first-frame "https://example.com/start.jpg" --last-frame "https://example.com/end.jpg"
```

## Python 代码调用

```python
from seedance_api import generate_video

# 简单调用
result = generate_video("一只小猫打哈欠")
print(result["local_paths"])

# 高级调用
result = generate_video(
    prompt="一只小猫打哈欠",
    model="1.5-pro",
    duration=5,
    ratio="16:9",
    resolution="720p",
    generate_audio=True,
    seed=42,
    watermark=True
)
```

## 功能说明

- **文生视频**: 输入文本提示词生成视频
- **图生视频**: 输入参考图片 + 文本提示词生成视频
- **首尾帧视频**: 输入首帧和尾帧图片生成过渡视频
- **有声视频**: 1.5-pro 模型支持自动生成音频

## 输出

生成视频自动保存到 `output` 目录。

## 注意事项

- 视频生成是异步任务，会自动轮询等待生成完成（默认超时 600 秒）
- 1.5-pro 模型支持有声视频，其他模型仅支持无声
- 生成的视频 URL 有时效性，建议及时下载保存
