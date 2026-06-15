*This project has been created as part of the 42 curriculum by gbenaven, acanadil.*

# Maze Generator - Reusable Module

This is the core reusable module of the **A-Maze-ing** project. It provides a high-performance, type-safe maze generation engine that can be imported and used in other Python projects via pip installation.

## Installation

### From Local Distribution

```bash
# Using the wheel (pre-built binary)
pip install ../mazegen-1.0.0-py3-none-any.whl

# Using the source archive
pip install ../mazegen-1.0.0.tar.gz

# Development installation (editable)
pip install -e ..
```

### Requirements

- Python 3.10 or later
- Dependencies (automatically installed):
  - `pydantic>=2.0` - Configuration validation
  - `numpy>=1.20` - Numerical operations

## Quick Start

### Basic Maze Generation

```python
from maze import MazeConfig, MazeGenerator

# Create a maze configuration
config = MazeConfig(
    WIDTH=20,
    HEIGHT=20,
    ENTRY=(0, 0),
    EXIT=(19, 19),
    OUTPUT_FILE="my_maze.txt",
    PERFECT=True,
    SEED=42  # Optional: for reproducible generation
)

# Generate the maze
maze = MazeGenerator(config)

# Access the maze structure
maze_grid = maze.maze  # List[List[Cell]]
solution = maze.solution  # Solution path string (e.g., "EESSWWN...")
```

### Using Configuration Files

```python
from parser_config import Data, lector
from maze import MazeGenerator

# Parse configuration file
parsed_data = Data.model_validate(lector("config.txt"))

# Generate maze from parsed config
config = parsed_data.to_maze_config()
maze = MazeGenerator(config)

# Check if solution exists
if maze.solution:
    print(f"Solution: {maze.solution}")
```

## Core Classes

### `MazeConfig`

Configuration dataclass with built-in validation.

**Parameters:**
- `WIDTH` (int): Maze width in cells (1-100)
- `HEIGHT` (int): Maze height in cells (1-100)
- `ENTRY` (tuple[int, int]): Entry coordinates (x, y)
- `EXIT` (tuple[int, int]): Exit coordinates (x, y)
- `OUTPUT_FILE` (str): Path for output file
- `PERFECT` (bool): Generate perfect maze (single solution) or imperfect (multiple solutions)
- `SEED` (int, optional): Random seed for reproducibility

**Example:**
```python
from maze import MazeConfig

config = MazeConfig(
    WIDTH=30,
    HEIGHT=30,
    ENTRY=(0, 0),
    EXIT=(29, 29),
    OUTPUT_FILE="maze.txt",
    PERFECT=False,
    SEED=12345
)
```

### `MazeGenerator`

Main class for maze generation and solving.

**Methods:**
- `__init__(config: MazeConfig)` - Initialize and generate maze
- `maze` (property) - Returns the generated maze grid (List[List[Cell]])
- `solution` (property) - Returns the solution path as a string of directions (N/E/S/W)

**Attributes:**
- `config` - The MazeConfig used for generation
- `WIDTH`, `HEIGHT` - Maze dimensions
- `entry`, `exit` - Entry and exit coordinates

**Example:**
```python
from maze import MazeConfig, MazeGenerator

config = MazeConfig(WIDTH=50, HEIGHT=50, ENTRY=(0, 0), EXIT=(49, 49), 
                   OUTPUT_FILE="maze.txt", PERFECT=True)

maze_gen = MazeGenerator(config)

# Access the grid
for row in maze_gen.maze:
    for cell in row:
        print(f"Cell walls: N={cell.walls.north}, E={cell.walls.east}, "
              f"S={cell.walls.south}, W={cell.walls.west}")

# Get solution path
print(f"Solution: {maze_gen.solution}")
```

### `Cell`

Represents a single maze cell with wall configuration.

**Attributes:**
- `walls` (Wall) - Wall state for all four directions
- `visited` (bool) - Whether cell was visited during generation
- `cell_type` (CellType) - Type of cell (NORMAL, ENTRY, EXIT, PATTERN)

**Wall Access:**
```python
cell = maze_gen.maze[0][0]
print(cell.walls.north)  # bool: True if wall exists
print(cell.walls.east)   # bool: True if wall exists
print(cell.walls.south)  # bool: True if wall exists
print(cell.walls.west)   # bool: True if wall exists
```

### `Wall`

Represents walls and their state.

**Properties:**
- `north`, `east`, `south`, `west` (bool) - Wall open/closed status

## Maze Generation Algorithm

The module uses a **multi-agent parallel recursive backtracker** algorithm:

1. **Initialization**: All walls start closed
2. **Mining**: Multiple agents (4-6) independently carve paths using recursive backtracking
3. **Merging**: When agents meet, paths merge with wall coherence maintained
4. **Perfect Mazes**: Generates spanning trees (single solution)
5. **Imperfect Mazes**: Injects loops by breaking ~40% of dead-end walls

