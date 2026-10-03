# YouTube AI Agent

A free, local-first YouTube video generator that turns a single idea into a short research-style video with motion graphics and voiceover.

## What this project does

- Accepts a topic or idea prompt
- Generates a structured script using a free LLM API if available
- Falls back to a smart local script template if no API key is configured
- Converts the script to speech using Google TTS
- Creates a simple animated video with moving background, title text, and subtitle overlays
- Saves the final MP4 locally

## Why this is free

This project uses free python libraries and optional free APIs:

- Gemini free tier or OpenRouter free models for research/script writing
- gTTS for free voice synthesis
- MoviePy + NumPy for video generation
- Local script fallback means it works even without an API key

## Project structure

- `youtube_ai_agent.py`: main generator logic
- `app.py`: Streamlit web interface
- `requirements.txt`: Python dependencies
- `.env.example`: environment variables
- `README.md`: usage guide

## Quick start

1. Clone the repo and move into it.
2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Optional: add API keys.

Create a `.env` file:

```bash
cp .env.example .env
```

Example:

```bash
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

If you do not add an API key, the app still works with a built-in local research template.

## Run the CLI

```bash
python youtube_ai_agent.py --idea "AI agents will replace software jobs in 2026" --output output/final_video.mp4
```

## Run the web UI

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit and enter a topic.

## How it works

1. Idea input
2. Research/script generation via LLM or local fallback
3. Storyboard + hook + sections + conclusion
4. Voiceover via gTTS
5. Motion animation via MoviePy
6. MP4 export to the `output/` folder

## Free model setup options

### Option A: Gemini (free tier)

- Get a Google AI Studio API key
- Set `GEMINI_API_KEY`
- The script uses `gemini-2.0-flash` if available

### Option B: OpenRouter (free models)

- Create an OpenRouter account
- Set `OPENROUTER_API_KEY`
- The script uses a free model such as `openai/gpt-4o-mini` or other low-cost providers

### Option C: No API key

- Local fallback creates a researched-style script with a clean voiceover and video output
- This is the simplest setup for zero-cost testing

## Current limitations

- This creates a video file locally, but YouTube upload is still a separate manual step
- A full AI video-generation pipeline with character animation or cinematic rendering would need heavier models and more GPU power
- For production-quality editing, tools like CapCut, Premiere Pro, Runway, or Pika are better, but this is a strong free starter project

## Useful next upgrades

- Auto-generate thumbnails
- Add subtitle timing per sentence
- Make video sections using scene cuts
- Connect to YouTube API for upload
- Add voice style selection
- Add background music using royalty-free library

## License

MIT
