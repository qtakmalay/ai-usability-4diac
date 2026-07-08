"""Claude Computer Use agent for 4diac IDE usability assessment.

Connects to 4diac IDE running in Docker via VNC, performs tasks,
and reports usability issues found during interaction.
"""

import sys
import io

# Fix Windows cp1252 encoding issues — force UTF-8 for stdout/stderr
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import anthropic
import base64
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tasks import TASKS, SYSTEM_PROMPT

# Load API key
load_dotenv(Path(__file__).parent.parent / "exploration" / ".env")

DISPLAY_WIDTH = 1024
DISPLAY_HEIGHT = 768
CONTAINER_NAME = "agent_interaction-4diac-ide-1"
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def take_screenshot() -> str:
    """Take screenshot from Docker container, return base64-encoded PNG."""
    # Take screenshot inside container
    subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "bash", "-c",
         "DISPLAY=:1 scrot -o /tmp/screen.png"],
        check=True, capture_output=True
    )
    # Copy to host
    tmp_path = "/tmp/4diac_screen.png"
    subprocess.run(
        ["docker", "cp", f"{CONTAINER_NAME}:/tmp/screen.png", tmp_path],
        check=True, capture_output=True
    )
    with open(tmp_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def _focus_window():
    """Focus the 4diac IDE window before any action."""
    subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "bash", "-c",
         "DISPLAY=:1 WID=$(xdotool search --name '4diac' | tail -1) && "
         "DISPLAY=:1 xdotool windowfocus --sync $WID && "
         "DISPLAY=:1 xdotool windowactivate --sync $WID"],
        capture_output=True, timeout=5
    )


def execute_action(action: dict) -> str:
    """Execute a computer use action in the Docker container."""
    action_type = action.get("action")
    coord = action.get("coordinate")
    text = action.get("text")

    if action_type == "screenshot":
        return "screenshot_requested"

    # Always focus window first
    _focus_window()

    cmd_parts = []
    post_delay = 1.0  # QEMU is slow, need longer delays

    if action_type == "mouse_move" and coord:
        cmd_parts = [f"DISPLAY=:1 xdotool mousemove {coord[0]} {coord[1]}"]

    elif action_type == "left_click" and coord:
        cmd_parts = [
            f"DISPLAY=:1 xdotool mousemove {coord[0]} {coord[1]}",
            "sleep 0.3",
            "DISPLAY=:1 xdotool click 1"
        ]

    elif action_type == "right_click" and coord:
        cmd_parts = [
            f"DISPLAY=:1 xdotool mousemove {coord[0]} {coord[1]}",
            "sleep 0.3",
            "DISPLAY=:1 xdotool click 3"
        ]

    elif action_type == "double_click" and coord:
        cmd_parts = [
            f"DISPLAY=:1 xdotool mousemove {coord[0]} {coord[1]}",
            "sleep 0.3",
            "DISPLAY=:1 xdotool click --repeat 2 --delay 200 1"
        ]

    elif action_type == "triple_click" and coord:
        cmd_parts = [
            f"DISPLAY=:1 xdotool mousemove {coord[0]} {coord[1]}",
            "sleep 0.3",
            "DISPLAY=:1 xdotool click --repeat 3 --delay 200 1"
        ]

    elif action_type == "left_click_drag" and coord:
        start = action.get("start_coordinate", [0, 0])
        cmd_parts = [
            f"DISPLAY=:1 xdotool mousemove {start[0]} {start[1]}",
            "sleep 0.3",
            "DISPLAY=:1 xdotool mousedown 1",
            "sleep 0.2",
            f"DISPLAY=:1 xdotool mousemove --delay 100 {coord[0]} {coord[1]}",
            "sleep 0.2",
            "DISPLAY=:1 xdotool mouseup 1"
        ]

    elif action_type == "type" and text:
        escaped = text.replace("'", "'\\''")
        cmd_parts = [f"DISPLAY=:1 xdotool type --clearmodifiers --delay 80 '{escaped}'"]

    elif action_type == "key" and text:
        key = text.replace("Return", "Return").replace("Tab", "Tab")
        cmd_parts = [f"DISPLAY=:1 xdotool key --clearmodifiers {key}"]

    elif action_type == "scroll" and coord:
        direction = action.get("delta_y", 0)
        button = 5 if direction > 0 else 4
        clicks = abs(direction) // 50 or 1
        cmd_parts = [
            f"DISPLAY=:1 xdotool mousemove {coord[0]} {coord[1]}",
            "sleep 0.3",
            f"DISPLAY=:1 xdotool click --repeat {clicks} {button}"
        ]

    elif action_type == "wait":
        time.sleep(action.get("duration", 2))
        return "waited"

    elif action_type == "cursor_position":
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "bash", "-c",
             "DISPLAY=:1 xdotool getmouselocation"],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    if cmd_parts:
        full_cmd = " && ".join(cmd_parts)
        subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "bash", "-c", full_cmd],
            capture_output=True, timeout=15
        )
        time.sleep(post_delay)  # QEMU needs longer delays
        return f"executed: {action_type}"

    return f"unknown action: {action_type}"


