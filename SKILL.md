---
name: "seedance-api"
description: "调用火山引擎 Seedance 2.0 视频生成 API。支持文生视频、图生视频、视频参考、音频参考、负面提示词等高级功能。当用户需要生成视频时使用此 skill。"
version: "2.0.0"
required_env_vars:
  - VOLCENGINE_API_KEY
---

# Seedance 2.0 Video API 调用

此 skill 用于调用火山引擎 Seedance 2.0 视频生成 API，支持多模态输入和高级控制功能。

**使用方式：** 用户提供视频描述或参考文件，直接调用 API 生成视频并返回本地文件。

## 🎯 核心功能

### 1. 文生视频 (Text-to-Video)
用户只需提供文本描述即可生成视频。

### 2. 图生视频 (Image-to-Video)
- 支持最多 **9 张参考图片**
- 使用标签系统 (`@Image1`, `@Image2` 等) 在提示词中引用
- 可指定角色 (character, background, style 等)

### 3. 视频参考生成
- 支持最多 **3 个参考视频**
- 控制运动、摄像机、编舞等
- 每个视频最长 15 秒，最大 50MB

### 4. 音频参考生成
- 支持最多 **3 个参考音频**
- 控制节奏、背景音乐、氛围
- 每个音频最长 15 秒，最大 15MB

### 5. 负面提示词
指定不想在视频中出现的内容，例如：
- `no blur, no text, no watermark`
- `no distortion, no artifacts`

### 6. 风格控制
- `cinematic` - 电影风格
- `anime` - 动漫风格
- `realistic` - 写实风格
- `artistic` - 艺术风格
- `documentary` - 纪录片风格

### 7. 摄像机运动
- `static` - 静态镜头
- `pan` - 左右平移
- `tilt` - 上下倾斜
- `zoom_in` / `zoom_out` - 放大/缩小
- `dolly` - 推拉镜头
- `track` - 跟踪拍摄
- `orbit` - 环绕拍摄

## 支持的模型

| 名称 | Model ID | 说明 |
|------|----------|------|
| **1.5-pro** (推荐) | `doubao-seedance-1-5-pro-251215` | 最新，支持有声视频 |
| 1.0-pro | `doubao-seedance-1-0-pro-250121` | 标准版本 |
| 1.0-pro-fast | `doubao-seedance-1-0-pro-fast-250121` | 快速模式 |
| 1.0-lite-t2v | `doubao-seedance-1-0-lite-t2v-241118` | 轻量级文生视频 |
| 1.0-lite-i2v | `doubao-seedance-1-0-lite-i2v-241118` | 轻量级图生视频 |

## 直接调用示例

### 基础文生视频
```bash
python seedance-api.py "一只小猫打哈欠"
```

### 带负面提示词
```bash
python seedance-api.py "一位女性在森林中行走" \
    -n "no blur, no text, no watermark"
```

### 风格和摄像机控制
```bash
python seedance-api.py "城市天际线" --style cinematic --camera dolly
```

### 图生视频
```bash
python seedance-api.py "小猫奔跑" -i "https://example.com/cat.jpg"
```

### 首尾帧视频
```bash
python seedance-api.py "过渡动画" \
    --first-frame "https://example.com/start.jpg" \
    --last-frame "https://example.com/end.jpg"
```

## Python 代码调用

### 基础调用
```python
from seedance_api import generate_video

result = generate_video("一只小猫打哈欠")
print(result["local_paths"])
```

### 高级调用 - 多模态参考
```python
# 使用多个参考图片
result = generate_video(
    prompt="@Image1 的角色在 @Image2 的场景中行走",
    images=[
        {"url": "character.jpg", "tag": "@Image1", "role": "character"},
        {"url": "scene.jpg", "tag": "@Image2", "role": "background"}
    ]
)

# 使用视频参考控制运动
result = generate_video(
    prompt="一位舞者表演，跟随 @Video1 的动作",
    videos=[
        {"url": "dance.mp4", "tag": "@Video1", "role": "motion"}
    ]
)

# 使用音频参考控制节奏
result = generate_video(
    prompt="烟花绽放，跟随 @Audio1 的节奏",
    audios=[
        {"url": "music.mp3", "tag": "@Audio1", "role": "background_music"}
    ]
)
```

### 风格和摄像机控制
```python
result = generate_video(
    prompt="一位女性在森林中行走",
    negative_prompt="no blur, no text, no watermark",
    style_preset="cinematic",
    camera_movement="dolly",
    motion_intensity=0.5
)
```

## 命令行参数说明

### 基础参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-m, --model` | 模型版本 | 1.5-pro |
| `-d, --duration` | 视频时长 (2-12秒) | 5 |
| `-r, --ratio` | 宽高比 | 16:9 |
| `-s, --resolution` | 分辨率 (480p/720p/1080p) | 720p |
| `-o, --output-dir` | 输出目录 | output |

### 参考文件
| 参数 | 说明 |
|------|------|
| `-i, --image` | 图生视频参考图片 URL |
| `--first-frame` | 首尾帧：首帧图片 URL |
| `--last-frame` | 首尾帧：尾帧图片 URL |

### 高级参数
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

## 使用此 Skill

当用户需要以下功能时，使用此 skill：

1. **生成视频** (文生视频)
   - "帮我生成一个xxx的视频"
   - "创建一段xxx的视频"

2. **根据图片生成视频** (图生视频)
   - "用这张图片生成视频"
   - "让这张图片动起来"

3. **视频参考生成**
   - "模仿这个视频的动作"
   - "跟随这个视频的摄像机运动"

4. **音频参考生成**
   - "配合这段音乐的节奏"
   - "跟随这个背景音的节奏"

5. **风格化视频生成**
   - "生成电影风格的视频"
   - "创建动漫风格的视频"

## 注意事项

### 调用前确认
1. 已获取火山引擎 API Key
2. 已开通 Seedance 2.0 视频生成服务
3. 账户余额充足

### API 限制
| 类型 | 最大数量 | 单文件大小 | 时长限制 |
|------|----------|-----------|---------|
| 图片 | 9 | 30MB | - |
| 视频 | 3 | 50MB | 15秒 |
| 音频 | 3 | 15MB | 15秒 |

### 超时建议
| 分辨率 | 建议超时 |
|--------|---------|
| 480p | 300-600秒 |
| 720p | 600秒 |
| 1080p | 900秒 |

## 最佳实践

1. **提示词结构**
   ```
   [主体] + [动作] + [环境] + [摄像机] + [风格] + [光照]
   ```

2. **使用负面提示词**
   ```
   no blur, no text, no watermark, no distortion, no artifacts
   ```

3. **迭代优化**
   - 从简单提示词开始
   - 逐步添加细节
   - 使用种子值复现好的结果

4. **合理设置参数**
   - 短视频 (2-4秒): 简单动作
   - 中等时长 (5-8秒): 完整动作
   - 长视频 (9-12秒): 复杂场景

## 更多信息

- 📘 [高级使用示例](EXAMPLES.md)
- 📖 [完整 README](README.md)
- 🌐 [官方文档](https://www.volcengine.com/docs/82379/1366799)

