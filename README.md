# Seedance 2.0 视频生成 API

调用火山引擎 Seedance 2.0 视频生成模型，支持文生视频、图生视频、视频参考、音频参考、负面提示词等高级功能。

## ✨ 主要功能

- 🎬 **文生视频** - 从文本描述生成视频
- 🖼️ **图生视频** - 支持最多 9 张参考图片，带标签系统
- 🎥 **视频参考** - 支持最多 3 个参考视频，控制运动和摄像机
- 🎵 **音频参考** - 支持最多 3 个参考音频，控制节奏和氛围
- 🚫 **负面提示词** - 指定不想出现的内容
- 🎨 **风格预设** - 电影、动漫、写实、艺术、纪录片等风格
- 📹 **摄像机运动** - 静态、平移、推拉、跟踪、环绕等
- 🔄 **自动重试** - 智能错误处理和指数退避
- 📊 **进度回调** - 实时监控生成进度
- 🎯 **种子复现** - 使用种子值复现结果

## 📋 快速开始

### 1. 安装依赖

```bash
pip install requests python-dotenv
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
VOLCENGINE_API_KEY=你的火山引擎API密钥
```

### 3. 基础使用

```bash
python seedance-api.py "一只小猫打哈欠"
```

## 📖 详细文档

- **[高级使用示例](EXAMPLES.md)** - 详细的代码示例和最佳实践
- **[Skill 配置](SKILL.md)** - Claude 技能集成配置

## 支持的模型

| 名称 | Model ID | 说明 |
|------|----------|------|
| **1.5-pro** (推荐) | `doubao-seedance-1-5-pro-251215` | 最新模型，支持有声视频 |
| 1.0-pro | `doubao-seedance-1-0-pro-250121` | 标准版本 |
| 1.0-pro-fast | `doubao-seedance-1-0-pro-fast-250121` | 快速模式 |
| 1.0-lite-t2v | `doubao-seedance-1-0-lite-t2v-241118` | 轻量级文生视频 |
| 1.0-lite-i2v | `doubao-seedance-1-0-lite-i2v-241118` | 轻量级图生视频 |

## 命令行参数

### 基础参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 视频描述提示词 | 必填 |
| `-m, --model` | 模型版本 | 1.5-pro |
| `-d, --duration` | 视频时长 (2-12秒) | 5 |
| `-r, --ratio` | 宽高比 | 16:9 |
| `-s, --resolution` | 分辨率 (480p/720p/1080p) | 720p |
| `-o, --output-dir` | 输出目录 | output |

### 参考文件

| 参数 | 说明 |
|------|------|
| `-i, --image` | 图生视频参考图片 URL |
| `--first-frame` | 首尾帧视频：首帧图片 URL |
| `--last-frame` | 首尾帧视频：尾帧图片 URL |

### 高级参数 (新)

| 参数 | 说明 | 选项 |
|------|------|------|
| `-n, --negative-prompt` | 负面提示词 | - |
| `--style` | 风格预设 | cinematic, anime, realistic, artistic, documentary |
| `--camera` | 摄像机运动 | static, pan, tilt, zoom_in, zoom_out, dolly, track, orbit |
| `--motion` | 运动强度 | 0.0-1.0 |

### 其他参数

| 参数 | 说明 |
|------|------|
| `--no-audio` | 不生成音频 |
| `--seed` | 随机种子 (用于复现) |
| `--fixed` | 固定摄像头 |
| `--watermark` | 添加水印 |
| `--debug` | 启用调试日志 |
| `--timeout` | 超时时间 (秒) |

## 使用示例

### 1. 基础文生视频

```bash
# 使用默认参数
python seedance-api.py "一只小猫打哈欠"

# 指定时长和分辨率
python seedance-api.py "一只小猫打哈欠" -d 10 -s 1080p
```

### 2. 使用负面提示词

```bash
python seedance-api.py "一位女性在森林中行走" \
    -n "no blur, no text, no watermark"
```

### 3. 风格和摄像机控制

