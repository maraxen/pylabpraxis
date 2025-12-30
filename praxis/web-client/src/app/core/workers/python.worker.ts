/// <reference lib="webworker" />

import { loadPyodide, PyodideInterface } from 'pyodide';

let pyodide: PyodideInterface;

interface PythonMessage {
  type: 'INIT' | 'EXEC' | 'INSTALL' | 'COMPLETE' | 'PLR_COMMAND' | 'STDOUT' | 'STDERR' | 'RAW_IO' | 'RAW_IO_RESPONSE';
  id?: string;
  payload?: any;
}

let currentExecutionId: string | undefined;

addEventListener('message', async (event) => {
  let data = event.data;

  // If data is a string, it might be a JSON message from Python
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data);
    } catch {
      // Not JSON, ignore or treat as raw
    }
  }

  const { type, id, payload } = data as PythonMessage;

  // Handle redirected output (from Python)
  // The structure from web_bridge is { type: 'STDOUT'|'STDERR', payload: string }
  // We need to attach the currentExecutionId to it for the frontend service
  if ((type === 'STDOUT' || type === 'STDERR') && currentExecutionId) {
    postMessage({ type, id: currentExecutionId, payload });
    return;
  }

  // Handle RAW_IO messages from Python (forward to Angular main thread)
  if (type === 'RAW_IO') {
    postMessage({ type: 'RAW_IO', id: currentExecutionId, payload });
    return;
  }

  // Handle RAW_IO_RESPONSE from Angular (route back to Python)
  if (type === 'RAW_IO_RESPONSE') {
    if (pyodide) {
      try {
        const bridge = pyodide.pyimport('web_bridge');
        bridge.handle_io_response(payload.request_id, payload.data);
      } catch (err) {
        console.error('Error routing IO response to Python:', err);
      }
    }
    return;
  }

  try {
    switch (type) {
      case 'INIT':
        // Load Pyodide
        pyodide = await loadPyodide({
          indexURL: 'assets/pyodide/'
        });

        // Install micropip for package management
        await pyodide.loadPackage('micropip');

        // Load WebBridge Python code
        const response = await fetch('assets/python/web_bridge.py');
        const bridgeCode = await response.text();
        pyodide.FS.writeFile('web_bridge.py', bridgeCode);

        // Bootstrap REPL environment (redirects stdout/stderr)
        const bridge = pyodide.pyimport('web_bridge');
        bridge.bootstrap_repl();

        postMessage({ type: 'INIT_COMPLETE', id });
        break;

      case 'EXEC':
        if (!pyodide) throw new Error('Pyodide not initialized');
        currentExecutionId = id;
        try {
          // runPythonAsync returns the result of the last expression
          const result = await pyodide.runPythonAsync(payload.code);
          postMessage({ type: 'EXEC_COMPLETE', id, payload: result });
        } finally {
          currentExecutionId = undefined;
        }
        break;

      case 'PLR_COMMAND':
        // Handle commands from LiquidHandlerBackend
        postMessage({ type: 'PLR_COMMAND', payload });
        break;

      case 'INSTALL':
        if (!pyodide) throw new Error('Pyodide not initialized');
        currentExecutionId = id;
        try {
          const micropip = pyodide.pyimport('micropip');
          await micropip.install(payload.packages);
          postMessage({ type: 'INSTALL_COMPLETE', id });
        } finally {
          currentExecutionId = undefined;
        }
        break;
      case 'COMPLETE':
        if (!pyodide) throw new Error('Pyodide not initialized');
        try {
          const bridge = pyodide.pyimport('web_bridge');
          const completionsProxy = bridge.get_completions(payload.code);
          const completions = completionsProxy.toJs();
          completionsProxy.destroy(); // valid memory management specific to pyodide proxies
          postMessage({ type: 'COMPLETE_RESULT', id, payload: { matches: completions } });
        } catch (err: any) {
          // Fallback or error
          console.error('Completion error:', err);
          postMessage({ type: 'COMPLETE_RESULT', id, payload: { matches: [] } });
        }
        break;
    }
  } catch (error: any) {
    postMessage({
      type: 'ERROR',
      id,
      payload: error.message || String(error)
    });
  }
});
