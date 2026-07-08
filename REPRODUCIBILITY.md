# Reproducibility Checklist

A quick pre-flight list for replicating the experiments in this repository. See
[README.md](README.md) for the full commands, and
[FULL_SESSION_LOG.md](FULL_SESSION_LOG.md) / [SESSION_LOG_WINDOWS.md](SESSION_LOG_WINDOWS.md)
for step-by-step logs (macOS and Windows).

## Environment
- [ ] Python 3.11 (conda env named `4diac`)
- [ ] Dependencies installed: `google-genai openai anthropic python-dotenv Pillow yt-dlp`
- [ ] `ffmpeg` and `yt-dlp` available on PATH
- [ ] Docker Desktop for the agent experiments (native x86_64 recommended; ARM/QEMU works but is slow)
- [ ] `exploration/.env` created with `GOOGLE_API_KEY`, `GOOGLE_API_KEY_NEW`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`

## Media in place (see README "Videos and frames")
- [ ] `videos/task_demo.mkv`, `videos/intro_v1.mkv`, `videos/intro_v2.webm` (from YouTube via yt-dlp)
- [ ] Agent/blinky recordings in `videos/` from Google Drive, exact filenames (spaces included)
- [ ] Frames in `exploration/frames/td/` and `exploration/frames/td_3s/` (download from Drive, or regenerate with the two ffmpeg commands)

## Passive analysis: video and screenshots
- [ ] `python gemini_video_assess.py td blind` (also `cd_guided`, `task_specific`)
- [ ] `python assess_screenshots.py <level> <models> 6frames` (and `20frames`)
- [ ] New outputs land in `exploration/outputs/` and line up with the reference outputs committed here

## Interactive assessment: computer-use agent (Docker)
- [ ] `docker compose up --build -d` brings up 4diac IDE + VNC (open http://localhost:6080/vnc.html)
- [ ] `python agent_interaction/claude_computer_use.py <task>` runs a task (e.g. `task1_orientation`, `blinky_expert`)
- [ ] Step screenshots, JSON, and a report are written to `agent_interaction/outputs/`

## AI-on-AI: assess an agent's own recording
- [ ] `python exploration/assess_agent_video.py` (agent screen recording)
- [ ] `python exploration/assess_agent_video_with_thinking.py` (recording plus the agent's reasoning trace)

## Sanity check
- [ ] Detected issues compared against the ten ground-truth issues from Wiesmayr et al. (2023)
- [ ] Results documented and limitations noted
