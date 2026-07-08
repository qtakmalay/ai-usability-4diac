"""
Gemini Video Assessment of Agent Interaction Recording.
Sends the 121-step agent screen recording to Gemini for usability analysis.

This is a novel experiment: AI observing another AI's interaction with the IDE.
"""

import os
import sys
import json
import time
from pathlib import Path
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

DEFAULT_VIDEO = Path(__file__).parent.parent / "videos" / "agent 121 step sonnet 4-6.mp4"
VIDEOS_DIR = Path(__file__).parent.parent / "videos"
OUTPUT_DIR = Path(__file__).parent / "outputs" / "agent_video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Prompt: blind assessment of the agent's interaction
AGENT_BLIND_PROMPT = """You are a UX/usability expert. Watch this screen recording of an AI agent (Claude Computer Use) attempting to use the Eclipse 4diac IDE — a visual programming environment for industrial automation based on IEC 61499.

The AI agent controls the mouse and keyboard automatically, trying to complete a usability assessment task: exploring the IDE, creating a project, finding function blocks, and navigating the hierarchy.

Assess the usability of this IDE based on what you observe in the agent's interaction. Focus on:
1. What usability issues does the agent encounter? Which are genuine IDE problems vs agent limitations?
2. Where does the agent get stuck or confused? What does this reveal about the IDE's design?
3. What UI elements are hard to interact with (small targets, unclear labels, missing feedback)?
4. What workflows seem unnecessarily complex or unintuitive?
5. What are the IDE's strengths that you observe?
6. How does the IDE's first-time user experience look (project creation, navigation, adding components)?

Be specific and reference particular moments or UI elements you observe. Note timestamps where possible.

Important: Distinguish between issues caused by the IDE's design (genuine usability problems) and issues caused by the AI agent's limitations (e.g., inability to drag-and-drop precisely)."""

# Prompt: CD-guided assessment
AGENT_CD_GUIDED_PROMPT = """You are a UX/usability expert. Watch this screen recording of an AI agent (Claude Computer Use) attempting to use the Eclipse 4diac IDE — a visual programming environment for industrial automation (IEC 61499 standard).

The AI agent controls mouse and keyboard automatically, trying to: explore the IDE, create a project, add function block types, and navigate the hierarchy.

Evaluate the usability using the Cognitive Dimensions of Notations framework. For each dimension, assess based on what you observe in the agent's interaction:

1. **Viscosity** — How much effort is needed to make changes? Are there repetitive actions?
2. **Visibility** — Can users easily see all relevant information? Is anything buried or hidden?
3. **Premature Commitment** — Are users forced to make decisions before having enough information?
4. **Hidden Dependencies** — Are there important links between elements that aren't visible?
5. **Role-Expressiveness** — Can users understand the purpose of each UI element from its appearance?
6. **Error-Proneness** — Does the interface invite mistakes? Is there sufficient protection/feedback?
7. **Abstraction** — Are the abstraction mechanisms appropriate?
8. **Secondary Notation** — Can users add informal notes/comments/colors?
9. **Closeness of Mapping** — How well does the visual representation match domain concepts?
10. **Consistency** — Are similar things expressed in similar ways throughout?
11. **Diffuseness** — Is the notation verbose? Do large elements reduce working area?
12. **Hard Mental Operations** — Are there tasks that place high cognitive load?
13. **Provisionality** — Can users make tentative changes easily?
14. **Progressive Evaluation** — Can users check their work-in-progress?

For each dimension, rate it as: GOOD, MODERATE, or POOR, and explain what you observed from the agent's interaction.

Important: Note where issues are IDE design problems vs AI agent limitations.

End with a summary of the top 5 most critical usability issues observed."""


def upload_video(video_path: Path):
    """Upload video to Gemini API and wait for processing."""
    print(f"Uploading {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    video_file = client.files.upload(file=str(video_path))
    print(f"Upload complete. Waiting for processing...")

    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)
        print(f"  State: {video_file.state.name}")

    if video_file.state.name == "FAILED":
        raise ValueError(f"Video processing failed: {video_file.state.name}")

    print(f"Video ready: {video_file.uri}")
    return video_file


def assess_video(video_file, prompt: str) -> str:
    """Send video + prompt to Gemini and get assessment."""
    print(f"Sending to {MODEL}...")
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
                    types.Part.from_text(text=prompt),
                ],
            )
        ],
    )
    return response.text


def main():
    # Usage: python assess_agent_video.py [blind|cd_guided|all] [video_filename]
    level = sys.argv[1] if len(sys.argv) > 1 else "blind"
    video_arg = sys.argv[2] if len(sys.argv) > 2 else None

    if video_arg:
        VIDEO_PATH = VIDEOS_DIR / video_arg
    else:
        VIDEO_PATH = DEFAULT_VIDEO

    if not VIDEO_PATH.exists():
        print(f"ERROR: Video not found: {VIDEO_PATH}")
        print(f"Available videos:")
        for f in VIDEOS_DIR.glob("*.mp4"):
            print(f"  {f.name}")
        for f in VIDEOS_DIR.glob("*.mkv"):
            print(f"  {f.name}")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"Gemini Video Assessment — Agent Interaction Recording")
    print(f"Video: {VIDEO_PATH.name}")
    print(f"Model: {MODEL}")
    print(f"Prompt: {level}")
    print(f"{'='*60}\n")

    video_file = upload_video(VIDEO_PATH)

    prompts = {}
    if level in ("all", "blind"):
        prompts["agent_blind"] = AGENT_BLIND_PROMPT
    if level in ("all", "cd_guided"):
        prompts["agent_cd_guided"] = AGENT_CD_GUIDED_PROMPT

    results = {}
    for name, prompt in prompts.items():
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")

        try:
            response = assess_video(video_file, prompt)
            results[name] = {
                "prompt_level": name,
                "model": MODEL,
                "video": VIDEO_PATH.name,
                "response": response,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            output_file = OUTPUT_DIR / f"{name}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Gemini Assessment: {name}\n")
                f.write(f"**Video:** {VIDEO_PATH.name}\n")
                f.write(f"**Model:** {MODEL}\n")
                f.write(f"**Timestamp:** {results[name]['timestamp']}\n")
                f.write(f"**Context:** Screen recording of Claude Sonnet 4.6 (Computer Use) interacting with 4diac IDE 3.0.2 in Docker at 1024x768. 121 steps, unlimited mode.\n\n")
                f.write(f"---\n\n")
                f.write(response)

            print(f"\nSaved to: {output_file}")
            print(f"\nResponse preview:\n{response[:500]}...")

        except Exception as e:
            print(f"ERROR on {name}: {e}")
            results[name] = {"error": str(e)}

        if len(prompts) > 1:
            print("\nWaiting 5s (rate limit)...")
            time.sleep(5)

    combined_file = OUTPUT_DIR / "agent_video_results.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nAll results saved to: {combined_file}")

    try:
        client.files.delete(name=video_file.name)
        print("Uploaded video cleaned up.")
    except Exception:
        pass

    print(f"\n{'='*60}")
    print(f"DONE — {len([r for r in results.values() if 'error' not in r])} successful assessments")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