def run_task(task_key: str, max_steps_override: int | None = None) -> dict:
    """Run a single usability assessment task."""
    task = TASKS[task_key]
    print(f"\n{'='*60}")
    print(f"Starting: {task['name']}")
    print(f"{'='*60}\n")

    client = anthropic.Anthropic()

    tools = [
        {
            "type": "computer_20251124",
            "name": "computer",
            "display_width_px": DISPLAY_WIDTH,
            "display_height_px": DISPLAY_HEIGHT,
            "display_number": 1,
        }
    ]

    # Use per-task system prompt if defined, else default
    task_system_prompt = task.get("system_prompt", SYSTEM_PROMPT)

    print("Taking initial screenshot...")
    initial_ss = take_screenshot()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": task["description"]},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": initial_ss,
                    },
                },
            ],
        }
    ]

    steps = []
    thinking_log = []  # Capture all agent reasoning per step
    step_num = 0
    configured_max_steps = task.get("max_steps")
    max_steps = max_steps_override if max_steps_override is not None else configured_max_steps
    hard_cap = int(os.getenv("HARD_MAX_STEPS", "300"))
    final_text = ""
    termination_reason = None

    while True:
        if max_steps is not None and step_num >= max_steps:
            termination_reason = f"configured_max_steps_reached:{max_steps}"
            print(f"Stopping: configured max_steps reached ({max_steps})")
            break

        if step_num >= hard_cap:
            termination_reason = f"hard_cap_reached:{hard_cap}"
            print(f"Stopping: hard cap reached ({hard_cap})")
            break

        step_num += 1
        step_label = f"{step_num}/{max_steps}" if max_steps is not None else f"{step_num}/∞"
        print(f"\n--- Step {step_label} ---")

        try:
            response = client.beta.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=task_system_prompt,
                tools=tools,
                messages=messages,
                betas=["computer-use-2025-11-24"],
            )
        except Exception as e:
            termination_reason = f"api_error:{e}"
            print(f"API error: {e}")
            break

        for block in response.content:
            if hasattr(block, "text"):
                print(f"Claude: {block.text[:200]}")
                final_text += block.text + "\n"
                thinking_log.append({
                    "step": step_num,
                    "timestamp": datetime.now().isoformat(),
                    "text": block.text,
                })

        if response.stop_reason == "end_turn":
            termination_reason = "task_completed_end_turn"
            print("Task completed (end_turn)")
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    action = block.input
                    action_type = action.get("action", "unknown")
                    print(f"  Action: {action_type} {action.get('coordinate', '')}")

                    step_record = {
                        "step": step_num,
                        "action": action_type,
                        "coordinate": action.get("coordinate"),
                        "text": action.get("text"),
                        "timestamp": datetime.now().isoformat(),
                    }
                    steps.append(step_record)

                    if action_type == "screenshot":
                        ss_data = take_screenshot()
                        ss_path = OUTPUT_DIR / f"{task_key}_step{step_num:03d}.png"
                        with open(ss_path, "wb") as f:
                            f.write(base64.b64decode(ss_data))

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": ss_data,
                                    },
                                }
                            ],
                        })
                    else:
                        result = execute_action(action)
                        ss_data = take_screenshot()
                        ss_path = OUTPUT_DIR / f"{task_key}_step{step_num:03d}.png"
                        with open(ss_path, "wb") as f:
                            f.write(base64.b64decode(ss_data))

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

            messages.append({"role": "user", "content": tool_results})
        else:
            termination_reason = f"unexpected_stop_reason:{response.stop_reason}"
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

    result = {
        "task": task["name"],
        "task_key": task_key,
        "total_steps": step_num,
        "max_steps": max_steps,
        "hard_cap": hard_cap,
        "termination_reason": termination_reason,
        "steps": steps,
        "thinking_log": thinking_log,
        "final_report": final_text,
        "timestamp": datetime.now().isoformat(),
    }

    json_path = OUTPUT_DIR / f"{task_key}_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save thinking log as separate file for analysis
    thinking_path = OUTPUT_DIR / f"{task_key}_thinking_log.md"
    with open(thinking_path, "w", encoding="utf-8") as f:
        f.write(f"# Thinking Log — {task['name']}\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Model:** claude-sonnet-4-6\n")
        f.write(f"**Steps:** {step_num}\n\n---\n\n")
        for entry in thinking_log:
            f.write(f"### Step {entry['step']} ({entry['timestamp'][:19]})\n\n")
            f.write(entry['text'])
            f.write("\n\n---\n\n")

    md_path = OUTPUT_DIR / f"{task_key}_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {task['name']} — Claude Computer Use Assessment\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Model:** claude-sonnet-4-6\n")
        f.write(f"**Steps taken:** {step_num}\n")
        f.write(f"**Configured max_steps:** {max_steps}\n")
        f.write(f"**Hard cap:** {hard_cap}\n")
        f.write(f"**Termination reason:** {termination_reason}\n\n")
        f.write("## Agent's Report\n\n")
        f.write(final_text)
        f.write("\n\n## Action Log\n\n")
        f.write("| Step | Action | Coordinate | Text |\n")
        f.write("|------|--------|------------|------|\n")
        for s in steps:
            text_val = s.get('text') or ''
            f.write(f"| {s['step']} | {s['action']} | {s.get('coordinate', '')} | {text_val[:50]} |\n")

    print(f"\nResults saved to {json_path} and {md_path}")
    return result


def main():
    import sys

    print("Ensuring xdotool is installed in container...")
    subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "bash", "-c",
         "which xdotool || (apt-get update -qq && apt-get install -y -qq xdotool)"],
        capture_output=True
    )

    max_steps_override = None
    task_key = None

    args = sys.argv[1:]
    for arg in args:
        if arg.startswith("--max-steps="):
            value = arg.split("=", 1)[1].strip().lower()
            max_steps_override = None if value in ("none", "inf", "unlimited") else int(value)
        else:
            task_key = arg

    if task_key:
        if task_key in TASKS:
            run_task(task_key, max_steps_override=max_steps_override)
        else:
            print(f"Unknown task: {task_key}")
            print(f"Available: {', '.join(TASKS.keys())}")
    else:
        for task_key in TASKS:
            run_task(task_key, max_steps_override=max_steps_override)
            print("\nWaiting 5s before next task...")
            time.sleep(5)


if __name__ == "__main__":
    main()
