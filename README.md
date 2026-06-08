*This project has been created as part of the 42 curriculum by gbenaven, acanadil.*

## Description

A-Maze-ing is a maze generation and visualization engine built in Python with support for multiple solving algorithms and interactive 3D exploration. The project generates perfect and imperfect mazes using a multi-agent parallel mining algorithm, provides pathfinding solutions using different search strategies, and offers both 2D top-down and 3D first-person visualization modes.

### Goal

To create a comprehensive maze generation and solving system that supports:
- Procedural maze generation with configurable parameters
- Multiple maze-solving algorithms (standard DFS and heuristic-optimized DFS)
- Interactive 2D visualization with real-time configuration reloading
- Immersive 3D first-person exploration using raycasting
- Perfect and imperfect maze variants

## Instructions

### Compilation & Installation

```bash
make install
```

This command sets up a Python virtual environment, installs dependencies (pydantic, numpy, flake8, mypy), builds MiniLibX from source, and compiles the required graphics library.

### Execution

```bash
make run config.txt
```

Or directly:
```bash
python3 a_maze_ing.py config.txt
```

Replace `config.txt` with your configuration file path.

### Configuration File Format

Create a configuration file with the following parameters:

```
WIDTH=100
HEIGHT=100
ENTRY=0,0
EXIT=7,9
OUTPUT_FILE=maze.txt
PERFECT=False
ALGORITM=1
VISUAL3D=False
# SEED=42
```

**Configuration Parameters:**
- `WIDTH` (int, 1-100): Maze grid width
- `HEIGHT` (int, 1-100): Maze grid height
- `ENTRY` (tuple): Starting position as `x,y`
- `EXIT` (tuple): Exit position as `x,y`
- `OUTPUT_FILE` (str): Output file path for maze data
- `PERFECT` (bool): Generate perfect maze (True) or imperfect with loops (False)
- `ALGORITM` (int): Solver algorithm (0=DFS, 1=DFS with Manhattan heuristic)
- `VISUAL3D` (bool): Enable 3D mode (False=2D top-down)
- `SEED` (int, optional): Random seed for reproducibility

### User Interactions

**2D Mode (default) Keyboard Controls:**
- `0` – Show ALL solution paths
- `1` – Change ALL colors
- `2` – Change WALL colors
- `3` – Change ENTRY color
- `4` – Change WAY (solution path) color
- `5` – Change EXIT color
- `6` – Change FLOOR color
- `7` – Change 42 pattern color
- `8` – Reload maze from configuration file
- `9` – Animate solution pathfinding step by step
- `P` – Show / Hide solution path
- `ESC` – Exit program

**3D Mode (first-person) Keyboard Controls:**
- `W` / `↑` / `Numpad 8` – Move forward
- `S` / `↓` / `Numpad 2` – Move backward
- `A` / `←` / `Numpad 4` – Turn left / strafe
- `D` / `→` / `Numpad 6` – Turn right / strafe
- `ESC` – Exit program
- Reach the EXIT cell – Automatically exit the program

**Configuration Reloading:**
Press `8` in 2D mode to re-read the configuration file and generate a new maze with updated parameters.

**Visual Modes:**
- **2D Mode** (default): Top-down grid view with maze structure, entry/exit, paths, and solution highlighting
- **3D Mode** (bonus): First-person raycasting exploration through the maze with collision detection

### Output File Format

The maze is written to the output file using **one hexadecimal digit per cell**, encoding which walls are closed:

```
Bit (Position)  Direction
0 (LSB)         North
1               East
2               South
3               West
```

**Examples:**
- `0x3` (binary `0011`): North + East walls closed, South + West open
- `0xA` (binary `1010`): East + West walls closed, North + South open
- `0xF` (binary `1111`): All walls closed
- `0x0` (binary `0000`): All walls open

**File Structure:**
```
Row 1: Hexadecimal maze cells for row 1 (one digit per cell)
Row 2: Hexadecimal maze cells for row 2
...
Row N: Hexadecimal maze cells for row N

<empty line>
x,y          (entry coordinates)
x,y          (exit coordinates)
NNNEEESSSW   (solution path: N=North, E=East, S=South, W=West)
```

