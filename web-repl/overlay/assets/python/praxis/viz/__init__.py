"""Browser visualizer transport for the praxis REPL (Phase 6 slices 2-3).

``browser`` imports ``pylabrobot`` and (lazily, inside one function) ``js``;
``transport`` imports neither, which is what keeps the ordered-event tests
runnable under plain CPython. Import from the submodules directly rather than
re-exporting here, so that a CPython test can pull in ``transport`` without
dragging ``pylabrobot`` into the process.
"""
