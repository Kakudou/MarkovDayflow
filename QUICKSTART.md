# Quickstart Guide

Get up and running with Markov Dayflow's intelligent focus block system in 5 minutes.

## Installation (1 minute)

### Using Poetry (Recommended)
```bash
cd MarkovDayflow
poetry install
poetry shell  # Activate virtual environment
```

### Using pip
```bash
cd MarkovDayflow
pip install -e .
```

## 1. First Run (30 seconds)

```bash
MarkovDayflow
# or explicitly:
MarkovDayflow plan
```

This automatically:
- Creates empty `data/tasks.json`
- Initializes weekly state tracking
- Generates your first focus block plan

## 2. Add Real Tasks (2 minutes)

```bash
# Add different types of work (using t-shirt sizing)
MarkovDayflow task add Feature "Implement user authentication" --urgency 4 --impact 5 --size L

MarkovDayflow task add Bug "Fix login timeout bug" --urgency 3 --impact 4 --size S

MarkovDayflow task add Learning "Research new frameworks" --urgency 2 --impact 4 --size M

MarkovDayflow task add Documentation "Update API docs" --urgency 1 --impact 3 --size S
```

## 3. Generate Smart Plan (30 seconds)

```bash
MarkovDayflow plan generate
# or just:
MarkovDayflow plan
```

Now you'll see a real plan (default 5-block system):
```
[Calendar] Today's Focus Blocks:
============================================================
Block 1 (2.0h, high focus): High Focus Block: Implement user authentication
         Bucket: Feature | Score: 8.7
Block 2 (1.5h, medium focus): Mid Focus Block: Fix login timeout bug  
         Bucket: Bug | Score: 6.4
Block 3 (1.0h, light focus): Light Focus Block: Update API docs
         Bucket: Documentation | Score: 4.2
Block 4 (1.0h, low focus): Small Focus Block: Research new frameworks
         Bucket: Learning | Score: 3.1
Block 5 (2.0h, chaos focus): Chaos Block: No tasks available
         Bucket: Chaos | Score: 0.0
============================================================
```

## 4. Work Your Blocks (2 minutes setup)

As you complete work, log it:

```bash
# After completing Block 1 (uses planned bucket/title)
MarkovDayflow plan log --block 1

# After Block 2 (uses planned bucket/title)
MarkovDayflow plan log --block 2

# Override if you did something different than planned
MarkovDayflow plan log --block 3 --bucket Meeting --title "Sprint planning instead"

# Update task status
MarkovDayflow task update 1 wip
MarkovDayflow task update 2 done
```

## 5. Check Progress (30 seconds)

```bash
MarkovDayflow plan show
# or use default charts:
MarkovDayflow plan show 
```

Shows:
```
[Calendar] Today's Plan (2025-01-17):
==================================================
[DONE] Block 1: High Focus Block: Implement user authentication
[DONE] Block 2: Mid Focus Block: Fix login timeout bug
[PENDING] Block 3: Light Focus Block: Update API docs  
[PENDING] Block 4: Small Focus Block: Research new frameworks
[DONE] Block 5: Chaos Block: Sprint planning meeting
==================================================

[Chart] Task Summary:
  todo: 2
  wip: 1
  done: 1
```

## The Chaos Bucket Feature

Any non-standard bucket names automatically map to **Chaos** for planning but preserve their original display names:

```bash
# These automatically route to Chaos bucket for planning:
MarkovDayflow task add Meeting "Daily standup"        # Shows as [Meeting] → plans as Chaos
MarkovDayflow task add Email "Respond to clients"     # Shows as [Email] → plans as Chaos  
MarkovDayflow task add Admin "Setup dev env"          # Shows as [Admin] → plans as Chaos

# Standard buckets work normally:
MarkovDayflow task add Feature "Build user auth"      # Shows as [Feature] → plans as Feature
MarkovDayflow task add Bug "Fix memory leak"          # Shows as [Bug] → plans as Bug
```

**Standard Planning Buckets:** Feature, Bug, R&D, Docs, Review, Support, Urgent  
**Everything Else:** Maps to Chaos bucket for planning balance

## New Grouped Commands

