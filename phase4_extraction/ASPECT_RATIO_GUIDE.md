# 16:9 Aspect Ratio Requirement - Video Production Standards

## 🎬 CRITICAL REQUIREMENT

**ALL storyboard frame images MUST be exactly 16:9 aspect ratio (1920x1080 resolution).**

This is non-negotiable for video production. Every frame will be used directly for video generation without any cropping, letterboxing, or pillarboxing.

---

## 📐 Why 16:9?

### Standard Widescreen Format
- **16:9** is the universal standard for:
  - HD Video (720p, 1080p, 4K)
  - YouTube
  - Streaming platforms (Netflix, Prime Video)
  - Cinema (close to 1.85:1)
  - Television
  - Professional video production

### Video Generation Compatibility
- AI video generation tools (Runway Gen-2, Pika Labs, Stable Video Diffusion) expect **16:9 input**
- Using non-16:9 images causes:
  - ❌ Automatic cropping (losing important parts of frame)
  - ❌ Letterboxing (black bars top/bottom)
  - ❌ Pillarboxing (black bars left/right)
  - ❌ Distortion when resizing

### Direct Use in Final Video
- Frame images → Video clips → Final video
- **No post-processing needed** if all frames are 16:9
- Clean, professional output

---

## 📊 Aspect Ratio Specifications

### Recommended Resolution
```
Width:  1920 pixels
Height: 1080 pixels
Ratio:  16:9 (1.777...)
Name:   1080p / Full HD
```

### Other Valid 16:9 Resolutions
```
4K:     3840 × 2160  (16:9)
1080p:  1920 × 1080  (16:9) ← RECOMMENDED
720p:   1280 × 720   (16:9)
480p:   854  × 480   (16:9)
```

All are acceptable, but **1920×1080 is recommended** for best quality/performance balance.

---

## 🎨 Image Composition for 16:9

### Horizontal Format
```
┌─────────────────────────────────┐
│                                 │  ← 16:9 is WIDE (horizontal)
│      Your Scene Content         │
│                                 │
└─────────────────────────────────┘
       ↑                    ↑
    1920 pixels wide
```

### Use the Width!
- **Wide shots:** Spread scene across full horizontal space
- **Dialogue:** Position characters left/right (not centered)
- **Action:** Show movement horizontally
- **Insert shots:** Frame props in 16:9 rectangle

### Rule of Thirds (16:9)
```
┌─────┬─────┬─────┬─────┬─────┬─────┐
│     │     │     │     │     │     │
│  ✓  │     │  ✓  │  ✓  │     │  ✓  │  ← Place subjects at intersection points
│     │     │     │     │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┘
   1/3    1/3    1/3    1/3    1/3    1/3
```

---

## 🖼️ Frame Types in 16:9

### 1. Wide Establishing Shot
```
┌────────────────────────────────────────────┐
│ ╔════════════════════════════════════════╗ │
│ ║   Entire Room/Location Visible        ║ │
│ ║   Character small in environment       ║ │
│ ╚════════════════════════════════════════╝ │
└────────────────────────────────────────────┘
        16:9 - Full width utilized
```

### 2. Medium Shot
```
┌────────────────────────────────────────────┐
│          ┌──────────────────┐              │
│          │  Character       │              │
│          │  Waist-Up        │              │
│          └──────────────────┘              │
└────────────────────────────────────────────┘
        16:9 - Subject positioned in frame
```

### 3. Close-Up (Dialogue)
```
┌────────────────────────────────────────────┐
│     ╔════════╗                             │
│     ║ Face A ║         ╔════════╗          │
│     ╚════════╝         ║ Face B ║          │
│                        ╚════════╝          │
└────────────────────────────────────────────┘
    16:9 - Two-shot dialogue composition
```

### 4. Insert Shot (Props)
```
┌────────────────────────────────────────────┐
│                                            │
│              ┌──────────┐                  │
│              │  Phone   │                  │
│              └──────────┘                  │
└────────────────────────────────────────────┘
        16:9 - Centered object in widescreen
```

---

## 🎯 Implementation in Phase 4

### Image Generation Prompts

