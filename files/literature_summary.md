# Literature Review Summary
## 18 Papers Surveyed, 6 Deep Summaries

---

## Tier 1: Core Papers (MUST CITE in report)

| # | Paper | Venue | Key Contribution to Our Work |
|---|-------|-------|------------------------------|
| 1 | **UXAgent** (2025) | CHI EA | Closest system — simulates usability testing with LLM agents + video replay |
| 2 | **UXCascade** (2026) | arXiv | Extends UXAgent with multi-level analysis workflow; 25-step agent budget |
| 3 | **Multimodal Insight Summarization** (2024) | ACM ICMI | 75,464 UX studies deployed; explicitly calls for Gemini video as future work |
| 4 | **VideoWebArena** (2025) | ICLR | Proves video > screenshots; agents can't learn skills from video tutorials |
| 5 | **SoSyM 2023** — Wiesmayr et al. | SoSyM | Our ground truth — 10 issues, 14 CD dimensions, 4 tasks |
| 6 | **CD Framework** — Blackwell & Green (2003) | Book chapter | Theoretical foundation for our structured prompting |

## Tier 2: Supporting Papers (SHOULD CITE)

| # | Paper | Key Finding |
|---|-------|-------------|
| 7 | CHI 2024 — UI Mockup Feedback | GPT-4 F1=0.466 vs human F1=0.478; quality decreases over iterations |
| 8 | UICrit (UIST 2024) | LLM critique improves with structured prompting (validates our CD approach) |
| 9 | SeeAct (2024) | "Grounding is the bottleneck" — explains our coordinate mismatch |
| 10 | OSWorld (NeurIPS 2024) | Best desktop agent: 22% success (frames our 0% as consistent) |
| 11 | WorldGUI (2025) | Starting state matters — explains Welcome screen trap |
| 12 | Online-Mind2Web (2025) | LLM-as-judge reaches ~85% agreement with humans |

## Tier 3: For Bachelor Thesis

| # | Paper |
|---|-------|
| 13 | Windows Agent Arena (2024) — human 74.5% vs agent 19.5% |
| 14 | ScreenAI (2024) — UI-specialized vision model |
| 15 | Qwen2.5-VL — open-source video model for reproducibility |
| 16 | GUI-360 (2025) — separates perception vs planning quality |
| 17 | WebArena (2023) — reproducible agent evaluation methodology |
| 18 | Mind2Web (2023) — task collection from real interfaces |

---

## Key Quotes for Report

> **ICMI '24:** "Future work should examine whether leveraging **inherently multimodal LLMs such as Gemini** could improve performance." — **We are already doing this.**

> **UXCascade E4:** "I don't think the AI could ever replace a human study. But it could be one more data point, a proxy that we run through to see what it says."

> **VideoWebArena:** "Long-context models perform **worse** with video tutorials than without them, showing a 5-10% performance decrease." — Validates our Phase 1 (observe) vs Phase 2 (interact) gap.

> **CHI 2024:** GPT-4 precision 0.603 vs human 0.829 — our Gemini video approach likely has HIGHER precision due to richer temporal evidence.
