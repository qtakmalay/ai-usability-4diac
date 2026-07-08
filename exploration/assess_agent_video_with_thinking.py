#!/usr/bin/env python3
"""
Phase 4 EXTENSION (Experiment 25): Gemini analyzes the agent's screen recording
AND the agent's per-step reasoning trace simultaneously. Tests whether intent
context (what the agent THOUGHT it was doing) sharpens the usability insights
beyond video-only analysis (Experiment 22).

Inputs:  videos/blinky_expert_80steps_2026-04-16.mkv  +  blinky_expert_thinking_log.md
Output:  exploration/outputs/agent_video/blinky_80step_video_plus_thinking.md
"""
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from google import genai
from google.genai import types

# Read from exploration/.env — fails fast if missing, never commit a default.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY_NEW")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY_NEW not set. Add it to exploration/.env (gitignored).")
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL = "gemini-2.5-flash"

VIDEO = Path(__file__).parent.parent / "videos" / "blinky_expert_80steps_2026-04-16.mkv"
THINKING_LOG = Path(__file__).parent.parent / "agent_interaction" / "outputs" / "2026-04-16_blinky_expert_80steps_1024x768" / "blinky_expert_thinking_log.md"
OUT_DIR = Path(__file__).parent / "outputs" / "agent_video"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "blinky_80step_video_plus_thinking.md"

PROMPT = """You are a senior usability researcher evaluating Eclipse 4diac IDE (3.0.2), an IEC 61499 industrial-automation IDE.

INPUTS provided to you:
1. A screen recording of an autonomous AI agent (Claude Sonnet 4.6 via Computer Use API) building the Blinky tutorial (E_CYCLE → E_SWITCH → E_SR toggling Q every second) in the IDE inside a Docker container at 1024×768, 80 steps total.
2. The agent's per-step textual reasoning trace, including [THINKING], [STEP], [OBSERVATION], [CD-DIMENSION], [SEVERITY], and [IDE-vs-AGENT] annotations the agent generated as it worked.

Compared to a video-only analysis, the reasoning trace tells you what the agent INTENDED at each step. Your unique job here is to find INTENT-vs-OUTCOME mismatches — moments where the agent thought it was doing one thing but the IDE silently did another, or refused, or led the agent down a different path than the agent expected.

Produce a usability assessment with this structure:

## 1. Intent-vs-outcome mismatches (the headline of this analysis)
For each: cite the step number and approximate video timestamp; quote the agent's intent (1 sentence); describe what actually happened on screen; map to a Cognitive Dimension (Blackwell & Green 2003); assign severity (Critical / Major / Minor).

## 2. Findings that are sharper with intent context
Usability issues that ARE present in the video alone, but that the agent's intent makes more confident or better-classified. Briefly note what intent context adds (e.g., "without intent we'd guess this was a user mistake; intent makes clear it's an IDE silent failure").

## 3. Findings that intent contradicts
Cases where the video LOOKS fine but the agent's reasoning reveals confusion or wasted effort.

## 4. Comparison with the video-only baseline (Experiment 22)
You don't have direct access to the prior assessment, but state which of your findings would have been impossible/weak from video alone, and which would have been findable from the video without intent.

## 5. Methodology verdict
Does adding the thinking log meaningfully change what AI-on-AI catches? One paragraph, direct answer.

Be specific. Cite step numbers. Use exact CD dimension names (Visibility, Viscosity, Hidden Dependencies, Role-Expressiveness, Error-Proneness, Consistency, Closeness of Mapping, Diffuseness, Premature Commitment, Abstraction, Hard Mental Operations, Provisionality, Secondary Notation, Progressive Evaluation).

The agent's thinking log follows after the video.
"""


def upload_video(video_path: Path):
    print(f"[upload] {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    video_file = client.files.upload(file=str(video_path))
    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)
        print(f"  state: {video_file.state.name}")
    if video_file.state.name == "FAILED":
        raise ValueError(f"video processing failed: {video_file.state.name}")
    print(f"[upload] ready: {video_file.uri}")
    return video_file


def main():
    if not VIDEO.exists():
        raise FileNotFoundError(VIDEO)
    if not THINKING_LOG.exists():
        raise FileNotFoundError(THINKING_LOG)

    thinking_text = THINKING_LOG.read_text()
    print(f"[input] thinking log: {len(thinking_text)} chars / {thinking_text.count(chr(10))} lines")

    video_file = upload_video(VIDEO)

    print(f"[infer] {MODEL}, prompt+video+thinking_log → assessment...")
    t0 = time.time()
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
                    types.Part.from_text(text=PROMPT),
                    types.Part.from_text(text="\n--- AGENT THINKING LOG ---\n\n" + thinking_text),
                ],
            )
        ],
    )
    dt = time.time() - t0
    print(f"[infer] done in {dt:.1f}s")

    text = response.text or ""
    header = (
        "# Gemini Assessment: video + thinking-log (Experiment 25 — flagship Blinky 80-step)\n"
        f"**Video:** {VIDEO.name} (29 MB)\n"
        f"**Thinking log:** {THINKING_LOG.name} ({thinking_text.count(chr(10))} lines)\n"
        f"**Model:** {MODEL}\n"
        f"**Timestamp:** {datetime.utcnow().isoformat()}Z\n"
        f"**Inference duration:** {dt:.1f}s\n"
        "**Context:** Phase 4 EXTENSION — first run combining agent screen recording + per-step "
        "reasoning trace as joint input to a meta-analysis model. Extends Experiment 22 "
        "(video-only Phase 4) by adding intent context.\n\n---\n\n"
    )
    OUT_FILE.write_text(header + text)
    print(f"[write] {OUT_FILE} ({len(text)} chars)")


if __name__ == "__main__":
    main()