### Maze Validity Requirements

The generated maze must satisfy:

✓ **Valid Coordinates**: Entry and exit exist, are different, and within bounds  
✓ **Full Connectivity**: All cells reachable from entry (no isolated regions except the "42" pattern)  
✓ **Boundary Walls**: External borders are fully walled  
✓ **Wall Coherence**: When cell A has an open wall to cell B, cell B must have an open wall back to cell A (symmetry constraint)  
✓ **Width Constraint**: Corridors/open areas cannot exceed 2 cells width (no 3x3 open spaces)  
✓ **"42" Pattern**: A visible 3x3 or 2x4 pattern of fully closed cells forming the number "42" (omitted if maze too small)  
✓ **Perfect Maze Property** (if PERFECT=True): Exactly one valid solution path from entry to exit  

### Error Handling

The program gracefully handles:
- Missing or invalid configuration files with clear error messages
- Invalid maze parameters (out of bounds coordinates, impossible dimensions)
- File I/O errors (permissions, disk full, etc.)
- Configuration syntax errors
- Invalid cell/wall relationships
- Insufficient maze size for required patterns

### Development & Build Commands

```bash
make install       # Setup environment and install dependencies
make run           # Execute: python3 a_maze_ing.py [config_file]
make debug         # Run with Python debugger
make clean         # Remove __pycache__ and .mypy_cache
make lint          # Run flake8 and mypy (standard flags)
make lint-strict   # Run mypy with strict mode for enhanced checking
```

### Building the Reusable Package

```bash
# Build wheel distribution
python -m build

# Install locally for testing
pip install -e .

# The resulting package can be distributed as:
# - mazegen-1.0.0-py3-none-any.whl (binary wheel)
# - mazegen-1.0.0.tar.gz (source distribution)
```

## Maze Generation Algorithm

### Chosen Algorithm: Multi-Agent Parallel Recursive Backtracker

The project implements a **multi-agent parallel maze mining algorithm** (multiple simultaneous carvers) based on recursive backtracking principles with optimized merging of independent paths.

### Why This Algorithm?

1. **Efficiency**: Using ~4% of grid cells as independent miners with parallel carving significantly reduces runtime compared to single-carver algorithms
2. **Scalability**: Scales well to large grid sizes (tested up to 100x100)
3. **Predictability**: Produces mazes with well-distributed characteristics and balanced path lengths
4. **Flexibility**: Easily adaptable to both perfect and imperfect maze generation
5. **Reproducibility**: Seed-based randomization ensures deterministic maze generation

### Algorithm Details

- **Perfect Mazes**: Generates spanning trees with guaranteed single solution path between any two points
- **Imperfect Mazes**: Adds loops by breaking 40% of dead-end walls, creating multiple solution paths and increased complexity

## Reusable Components

### 1. **Core Maze Generation (`maze/` module)**
   - **Reusability**: Generic cell-based maze representation can adapt to non-rectangular grids
   - **Usage**: Import `MazeConfig` and `MazeGenerator` to generate custom mazes with configurable dimensions and algorithms
   - **Standalone**: The `maze/` module is self-contained with its own lightweight `MazeConfig` dataclass — no external dependencies required
   - **Example**:
   ```python
   from maze import MazeConfig, MazeGenerator
   
   config = MazeConfig(WIDTH=50, HEIGHT=50, ENTRY=(0,0), EXIT=(49,49),
                       OUTPUT_FILE="my_maze.txt", PERFECT=True)
   maze = MazeGenerator(config)
   ```

### 2. **Pathfinding Algorithms (`algoritm.py`)**
   - **Reusability**: Standalone solver functions independent of visualization
   - **Usage**: Can be applied to any grid-based maze representation
   - `found_all()`: Standard DFS pathfinding (finds all solutions)
   - `found_weight()`: Heuristic-optimized DFS using Manhattan distance
   - **Example**:
   ```python
   from algoritm import found_weight
   
   solver = found_weight(entry=(0,0), exits=(99,99), maps=maze_grid)
   solution = solver["sorter"]()  # Get shortest path
   ```

