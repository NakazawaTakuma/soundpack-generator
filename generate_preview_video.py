#!/usr/bin/env python3
"""
generate_audio.py

Batch-generates forest-themed SFX using Stability AI’s StableAudioPipeline.
Outputs WAV files and per-language README to a timestamped folder.
"""
import os
import argparse
import random
from datetime import datetime
import torch
import soundfile as sf
from diffusers import StableAudioPipeline
from pydub import AudioSegment
from config.config_forest import title, common_prompt, prompts

# --- Argument parser ---
parser = argparse.ArgumentParser(
    description="Generate forest-themed sound effects pack"
)
parser.add_argument(
    "--output-root", "-o",
    default=os.path.join(os.path.dirname(__file__), "outputs"),
    help="Root directory to create timestamped output subfolder"
)
parser.add_argument(
    "--hf-token", "-t",
    default=None,
    help="Hugging Face API token (or set HUGGINGFACE_TOKEN env var)"
)
args = parser.parse_args()

# --- Setup directories ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.abspath(args.output_root)
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Timestamped folder for this run
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(OUTPUT_ROOT, f"{title}_{timestamp}")
os.makedirs(output_dir, exist_ok=True)
print(f"Saving all .wav files into '{output_dir}'")

# --- Prepare README content ---
readme_en = f"""{title} Readme

This folder contains AI-generated forest-themed sound effects.

Files:

ENV_... : Loopable: Yes
SFX_... : Loopable: No
"""
for filename, _, eng_desc in prompts:
    readme_en += f"- {filename:<25}: {eng_desc}\n"

readme_jp = f"""{title} の説明

このフォルダには、AIを使用して生成した「森林」テーマの効果音が含まれています。

ファイル一覧:

ENV_... : ループ再生: 対応
SFX_... : ループ再生: 非対応
"""
for filename, jp_desc, _ in prompts:
    readme_jp += f"- {filename:<25}: {jp_desc}\n"

# Write READMEs
with open(os.path.join(output_dir, 'README_en.txt'), 'w', encoding='utf-8') as f:
    f.write(readme_en)
with open(os.path.join(output_dir, 'README_jp.txt'), 'w', encoding='utf-8') as f:
    f.write(readme_jp)
print("Created README_en.txt and README_jp.txt.")

# --- Configure pipeline ---
token = args.hf_token or os.getenv("HUGGINGFACE_TOKEN")
if not token:
    raise ValueError("Hugging Face token must be provided via --hf-token or HUGGINGFACE_TOKEN env var")
os.environ["HUGGINGFACE_TOKEN"] = token
pipe = StableAudioPipeline.from_pretrained(
    "stabilityai/stable-audio-open-1.0", torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

# --- Generate audio ---
for idx, (filename, jp_desc, eng_desc) in enumerate(prompts):
    loop_flag = filename.startswith("ENV_")
    duration = 10.0 if loop_flag else 1.0
    full_prompt = f"{filename}, {eng_desc}, {common_prompt}"
    if loop_flag:
        full_prompt = f"{filename}, {title}, {eng_desc}, {common_prompt}"
    negative_prompt = "Low quality."

    for rep in (1, 2):
        seed = random.randint(0, 2**32 - 1)
        gen = torch.Generator("cuda").manual_seed(seed)
        print(f"Generating '{filename}{rep}' with seed: {seed}")
        audios = pipe(
            full_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=200,
            audio_end_in_s=duration,
            num_waveforms_per_prompt=1,
            generator=gen
        ).audios

        audio_np = audios[0].T.float().cpu().numpy()
        wav_name = f"{filename}{rep}.wav"
        wav_path = os.path.join(output_dir, wav_name)
        sf.write(wav_path, audio_np, pipe.vae.sampling_rate)
        print(f"Saved raw output: {wav_path}")

        if loop_flag:
            seg = AudioSegment.from_file(wav_path, format="wav")
            cut_ms = 1000
            trimmed = seg[cut_ms:len(seg)-cut_ms]
            fade_ms = 2000
            loop_seg = trimmed.append(trimmed, crossfade=fade_ms)
            loop_seg = loop_seg[:len(seg)]
            loop_seg.export(wav_path, format="wav")
            print(f"Saved loopable file: {wav_path}")
