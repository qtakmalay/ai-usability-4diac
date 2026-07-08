# Agent Interaction — Experiment Summary
## Based on: C:\Users\you\Desktop\ai-user\4diac\agent_interaction

---

## Overview

The `agent_interaction/` directory contains all code, configuration, and outputs for Phase 2 of the project: AI agent-based interactive usability assessment of 4diac IDE.

**Approach:** Claude Sonnet 4.6 (Computer Use API) operates 4diac IDE inside a Docker container via mouse/keyboard simulation, taking screenshots at each step and reporting usability issues from first-hand interaction.

---

## Scripts & Configuration

| File | Purpose | Key Details |
|------|---------|-------------|
| `claude_computer_use.py` | Main agent script | Agent loop: screenshot → API → action → repeat. Fixed for Windows UTF-8 encoding |
| `tasks.py` | Task definitions | 4 maintenance tasks from Wiesmayr et al. (2023) + system prompt |
| `Dockerfile` | Container build | Ubuntu 22.04 + Java 17 + 4diac IDE 3.0.2 + Xvfb + VNC |
| `docker-compose.yml` | Container config | Ports 5900 (VNC), 6080 (noVNC), 2GB shared memory |
| `start.sh` | Container entrypoint | Launches Xvfb, fluxbox, x11vnc, noVNC, 4diac IDE |
| `EXPERIMENTS.md` | Experiment documentation | Full timeline, screenshots, analysis (624 lines) |
| `RESEARCH_UI_AGENTS.md` | Agent survey | 12+ UI interaction agents evaluated |

## Changes Since Initial Commit

### Code Changes (claude_computer_use.py)
1. **UTF-8 encoding fix** — Added `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")` for Windows cp1252 compatibility
2. **File write encoding** — Added `encoding="utf-8"` to all `open()` calls for JSON and markdown output
3. **ensure_ascii=False** — Added to `json.dump()` to preserve Unicode characters in output

### Documentation Changes (EXPERIMENTS.md)
- Expanded from 313 lines (initial macOS results) to 624 lines
- Added Section 9: Windows x86_64 Replication (all 4 tasks)
- Added Section 10: Updated Conclusions
- Added Section 11: Next Steps

---

## Experiment Results

### macOS Run (2026-03-11) — QEMU Limited

| Task | Steps | Result |
|------|-------|--------|
| Task 1: Orientation | 30/30 | Blocked by QEMU — SWT dialogs failed |

Issues found: 3 genuine + 3 QEMU artifacts

### Windows Run (2026-03-23) — Native x86_64

| Task | Steps | Result | Issues |
|------|-------|--------|--------|
| Task 1: Orientation | 30/30 | Not completed — Welcome tab blocker | 5 |
| Task 2: Hierarchy | 30/30 | Not completed — coordinate mismatch | 3 |
| Task 3: Library | 30/30 | Not completed — coordinate mismatch | 3 |
| Task 4: Editing | 30/30 | **Partial** — New Wizard dialog opened! | 4 |

Issues found: **12 unique, all genuine IDE issues**

### Key Breakthrough: Task 4 on Windows
Ctrl+N keyboard shortcut opened the New Wizard dialog — proving:
- SWT dialogs **work** on native x86_64
- The macOS QEMU issues were emulation artifacts, not IDE bugs
- Agent can trigger complex UI interactions on proper hardware

---

## Output Files

### Reports (4 per platform)
```
outputs/
├── task1_orientation_report.md   — Agent's usability report
├── task2_hierarchy_report.md
├── task3_library_report.md
└── task4_editing_report.md
```

### JSON Logs (4 per platform)
```
outputs/
├── task1_orientation_results.json   — Full action log + timestamps
├── task2_hierarchy_results.json
├── task3_library_results.json
└── task4_editing_results.json
```

### Screenshots (30 per task, 120 total on Windows)
```
outputs/
├── pre_task_screen.png              — IDE state before experiments
├── task1_orientation_step01-30.png  — 30 step screenshots
├── task2_hierarchy_step01-30.png    — 30 step screenshots
├── task3_library_step01-30.png      — 30 step screenshots
└── task4_editing_step01-30.png      — 30 step screenshots
```

