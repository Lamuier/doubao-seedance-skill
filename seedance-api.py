"""
Seedance Video API 调用模块
可直接导入使用: from seedance_api import generate_video

支持的功能:
- 文生视频 (Text-to-Video)
- 图生视频 (Image-to-Video) - 支持最多9张参考图
- 视频参考生成 - 支持最多3个参考视频
- 音频参考生成 - 支持最多3个参考音频
- 首尾帧视频生成
- 负面提示词 (Negative Prompts)
- 高级参数控制 (风格、摄像机运动、运动强度等)
"""
import requests
import os
import sys
import time
import logging
from typing import Optional, List, Dict, Any, Union, Literal, Callable
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("VOLCENGINE_API_KEY")
API_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
QUERY_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"

MODELS = {
    "1.5-pro": "doubao-seedance-1-5-pro-251215",
    "1.0-pro": "doubao-seedance-1-0-pro-250121",
    "1.0-pro-fast": "doubao-seedance-1-0-pro-fast-250121",
    "1.0-lite-t2v": "doubao-seedance-1-0-lite-t2v-241118",
    "1.0-lite-i2v": "doubao-seedance-1-0-lite-i2v-241118",
}

DEFAULT_MODEL = MODELS["1.5-pro"]

# API 限制常量
MAX_IMAGES = 9  # 最多9张参考图片
MAX_VIDEOS = 3  # 最多3个参考视频
MAX_AUDIOS = 3  # 最多3个参考音频
MAX_IMAGE_SIZE_MB = 30  # 单张图片最大30MB
MAX_VIDEO_SIZE_MB = 50  # 单个视频最大50MB
MAX_AUDIO_SIZE_MB = 15  # 单个音频最大15MB
MAX_VIDEO_DURATION = 15  # 参考视频最长15秒
MAX_AUDIO_DURATION = 15  # 参考音频最长15秒

# 支持的宽高比
VALID_RATIOS = ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"]

# 支持的分辨率
VALID_RESOLUTIONS = ["480p", "720p", "1080p"]

# 支持的风格预设
VALID_STYLES = ["cinematic", "anime", "realistic", "artistic", "documentary", None]

# 支持的摄像机运动
VALID_CAMERA_MOVEMENTS = ["static", "pan", "tilt", "zoom_in", "zoom_out", "dolly", "track", "orbit", None]


def _validate_parameters(duration: int, ratio: str, resolution: str,
                        images: Optional[List] = None,
                        videos: Optional[List] = None,
                        audios: Optional[List] = None,
                        style_preset: Optional[str] = None,
                        camera_movement: Optional[str] = None) -> None:
    """验证输入参数"""

    # 验证时长
    if not (2 <= duration <= 12):
        raise ValueError(f"视频时长必须在 2-12 秒之间，当前: {duration}")

    # 验证宽高比
    if ratio not in VALID_RATIOS:
        raise ValueError(f"不支持的宽高比 '{ratio}'，支持的选项: {', '.join(VALID_RATIOS)}")

    # 验证分辨率
    if resolution not in VALID_RESOLUTIONS:
        raise ValueError(f"不支持的分辨率 '{resolution}'，支持的选项: {', '.join(VALID_RESOLUTIONS)}")

    # 验证参考文件数量
    if images and len(images) > MAX_IMAGES:
        raise ValueError(f"参考图片最多 {MAX_IMAGES} 张，当前: {len(images)}")

    if videos and len(videos) > MAX_VIDEOS:
        raise ValueError(f"参考视频最多 {MAX_VIDEOS} 个，当前: {len(videos)}")

    if audios and len(audios) > MAX_AUDIOS:
        raise ValueError(f"参考音频最多 {MAX_AUDIOS} 个，当前: {len(audios)}")

    # 验证风格预设
    if style_preset and style_preset not in VALID_STYLES:
        raise ValueError(f"不支持的风格预设 '{style_preset}'，支持的选项: {', '.join(str(s) for s in VALID_STYLES if s)}")

    # 验证摄像机运动
    if camera_movement and camera_movement not in VALID_CAMERA_MOVEMENTS:
        raise ValueError(f"不支持的摄像机运动 '{camera_movement}'，支持的选项: {', '.join(str(c) for c in VALID_CAMERA_MOVEMENTS if c)}")


