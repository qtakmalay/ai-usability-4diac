# 4diac IDE — AI-Based Usability Assessment

Automated usability assessment of [Eclipse 4diac IDE](https://eclipse.dev/4diac/) using multimodal AI models and agent-based interaction.

**Seminar + Practicum** at JKU Linz (LIT CPS Lab)
**Student:** Azat Vakhitov | **Supervisors:** Prof. Alois Zoitl, Rick Rabiser

---

## What This Is

Two approaches to automated usability evaluation:

1. **Passive Analysis** — Send IDE demo videos/screenshots to AI models (Gemini, GPT-4o, Claude) and ask them to identify usability issues
2. **Interactive Assessment** — An AI agent (Claude Computer Use) runs the IDE in Docker and interacts with it via mouse/keyboard, reporting issues from first-hand experience

Both are compared against ground truth from [Wiesmayr et al. (2023)](https://doi.org/10.1007/s10270-023-01084-7) — a human usability study with 10 automation engineers.

**Key result:** Gemini + video detected roughly 8/10 of the known usability issues (6 full, 2 partial) from a single video with zero human participants.

---

## Project Structure

```
├── exploration/                    # Passive analysis: video + screenshot assessment
│   ├── prompts.py                  # 3 prompt levels (blind, CD-guided, task-specific)
│   ├── gemini_video_assess.py      # Gemini video assessment (task_demo / intro videos)
│   ├── assess_screenshots.py       # Multi-model screenshot (frame) assessment
│   ├── assess_agent_video.py       # AI-on-AI: Gemini assesses an agent's screen recording
│   ├── assess_agent_video_with_thinking.py  # AI-on-AI, recording + agent reasoning trace
│   ├── assess_new_videos.py        # Newer-version video assessment (see note under Setup)
│   ├── frames/                     # Extracted frames (gitignored; from Drive or ffmpeg)
│   └── outputs/                    # Outputs: gemini_video/, screenshots/, agent_video/, new_version/
│
├── agent_interaction/              # Interactive assessment: computer-use agent
│   ├── Dockerfile                  # Ubuntu + Java + 4diac IDE + VNC
│   ├── docker-compose.yml          # Container config (1024x768)
│   ├── start.sh                    # Entrypoint script
│   ├── tasks.py                    # 4 task definitions from the paper + blinky_expert
│   ├── claude_computer_use.py      # Claude Computer Use agent loop
│   ├── EXPERIMENTS.md              # Experiment documentation
│   ├── RESEARCH_UI_AGENTS.md       # Survey of 12+ UI agents
│   ├── RUN_BLINKY_EXPERIMENT.md    # How to run the Blinky tutorial build
│   └── outputs/                    # Agent results + per-step screenshots
│
└── videos/                         # Video inputs (gitignored; from YouTube + Google Drive)
```

---

## Setup (Windows)

### Prerequisites

1. **Python 3.11+** via [Miniconda](https://docs.anaconda.com/miniconda/)
2. **Docker Desktop** for Windows (with WSL2 backend)
3. **Git** for Windows
4. **ffmpeg** — `winget install ffmpeg` or download from https://ffmpeg.org
5. **yt-dlp** — `pip install yt-dlp`

### Step 1: Clone & Setup Environment

```powershell
git clone https://github.com/qtakmalay/ai-usability-4diac.git
cd ai-usability-4diac

# Create conda environment
conda create -n 4diac python=3.11 -y
conda activate 4diac

# Install Python dependencies
pip install google-genai openai anthropic python-dotenv Pillow yt-dlp
```

### Step 2: API Keys

Create `exploration/.env`:

```env
GOOGLE_API_KEY=<your-google-gemini-api-key>
GOOGLE_API_KEY_NEW=<a-second-gemini-key>
OPENAI_API_KEY=<your-openai-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

Get keys from:
- Google: https://aistudio.google.com/apikey
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

`GOOGLE_API_KEY_NEW` is a second Gemini key used only by the agent-video scripts
(`assess_agent_video.py`, `assess_agent_video_with_thinking.py`); it can be the same value as
`GOOGLE_API_KEY`. The `.env` file must live at `exploration/.env` and is gitignored — never commit it.

### Step 3: Videos and frames

All video inputs live in a `videos/` folder at the repo root; extracted frames live under
`exploration/frames/`. Both are gitignored (too large for git), so fetch them once.

**a) The three demo videos come from YouTube** (via yt-dlp):

```powershell
mkdir videos
yt-dlp -o "videos/task_demo.%(ext)s" "https://youtu.be/xishphcgYmc"
yt-dlp -o "videos/intro_v1.%(ext)s" "https://youtu.be/K9iItQBC-ac"
yt-dlp -o "videos/intro_v2.%(ext)s" "https://youtu.be/by02Xu2yrPE"
```

**b) The agent recordings and user-session videos come from Google Drive:**

Download folder: **https://drive.google.com/drive/folders/1aPE9RjXhAXFG0XiRws4NSEL2VcWAzV2-?usp=sharing**

Place these into `videos/` with their **exact filenames** (the spaces matter — the scripts reference them literally):

| File | Used by |
|------|---------|
| `agent 121 step sonnet 4-6.mp4` | `assess_agent_video.py` (default input) |
| `blinky_expert_80steps_2026-04-16.mkv` | `assess_agent_video_with_thinking.py` |
| `blinky_expert_38steps_failed_2026-04-16.mkv` | reference (a failed agent run) |
| `blinky_expert_30steps_test_2026-04-16.mkv` | reference (a short test run) |
| `user 5-20.mkv`, `user 11-44.mkv` | reference user-session recordings |

**c) Frames** (needed for the screenshot experiments) are in the same Drive folder under `frames/`.
Download it so you end up with `exploration/frames/td/` and `exploration/frames/td_3s/`. If you would
rather regenerate them, use the two ffmpeg commands in the run section below — they derive only from
`task_demo.mkv` (`td` = 1 frame every 10 s, `td_3s` = 1 frame every 3 s).

> **Note:** `assess_new_videos.py` and the `new_a` / `new_b` keys in `gemini_video_assess.py` refer
> to two newer-version recordings (`2026-03-19 …`) that are **not included** in the Drive folder, so
> that specific comparison is not reproducible from this repo as-is. Every other experiment is.

### Step 4: Download Papers (not in repo)

- Ground truth paper: https://doi.org/10.1007/s10270-023-01084-7 → save as `s10270-023-01084-7-1.pdf`
- Gemini paper: https://arxiv.org/abs/2312.11805 → save as `2312.11805v5.pdf`

---

## Running Passive Analysis: Video/Screenshot Assessment

```powershell
conda activate 4diac
cd exploration

# Gemini video assessments
python gemini_video_assess.py td blind
python gemini_video_assess.py td cd_guided
python gemini_video_assess.py td task_specific

# Extract frames for the screenshot assessment
# (skip this if you already downloaded the frames/ folder from Google Drive)
mkdir -p frames\td frames\td_3s
ffmpeg -i ..\videos\task_demo.mkv -vf "fps=1/10" -q:v 2 frames\td\frame_%04d.jpg
ffmpeg -i ..\videos\task_demo.mkv -vf "fps=1/3" -q:v 2 frames\td_3s\frame_%04d.jpg

# Screenshot assessments
python assess_screenshots.py blind all 6frames
python assess_screenshots.py cd_guided all 6frames
python assess_screenshots.py blind claude 20frames
python assess_screenshots.py cd_guided claude 20frames

# AI-on-AI: Gemini assesses an agent's own screen recording
# (needs GOOGLE_API_KEY_NEW and the agent videos from Google Drive)
python assess_agent_video.py
python assess_agent_video_with_thinking.py
```

---

## Running Interactive Assessment: Agent Interaction (Docker)

**Windows advantage:** No QEMU emulation needed — Docker runs natively on x86_64.

```powershell
cd agent_interaction

# Build and start 4diac IDE container
docker compose up --build -d

# Verify IDE is running (should see Java process)
docker exec agent_interaction-4diac-ide-1 ps aux | findstr 4diac

# Install interaction tools
docker exec agent_interaction-4diac-ide-1 bash -c "apt-get update -qq && apt-get install -y -qq xdotool scrot"

# Take test screenshot
docker exec agent_interaction-4diac-ide-1 bash -c "DISPLAY=:1 scrot /tmp/screen.png"
docker cp agent_interaction-4diac-ide-1:/tmp/screen.png screen_check.png

# Open in browser to verify visually
start http://localhost:6080/vnc.html

# Run agent experiment (Task 1)
cd ..
python agent_interaction\claude_computer_use.py task1_orientation

# Run all 4 tasks
python agent_interaction\claude_computer_use.py

# Stop container
cd agent_interaction
docker compose down
```

### Windows-Specific Notes

- **No `platform: linux/amd64` needed** on x86_64 Windows — remove or comment out that line in `docker-compose.yml` if it causes issues
- **Docker Desktop WSL2 backend** is required (not Hyper-V)
- **VNC access:** Open `http://localhost:6080/vnc.html` in a browser to see the IDE visually
- **Path separators:** Use `\` in PowerShell or `/` in Git Bash

---

## Results Summary

| Approach | Model | Input | Issues Detected | Notes |
|----------|-------|-------|:---:|-------|
| Video | Gemini 2.5 Flash | task_demo.mkv | **~8/10** | Best overall approach |
| Screenshots (20) | Gemini 2.5 Flash | 20 frames | ~5/10 | |
| Screenshots (20) | Claude Sonnet 4 | 20 frames | ~3/10 | |
| Screenshots (20) | GPT-4o | 20 frames | ~2/10 | |
| Agent (initial) | Claude Sonnet 4.6 (CU) | Live IDE 1920x1080 | 12 unique | Surface-level (Welcome/menus) |
| Agent (refined) | Claude Sonnet 4.6 (CU) | Live IDE 1024x768 | **15 unique** | **Deep workflow issues** |

---

## Documentation

| Document | Description |
|----------|-------------|
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Pre-flight checklist for replicating every experiment |
| [FULL_SESSION_LOG.md](FULL_SESSION_LOG.md) | Step-by-step replication log (macOS), with commands and gotchas |
| [SESSION_LOG_WINDOWS.md](SESSION_LOG_WINDOWS.md) | Step-by-step replication log (Windows, native x86_64) |
| [progress.md](progress.md) | Project overview: ground-truth issues, experiments, model comparison, tips |
| [agent_interaction/EXPERIMENTS.md](agent_interaction/EXPERIMENTS.md) | Agent interaction experiment details + screenshots |
| [agent_interaction/RUN_BLINKY_EXPERIMENT.md](agent_interaction/RUN_BLINKY_EXPERIMENT.md) | How to run the Blinky tutorial-build experiment |
| [agent_interaction/RESEARCH_UI_AGENTS.md](agent_interaction/RESEARCH_UI_AGENTS.md) | Survey of 12+ UI interaction agents |

---

## References

1. Wiesmayr, B., Zoitl, A., & Rabiser, R. (2023). *Assessing the usefulness of a visual programming IDE for large-scale automation software.* Software and Systems Modeling, 22, 1619-1643.
2. Blackwell, A.F. & Green, T.R.G. (2003). *Notational systems — The cognitive dimensions of notations framework.*
3. Study materials: [Zenodo DOI 10.5281/ZENODO.4758816](https://doi.org/10.5281/ZENODO.4758816)