```bash
# 电影风格 + 推拉镜头
python seedance-api.py "城市天际线" --style cinematic --camera dolly

# 动漫风格 + 静态镜头
python seedance-api.py "魔法少女" --style anime --camera static
```

### 4. 图生视频

```bash
python seedance-api.py "小猫奔跑" -i "https://example.com/cat.jpg"
```

### 5. 首尾帧视频

```bash
python seedance-api.py "过渡动画" \
    --first-frame "https://example.com/start.jpg" \
    --last-frame "https://example.com/end.jpg"
```

### 6. 使用种子复现结果

```bash
# 第一次生成会输出使用的种子值
python seedance-api.py "日落时分的海滩"
# 输出: 使用的种子: 12345

# 使用相同种子复现
python seedance-api.py "日落时分的海滩" --seed 12345
```

## Python 代码调用

### 基础调用

```python
from seedance_api import generate_video

# 简单调用
result = generate_video("一只小猫打哈欠")
print(result["local_paths"])
```

### 高级调用

```python
from seedance_api import generate_video

# 带负面提示词和风格控制
result = generate_video(
    prompt="一位女性在森林中优雅地行走",
    model="1.5-pro",
    duration=8,
    ratio="16:9",
    resolution="720p",
    negative_prompt="no blur, no text, no watermark",
    style_preset="cinematic",
    camera_movement="dolly",
    generate_audio=True,
    seed=42
)

print(f"视频 URL: {result['video_url']}")
print(f"本地路径: {result['local_paths']}")
print(f"使用的种子: {result['seed_used']}")
```

### 多模态参考

```python
# 使用多个参考图片
result = generate_video(
    prompt="@Image1 的角色在 @Image2 的场景中行走",
    images=[
        {"url": "https://example.com/character.jpg", "tag": "@Image1", "role": "character"},
        {"url": "https://example.com/scene.jpg", "tag": "@Image2", "role": "background"}
    ]
)

# 使用视频参考控制运动
result = generate_video(
    prompt="一位舞者表演，跟随 @Video1 的动作节奏",
    videos=[
        {"url": "https://example.com/dance.mp4", "tag": "@Video1", "role": "motion"}
    ]
)

# 使用音频参考控制节奏
result = generate_video(
    prompt="烟花绽放，跟随 @Audio1 的音乐节奏",
    audios=[
        {"url": "https://example.com/music.mp3", "tag": "@Audio1", "role": "background_music"}
    ]
)
```

### 进度监控

```python
def on_progress(status, progress):
    print(f"状态: {status}, 进度: {progress}%")

result = generate_video(
    prompt="一段视频",
    on_progress=on_progress
)
```

## 功能特性

### 1. 多模态参考支持

- **图片参考**: 最多 9 张，每张最大 30MB
- **视频参考**: 最多 3 个，每个最大 50MB，最长 15 秒
- **音频参考**: 最多 3 个，每个最大 15MB，最长 15 秒
- **标签系统**: 使用 `@Image1`, `@Video1`, `@Audio1` 在提示词中引用

### 2. 风格控制

| 风格 | 说明 |
|------|------|
| `cinematic` | 电影级画质，专业光影和色彩 |
| `anime` | 日本动漫风格 |
| `realistic` | 真实照片风格 |
| `artistic` | 艺术化、风格化 |
| `documentary` | 纪录片风格 |

### 3. 摄像机运动

| 运动类型 | 说明 |
|---------|------|
| `static` | 静态镜头，无运动 |
| `pan` | 左右平移 |
| `tilt` | 上下倾斜 |
| `zoom_in` | 放大推进 |
| `zoom_out` | 缩小拉远 |
| `dolly` | 推拉镜头 (物理移动) |
| `track` | 跟踪拍摄 |
| `orbit` | 环绕拍摄 |

### 4. 智能错误处理

- ✅ HTTP 状态码识别 (401, 402, 403, 429, 500 等)
- ✅ 指数退避重试机制
- ✅ 详细的错误信息和建议
- ✅ 超时自动处理

