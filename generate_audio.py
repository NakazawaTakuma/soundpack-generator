#!/usr/bin/env python3
"""
generate_preview_video.py

Creates a captioned preview video for the forest-themed SFX pack.
Reads prompts from config_forest.py and assembles WAV clips into a scrolling video.
"""
import os
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip, ImageClip,
    CompositeVideoClip, concatenate_videoclips
)
from config.config_forest import title, prompts

# --- Argument parser ---
parser = argparse.ArgumentParser(
    description="Generate preview video for forest SFX pack"
)
parser.add_argument(
    "--assets-dir", "-a",
    default=os.path.join(os.path.dirname(__file__), "assets"),
    help="Directory containing forest background and assets"
)
parser.add_argument(
    "--output-dir", "-o",
    default=os.path.join(os.path.dirname(__file__), "outputs"),
    help="Directory to save generated video files"
)
args = parser.parse_args()

# --- Base directories ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(args.assets_dir)
OUTPUT_DIR = os.path.abspath(args.output_dir)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Folder containing generated WAV files (timestamped folder under outputs)
folder = os.path.join(OUTPUT_DIR, f"forest_{title}_{len(prompts)}")
bg_image = os.path.join(ASSETS_DIR, "forest_bg.png")
output_video = os.path.join(OUTPUT_DIR, f"{title}.mp4")
output_video_jp = os.path.join(OUTPUT_DIR, f"{title}_jp.mp4")

# --- Text rendering parameters ---
font_path = r"assets/fonts/meiryo.ttc"
font_size = 30
line_height = int(font_size * 1.5)
max_lines = 7
slide_time = 0.5

# Load background to get dimensions
bg = Image.open(bg_image)
video_w, video_h = bg.size
# Precompute text positions
center_y = video_h // 2
half = max_lines // 2
positions = [
    (video_w * 0.05, center_y + (i - half) * line_height)
    for i in range(max_lines)
]

# Fade alpha for lines farther from center
def fade_alpha(idx):
    dist = abs(idx - half)
    return max(0.1, 1 - (dist * 3) / (half + 1))

# Create an RGBA image of text
def make_text_image(text, fontsize, font_path, alpha):
    font = ImageFont.truetype(font_path, fontsize)
    ascent, descent = font.getmetrics()
    dummy = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], ascent + descent
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=(255, 255, 255, int(alpha * 255)))
    return img

# Gather WAV files and names
wav_files = []
audio_names = []
audio_names_jp = []
for filename, jp_desc, eng_desc in prompts:
    for i in (1, 2):
        path = os.path.join(folder, f"{filename}{i}.wav")
        if os.path.exists(path):
            wav_files.append(path)
            audio_names.append(eng_desc)
            audio_names_jp.append(jp_desc)

# Build video clips
clips = []
clips_jp = []
total = len(wav_files)
for idx, wav_path in enumerate(wav_files):
    audio = AudioFileClip(wav_path)
    if audio.duration > 3.3:
        audio = audio.subclip(0, 3.3)
    duration = audio.duration
    bg_clip = ImageClip(bg_image).set_duration(duration)

    text_clips = []
    text_clips_jp = []
    for j in range(max_lines):
        i2 = idx + (j - half)
        if i2 < 0 or i2 >= total:
            continue
        raw = os.path.basename(wav_files[i2])
        txt = f"{i2+1}. {audio_names[i2]} ({raw})"
        txt_jp = f"{i2+1}. {audio_names_jp[i2]} ({raw})"
        alpha = fade_alpha(j)
        img = make_text_image(txt, font_size, font_path, alpha)
        img_jp = make_text_image(txt_jp, font_size, font_path, alpha)
        clip = ImageClip(np.array(img)).set_duration(duration)
        clip_jp = ImageClip(np.array(img_jp)).set_duration(duration)
        # Slide-in effect
        def pos_fn(j_idx, x0, y0):
            def pos(t):
                if t < slide_time:
                    return x0, y0 + line_height * (1 - t/slide_time)
                return x0, y0
            return pos
        x0, y0 = positions[j]
        clip = clip.set_position(pos_fn(j, x0, y0))
        clip_jp = clip_jp.set_position(pos_fn(j, x0, y0))
        text_clips.append(clip)
        text_clips_jp.append(clip_jp)

    comp = CompositeVideoClip([bg_clip, *text_clips]).set_audio(audio)
    comp_jp = CompositeVideoClip([bg_clip, *text_clips_jp]).set_audio(audio)
    clips.append(comp)
    clips_jp.append(comp_jp)

# Concatenate and write outputs
final = concatenate_videoclips(clips, method="compose")
final.write_videofile(output_video, fps=24, codec="libx264")

final_jp = concatenate_videoclips(clips_jp, method="compose")
final_jp.write_videofile(output_video_jp, fps=24, codec="libx264")
