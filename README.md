# Markov Dayflow

**An intelligent focus scheduler that learns your work patterns using Markov chains.**

Stop fighting your natural workflow. Markov Dayflow learns from how you actually work and generates optimized daily plans that get smarter over time.

---

## The Problem with Traditional Planning

Most productivity tools fail because they fight reality:

- **Rigid schedules** that assume perfect conditions
- **Idealized time blocks** that ignore interruptions
- **Static plans** that don't adapt to your rhythm
- **Guilt-driven** systems that treat deviations as failures
- **One-size-fits-all** approaches that ignore individual patterns

**The truth?** No two days are the same. Meetings happen. Urgent bugs appear. Context switching is real. Your energy levels vary. Traditional planners pretend these don't exist.

---

## The Markov Dayflow Solution

Markov Dayflow embraces reality by **learning from it**:

### Learns Your Natural Patterns

Instead of imposing structure, it discovers yours:
- Tracks transitions between work types (Feature → Bug → Review)
- Builds a probabilistic model of your actual workflow
- Adapts to your personal rhythm (morning person vs night owl)
- Gets smarter with each week of data

### Handles Chaos Intelligently

Real work includes interruptions. Markov Dayflow expects them:
- **Chaos Bucket**: Automatically maps meetings, emails, admin to balanced planning
- **Preemption System**: Urgent work can override plans without breaking the model
- **Deviation Tracking**: Logs what actually happened vs what was planned
- **No Guilt**: Deviations are data, not failures

### Generates Optimal Plans

Uses Markov chains to predict the best work sequences:
- **Context-Aware**: Suggests work based on what you just finished
- **Balance-Focused**: Ensures you don't neglect important work types
- **Energy-Matched**: Different blocks for different focus levels
- **Priority-Driven**: Smart scoring considers urgency, impact, deadlines, and age

### Provides Visual Insights

See your patterns through Mermaid charts:
- **Daily Gantt**: Compare planned vs actual work
- **Distribution Pie Charts**: Visualize work type balance
- **Global Timeline**: Understand multi-day patterns
- **Copy/Paste Ready**: Use in Notion, GitHub, or any Markdown tool

---

## Why Markov Chains?

### The Insight

Your work follows **probabilistic patterns**, not rigid rules:

```
After working on a Feature, you typically:
  - Fix related Bugs (40%)
  - Do Code Reviews (30%)
  - Write Docs (20%)
  - Start another Feature (10%)
```

Traditional planners ignore these patterns. Markov Dayflow uses them to generate **naturally-flowing plans** that match how you actually work.

### The Magic

**Week 1:** System observes your transitions
```
Feature → Bug → Docs → Feature → Review
Feature → Review → Bug → Chaos → Feature
Bug → Feature → Docs → Feature → Feature
```

**Week 2:** System generates plans based on learned patterns
```
After Feature work → Suggests Bug (40% likely)
After Bug work → Suggests Feature (60% likely)
After morning Chaos → Suggests Feature (high focus recovery)
```

**Week 3:** Plans feel natural because they match your rhythm

### The Balance

Pure pattern-following would reinforce bad habits. Markov Dayflow adds:
- **Ratio Bias**: Nudges toward target work distributions
- **Laplace Smoothing**: Prevents getting stuck in rigid patterns
- **Focus Block Bias**: Matches work types to energy levels
- **Preemption**: Allows urgent work to break patterns when needed

---

## Core Concepts

### Focus Blocks

Time is divided into customizable focus blocks (default: 5 per day):

**Block 1 - High Focus** (2h): Complex features, architecture decisions  
**Block 2 - Mid Focus** (1.5h): Bug fixes, code reviews, systematic work  
**Block 3 - Light Focus** (1h): Documentation, planning, light tasks  
**Block 4 - Small Focus** (1h): Admin, support, quick wins  
**Block 5 - Chaos Block** (2h): Meetings, emails, interruptions  

**Customizable:** Use 2 blocks (morning/afternoon) or 8 blocks (hourly). The Markov learning adapts to any structure.

### Work Buckets

**Standard Buckets** (tracked for core work):
- `Feature` - New functionality
- `Bug` - Fixes and maintenance
- `R&D` - Research and experimentation
- `Docs` - Documentation
- `Review` - Code/design reviews
- `Support` - User support
- `Urgent` - Critical issues

**Chaos Bucket** (everything else):
- Automatically maps non-standard work (Meeting, Email, Admin, Learning, Testing)
- Maintains planning balance while tracking reality
- Original names preserved in displays and analytics

### Task Scoring

Priority is calculated dynamically:

```
score = (urgency + impact + age_bonus + sla_penalty + deadline_bonus) /
        (size × difficulty_factor)
```

**Higher score = Higher priority.** System considers:
- Business impact and urgency
- How long the task has been waiting
- Approaching deadlines
- Task size (larger tasks need higher scores to compete)
- Technical difficulty

