# Changelog

## Version 2.0.0 (2026-03-17)

### 🎉 Major Updates - Seedance 2.0 Feature Parity

Based on official Volcengine documentation:
- [SDK 示例官方教程](https://www.volcengine.com/docs/82379/1366799)
- [API 参考官方文档](https://www.volcengine.com/docs/82379/1520757)
- [使用指南](https://www.volcengine.com/docs/82379/1521309)

### ✨ New Features

#### Multi-Modal Reference System
- **Video References**: Support up to 3 reference videos for motion control (max 50MB, 15s each)
- **Audio References**: Support up to 3 reference audio files for rhythm sync (max 15MB, 15s each)
- **Enhanced Image References**: Support up to 9 reference images (previously limited to 4)
- **Tagging System**: Use `@Image1`, `@Video1`, `@Audio1` tags in prompts to reference specific files
- **Role Assignment**: Assign roles to references (character, background, motion, etc.)

#### Advanced Parameters
- **Negative Prompts**: Specify unwanted elements (`negative_prompt` parameter)
- **Style Presets**: 5 style options (cinematic, anime, realistic, artistic, documentary)
- **Camera Movement**: 8 camera movement types (static, pan, tilt, zoom_in, zoom_out, dolly, track, orbit)
- **Motion Intensity**: Fine-tune motion strength (0.0-1.0)

#### Enhanced Response Data
- **Thumbnail URL**: Preview images for generated videos
- **Seed Value**: Track and reproduce results with seed values
- **Cost Tracking**: Monitor credit consumption
- **Metadata**: Additional generation information

#### Developer Experience
- **Progress Callbacks**: Real-time progress monitoring with `on_progress` parameter
- **Webhook Support**: Async notifications via `callback_url` parameter
- **Type Hints**: Complete type annotations throughout
- **Proper Logging**: Replaced print statements with structured logging

### 🛡️ Improved Error Handling

#### HTTP Status Code Handling
- **401**: Authentication failures with actionable messages
- **402**: Insufficient credits with recharge guidance
- **403**: Permission errors with service activation hints
- **429**: Rate limiting with retry-after information
- **500+**: Server errors with automatic retry

#### Retry Logic
- **Exponential Backoff**: Smart retry with increasing intervals
- **Configurable Retries**: Up to 3 retry attempts by default
- **Transient Error Detection**: Distinguishes retryable from fatal errors

#### Enhanced Error Messages
- Detailed error context and suggestions
- Failure reason extraction from API responses
- Error codes for debugging

### 🚀 Performance Improvements

#### Adaptive Polling
- Starts with 2-second intervals for quick jobs
- Gradually increases to configured maximum
- Reduces unnecessary API calls

#### Request Timeout
- Configurable timeout per request (default: 30s)
- Separate timeout for video downloads (120s)
- Overall task timeout remains configurable

### 📚 Documentation Enhancements

#### New Files
- **EXAMPLES.md**: Comprehensive usage examples and best practices
- **CHANGELOG.md**: Version history and update notes

#### Updated Documentation
- **README.md**: Complete feature documentation with examples
- **SKILL.md**: Updated for Seedance 2.0 capabilities
- Added API limits and constraints tables
- Added troubleshooting guide
- Added prompt engineering guidelines

### 🔧 API Changes

#### New Parameters

```python
generate_video(
    # Existing parameters (unchanged)
    prompt, model, duration, ratio, resolution,
    image, first_frame, last_frame, reference_images,
    generate_audio, seed, camera_fixed, watermark,
    download, output_dir, poll_interval, timeout,

    # NEW: Multi-modal references
    images=[{"url": "...", "tag": "@Image1", "role": "character"}],
    videos=[{"url": "...", "tag": "@Video1", "role": "motion"}],
    audios=[{"url": "...", "tag": "@Audio1", "role": "background_music"}],

    # NEW: Advanced control
    negative_prompt="no blur, no text",
    style_preset="cinematic",
    camera_movement="dolly",
    motion_intensity=0.5,

    # NEW: Developer features
    on_progress=callback_function,
    callback_url="https://webhook.example.com"
)
```

#### New Command-Line Arguments

```bash
# Advanced parameters
-n, --negative-prompt   # Negative prompts
--style                 # Style preset
--camera                # Camera movement
--motion                # Motion intensity

# Developer options
--debug                 # Enable debug logging
--timeout               # Custom timeout
```

### 📊 API Limits Documentation

| Type | Max Count | File Size | Duration |
|------|-----------|-----------|----------|
| Images | 9 | 30MB | - |
| Videos | 3 | 50MB | 15s |
| Audios | 3 | 15MB | 15s |

### 🔄 Backward Compatibility

All existing code continues to work without modifications. New features are opt-in through additional parameters.

#### Example - Old Code Still Works
```python
# v1.0.0 code (still works in v2.0.0)
result = generate_video("一只小猫打哈欠")

# v2.0.0 with new features
result = generate_video(
    "一只小猫打哈欠",
    negative_prompt="no blur",
    style_preset="cinematic"
)
```

### 🏗️ Technical Improvements

#### Code Quality
- Added comprehensive parameter validation
- Implemented helper functions for reusability
- Improved error handling with context
- Added debug logging support

#### Testing & Validation
- Parameter range validation
- File count limit validation
- Style/camera movement option validation
- Type checking with type hints

### 📝 Best Practices Added

1. **Prompt Engineering**: Structured prompt format recommendations
2. **Iterative Optimization**: Start simple, add details progressively
3. **Resource Management**: Appropriate timeout values for different resolutions
4. **Error Handling**: Comprehensive error handling patterns
5. **Seed Usage**: Reproducibility guidelines

### 🔗 Resources

- [Official SDK Documentation](https://www.volcengine.com/docs/82379/1366799)
- [API Reference](https://www.volcengine.com/docs/82379/1520757)
- [Usage Guide](https://www.volcengine.com/docs/82379/1521309)

---

## Version 1.0.0 (Initial Release)

### Features
- Basic text-to-video generation
- Image-to-video with single image reference
- First/last frame video generation
- Model selection (1.5-pro, 1.0-pro, 1.0-lite variants)
- Basic parameter control (duration, ratio, resolution)
- Audio generation toggle
- Seed support for reproducibility
- Auto-download to local directory