---

## Consolidated Usability Issues (Windows)

| # | Issue | Severity | Explanation |
|---|-------|----------|-------------|
| 1 | Welcome tab X intercepted by zoom toolbar | **Critical** | All 4 tasks spent 50-66% of budget on this |
| 2 | Welcome content persists after tab closes | Major | Confusing — content visible with no tab header |
| 3 | Updates dialog X triggers Help window | Major | Clicking close opens unrelated window |
| 4 | Tutorial links → broken Help | Minor | "Topic not found" when clicking tutorials |
| 5 | Tab header inconsistently visible | Major | Appears/disappears on hover — state confusion |
| 6 | Menu items tightly spaced | Minor | Easy to misclick adjacent menu items |
| 7 | No keyboard shortcut for System Explorer | Major | Must navigate Window > Show View manually |
| 8 | Type Library not discoverable | Major | Hidden behind Window menu, no visible palette |
| 9 | File > New submenu inconsistent | Minor | Click doesn't open submenu, only hover works |
| 10 | New Wizard tree arrows too small | Minor | ~8px click target for expand triangle |
| 11 | "General" auto-selected in New Wizard | Minor | Wrong default — should default to "4diac IDE" |
| 12 | No guided project creation | Major | Welcome screen doesn't offer clear creation flow |

---

---

## April 16, 2026 — Post-Fix Experiments (BREAKTHROUGH)

### Fixes Applied
- Resolution: 1920x1080 → **1024x768** (eliminates coordinate mismatch)
- Max steps: 30 → **unlimited** (`--max-steps=none`, hard cap 300)

### Run 1: 30 steps at 1024x768
- Agent dismissed Welcome, opened Import dialog — no coordinate issues
- Blocked by blank GTK file chooser in Docker

### Run 2: 121 steps UNLIMITED (BREAKTHROUGH)
- **Created "MotorControlSystem" project** from scratch
- **Created "MotorControl" Basic FB type**
- Explored palette, searched for "motor", navigated System Explorer + Type Navigator
- Attempted drag-and-drop FB placement (failed silently)
- **15 NEW usability issues found** — deeper workflow-level problems
- Terminated at step 121 (API credits exhausted)

### 15 New Issues (April 16)

| # | Issue | Severity |
|---|-------|----------|
| 1 | Tab labels "Sys"/"Typ" unclear | Minor |
| 2 | "4diac IDE Project" vs "IEC 61499 System" confusing | Minor |
| 3 | Example project list empty | Major |
| 4 | Tree items truncated in narrow panels | Minor |
| 5 | **Breadcrumb navigation doesn't change view** | Critical |
| 6 | Palette search: no "No results" feedback | Major |
| 7 | No context menu on Type Library | Major |
| 8 | Tab abbreviations non-standard | Minor |
| 9 | System Explorer doesn't refresh for new types | Major |
| 10 | Type names truncated | Minor |
| 11 | **No visual distinction system vs app level** | Critical |
| 12 | **Palette drag-drop to canvas fails silently** | Major |
| 13 | **No context menu on empty canvas** | Critical |
| 14 | Canvas empty despite application existing | Major |
| 15 | Edit menu missing "Insert FB" option | Major |

### Reorganized Output Folders

```
outputs/
├── 2026-03-23_all-tasks_30steps_1920x1080/    # March: 4 tasks at high res
├── 2026-04-16_task1_30steps_1024x768/         # April: 30-step fixed-res run
├── 2026-04-16_task1_121steps_1024x768/        # April: 121-step BREAKTHROUGH
└── logs/                                       # Terminal session logs
```

---

## What This Proves

1. **Agent-based assessment works** — finds real issues through direct interaction
2. **Different from video assessment** — catches interaction-level bugs (click targets, feedback gaps, onboarding)
3. **Desktop is harder than web** — consistent with OSWorld (22% best) and Windows Agent Arena (19.5%)
4. **Resolution fix eliminated coordinate mismatch** — agent clicks correct targets
5. **Unlimited steps dramatically improve results** — 15 deep issues at 121 steps vs 12 surface issues at 30 steps
6. **Agent can create projects and types** — first time completing complex multi-step IDE workflows
