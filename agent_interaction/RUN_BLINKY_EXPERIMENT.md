# How to Run the Expert Blinky Experiment
## 4diac IDE 3.0.2 | Windows 11 x86_64 | April 2026

---

## Prerequisites

- Docker Desktop running (WSL2 backend)
- Conda environment `4diac` with `anthropic` package
- Anthropic API key with ~$15 credit (estimate: 80 steps × ~$0.15/step)
- OBS Studio (optional, for screen recording → Gemini analysis)

---

## Step-by-Step Instructions

### 1. Start Fresh Docker Container

```powershell
cd C:\Users\you\Desktop\ai-user\4diac\agent_interaction

# Clean previous workspace state (ensures Welcome screen appears)
rmdir /s /q workspace\.metadata 2>nul

# Build and start container
docker compose down 2>nul
docker compose up --build -d

# Wait for IDE to fully load (~15 seconds)
timeout /t 15
```

### 2. Install Interaction Tools (required after every rebuild)

```powershell
docker exec agent_interaction-4diac-ide-1 bash -c "apt-get update -qq && apt-get install -y -qq xdotool scrot"
```

### 3. Verify IDE is Running

```powershell
# Check all processes
docker exec agent_interaction-4diac-ide-1 ps aux | findstr "4diac java Xvfb vnc fluxbox"

# Verify screenshot works
docker exec agent_interaction-4diac-ide-1 bash -c "DISPLAY=:1 scrot /tmp/screen.png"
docker cp agent_interaction-4diac-ide-1:/tmp/screen.png screen_check.png

# Visual check in browser
start http://127.0.0.1:6080/vnc.html
```

Confirm you see: 4diac IDE Welcome screen at **1024x768** resolution.

### 4. (Optional) Start OBS Recording

Open OBS Studio, set source to the noVNC browser window or full screen capture.
Start recording BEFORE running the agent. Save as MP4.

### 5. Run the Expert Blinky Experiment

```powershell
cd C:\Users\you\Desktop\ai-user\4diac

# With max 80 steps (recommended — covers Blinky build, ~$12 estimated cost)
C:/Users/you/anaconda3/envs/4diac/python.exe agent_interaction/claude_computer_use.py blinky_expert

# Or unlimited (will stop on end_turn or credits, hard cap 300)
C:/Users/you/anaconda3/envs/4diac/python.exe agent_interaction/claude_computer_use.py blinky_expert --max-steps=none
```

### 6. Stop OBS Recording

After the agent finishes (prints "Results saved to..."), stop OBS recording.
Save the video as: `videos/blinky_expert_YYYY-MM-DD.mp4`

### 7. Check Output

Output files will be in `agent_interaction/outputs/`:
```
blinky_expert_results.json      — Full action log + thinking
blinky_expert_report.md         — Agent's usability report
blinky_expert_thinking_log.md   — Step-by-step reasoning (NEW)
blinky_expert_step001.png       — Screenshot at each step
blinky_expert_step002.png
...
```

### 8. Move Outputs to Dated Folder

```powershell
cd agent_interaction\outputs
mkdir "2026-MM-DD_blinky_expert_80steps_1024x768"
move blinky_expert_* "2026-MM-DD_blinky_expert_80steps_1024x768\"
```

### 9. Stop Container

```powershell
cd C:\Users\you\Desktop\ai-user\4diac\agent_interaction
docker compose down
```

---

## Step Estimate & Cost

| Scenario | Steps | Est. Cost | Time |
|----------|:-----:|:---------:|:----:|
| Blinky build succeeds smoothly | ~40-50 | ~$7 | ~5 min |
| Blinky build with some struggles | ~60-80 | ~$12 | ~8 min |
| Gets stuck, uses full budget | 80 | ~$12 | ~10 min |
| Unlimited (runs until credits out) | 100-150 | ~$15-25 | ~15 min |

**Recommended: 80 steps** — enough to build Blinky + write report. The task prompt tells the agent to stop after Phase 4 and write the report.

---

## What's Different From Previous Runs

| Feature | Previous Runs | This Run |
|---------|--------------|----------|
| System prompt | Generic usability expert | **Expert IEC 61499 engineer persona** |
| Task | Open-ended exploration | **Specific: build Blinky step-by-step** |
| CD assessment | Not in prompt | **Built into every observation** |
| Thinking log | Not saved | **Saved per-step as `_thinking_log.md`** |
| Blocker handling | Agent loops forever | **Skip after 5 attempts, document blocker** |
| IDE knowledge | None | **Full tutorial + manual knowledge in prompt** |
| Trade-off reasoning | None | **CD trade-off analysis per issue** |
| Stop mechanism | Max steps or API credits | **Agent instructed to stop after Phase 4** |
| Issue format | Free-form | **Structured: step/observation/CD/severity/IDE-vs-agent** |

---

## Paper Practices Applied

| Practice | Source Paper | How Applied |
|----------|-------------|-------------|
| Expert persona | UXAgent (CHI EA '25) | Dr. Elena Vogt, 12 years IEC 61499 experience |
| CD-guided assessment | CD Framework (2003) | All 14 dimensions in prompt, per-issue tagging |
| Trade-off reasoning | CD Framework | "Would fixing this create a new problem?" |
| Few-shot examples | UICrit (UIST 2024) | Example critique format in prompt |
| Structured observation | UXCascade (2026) | Step/Observation/CD/Severity/IDE-vs-Agent format |
| Thinking-first | UXAgent slow loop | [THINKING] block before every action |
| Stop-and-report | UXCascade 25-step cap | Agent instructed to stop after Phase 4 |
| F1 ground truth matching | CHI 2024 | Agent told to match against known 10 issues |
| Keyboard fallbacks | SeeAct grounding | Alt+F, Ctrl+N when clicks fail |
| IDE knowledge in context | VideoWebArena factual retention | Full tutorial embedded in prompt |

---

## For Manual Testing (If You Want to Do It Yourself)

### Open the IDE

```
http://127.0.0.1:6080/vnc.html
```

### Follow the Blinky Tutorial Manually

1. File > New > 4diac IDE Project > Name: "BlinkTest" > Finish
2. In the Application Editor (should open automatically):
   - From Palette (right side) > Standard Libraries > events:
     - Drag **E_CYCLE** onto canvas
     - Drag **E_SWITCH** onto canvas
     - Drag **E_SR** onto canvas
3. Click E_CYCLE > Properties > set **DT** = `T#1s`
4. Connect:
   - E_CYCLE.**EO** → E_SWITCH.**EI** (event connection)
   - E_SR.**Q** → E_SWITCH.**G** (data connection)
   - E_SWITCH.**EO0** → E_SR.**R** (event connection)
   - E_SWITCH.**EO1** → E_SR.**S** (event connection)
5. Verify: you should see 3 FBs connected in a cycle

### Document What You Notice

As you work, note:
- What was easy?
- What was confusing?
- Where did you have to guess?
- What feedback was missing?
- Compare your experience to what the agent experienced

---

## After the Experiment: Gemini Analysis

If you recorded a video, send it to Gemini for the AI-on-AI analysis:

```powershell
# Copy video to videos folder
copy "C:\path\to\recording.mp4" "C:\Users\you\Desktop\ai-user\4diac\videos\blinky_expert_recording.mp4"

# Run Gemini assessment (on macOS or wherever Gemini API works)
cd exploration
python assess_agent_video.py blind
python assess_agent_video.py cd_guided
```

Or update `assess_agent_video.py` with the new video path and run both assessments.