### 5. 自适应轮询

- 初始 2 秒快速轮询
- 逐步增加轮询间隔
- 优化 API 调用次数

## API 限制

### 参数范围

| 参数 | 范围 | 默认值 |
|------|------|--------|
| duration | 2-12 秒 | 5 |
| ratio | 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive | 16:9 |
| resolution | 480p, 720p, 1080p | 720p |
| motion_intensity | 0.0-1.0 | 自动 |

### 文件限制

| 类型 | 最大数量 | 单文件大小 | 时长限制 |
|------|----------|-----------|---------|
| 图片 | 9 | 30MB | - |
| 视频 | 3 | 50MB | 15秒 |
| 音频 | 3 | 15MB | 15秒 |

### 建议超时时间

| 分辨率 | 建议超时 |
|--------|---------|
| 480p | 300-600秒 |
| 720p | 600秒 |
| 1080p | 900秒 |

## 最佳实践

### 1. 提示词建议结构

```
[主体] + [动作] + [环境] + [摄像机] + [风格] + [光照]
```

示例:
```python
prompt = "一位年轻女性 | 悠闲散步 | 樱花街道 | 跟踪拍摄 | 电影风格 | 日落光线"
```

### 2. 迭代优化

从简单开始，逐步添加细节：

```python
# 第一次: 基础
result1 = generate_video("一只猫", duration=4)

# 第二次: 添加动作
result2 = generate_video("一只猫在打哈欠", duration=4)

# 第三次: 完善细节
result3 = generate_video(
    "一只猫在阳光下舒适地打哈欠",
    duration=4,
    style_preset="cinematic",
    camera_movement="static"
)
```

### 3. 使用负面提示词

常用模板：
```python
negative_prompt = "no blur, no text, no watermark, no distortion, no artifacts"
```

### 4. 进度监控

```python
def on_progress(status, progress):
    if status == "processing":
        print(f"生成中: {progress}%")
    elif status == "succeeded":
        print("生成完成!")

result = generate_video("提示词", on_progress=on_progress)
```

## 错误处理

### 常见错误和解决方案

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 401 | API Key 无效 | 检查 VOLCENGINE_API_KEY 环境变量 |
| 402 | 余额不足 | 前往控制台充值 |
| 403 | 未开通服务 | 开通 Seedance 服务 |
| 429 | 请求频率超限 | 稍后重试 |
| 超时 | 生成时间过长 | 降低分辨率或缩短时长 |

### 示例代码

```python
try:
    result = generate_video("一只小猫")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"生成失败: {e}")
```

## 输出格式

生成成功后返回的数据结构：

```python
{
    "success": True,
    "task_id": "abc123",
    "model": "doubao-seedance-1-5-pro-251215",
    "video_url": "https://...",
    "thumbnail_url": "https://...",  # 缩略图
    "local_paths": ["output/video.mp4"],
    "duration": 5,
    "ratio": "16:9",
    "seed_used": 12345,  # 使用的种子
    "cost": 0.05,  # 消耗费用
    "metadata": {}  # 额外元数据
}
```

## 注意事项

1. **视频生成是异步任务**，会自动轮询等待完成
2. **1.5-pro 模型支持有声视频**，其他模型仅支持无声
3. **生成的 URL 有时效性**，建议及时下载保存
4. **使用种子值可以复现结果**，适合调试和优化
5. **高分辨率需要更长的生成时间**，建议适当增加超时时间

## 更多资源

- 📘 [高级使用示例](EXAMPLES.md) - 详细的代码示例和最佳实践
- 🎯 [Skill 配置](SKILL.md) - Claude 技能集成
- 🌐 [官方 SDK 文档](https://www.volcengine.com/docs/82379/1366799)
- 📖 [API 参考文档](https://www.volcengine.com/docs/82379/1520757)
- 📚 [使用指南](https://www.volcengine.com/docs/82379/1521309)

## License

MIT License