### Adaptive Learning

The system continuously improves:

1. **Tracks Transitions**: Every logged work block updates the Markov model
2. **Weekly Decay**: Old patterns fade (0.85 retention), preventing outdated habits
3. **Ratio Correction**: Gently guides toward target work distributions
4. **Smoothing**: Prevents rigid patterns from forming

---

## Key Benefits

### For Individual Contributors

- **Natural Flow**: Plans match your personal rhythm
- **Less Decision Fatigue**: System suggests next work based on context
- **Guilt-Free**: Deviations are tracked as data, not failures
- **Visual Feedback**: See your patterns and improve over time
- **Flexible**: Customize block structure to your needs

### For Teams

- **Realistic Planning**: Accounts for interruptions and context switching
- **Pattern Visibility**: Charts show where time actually goes
- **Balance Tracking**: Ensures important work doesn't get neglected
- **Adaptable**: Works for any role (dev, design, PM, support)

### For Managers

- **Data-Driven**: Visual analytics show work distribution
- **Honest Metrics**: Tracks planned vs actual work
- **Pattern Detection**: Identify bottlenecks and interruption sources
- **Team Insights**: Understand actual workflow patterns

---

## What Makes It Different

### vs. Traditional Task Managers (Todoist, Asana)
- **Them**: Static task lists with manual prioritization
- **Markov**: Learns patterns, suggests optimal work sequences, adapts over time

### vs. Time Blockers (Clockwise, Reclaim)
- **Them**: Calendar-based with rigid time blocks
- **Markov**: Flexible focus blocks that handle reality, not just ideal schedules

### vs. Pomodoro Timers
- **Them**: Fixed intervals regardless of work type
- **Markov**: Customizable blocks matched to work complexity and energy levels

---

## Real-World Example

### Traditional Planner:
```
09:00-11:00: Work on Feature A
11:00-12:00: Bug fixes
12:00-13:00: Lunch
13:00-15:00: Work on Feature A
15:00-16:00: Code review
```

**Reality:** Emergency meeting at 10am, Feature A blocked, urgent bug at 2pm  
**Result:** Guilt, replanning, stress

### Markov Dayflow:
```
Block 1: Feature work (learned: you start with features)
Block 2: Bug fixes (learned: you often fix bugs after features)
Block 3: Code reviews (learned: afternoon low-energy work)
Block 4: Support work (learned: handle support in small chunks)
Block 5: Chaos block (expected: meetings and interruptions)
```

**Reality:** Emergency meeting during Block 3, urgent bug during Block 4  
**Result:** Log deviations, system learns, tomorrow's plan adapts. No guilt.

---

## Philosophy

### Work Is Probabilistic, Not Deterministic

You can't predict every day perfectly, but you can **model the probabilities**. Markov Dayflow doesn't promise perfect days—it promises plans that **adapt to reality**.

### Measure Reality, Not Ideals

Traditional planners measure you against an ideal. Markov Dayflow measures **what actually happens** and uses that to improve future plans.

### Embrace Chaos

Interruptions aren't failures—they're **expected patterns**. The Chaos bucket ensures they're planned for, tracked, and balanced with focused work.

### Learn and Adapt

Every day provides data. Every week improves the model. The tool **gets smarter as you use it**, not more rigid.

---

## Architecture

Built with clean architecture principles:
- **Domain Layer**: Markov chains, scoring algorithms, entities
- **Application Layer**: Plan generation, logging, reporting use cases
- **Adapters Layer**: CLI interface, repositories, visualization
- **Infrastructure**: Configuration, utilities

**Minimal Dependencies**: Just PyYAML and Click - lightweight and maintainable.

---

## Quick Start

```bash
# Install
cd MarkovPlanning
poetry install && poetry shell

# Run once to see how it works
markov-dayflow
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed setup and usage examples.**

---

## Who Is This For?

### Perfect For:
- **Knowledge workers** with varied task types
- **Developers** juggling features, bugs, reviews, meetings
- **Anyone** frustrated with rigid planning tools
- **Teams** wanting to understand real workflow patterns
- **People** who want tools that adapt to them, not vice versa

### Not Ideal For:
- **Single-focus work** (if you only do one thing all day, patterns don't matter)
- **Meeting-heavy roles** with no flexibility (though Chaos tracking still helps)
- **Rigid schedules** required by external constraints

---

## Why "Markov Dayflow"?

- **Markov**: Named after Andrey Markov, whose chains model probabilistic sequences
- **Day**: Daily planning cycles that compound over time
- **Flow**: Natural work transitions that match your rhythm

---

## License

MIT - Use it, modify it, learn from it.

---

## Getting Started

Ready to stop fighting your workflow and start learning from it?

**→ [QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide  
**→ Installation**: `poetry install && poetry shell`  
**→ First Run**: `markov-dayflow`

The system learns from day one. The more you use it, the better it gets.
