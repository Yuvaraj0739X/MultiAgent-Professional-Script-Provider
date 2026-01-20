# 16:9 ASPECT RATIO - Quick Reference Card

## ✅ REQUIRED SPECIFICATIONS

```
Aspect Ratio:  16:9
Resolution:    1920 × 1080 pixels
Format:        Widescreen / Horizontal
Ratio Value:   1.777... (16÷9)
```

## 🎬 WHY 16:9?

✅ Standard HD video format
✅ Direct video generation (no cropping)
✅ YouTube, streaming platform standard
✅ Professional cinematic output

## 🚫 AVOID

❌ Square (1:1)
❌ Portrait (9:16)
❌ Old TV (4:3)
❌ Ultra-wide (21:9)
❌ Custom ratios

## 📊 FRAME COMPOSITION

```
┌─────────────────────────────────┐
│                                 │  ← 1080 pixels high
│    YOUR SCENE (16:9)            │
│                                 │
└─────────────────────────────────┘
         1920 pixels wide
```

## 💾 IN CODE

### Character Prompts
```python
"16:9 aspect ratio"
"1920x1080 resolution"
"widescreen cinematic frame"
"NO letterboxing"
```

### Environment Prompts
```python
"16:9 aspect ratio"
"1920x1080 resolution"
"widescreen cinematic frame"
"NO pillarboxing"
```

### Frame Data
```python
{
  "aspect_ratio": "16:9",
  "resolution": "1920x1080",
  "widescreen": True
}
```

## 🎯 VALIDATION

```python
from phase4_extraction.video_specs import validate_aspect_ratio

validate_aspect_ratio(1920, 1080)  # ✅ True
validate_aspect_ratio(1080, 1920)  # ❌ False (portrait!)
```

## 📋 CHECKLIST

Before Phase 5:
- [ ] All frames marked as 16:9
- [ ] Resolution is 1920×1080
- [ ] All prompts include "16:9 aspect ratio"
- [ ] Composition designed for widescreen
- [ ] No portrait/vertical orientations

## 🎬 RESULT

→ Professional widescreen video
→ Ready for any platform
→ No cropping needed
→ Cinematic quality

---

**Remember: 1920 × 1080 = 16:9 = Perfect for video! 🎬**

For full details, see: [ASPECT_RATIO_GUIDE.md](ASPECT_RATIO_GUIDE.md)