### Task Management
```bash
MarkovDayflow task add <bucket> <title> [options]    # Add new task
MarkovDayflow task list [--status STATUS]            # List tasks
MarkovDayflow task edit <id> [options]               # Edit task
MarkovDayflow task update <id> <status>              # Update status
MarkovDayflow task delete <id>                       # Delete task
```

### Planning
```bash
MarkovDayflow plan                                    # Show today's plan (default)
MarkovDayflow plan show [--date DATE]                 # Show specific plan
MarkovDayflow plan generate [--date DATE]             # Generate new plan
MarkovDayflow plan log --block N [options]            # Log completed work
```

### Reporting
```bash
MarkovDayflow report                                  # Show weekly report (default)
MarkovDayflow report weekly [--with-chart]            # Weekly with visuals
MarkovDayflow report reset                            # Reset weekly state
```

### Configuration
```bash
MarkovDayflow config                                  # Show configuration
```

## Daily Workflow

### Morning (30 seconds)
```bash
MarkovDayflow plan  # Show or generate today's focus blocks
```

### During Work (10 seconds per block)
```bash
# Simple logging - uses planned work
MarkovDayflow plan log --block 1
MarkovDayflow plan log --block 2

# Override if you did something different
MarkovDayflow plan log --block 3 --bucket Meeting --title "Emergency call"
```

### Evening (10 seconds)
```bash
MarkovDayflow plan show --with-chart  # See progress with visualizations
```

### Weekly (1 minute)
```bash
MarkovDayflow report --with-chart  # See patterns with global analytics
```

## Customizing Your Block System

Edit `markov_dayflow/infrastructure/config/blocks_config.yaml`:

**Default 5-Block System:**
```yaml
blocks_per_day: 5
targets:
  Feature: 0.30
  Bug: 0.15
  R&D: 0.15
  Docs: 0.10
  Review: 0.10
  Support: 0.05
  Urgent: 0.05
  Chaos: 0.10

block_config:
  1:
    name: "High Focus Block"
    duration_hours: 2.0
    preferred_buckets: ["Feature", "R&D"]
  # ... etc
```

**Simple 2-Block System:**
```yaml
blocks_per_day: 2
block_config:
  1:
    name: "Morning Block"
    duration_hours: 4.0
  2:
    name: "Afternoon Block"
    duration_hours: 4.0
```

The Markov learning adapts to whatever structure you choose!

## Pro Tips

### Work Patterns (Default 5-Block System)
- **Block 1 (High Focus)**: Complex features, architecture
- **Block 2 (Mid Focus)**: Bug fixes, code reviews  
- **Block 3 (Light Focus)**: Documentation, planning
- **Block 4 (Small Focus)**: Admin, support, quick wins
- **Block 5 (Chaos Block)**: Meetings, emails, interruptions

### Quick Task Operations
```bash
# Add tasks quickly
MarkovDayflow task add Urgent "Critical hotfix" --urgency 5 --size XS
MarkovDayflow task add Testing "Write tests" --size S

# Batch status updates
MarkovDayflow task update 3 wip
MarkovDayflow task update 4 done
```

### Bucket Strategy
- Use **standard buckets** for core work (Feature, Bug, R&D, etc.)
- Use **custom buckets** for everything else (Meeting, Email, Admin, etc.)
- Custom buckets automatically map to Chaos for balanced planning
- Original names preserved in all reports and charts

## You're Ready! 

The system learns from all your work:

- **Planned work**: `MarkovDayflow plan log --block N`
- **Deviations**: `MarkovDayflow plan log --block N --bucket X --title "what happened"`
- **Task completion**: Update status with `MarkovDayflow task update ID done`

Run `MarkovDayflow` each morning and log as you work. The Markov learning system gets smarter with each use!

## Visual Analytics

### Global Analysis  
```bash
MarkovDayflow report --with-chart       # Multi-day work patterns
```

**Visual Features:**
- 🟢 **Green**: Work completed as planned
- 🟡 **Yellow**: Deviated from plan  
- 🔴 **Red**: Planned but not completed
- 📊 **Pie charts**: Bucket distributions
- 📈 **Timeline**: Actual work flow

Charts are Mermaid format - copy/paste into Notion, GitHub, or any Markdown docs!
