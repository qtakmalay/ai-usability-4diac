# New Version Changes — Old vs New 4diac IDE
## Summary of Phase 3 Findings

---

## What Changed Between Versions

### Issues RESOLVED in New Version
| # | Issue | Old Version | New Version |
|---|-------|-------------|-------------|
| 1 | No dark theme | Light theme only | **Dark theme added** — all models praise it |
| 2 | Poor getting-started experience | Basic Welcome screen | **Improved welcome screen** with clear creation options |
| 3 | No template descriptions | Type selection unclear | **Template descriptions shown** in New Type dialog |

### Issues STILL PRESENT in New Version
| # | Issue | Evidence |
|---|-------|----------|
| 1 | Visual density / too many panels | 5/5 assessments flag this |
| 2 | Cryptic FB names (E_SWITCH, E_CTU) | Role-Expressiveness rated POOR |
| 3 | Vague/misleading error messages | Red X with no explanation |
| 4 | No contextual tooltips/help | All 3 screenshot models flag |
| 5 | Text truncation | Description column in New Type dialog |

### NEW Issues in New Version (Regressions)
| # | Issue | Severity | Impact |
|---|-------|----------|--------|
| 1 | **ECC Editor undiscoverable** | CRITICAL | Hidden tab only appears when FB selected; no right-click access |
| 2 | **Empty Palette on new project** | HIGH | Must click non-obvious "Add Standard Libraries" button |
| 3 | **Data pin connection difficulty** | HIGH | Repeated fumbling, unclear interaction model |
| 4 | **Inconsistent FB insertion methods** | MEDIUM | Palette, right-click, search all work differently |
| 5 | **Global search returns irrelevant results** | MEDIUM | "FB" search shows "FB Debug" view |
| 6 | **Mysterious white bar in editor** | LOW | Unclear purpose, wastes space |

---

## Cognitive Dimensions Shift

| Dimension | Old (Expert) | New A (Beginner) | New B (Beginner) | Trend |
|-----------|:---:|:---:|:---:|:---:|
| Viscosity | MODERATE | POOR | POOR | Worsened |
| Visibility | GOOD | MOD-POOR | POOR | Worsened |
| Hidden Dependencies | MODERATE | MODERATE | POOR | Worsened |
| Role-Expressiveness | GOOD | POOR | POOR | Worsened |
| Error-Proneness | POOR | MOD-POOR | POOR | Stable-bad |
| Consistency | MODERATE | GOOD | POOR | Mixed |
| Hard Mental Ops | POOR | MOD-POOR | POOR | Stable-bad |

**5 of 7 tracked dimensions worsened or stayed poor.**

---

## Recommendations for 4diac IDE Team

1. **Fix ECC discoverability** — Add right-click > "Edit ECC" on function blocks
2. **Auto-populate Palette** for new projects with Standard Libraries
3. **Improve connection feedback** — show compatible ports, explain why connections fail
4. **Add contextual tooltips** for all UI elements, especially FB port labels
5. **Reduce default panel count** — collapse non-essential panels by default
6. **Verify connection preservation** on type changes (if still broken)