def _handle_api_error(response: requests.Response, context: str = "") -> None:
    """处理 API 错误响应"""
    status_code = response.status_code

    try:
        error_data = response.json()
        error_msg = error_data.get("error", {}).get("message", "未知错误")
        error_type = error_data.get("error", {}).get("type", "")
    except:
        error_msg = response.text or "未知错误"
        error_type = ""

    if status_code == 400:
        raise ValueError(f"请求参数错误: {error_msg}")
    elif status_code == 401:
        raise ValueError(f"认证失败: API Key 无效或已过期。请检查 VOLCENGINE_API_KEY 环境变量")
    elif status_code == 402:
        raise ValueError(f"余额不足: {error_msg}。请前往火山引擎控制台充值")
    elif status_code == 403:
        raise ValueError(f"权限不足: {error_msg}。请检查是否已开通 Seedance 服务")
    elif status_code == 429:
        retry_after = response.headers.get("Retry-After", "60")
        raise ValueError(f"请求频率超限: 请在 {retry_after} 秒后重试")
    elif status_code >= 500:
        raise Exception(f"服务器错误 ({status_code}): {error_msg}。请稍后重试")
    else:
        raise Exception(f"{context} 失败 ({status_code}): {error_msg}")


def _make_request_with_retry(method: str, url: str, headers: Dict,
                             json_data: Optional[Dict] = None,
                             max_retries: int = 3) -> requests.Response:
    """发送 HTTP 请求，支持重试"""
    last_exception = None

    for attempt in range(max_retries):
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)

            # 检查是否需要重试
            if response.status_code in [500, 502, 503, 504]:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"服务器错误 {response.status_code}，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue

            return response

        except requests.exceptions.Timeout as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"请求超时，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
        except requests.exceptions.RequestException as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"请求失败: {e}，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue

    raise Exception(f"请求失败，已重试 {max_retries} 次: {last_exception}")


