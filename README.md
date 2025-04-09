# Task Scheduler

A dependency-aware task scheduling system that manages the execution of interdependent tasks in a controlled manner.

## Overview

This Task Scheduler is designed to handle two types of entities: Consumer Inputs (Cin) and Data Inputs (Din). The scheduler manages dependencies between these entities and ensures they are executed in the correct order based on their dependency relationships.

## Features

- Dependency-based execution ordering
- Circular dependency detection (deadlock detection)
- Thread-safe operations
- Dynamic addition and removal of entities
- Automatic scheduling of eligible tasks

## Concepts

### Entities

The system works with two types of entities:

- **Consumer Inputs (Cin)**: Entities that consume data from Din entities
- **Data Inputs (Din)**: Entities that provide data to Cin entities

Each entity has:
- A unique identifier
- A list of dependencies
- An execution counter
- A record of the last execution count of its dependencies

### Dependencies

Dependencies define the execution order:
- A Cin depends on Dins: The Cin can only execute after its dependent Dins have executed
- A Din depends on Cins: The Din can only execute after its dependent Cins have executed

### Execution Logic

The scheduler:
1. Maintains queues of Cin and Din entities
2. Checks if entities are eligible for execution based on their dependencies
3. Executes eligible entities
4. Updates execution counters and dependency records
5. Detects deadlocks when no entities can be executed

## Usage

### Basic Setup

```python
from task_scheduler import Scheduler

# Create a scheduler
scheduler = Scheduler()

# Add entities with their dependencies
scheduler.add_cin("CinA", ["DinX", "DinY"])  # CinA depends on DinX and DinY
scheduler.add_din("DinX", ["CinB"])          # DinX depends on CinB
scheduler.add_din("DinY", [])                # DinY has no dependencies
scheduler.add_cin("CinB", [])                # CinB has no dependencies

# The scheduler automatically runs in a background thread
```

### Adding and Removing Entities

```python
# Add a new Cin with dependencies
scheduler.add_cin("CinC", ["DinZ"])

# Add a new Din with dependencies
scheduler.add_din("DinZ", ["CinA"])

# Remove entities
scheduler.remove_cin("CinB")
scheduler.remove_din("DinY")
```

## Implementation Details

### Thread Safety

All operations on the scheduler are thread-safe, protected by a lock to prevent race conditions when adding or removing entities.

### Deadlock Detection

The scheduler detects deadlocks by monitoring if any entities can be executed in a round. If no entities are eligible for execution, it reports a deadlock.

### Execution Rounds

To prevent starvation, the scheduler uses a round-based approach where each entity can execute at most once per round.

## Example

```python
import time
from task_scheduler import Scheduler

# Create a scheduler
scheduler = Scheduler()

# Set up a simple dependency cycle to demonstrate deadlock detection
scheduler.add_cin("A", ["B"])
scheduler.add_din("B", ["A"])

# Let the scheduler run for a while
time.sleep(2)  # In a real application, the scheduler would run indefinitely
```

## Limitations

- The scheduler currently only prints execution information and doesn't provide hooks for custom execution logic
- Deadlock resolution is not implemented - the scheduler simply reports deadlocks
- The scheduler runs in a daemon thread, which means it will terminate when the main program exits

## Future Enhancements

- Add callback support for entity execution
- Implement deadlock resolution strategies
- Add priority-based scheduling
- Provide metrics and monitoring capabilities