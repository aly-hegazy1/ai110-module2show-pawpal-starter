# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted.

---

## Agent Workflow (SF7)

**What task did you give the agent?**

I gave Claude Code (agent mode, in VS Code) the full PawPal+ project brief and asked it to build the project phase by phase: UML draft → class skeleton → core logic and CLI demo → Streamlit wiring → sorting, filtering, recurrence, and conflict detection → test suite → UI polish, final UML, README, and reflection. It was to commit at the end of each phase.

**What did the agent do?**

1. Read the starter files (`README.md`, `app.py`, `reflection.md`, `diagrams/uml.mmd`).
2. Wrote `diagrams/uml_draft.mmd` and a dataclass skeleton in `pawpal_system.py`, then committed.
3. Reviewed the skeleton, added `pet_name` and `due_date` to `Task`, implemented the classes, wrote `main.py` and two starter tests, ran both, and committed.
4. Wired `app.py` to the classes through `st.session_state`, smoke-tested it headlessly with `streamlit.testing.v1.AppTest`, and committed.
5. Added `sort_by_time`, `sort_by_priority`, `filter_tasks`, `mark_task_complete` / `next_occurrence`, `detect_conflicts`, `generate_daily_plan` / `DailyPlan`, and field validation. Expanded `main.py`, ran it, fixed what the output showed, updated the README, and committed.
6. Wrote 30 pytest tests, ran them, documented them, and committed. It then added a guard and a 31st test for completing a task twice.
7. Rebuilt the UI (sidebar, filters, conflict warnings, mark-done, plan), drove it end to end with `AppTest`, wrote `diagrams/uml_final.mmd` and checked that it renders with mermaid-cli, then finished the README and reflection.

**What did you have to verify or fix manually?**

- **A sorting bug the agent introduced and then caught.** `sort_by_time()` first sorted only by `HH:MM`, so tomorrow's recurring task appeared before today's. It showed up in the `main.py` output, was fixed with a `(due_date, time)` key, and is now covered by a regression test.
- **A deprecated Streamlit argument.** `use_container_width` was removed after checking the installed Streamlit (1.54) source.
- **Reflection wording.** The agent drafted `reflection.md` from what happened in the session, so it needs a human read for accuracy and to put it in my own voice.