def generate_video(prompt: str,
                  model: Optional[str] = None,
                  duration: int = 5,
                  ratio: str = "16:9",
                  resolution: str = "720p",
                  # 参考文件 (支持多文件和标签系统)
                  image: Optional[Union[str, List[str]]] = None,
                  images: Optional[List[Dict[str, str]]] = None,  # 新增: 支持带标签的多图片
                  videos: Optional[List[Dict[str, str]]] = None,  # 新增: 视频参考
                  audios: Optional[List[Dict[str, str]]] = None,  # 新增: 音频参考
                  first_frame: Optional[str] = None,
                  last_frame: Optional[str] = None,
                  reference_images: Optional[List] = None,
                  # 负面提示词
                  negative_prompt: Optional[str] = None,  # 新增
                  # 高级参数
                  style_preset: Optional[str] = None,  # 新增: 风格预设
                  camera_movement: Optional[str] = None,  # 新增: 摄像机运动
                  motion_intensity: Optional[float] = None,  # 新增: 运动强度 0.0-1.0
                  # 其他参数
                  generate_audio: bool = True,
                  seed: Optional[int] = None,
                  camera_fixed: bool = False,
                  watermark: bool = False,
                  # 下载和轮询
                  download: bool = True,
                  output_dir: str = "output",
                  poll_interval: int = 5,
                  timeout: int = 600,
                  on_progress: Optional[Callable[[str, float], None]] = None,  # 新增: 进度回调
                  callback_url: Optional[str] = None  # 新增: Webhook 回调
                  ) -> Dict[str, Any]:
    """
    调用火山引擎 Seedance 2.0 生成视频

    参数:
        prompt (str): 文本提示词，建议格式: [主体] + [动作] + [摄像机] + [风格] + [光照]
        model (str): 模型 ID，可选 "1.5-pro", "1.0-pro", "1.0-pro-fast", "1.0-lite-t2v", "1.0-lite-i2v" 或具体 ID
        duration (int): 视频时长(秒)，支持 2-12，默认 5
        ratio (str): 宽高比，支持 "16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"
        resolution (str): 分辨率，支持 "480p", "720p", "1080p"

        # 参考文件 (支持多模态输入)
        image (str/list): 简单图片参考 URL 或 Base64 (向后兼容)
        images (list[dict]): 高级图片参考，支持最多9张，格式: [{"url": "...", "tag": "@Image1", "role": "character"}, ...]
        videos (list[dict]): 视频参考，支持最多3个，格式: [{"url": "...", "tag": "@Video1", "role": "motion"}, ...]
        audios (list[dict]): 音频参考，支持最多3个，格式: [{"url": "...", "tag": "@Audio1", "role": "background_music"}, ...]
        first_frame (str): 首帧图片 URL (首尾帧模式)
        last_frame (str): 尾帧图片 URL (首尾帧模式)
        reference_images (list): 参考图列表 (向后兼容)

        # 负面提示词
        negative_prompt (str): 负面提示词，指定不想出现的内容，例如 "no text, no watermark, no blur"

        # 高级参数
        style_preset (str): 风格预设，支持 "cinematic", "anime", "realistic", "artistic", "documentary"
        camera_movement (str): 摄像机运动，支持 "static", "pan", "tilt", "zoom_in", "zoom_out", "dolly", "track", "orbit"
        motion_intensity (float): 运动强度，范围 0.0-1.0，默认自动

        # 其他参数
        generate_audio (bool): 是否生成音频 (1.5-pro 支持)
        seed (int): 随机种子，用于复现结果
        camera_fixed (bool): 是否固定摄像头
        watermark (bool): 是否添加水印

        # 下载和轮询
        download (bool): 是否下载到本地
        output_dir (str): 输出目录
        poll_interval (int): 轮询间隔(秒)，默认 5，会自适应调整
        timeout (int): 超时时间(秒)，建议: 720p=600s, 1080p=900s
        on_progress (callable): 进度回调函数 on_progress(status: str, progress: float)
        callback_url (str): Webhook 回调 URL (异步模式)

    返回:
        dict: {
            "success": bool,
            "task_id": str,
            "model": str,
            "video_url": str,
            "thumbnail_url": str,  # 新增
            "local_paths": list,
            "duration": int,
            "ratio": str,
            "seed_used": int,  # 新增
            "cost": float,  # 新增
            "metadata": dict  # 新增
        }

    示例:
        # 基础文生视频
        >>> result = generate_video("一只小猫打哈欠")

        # 带负面提示词
        >>> result = generate_video("一只小猫", negative_prompt="no blur, no text")

        # 使用视频参考控制运动
        >>> result = generate_video(
        ...     prompt="一位舞者表演，跟随 @Video1 的动作节奏",
        ...     videos=[{"url": "https://example.com/dance.mp4", "tag": "@Video1", "role": "motion"}]
        ... )

        # 使用音频参考控制节奏
        >>> result = generate_video(
        ...     prompt="烟花绽放，跟随 @Audio1 的节奏",
        ...     audios=[{"url": "https://example.com/music.mp3", "tag": "@Audio1", "role": "background_music"}]
        ... )

        # 多图片参考
        >>> result = generate_video(
        ...     prompt="@Image1 的角色在 @Image2 的场景中行走",
        ...     images=[
        ...         {"url": "https://example.com/character.jpg", "tag": "@Image1", "role": "character"},
        ...         {"url": "https://example.com/scene.jpg", "tag": "@Image2", "role": "background"}
        ...     ]
        ... )

    可用模型:
        - "1.5-pro" / "doubao-seedance-1-5-pro-251215" (默认，支持有声视频)
        - "1.0-pro" / "doubao-seedance-1-0-pro-250121"
        - "1.0-pro-fast" / "doubao-seedance-1-0-pro-fast-250121"
        - "1.0-lite-t2v" / "doubao-seedance-1-0-lite-t2v-241118" (文生视频)
        - "1.0-lite-i2v" / "doubao-seedance-1-0-lite-i2v-241118" (图生视频)
    """
    if not API_KEY:
        raise ValueError("未设置 VOLCENGINE_API_KEY 环境变量。请在 .env 文件中配置或设置环境变量")

    # 参数验证
    _validate_parameters(duration, ratio, resolution, images, videos, audios, style_preset, camera_movement)

    # 确定模型
    if model is None:
        model = DEFAULT_MODEL
    elif model in MODELS:
        model = MODELS[model]

    logger.info(f"使用模型: {model}")

    # 构建请求头
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 构建内容数组 (支持多模态参考)
    content = [{"type": "text", "text": prompt}]

    # 首尾帧模式
    if first_frame and last_frame:
        content.append({"type": "image_url", "image_url": {"url": first_frame}, "role": "first_frame"})
        content.append({"type": "image_url", "image_url": {"url": last_frame}, "role": "last_frame"})

    # 高级多模态参考 (新功能)
    if images:
        for img_ref in images[:MAX_IMAGES]:
            item = {"type": "image_url", "image_url": {"url": img_ref["url"]}}
            if "tag" in img_ref:
                item["tag"] = img_ref["tag"]
            if "role" in img_ref:
                item["role"] = img_ref["role"]
            content.append(item)

    if videos:
        for vid_ref in videos[:MAX_VIDEOS]:
            item = {"type": "video_url", "video_url": {"url": vid_ref["url"]}}
            if "tag" in vid_ref:
                item["tag"] = vid_ref["tag"]
            if "role" in vid_ref:
                item["role"] = vid_ref["role"]
            content.append(item)

    if audios:
        for aud_ref in audios[:MAX_AUDIOS]:
            item = {"type": "audio_url", "audio_url": {"url": aud_ref["url"]}}
            if "tag" in aud_ref:
                item["tag"] = aud_ref["tag"]
            if "role" in aud_ref:
                item["role"] = aud_ref["role"]
            content.append(item)

    # 向后兼容: 简单图片参考
    if not images and not first_frame:
        if reference_images and isinstance(reference_images, list):
            for img in reference_images[:MAX_IMAGES]:
                content.append({"type": "image_url", "image_url": {"url": img}})
        elif image:
            if isinstance(image, list):
                for img in image[:MAX_IMAGES]:
                    content.append({"type": "image_url", "image_url": {"url": img}})
            else:
                content.append({"type": "image_url", "image_url": {"url": image}})

    # 构建请求数据
    data = {
        "model": model,
        "content": content,
        "duration": duration,
        "ratio": ratio,
        "resolution": resolution,
        "generate_audio": generate_audio,
        "camera_fixed": camera_fixed,
        "watermark": watermark
    }

    # 添加可选参数
    if seed is not None:
        data["seed"] = seed

    if negative_prompt:
        data["negative_prompt"] = negative_prompt

    if style_preset:
        data["style_preset"] = style_preset

    if camera_movement:
        data["camera_movement"] = camera_movement

    if motion_intensity is not None:
        if not (0.0 <= motion_intensity <= 1.0):
            raise ValueError(f"运动强度必须在 0.0-1.0 之间，当前: {motion_intensity}")
        data["motion_intensity"] = motion_intensity

    if callback_url:
        data["callback_url"] = callback_url

    # 创建任务
    logger.info(f"正在创建视频生成任务...")
    logger.debug(f"请求数据: {data}")

    response = _make_request_with_retry("POST", API_URL, headers, data)

    if response.status_code != 200:
        _handle_api_error(response, "创建任务")

    result = response.json()

    if "id" not in result:
        error_msg = result.get("error", {}).get("message", "未知错误")
        raise Exception(f"创建任务失败: {error_msg}")

    task_id = result["id"]
    logger.info(f"任务 ID: {task_id}")
    logger.info(f"正在生成视频 (超时: {timeout}秒)...")

    # 自适应轮询
    start_time = time.time()
    adaptive_interval = 2  # 初始轮询间隔
    max_interval = poll_interval

    while time.time() - start_time < timeout:
        time.sleep(adaptive_interval)

        query_response = _make_request_with_retry("GET", f"{QUERY_URL}/{task_id}", headers)

        if query_response.status_code != 200:
            _handle_api_error(query_response, "查询任务")

        query_result = query_response.json()

        status = query_result.get("status", "unknown")
        progress = query_result.get("progress", 0)

        logger.info(f"状态: {status} ({progress}%)")

        # 进度回调
        if on_progress:
            on_progress(status, progress)

        if status == "succeeded":
            content_data = query_result.get("content", {})
            video_url = content_data.get("video_url")
            thumbnail_url = content_data.get("thumbnail_url")

            local_paths = []

            if download and video_url:
                os.makedirs(output_dir, exist_ok=True)
                filename = f"{prompt[:20]}_{int(time.time())}.mp4"
                filename = "".join(c for c in filename if c not in r'<>:"/\|?*')
                filepath = os.path.join(output_dir, filename)

                logger.info(f"正在下载视频...")
                video_response = requests.get(video_url, timeout=120)
                with open(filepath, "wb") as f:
                    f.write(video_response.content)
                local_paths.append(filepath)
                logger.info(f"已保存: {filepath}")

            return {
                "success": True,
                "task_id": task_id,
                "model": model,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "local_paths": local_paths if download else [],
                "duration": query_result.get("duration"),
                "ratio": query_result.get("ratio"),
                "seed_used": query_result.get("seed_used"),
                "cost": query_result.get("cost"),
                "metadata": query_result.get("metadata", {})
            }
        elif status in ["failed", "expired"]:
            error_msg = query_result.get("failure_reason", query_result.get("status", "任务失败"))
            error_code = query_result.get("error_code", "")
            raise Exception(f"视频生成失败 (错误码: {error_code}): {error_msg}")

        # 自适应增加轮询间隔
        if adaptive_interval < max_interval:
            adaptive_interval = min(adaptive_interval + 1, max_interval)

    raise Exception(f"视频生成超时 ({timeout}秒)。可以稍后使用任务 ID {task_id} 查询结果")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Seedance 2.0 视频生成 - 支持文生视频、图生视频、视频参考、音频参考等",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础文生视频
  python seedance-api.py "一只小猫打哈欠"

  # 带负面提示词
  python seedance-api.py "一只小猫" --negative-prompt "no blur, no text"

  # 使用风格预设和摄像机运动
  python seedance-api.py "森林中的小屋" --style cinematic --camera dolly

  # 图生视频
  python seedance-api.py "小猫奔跑" -i "https://example.com/cat.jpg"

  # 首尾帧视频
  python seedance-api.py "过渡动画" --first-frame "url1" --last-frame "url2"
        """
    )

    # 基础参数
    parser.add_argument("prompt", nargs="?", default="一只小猫对着镜头打哈欠", help="视频描述提示词")
    parser.add_argument("-m", "--model", help=f"模型版本: {', '.join(MODELS.keys())} (默认: 1.5-pro)")
    parser.add_argument("-d", "--duration", type=int, default=5, help="视频时长 2-12秒 (默认: 5)")
    parser.add_argument("-r", "--ratio", default="16:9", help=f"宽高比 {', '.join(VALID_RATIOS)} (默认: 16:9)")
    parser.add_argument("-s", "--resolution", default="720p", help=f"分辨率 {', '.join(VALID_RESOLUTIONS)} (默认: 720p)")
    parser.add_argument("-o", "--output-dir", default="output", help="输出目录 (默认: output)")

    # 参考文件
    parser.add_argument("-i", "--image", help="图生视频：参考图片 URL")
    parser.add_argument("--first-frame", help="首尾帧视频：首帧图片 URL")
    parser.add_argument("--last-frame", help="首尾帧视频：尾帧图片 URL")

    # 新增: 高级参数
    parser.add_argument("-n", "--negative-prompt", help="负面提示词，指定不想出现的内容")
    parser.add_argument("--style", choices=[s for s in VALID_STYLES if s], help="风格预设")
    parser.add_argument("--camera", choices=[c for c in VALID_CAMERA_MOVEMENTS if c], help="摄像机运动方式")
    parser.add_argument("--motion", type=float, help="运动强度 0.0-1.0")

    # 其他参数
    parser.add_argument("--no-audio", action="store_true", help="不生成音频")
    parser.add_argument("--seed", type=int, help="随机种子 (用于复现结果)")
    parser.add_argument("--fixed", action="store_true", help="固定摄像头")
    parser.add_argument("--watermark", action="store_true", help="添加水印")

    # 调试选项
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    parser.add_argument("--timeout", type=int, default=600, help="超时时间 秒 (默认: 600)")

    args = parser.parse_args()

    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"正在生成视频: {args.prompt}")
    if args.model:
        logger.info(f"使用模型: {args.model}")
    if args.negative_prompt:
        logger.info(f"负面提示词: {args.negative_prompt}")
    if args.style:
        logger.info(f"风格预设: {args.style}")
    if args.camera:
        logger.info(f"摄像机运动: {args.camera}")

    try:
        result = generate_video(
            prompt=args.prompt,
            model=args.model,
            duration=args.duration,
            ratio=args.ratio,
            resolution=args.resolution,
            image=args.image,
            first_frame=args.first_frame,
            last_frame=args.last_frame,
            negative_prompt=args.negative_prompt,
            style_preset=args.style,
            camera_movement=args.camera,
            motion_intensity=args.motion,
            generate_audio=not args.no_audio,
            seed=args.seed,
            camera_fixed=args.fixed,
            watermark=args.watermark,
            output_dir=args.output_dir,
            timeout=args.timeout
        )

        logger.info(f"\n{'='*60}")
        logger.info(f"生成成功! (模型: {result['model']})")
        logger.info(f"{'='*60}")
        logger.info(f"任务 ID: {result['task_id']}")
        logger.info(f"视频 URL: {result['video_url']}")
        if result.get('thumbnail_url'):
            logger.info(f"缩略图 URL: {result['thumbnail_url']}")
        if result.get('seed_used'):
            logger.info(f"使用的种子: {result['seed_used']}")
        if result.get('cost'):
            logger.info(f"消耗费用: {result['cost']}")

        if result["local_paths"]:
            logger.info(f"\n本地文件:")
            for path in result["local_paths"]:
                logger.info(f"  {path}")

        return 0

    except ValueError as e:
        logger.error(f"参数错误: {e}")
        return 1
    except Exception as e:
        logger.error(f"生成失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