### 3. **3D Engine (`maze_3d/` module)**
   - **Reusability**: Raycasting renderer can be adapted for other grid-based environments
   - **Components**:
     - `Raycaster`: Column-based raycasting with directional shading
     - `Player`: First-person camera with smooth movement
     - `Map`: Spatial data structure optimized for raycasting queries
   - **Usage**: Encapsulated 3D visualization pipeline suitable for games and VR applications

### 4. **Configuration System (`parser_config.py`)**
   - **Reusability**: Pydantic-based configuration parser with validation
   - **Usage**: Parses `.txt` config files into a validated `Data` object, convertible to `MazeConfig` via `.to_maze_config()`
   - **Integration**: Use the parser for file-based config, then convert for maze generation:
     ```python
     from parser_config import Data, lector
     from maze import MazeConfig, MazeGenerator

     data = Data.model_validate(lector("config.txt"))
     maze = MazeGenerator(data.to_maze_config())
     ```

## Reusable Package Distribution

The maze generator is packaged as **`mazegen-1.0.0-py3-none-any.whl`** for distribution via pip.

### Installation in External Projects

```bash
# Install from local wheel
pip install mazegen-1.0.0-py3-none-any.whl

# Or from source
pip install -e .
```

### Using as Imported Module

```python
from maze import MazeConfig, MazeGenerator

# Create configuration
config = MazeConfig(
    WIDTH=50,
    HEIGHT=50,
    ENTRY=(0, 0),
    EXIT=(49, 49),
    OUTPUT_FILE="maze.txt",
    PERFECT=True,
)

# Generate maze
maze = MazeGenerator(config)

# Access generated maze structure
maze_grid = maze.maze  # list[list[Cell]]
solution = maze.solution  # Solution path string (if PERFECT=True)

# Write to file
# Output file is automatically generated with hexadecimal representation
```

**With file-based configuration:**
```python
from parser_config import Data, lector
from maze import MazeGenerator

data = Data.model_validate(lector("config.txt"))
maze = MazeGenerator(data.to_maze_config())
```

### Package Contents

The `mazegen-*` distribution includes:
- Core maze generation engine (`maze/` module)
  - `MazeConfig`: Standalone configuration dataclass with built-in validation
  - `MazeGenerator`: Full maze generation pipeline
- Standalone pathfinding algorithms (`algoritm.py`)
- Configuration file parser (`parser_config.py`)
- Utility modules for cell and wall management
- Type hints and documentation for IDE support
- Examples and usage documentation

## Team & Project Management

### Team Members

| Member | GitHub | Contibutions |
|--------|--------|------|
| Guillermo Benavente Mora | @gbenaven (guillermobm) | Algorithm maze create, 2D maze |
| Airan Cana | @acanadil (AiranCana) | Parser, Algorithm maze solution, 3D maze |

### Project Planning Evolution

**Initial Phase**: Basic 2D maze generation and visualization with single-threaded carving algorithm

**Iteration 1**: Implementation of multiple solving algorithms (standard DFS and heuristic-based approaches)

**Iteration 2**: 3D raycasting engine development for first-person exploration

**Iteration 3**: Multi-agent parallel mining optimization reducing generation time by ~70%

**Iteration 4**: Imperfect maze support with configurable loop generation

**Final Phase**: Code cleanup, comprehensive documentation, type checking with mypy, and linting with flake8

### What Worked Well

**Modular Architecture**: Clear separation between generation, solving, and visualization allowed parallel development

**Configuration-Driven Design**: Hot-reloadable config system enabled rapid iteration during 2D visualization development

**Type Safety**: Pydantic models caught configuration errors early; mypy enforced type consistency

**Algorithm Reusability**: Solving algorithms independent from visualization enabled testing and optimization in isolation

**Parallel Mining**: Multi-agent approach significantly improved performance for larger mazes

### Areas for Improvement

**Performance**: 3D raycasting could benefit from SIMD optimizations or Rust rewrite for large mazes

**Scaling**: Grid limitation of 100x100 could be extended with chunked maze management

**Mobile Support**: Current MLX library limited to desktop; web/mobile variants possible with WebGL

**Advanced Features**: Could add maze themes, difficulty levels, multiplayer exploration, and custom textures