**Every image prompt includes:**
```python
"16:9 aspect ratio"
"1920x1080 resolution"
"widescreen cinematic frame"
"NO letterboxing"
"NO pillarboxing"
"fills entire 16:9 rectangle"
```

### Character Reference Images
```python
generate_character_image_prompt(character)
# Output includes: "16:9 aspect ratio, 1920x1080, widescreen frame..."
```

### Environment Anchor Images
```python
generate_environment_image_prompt(environment, name)
# Output includes: "16:9 aspect ratio, 1920x1080, widescreen frame..."
```

### Storyboard Frame Specifications
```python
frame_data = {
    "aspect_ratio": "16:9",      # ALWAYS 16:9
    "resolution": "1920x1080",   # Recommended resolution
    "widescreen": True,          # Flag for video production
    "shot_type": "medium",
    "camera_angle": "close-up",
    # ... other fields
}
```

---

## 🎬 Video Production Workflow

### Phase 5 Pipeline
```
1. Generate Frame Images (16:9)
   ↓
2. Frame Image Files (1920×1080 .png/.jpg)
   ↓
3. AI Video Generation (accepts 16:9 input)
   ↓
4. Video Clips (16:9 .mp4)
   ↓
5. Video Assembly (FFmpeg)
   ↓
6. Final Video (16:9 .mp4)
```

### No Post-Processing Needed
Because all frames are **exactly 16:9**:
- ✅ Direct video generation
- ✅ No cropping
- ✅ No resizing
- ✅ No black bars
- ✅ Professional output

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T DO:
- **Square images (1:1)** - Not widescreen
- **Portrait images (9:16)** - Wrong orientation
- **4:3 ratio** - Old TV format
- **21:9 ultra-wide** - Too wide for standard video
- **Custom ratios** - Will require cropping

### ✅ DO:
- **Always 16:9 (1.777:1 ratio)**
- **Horizontal/landscape orientation**
- **1920×1080 recommended**
- **Compose for widescreen**

---

## 🔍 Validation

### Check Aspect Ratio
```python
from phase4_extraction.video_specs import validate_aspect_ratio

# Example
width = 1920
height = 1080
is_valid = validate_aspect_ratio(width, height)
# Returns: True (16/9 = 1.777...)

width = 1080
height = 1920
is_valid = validate_aspect_ratio(width, height)
# Returns: False (9/16 = 0.5625 - this is portrait!)
```

### Image Generation Validation
Before sending to Phase 5, verify:
1. All frames have `"aspect_ratio": "16:9"`
2. All image prompts include "16:9 aspect ratio"
3. Resolution is 1920×1080 or other 16:9 resolution

---

## 📋 Quality Checklist

Before Phase 5 image generation:

- [ ] All character prompts specify 16:9
- [ ] All environment prompts specify 16:9
- [ ] All storyboard frames marked as 16:9
- [ ] Frame composition designed for widescreen
- [ ] No portrait/vertical compositions
- [ ] Resolution is 1920×1080 (recommended)
- [ ] Image generation notes mention "widescreen cinematic frame"

---

## 🎥 Final Output

### What You Get
- **Professional widescreen video**
- **Standard HD format (1080p)**
- **Ready for any platform** (YouTube, Vimeo, streaming)
- **No cropping artifacts**
- **Clean, cinematic look**

### Platform Compatibility
✅ YouTube (16:9 native)
✅ Vimeo (16:9 native)
✅ Instagram (supports 16:9)
✅ TikTok (can use 16:9)
✅ Facebook (16:9 native)
✅ Twitter/X (16:9 native)
✅ LinkedIn (16:9 native)
✅ All professional platforms

---

## 📚 References

- **video_specs.py** - All constants and validation
- **utils.py** - Prompt generation with 16:9
- **models.py** - StoryboardFrame includes aspect_ratio
- **storyboard_planning.py** - Enforces 16:9 in prompts

---

## 🎯 Summary

**Remember:** Every single image generated in Phase 5 MUST be 16:9.

This ensures:
1. ✅ Direct video generation (no processing)
2. ✅ Professional quality output
3. ✅ Platform compatibility
4. ✅ No cropping or distortion
5. ✅ Clean, cinematic results

**The golden rule: 1920 × 1080 pixels = 16:9 ratio = Perfect for video! 🎬**
