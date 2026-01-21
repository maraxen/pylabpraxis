from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def simulate_output(
  shape: tuple[int, int],
  value_range: tuple[float, float],
  strategy: str = "uniform",
) -> Callable[[F], F]:
  """Declares simulation metadata for a function's output.

  This metadata is used by the Browser Simulation engine to generate
  synthetic data when running in simulator mode.

  Args:
      shape: The (rows, cols) shape of the expected output matrix.
      value_range: The (min, max) value range for generated data.
      strategy: The simulation strategy (default: "uniform").

  Example:
      @simulate_output(shape=(8, 12), value_range=(10.0, 50.0))
      def read_absorbance():
          ...

  """

  def decorator(func: F) -> F:
    func.__praxis_simulation__ = {  # type: ignore
      "shape": shape,
      "range": value_range,
      "strategy": strategy,
    }
    return func

  return decorator
