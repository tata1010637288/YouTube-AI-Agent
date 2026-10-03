import argparse
import json
import os
import re
import textwrap
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip, TextClip, VideoClip

load_dotenv()


def call_gemini(prompt: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except Exception:
        return None


def call_openrouter(prompt: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "YouTubeAI" 
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a YouTube script writer. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def parse_json_from_response(raw_text: str):
    if not raw_text:
        return None

    match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    if match:
        raw_text = match.group(1)

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw_text[start : end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    try:
        return json.loads(raw_text)
    except Exception:
        return None


def generate_local_script(topic: str):
    title = f"{topic}: The Future Nobody Talks About"
    sections = [
        "The problem is bigger than most people think.",
        "Here is what is really happening behind the scenes.",
        "Why this matters right now for businesses, creators, and workers.",
        "The biggest opportunity is not in chasing hype but in understanding the shift.",
        "If you act early, you can build leverage before the market becomes crowded."
    ]

    hook = f"Everyone is talking about {topic}, but most explanations are shallow. Here is the real story behind the trend."
    conclusion = "The future belongs to people who learn early, apply quickly, and build systems that compound over time."

    return {
        "title": title,
        "hook": hook,
        "sections": sections,
        "conclusion": conclusion,
    }


def generate_script(topic: str):
    prompt = f"""
You are a high-end YouTube script writer.

Create a polished 2-3 minute explanatory video script about: {topic}

Return ONLY valid JSON with this structure:
{{
  "title": "short strong title",
  "hook": "1-2 sentence hook",
  "sections": ["section 1 sentence", "section 2 sentence", "section 3 sentence", "section 4 sentence"],
  "conclusion": "closing sentence"
}}

Make it compelling, clear, and suitable for a YouTube audience.
    """

    raw = call_gemini(prompt) or call_openrouter(prompt)
    if raw:
        parsed = parse_json_from_response(raw)
        if parsed:
            return parsed

    return generate_local_script(topic)


def build_voiceover_text(script: dict):
    sentences = [script.get("hook", ""), *script.get("sections", []), script.get("conclusion", "")]
    return " ".join(sentence for sentence in sentences if sentence)


def create_tts(script: dict, output_dir: Path):
    text = build_voiceover_text(script)
    audio_path = output_dir / "voiceover.mp3"
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(str(audio_path))
    return audio_path


def render_background(duration: float, width: int = 1280, height: int = 720):
    def make_frame(t):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # gradient
        y_norm = np.linspace(0, 1, height)[:, None]
        x_norm = np.linspace(0, 1, width)[None, :]
        r = (200 + 50 * np.sin(t * 0.7)).astype(np.float32)
        g = (40 + 80 * np.cos(t * 0.9)).astype(np.float32)
        b = (120 + 100 * np.sin(t * 0.5 + 1.2)).astype(np.float32)

        frame[:, :, 0] = (40 + 120 * y_norm + r * x_norm).astype(np.uint8)
        frame[:, :, 1] = (30 + 100 * (1 - y_norm) + g * x_norm).astype(np.uint8)
        frame[:, :, 2] = (140 + 100 * np.sin(t + x_norm * 2.0) + b).astype(np.uint8)

        for i in range(8):
            cx = width * ((0.15 * i + 0.2) + 0.1 * np.sin(t * (0.5 + i * 0.12)))
            cy = height * (0.2 + 0.15 * np.cos(t * 0.8 + i))
            rr, cc = np.ogrid[:height, :width]
            dist = (rr - cy) ** 2 + (cc - cx) ** 2
            radius = 110 + i * 24
            mask = dist < radius**2
            color = np.array([60 + i * 10, 30 + i * 9, 180 - i * 5], dtype=np.uint8)
            frame[mask] = np.clip(frame[mask] + color, 0, 255)

        return frame

    return VideoClip(make_frame, duration=duration)


def render_text_clips(script: dict, duration: float):
    title = script.get("title", "AI Idea Video")
    hook = script.get("hook", "")
    sections = script.get("sections", [])

    title_clip = TextClip(
        title,
        font="DejaVu-Sans-Bold",
        fontsize=52,
        color="white",
        stroke_color="black",
        stroke_width=2,
        method="label",
    ).set_position(lambda t: ("center", 100)).set_duration(duration)

    subtitle_lines = textwrap.wrap(hook, width=44)
    subtitle_text = "\n".join(subtitle_lines)
    subtitle_clip = TextClip(
        subtitle_text,
        font="DejaVu-Sans-Bold",
        fontsize=32,
        color="#EAF2FF",
        method="label",
    ).set_position(lambda t: ("center", 540)).set_duration(duration)

    section_text = " • ".join(sections[:3])
    feature_clip = TextClip(
        section_text[:140],
        font="DejaVu-Sans",
        fontsize=24,
        color="#FBD7A4",
        method="label",
    ).set_position(lambda t: ("center", 610)).set_duration(duration)

    return [title_clip, subtitle_clip, feature_clip]


def build_video(script: dict, audio_path: Path, output_path: Path):
    audio_clip = AudioFileClip(str(audio_path))
    duration = audio_clip.duration

    background_clip = render_background(duration)
    text_clips = render_text_clips(script, duration)
    final_clip = CompositeVideoClip([background_clip, *text_clips], size=(1280, 720), bg_color=(0, 0, 0))
    final_clip = final_clip.set_duration(duration)
    final_clip.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio=str(audio_path),
        audio_codec="aac",
        temp_audiofile=str(output_path.with_suffix(".tmp_audio.wav")),
        remove_temp=True,
    )


def generate_video_from_idea(idea: str, output_path: str = "output/final_video.mp4"):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    script = generate_script(idea)
    audio_path = create_tts(script, output_file.parent)
    build_video(script, audio_path, output_file)
    return script, output_file


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a YouTube-style AI video from an idea")
    parser.add_argument("--idea", required=True, help="Topic or idea for the video")
    parser.add_argument("--output", default="output/final_video.mp4", help="Output video path")
    return parser.parse_args()


def main():
    args = parse_args()
    script, output_path = generate_video_from_idea(args.idea, args.output)
    print(json.dumps({"title": script.get("title"), "video": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