**Documentation**: Inline comments could be more extensive for complex algorithms

### Tools & Technologies Used

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core language with type hints |
| **Pydantic** | Configuration validation and parsing |
| **NumPy** | Numerical operations (distance calculations) |
| **MiniLibX (MLX)** | Cross-platform graphics library |
| **Flake8** | Code style linting (PEP 8 compliance) |
| **MyPy** | Static type checking |
| **Git** | Version control with feature branching |
| **Makefile** | Build and automation orchestration |

## Mandatory Features ✓

- **Maze Generation**: Multi-agent parallel recursive backtracker with full configurability
- **Perfect Mazes**: Single-solution guaranteed pathfinding
- **Output Format**: Hexadecimal cell encoding with solution path
- **Visual Representation**: 2D top-down grid display with MLX graphics
- **User Interactions**: Color customization per element type, solution path animation, multi-path display, configuration reload
- **Configuration System**: File-based parameters with validation and error handling
- **Code Reusability**: Standalone MazeGenerator module distributable as pip package
- **Type Safety**: Full type hints with mypy compliance
- **Code Quality**: flake8 compliance and comprehensive documentation

## Advanced Features (BONUS)

### Multiple Maze Generation Algorithms
The project supports algorithms for:
- **Perfect Maze Generation**: Multi-agent parallel recursive backtracker (default)
- **Imperfect Maze Support**: Same generator with optional loop injection (40% dead-end wall breaking)

### Multiple Solving Algorithms
Two distinct pathfinding strategies included:
- **Standard DFS**: Explores paths sequentially without heuristic bias
- **Manhattan Heuristic DFS**: Prioritizes moves reducing Manhattan distance to exit (typically finds solutions faster)

### 3D Raycasting Visualization Engine
Full pseudo-3D first-person exploration with:
- Real-time raycasting for column-based rendering
- Directional wall shading (north/south/east/west) for depth perception
- Player movement with collision detection and smooth camera
- Seamless integration with existing 2D maze data
- Configurable via `VISUAL3D` flag

### Perfect & Imperfect Maze Variants
- **Perfect Mazes** (default): Guaranteed single solution, no loops, mathematical spanning tree property
- **Imperfect Mazes**: Multiple solutions with configurable loop density (40% dead-end wall breaking for natural-feeling mazes)

### Real-Time Configuration Reloading
2D visualizer watches configuration file and automatically regenerates maze on changes without restart

### Custom Visualization Themes
- Wall color customization (toggle between predefined color schemes)
- Optional "42" pattern highlighting in distinct colors
- Configurable entry/exit colors and solution path highlighting

## Resources

### Classic References
- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm) - Overview of recursive backtracking, Prim's, Kruskal's, and Wilson's algorithms
- [Raycasting Tutorial](https://lodev.org/cgtutor/raycasting.html) - Detailed raycasting implementation guide
- [A* Pathfinding](https://en.wikipedia.org/wiki/A*_search_algorithm) - Heuristic search foundations
- [MiniLibX Documentation](https://reactive.so/post/42-mlx/) - Graphics library reference

### AI Usage in Project

**AI was utilized for the following tasks:**

1. **Code Documentation & Comments**: Claude AI assisted in writing comprehensive docstrings and inline documentation for complex functions

2. **Type Hint Generation**: Help with Pydantic model definitions and Python type annotations throughout the codebase

3. **Algorithm Explanation & Optimization**: Guidance on algorithm complexity analysis and suggestions for performance improvements

4. **Error Handling Patterns**: Recommendations for validation patterns and exception handling

5. **Code Refactoring Suggestions**: Assistance in identifying code duplication and suggesting modularization approaches

6. **README & Project Documentation**: This document was co-created with AI assistance for structure, formatting, and comprehensive coverage

**Parts NOT generated by AI**: All core algorithmic implementations, raycasting engine, 3D player mechanics, configuration parser, and visualization systems were hand-coded by the team.

---

**Project Repository**: [A-Maze-ing on GitHub](https://github.com/Guillermo-Benavente/a_maze_ing)

**Status**: Complete and functional with all required features implemented.
