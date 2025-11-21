import ast
import os
from collections import defaultdict

# The list of core modules to be analyzed, as specified in the project description.
CORE_MODULES = [
  "praxis/backend/core/asset_lock_manager.py",
  "praxis/backend/core/asset_manager.py",
  "praxis/backend/core/celery.py",
  "praxis/backend/core/celery_tasks.py",
  "praxis/backend/core/container.py",
  "praxis/backend/core/decorators.py",
  "praxis/backend/core/orchestrator.py",
  "praxis/backend/core/protocol_code_manager.py",
  "praxis/backend/core/protocol_execution_service.py",
  "praxis/backend/core/run_context.py",
  "praxis/backend/core/scheduler.py",
  "praxis/backend/core/workcell.py",
  "praxis/backend/core/workcell_runtime.py",
]


def get_module_name(filepath):
  """Converts a file path to a module name."""
  return os.path.splitext(filepath.replace("/", "."))[0]


def get_filepath_from_module(module_name):
  """Converts a module name back to a file path."""
  return module_name.replace(".", "/") + ".py"


CORE_MODULE_NAMES = {get_module_name(fp) for fp in CORE_MODULES}


def analyze_dependencies(files):
  """Analyzes the import statements in a list of Python files to build a dependency graph.

  Args:
      files: A list of file paths to analyze.

  Returns:
      A dictionary representing the dependency graph.

  """
  dependency_graph = defaultdict(set)
  for filepath in files:
    with open(filepath) as f:
      content = f.read()
      tree = ast.parse(content)
      current_module = get_module_name(filepath)

      for node in ast.walk(tree):
        if isinstance(node, ast.Import):
          for alias in node.names:
            if alias.name in CORE_MODULE_NAMES:
              dependency_graph[current_module].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
          if node.module and node.module in CORE_MODULE_NAMES:
            dependency_graph[current_module].add(node.module)
          # Also consider relative imports within the core module structure
          elif (
            node.module
            and get_module_name(
              os.path.normpath(
                os.path.join(os.path.dirname(filepath), node.module.replace(".", "/")),
              )
              + ".py",
            )
            in CORE_MODULE_NAMES
          ):
            imported_module_path = (
              os.path.normpath(
                os.path.join(os.path.dirname(filepath), node.module.replace(".", "/")),
              )
              + ".py"
            )
            dependency_graph[current_module].add(get_module_name(imported_module_path))

  return dependency_graph


def find_circular_dependencies(graph):
  """Finds circular dependencies in a graph using Depth First Search.

  Args:
      graph: A dictionary representing the dependency graph.

  Returns:
      A list of tuples, where each tuple represents a circular dependency.

  """
  path = set()
  visited = set()
  cycles = []

  def dfs(node):
    path.add(node)
    visited.add(node)
    for neighbor in graph.get(node, []):
      if neighbor in path:
        # Found a cycle
        cycle_start_index = list(path).index(neighbor)
        cycles.append(tuple(list(path)[cycle_start_index:] + [neighbor]))
      if neighbor not in visited:
        dfs(neighbor)
    path.remove(node)

  for node in graph:
    if node not in visited:
      dfs(node)

  # To get the actual cycle path, we need a bit more work.
  # The above detects a back edge, but not the full cycle path easily.
  # Let's refine this to capture the cycle path.

  visiting = set()
  visited = set()
  cycles = []

  for node in list(graph):
    if node not in visited:
      path = []
      if detect_cycle_util(node, graph, visiting, visited, path):
        # cycle detected
        # path now contains the cycle
        cycle_path = []
        start_node = path[-1]
        cycle_started = False
        for item in path:
          if item == start_node:
            cycle_started = True
          if cycle_started:
            cycle_path.append(item)
        cycles.append(tuple(cycle_path))

  # A better approach for cycle detection and path retrieval
  final_cycles = []
  for node in graph:
    stack = [(node, [])]
    while stack:
      current, path = stack.pop()
      if current in path:
        # Cycle detected
        cycle_path = path[path.index(current) :] + [current]
        # Normalize cycle to avoid duplicates (e.g., A->B->A vs B->A->B)
        sorted_cycle = tuple(sorted(list(set(cycle_path))))
        if sorted_cycle not in [tuple(sorted(list(set(c)))) for c in final_cycles]:
          final_cycles.append(cycle_path)
        continue
      path.append(current)
      for neighbor in graph.get(current, []):
        stack.append((neighbor, list(path)))

  return final_cycles


def detect_cycle_util(node, graph, visiting, visited, path):
  visiting.add(node)
  path.append(node)

  for neighbour in graph.get(node, []):
    if neighbour in visiting:
      path.append(neighbour)
      return True
    if neighbour not in visited:
      if detect_cycle_util(neighbour, graph, visiting, visited, path):
        return True

  visiting.remove(node)
  path.pop()
  visited.add(node)
  return False


def analyze_global_state(files):
  """Analyzes files for potential global state.
  Looks for module-level variable assignments that are not constants.
  This is a heuristic and may not be 100% accurate.

  Args:
      files: A list of file paths to analyze.

  Returns:
      A dictionary where keys are filepaths and values are lists of global variable names.

  """
  global_state = defaultdict(list)
  for filepath in files:
    with open(filepath) as f:
      content = f.read()
      tree = ast.parse(content)
      for node in tree.body:
        # Check for module-level assignments
        if isinstance(node, ast.Assign):
          for target in node.targets:
            if isinstance(target, ast.Name):
              # A simple heuristic: if it's all caps, it's probably a constant.
              if not target.id.isupper():
                global_state[filepath].append(target.id)
        # Also consider annotated assignments
        elif isinstance(node, ast.AnnAssign):
          if isinstance(node.target, ast.Name):
            if not node.target.id.isupper():
              global_state[filepath].append(node.target.id)
  return global_state


if __name__ == "__main__":
  print("--- Phase 0: Dependency Analysis ---")

  # 1. Analyze dependencies
  dependency_graph = analyze_dependencies(CORE_MODULES)
  print("\n--- Dependency Graph ---")
  for module, dependencies in sorted(dependency_graph.items()):
    if dependencies:
      print(f"{module}:")
      for dep in sorted(list(dependencies)):
        print(f"  -> {dep}")

  # 2. Find circular dependencies
  circular_dependencies = find_circular_dependencies(dependency_graph)
  print("\n--- Circular Dependencies ---")
  if circular_dependencies:
    for i, cycle in enumerate(circular_dependencies, 1):
      print(f"Cycle {i}: {' -> '.join(cycle)}")
  else:
    print("No circular dependencies found.")

  # 3. Analyze global state
  global_state = analyze_global_state(CORE_MODULES)
  print("\n--- Global State Analysis (Heuristic) ---")
  if global_state:
    for module, variables in sorted(global_state.items()):
      if variables:
        print(f"{module}:")
        for var in variables:
          print(f"  - {var}")
  else:
    print("No potential global state found.")

  # 4. Assess container.py
  print("\n--- container.py Assessment ---")
  if "praxis/backend/core/container.py" in CORE_MODULES:
    with open("praxis/backend/core/container.py") as f:
      print(f.read())
  else:
    print("container.py not in the list of core modules.")
