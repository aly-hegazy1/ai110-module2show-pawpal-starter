# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet**: enter the owner's name and add one or more pets (name, species, age).
2. **Schedule a care task**: give a pet a task such as a walk, feeding, or medication, with a time, duration, priority, and how often it repeats (once, daily, weekly).
3. **See today's schedule**: view today's tasks across all pets in time order, with warnings when two tasks clash, and mark tasks done as the day goes on.

**a. Initial design**

My first UML draft (`diagrams/uml_draft.mmd`) had four classes:

- **Task** (dataclass): one care activity. It holds a description, a start time (`"HH:MM"`), a duration, a priority, a frequency, and whether it's done. Its only behavior is `mark_complete()`.
- **Pet** (dataclass): a pet's details plus the list of tasks that belong to it. It can add and remove tasks.
- **Owner**: the person using the app. It keeps a list of pets and how many minutes they have for pet care each day, and can collect every task across all its pets.
- **Scheduler**: the "brain." It takes an `Owner` and reads tasks through it, then sorts them and builds a daily plan. It doesn't store tasks itself.

Relationships: an Owner *has* many Pets (aggregation), a Pet *owns* many Tasks (composition), and the Scheduler *uses* an Owner.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
