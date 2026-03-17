# Seedance 2.0 高级使用示例

本文档提供 Seedance 2.0 API 的高级使用示例和最佳实践。

## 目录

- [基础使用](#基础使用)
- [多模态参考](#多模态参考)
- [负面提示词](#负面提示词)
- [风格控制](#风格控制)
- [摄像机运动](#摄像机运动)
- [提示词工程](#提示词工程)
- [最佳实践](#最佳实践)
- [错误处理](#错误处理)
- [常见问题](#常见问题)

---

## 基础使用

### 1. 简单的文生视频

```python
from seedance_api import generate_video

# 最简单的调用
result = generate_video("一只小猫打哈欠")
print(f"视频已保存: {result['local_paths']}")
```

```bash
# 命令行调用
python seedance-api.py "一只小猫打哈欠"
```

### 2. 指定参数

```python
result = generate_video(
    prompt="一只小猫在阳光下打哈欠",
    model="1.5-pro",
    duration=8,
    ratio="16:9",
    resolution="1080p",
    generate_audio=True,
    seed=42  # 用于复现结果
)
```

```bash
python seedance-api.py "一只小猫在阳光下打哈欠" \
    -m 1.5-pro \
    -d 8 \
    -r 16:9 \
    -s 1080p \
    --seed 42
```

---

## 多模态参考

### 1. 图生视频 (简单模式)

```python
# 单张参考图
result = generate_video(
    prompt="小猫在草地上奔跑",
    image="https://example.com/cat.jpg"
)
```

```bash
python seedance-api.py "小猫在草地上奔跑" -i "https://example.com/cat.jpg"
```

### 2. 多图片参考 (高级模式)

```python
# 最多支持 9 张参考图片，使用标签系统
result = generate_video(
    prompt="@Image1 的角色穿着 @Image2 的服装，在 @Image3 的场景中行走",
    images=[
        {
            "url": "https://example.com/character.jpg",
            "tag": "@Image1",
            "role": "character"
        },
        {
            "url": "https://example.com/outfit.jpg",
            "tag": "@Image2",
            "role": "style"
        },
        {
            "url": "https://example.com/scene.jpg",
            "tag": "@Image3",
            "role": "background"
        }
    ]
)
```

### 3. 视频参考 (运动控制)

```python
# 使用参考视频控制运动和摄像机
result = generate_video(
    prompt="一位舞者优雅地表演，跟随 @Video1 的舞蹈动作和节奏",
    videos=[
        {
            "url": "https://example.com/dance_reference.mp4",
            "tag": "@Video1",
            "role": "motion"  # motion: 运动参考
        }
    ],
    duration=10
)
```

**视频参考限制:**
- 最多 3 个参考视频
- 每个视频最长 15 秒
- 每个文件最大 50MB
- 支持的角色: `motion`, `camera`, `choreography`

### 4. 音频参考 (节奏同步)

```python
# 使用音频参考控制视频节奏
result = generate_video(
    prompt="烟花在夜空中绽放，跟随 @Audio1 的音乐节奏",
    audios=[
        {
            "url": "https://example.com/music.mp3",
            "tag": "@Audio1",
            "role": "background_music"  # 背景音乐
        }
    ]
)
```

**音频参考限制:**
- 最多 3 个参考音频
- 每个音频最长 15 秒
- 每个文件最大 15MB
- 支持的角色: `background_music`, `rhythm`, `ambient`

### 5. 混合多模态参考

```python
# 同时使用图片、视频和音频参考
result = generate_video(
    prompt="""
    @Image1 的角色在舞台上表演，
    跟随 @Video1 的舞蹈动作，
    配合 @Audio1 的音乐节奏
    """,
    images=[
        {"url": "https://example.com/character.jpg", "tag": "@Image1", "role": "character"}
    ],
    videos=[
        {"url": "https://example.com/dance.mp4", "tag": "@Video1", "role": "motion"}
    ],
    audios=[
        {"url": "https://example.com/music.mp3", "tag": "@Audio1", "role": "background_music"}
    ]
)
```

---

## 负面提示词

使用负面提示词可以指定不想在视频中出现的内容。

### 基础示例

```python
result = generate_video(
    prompt="一位女性在森林中行走",
    negative_prompt="no blur, no text, no watermark, no distortion"
)
```

```bash
python seedance-api.py "一位女性在森林中行走" \
    -n "no blur, no text, no watermark, no distortion"
```

### 常用负面提示词

```python
# 避免画质问题
negative_prompt = "no blur, no noise, no distortion, no artifacts"

# 避免不需要的元素
negative_prompt = "no text, no watermark, no logo, no subtitle"

# 避免风格问题
negative_prompt = "no cartoon, no anime, no 3d render, no painting"

# 避免内容问题
negative_prompt = "no violence, no gore, no nsfw content"

# 组合使用
negative_prompt = "no blur, no text, no watermark, no distortion, no cartoon"
```

---

## 风格控制

### 风格预设

```python
# 电影风格
result = generate_video(
    prompt="一辆汽车在公路上疾驰",
    style_preset="cinematic"
)

# 动漫风格
result = generate_video(
    prompt="一个魔法少女挥舞魔杖",
    style_preset="anime"
)

# 写实风格
result = generate_video(
    prompt="城市街道的日常生活",
    style_preset="realistic"
)

# 艺术风格
result = generate_video(
    prompt="抽象的色彩流动",
    style_preset="artistic"
)

# 纪录片风格
result = generate_video(
    prompt="野生动物在草原上",
    style_preset="documentary"
)
```

```bash
# 命令行使用
python seedance-api.py "一辆汽车在公路上疾驰" --style cinematic
```

**支持的风格:**
- `cinematic` - 电影风格，专业的光影和色彩
- `anime` - 日本动漫风格
- `realistic` - 真实照片风格
- `artistic` - 艺术化、风格化
- `documentary` - 纪录片风格

---

## 摄像机运动

### 摄像机运动类型

```python
# 静态镜头
result = generate_video(
    prompt="一朵花在风中摇曳",
    camera_movement="static"
)

# 平移
result = generate_video(
    prompt="城市天际线全景",
    camera_movement="pan"
)

# 推拉镜头
result = generate_video(
    prompt="从远处推近到人物特写",
    camera_movement="dolly"
)

# 放大
result = generate_video(
    prompt="逐渐放大到细节",
    camera_movement="zoom_in"
)

# 缩小
result = generate_video(
    prompt="从特写拉远到全景",
    camera_movement="zoom_out"
)

# 跟踪
result = generate_video(
    prompt="跟随奔跑的运动员",
    camera_movement="track"
)

# 环绕
result = generate_video(
    prompt="360度环绕展示产品",
    camera_movement="orbit"
)
```

```bash
python seedance-api.py "城市天际线全景" --camera pan
```

**摄像机运动选项:**
- `static` - 静态镜头，无运动
- `pan` - 左右平移
- `tilt` - 上下倾斜
- `zoom_in` - 放大推进
- `zoom_out` - 缩小拉远
- `dolly` - 推拉镜头（物理移动）
- `track` - 跟踪拍摄
- `orbit` - 环绕拍摄

---

## 提示词工程

### 提示词结构

建议使用以下结构组织提示词:

```
[主体] + [动作] + [环境/背景] + [摄像机] + [风格] + [光照]
```

### 示例

```python
# 结构化的提示词
prompt = """
主体: 一位年轻女性
动作: 在街道上悠闲地散步
环境: 樱花盛开的日本街道
摄像机: 跟踪拍摄，平滑运动
风格: 电影级画质
光照: 温暖的日落光线
"""

# 精简版
prompt = "一位年轻女性 | 悠闲散步 | 樱花街道 | 跟踪拍摄 | 电影风格 | 日落光线"
```

### 提示词最佳实践

1. **具体而精确**
   ```python
   # ❌ 不好
   prompt = "一只狗"

   # ✅ 好
   prompt = "一只金毛猎犬在公园草地上欢快地奔跑，阳光明媚，跟踪拍摄"
   ```

2. **包含运动描述**
   ```python
   # ❌ 缺少运动
   prompt = "一辆汽车"

   # ✅ 描述运动
   prompt = "一辆红色跑车在山路上疾驰，摄像机从侧面跟拍"
   ```

3. **指定摄像机视角**
   ```python
   prompt = "从低角度仰拍，一位舞者在舞台上旋转跳跃"
   ```

4. **添加环境细节**
   ```python
   prompt = "在薄雾弥漫的森林中，一只鹿缓缓走过，清晨的阳光透过树叶洒下"
   ```

5. **控制节奏和情绪**
   ```python
   prompt = "快节奏的城市街头，人群匆忙穿梭，延时摄影效果"
   ```

---

## 最佳实践

### 1. 迭代优化

从简单开始，逐步添加细节:

```python
# 第一次: 基础版本
result1 = generate_video("一只猫", duration=4)

# 第二次: 添加动作
result2 = generate_video("一只猫在打哈欠", duration=4, seed=result1['seed_used'])

# 第三次: 添加环境
result3 = generate_video(
    "一只猫在阳光下舒适地打哈欠",
    duration=4,
    seed=result2['seed_used']
)

# 第四次: 添加摄像机和风格
result4 = generate_video(
    "一只猫在阳光下舒适地打哈欠",
    duration=4,
    camera_movement="static",
    style_preset="cinematic",
    seed=result3['seed_used']
)
```

### 2. 使用种子复现结果

```python
# 第一次生成
result = generate_video("日落时分的海滩")
print(f"使用的种子: {result['seed_used']}")

# 使用相同种子复现
result2 = generate_video(
    "日落时分的海滩",
    seed=result['seed_used']  # 使用之前的种子
)
```

### 3. 时长建议

```python
# 短视频 (2-4秒): 适合简单动作
result = generate_video("一个人眨眼", duration=2)

# 中等时长 (5-8秒): 适合完整动作
result = generate_video("一个人从坐到站起", duration=6)

# 长视频 (9-12秒): 适合复杂场景
result = generate_video("一段完整的舞蹈表演", duration=12)
```

### 4. 分辨率选择

```python
# 快速预览: 480p
result = generate_video("测试提示词", resolution="480p")

# 标准质量: 720p (推荐)
result = generate_video("正式内容", resolution="720p")

# 高质量: 1080p (耗时更长)
result = generate_video("最终成品", resolution="1080p", timeout=900)
```

### 5. 进度监控

```python
def on_progress(status, progress):
    print(f"状态: {status}, 进度: {progress}%")

result = generate_video(
    "一段视频",
    on_progress=on_progress
)
```

---

## 错误处理

### 1. 基本错误处理

```python
from seedance_api import generate_video

try:
    result = generate_video("一只小猫")
    print(f"成功: {result['video_url']}")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"生成失败: {e}")
```

### 2. 处理特定错误

```python
try:
    result = generate_video("一只小猫", duration=15)  # 超出范围
except ValueError as e:
    if "时长" in str(e):
        print("时长参数错误，使用默认值")
        result = generate_video("一只小猫")
    else:
        raise
```

### 3. 超时处理

```python
try:
    result = generate_video(
        "复杂场景",
        resolution="1080p",
        timeout=600
    )
except Exception as e:
    if "超时" in str(e):
        print("生成超时，尝试降低分辨率")
        result = generate_video(
            "复杂场景",
            resolution="720p",
            timeout=600
        )
    else:
        raise
```

---

## 常见问题

### Q1: 如何提高视频质量?

```python
result = generate_video(
    prompt="详细、具体的提示词描述",
    resolution="1080p",
    style_preset="cinematic",
    negative_prompt="no blur, no noise, no artifacts"
)
```

### Q2: 如何控制视频中的运动?

```python
# 方法 1: 使用摄像机运动参数
result = generate_video(
    "场景描述",
    camera_movement="static",  # 减少运动
    camera_fixed=True
)

# 方法 2: 使用运动强度
result = generate_video(
    "场景描述",
    motion_intensity=0.3  # 0.0-1.0，越小运动越少
)
```

### Q3: 如何保持角色一致性?

```python
# 使用参考图片
result = generate_video(
    prompt="@Image1 的角色在不同场景中的表现",
    images=[
        {"url": "character_ref.jpg", "tag": "@Image1", "role": "character"}
    ]
)
```

### Q4: 生成的视频与预期不符怎么办?

1. 使用负面提示词排除不想要的元素
2. 添加更具体的描述
3. 使用参考文件引导生成
4. 调整风格预设和摄像机参数
5. 多次迭代，使用种子复现好的结果

### Q5: 如何优化生成速度?

```python
# 使用快速模型
result = generate_video("提示词", model="1.0-pro-fast")

# 降低分辨率
result = generate_video("提示词", resolution="480p")

# 缩短时长
result = generate_video("提示词", duration=4)
```

---

## API 限制说明

### 文件大小和数量限制

| 类型 | 最大数量 | 单文件大小 | 时长限制 |
|------|----------|-----------|---------|
| 图片 | 9 张 | 30MB | - |
| 视频 | 3 个 | 50MB | 15秒 |
| 音频 | 3 个 | 15MB | 15秒 |

### 生成参数限制

| 参数 | 范围/选项 | 默认值 |
|------|----------|--------|
| duration | 2-12 秒 | 5 |
| ratio | 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive | 16:9 |
| resolution | 480p, 720p, 1080p | 720p |
| motion_intensity | 0.0-1.0 | 自动 |

### 建议的超时时间

| 分辨率 | 建议超时 |
|--------|---------|
| 480p | 300-600秒 |
| 720p | 600秒 |
| 1080p | 900秒 |

---

## 更多资源

- [官方 SDK 示例](https://www.volcengine.com/docs/82379/1366799)
- [API 参考文档](https://www.volcengine.com/docs/82379/1520757)
- [使用指南](https://www.volcengine.com/docs/82379/1521309)
- [项目 README](README.md)
- [Skill 配置](SKILL.md)