**Performance:**
- Time Complexity: O(WIDTH × HEIGHT) with ~4-6 parallel agents
- Space Complexity: O(WIDTH × HEIGHT)
- Typically generates 100×100 maze in <100ms

## Output File Format

Generated mazes are written in hexadecimal format:

```
3c 7e a5 2f ...  (Row 1: hex cells)
5f 2b 9d c1 ...  (Row 2: hex cells)
...
1e 4c 8a 6b ...  (Row N: hex cells)

<empty line>
0,0              (entry coordinates)
19,19            (exit coordinates)
EESSWWN...       (solution path)
```

**Hexadecimal Encoding** (per cell):
- Bit 0 (LSB) = North wall (1=closed, 0=open)
- Bit 1 = East wall
- Bit 2 = South wall
- Bit 3 = West wall

**Examples:**
- `0x0` (0000) = All walls open
- `0xF` (1111) = All walls closed
- `0xA` (1010) = East and West closed, North and South open

## Maze Validity Constraints

Generated mazes satisfy:

- ✓ Entry and exit are valid, different, and within bounds
- ✓ All cells reachable from entry (full connectivity)
- ✓ External borders fully walled
- ✓ Wall coherence (bidirectional symmetry)
- ✓ No corridors wider than 2 cells
- ✓ "42" pattern displayed (when space allows)
- ✓ Perfect mazes have exactly one solution
- ✓ Solution path connects entry to exit

## Error Handling

The module gracefully handles:

```python
try:
    config = MazeConfig(
        WIDTH=200,  # Too large
        HEIGHT=200,
        ENTRY=(0, 0),
        EXIT=(199, 199),
        OUTPUT_FILE="maze.txt",
        PERFECT=True
    )
except ValueError as e:
    print(f"Configuration error: {e}")

try:
    maze = MazeGenerator(config)
except Exception as e:
    print(f"Generation error: {e}")
```

## Advanced Usage

### Custom Pathfinding

```python
from maze import MazeConfig, MazeGenerator
from algoritm import found_weight

config = MazeConfig(WIDTH=50, HEIGHT=50, ENTRY=(0, 0), EXIT=(49, 49),
                   OUTPUT_FILE="maze.txt", PERFECT=True)

maze = MazeGenerator(config)

# Use heuristic pathfinding
solver = found_weight(entry=config.ENTRY, exits=config.EXIT, maps=maze.maze)
all_paths = list(solver["algoritm"]())  # Generate all solutions
best_path = solver["sorter"]()  # Get optimal path

print(f"Found {len(all_paths)} solution(s)")
print(f"Best path: {best_path}")
```

### Reproducible Generation

```python
from maze import MazeConfig, MazeGenerator

# Use same seed to get identical maze
config1 = MazeConfig(WIDTH=30, HEIGHT=30, ENTRY=(0, 0), EXIT=(29, 29),
                    OUTPUT_FILE="maze1.txt", PERFECT=True, SEED=42)
maze1 = MazeGenerator(config1)

config2 = MazeConfig(WIDTH=30, HEIGHT=30, ENTRY=(0, 0), EXIT=(29, 29),
                    OUTPUT_FILE="maze2.txt", PERFECT=True, SEED=42)
maze2 = MazeGenerator(config2)

# maze1.solution == maze2.solution (identical results)
assert maze1.solution == maze2.solution
```

### Batch Generation

```python
from maze import MazeConfig, MazeGenerator

for size in [10, 20, 30, 50, 100]:
    config = MazeConfig(
        WIDTH=size,
        HEIGHT=size,
        ENTRY=(0, 0),
        EXIT=(size-1, size-1),
        OUTPUT_FILE=f"maze_{size}x{size}.txt",
        PERFECT=True,
        SEED=42
    )
    maze = MazeGenerator(config)
    print(f"{size}x{size}: Solution length = {len(maze.solution)}")
```

## Module Structure

```
maze/
├── __init__.py           # Public API exports
├── config.py             # MazeConfig dataclass
├── cell.py               # Cell and Wall classes
├── enums.py              # CellType enumeration
├── maze_generator.py     # MazeGenerator class
└── maze_miner.py         # Multi-agent mining implementation
```

## Type Safety

The module is fully type-hinted and compatible with mypy strict mode:

```bash
# Type check
mypy --strict maze/

# IDE autocomplete and type hints fully supported
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | ≥2.0 | Configuration validation and parsing |
| numpy | ≥1.20 | Numerical operations (distance calculations) |

## License

MIT License - See LICENSE file in repository root

## Contributing

When using this module in external projects:

1. Ensure Python 3.10+ environment
2. Install dependencies: `pip install -e .`
3. Run type checking: `mypy --strict maze/`
4. Run linting: `flake8 maze/`

## Support

For issues, bug reports, or feature requests, visit:
https://github.com/Guillermo-Benavente/a_maze_ing/issues
