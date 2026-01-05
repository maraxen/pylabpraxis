/// <reference lib="webworker" />

import { loadPyodide, PyodideInterface } from 'pyodide';

let pyodide: PyodideInterface;
let pyConsole: any; // PyodideConsole instance

interface PythonMessage {
  type: 'INIT' | 'PUSH' | 'EXEC' | 'INSTALL' | 'COMPLETE' | 'SIGNATURES' | 'PLR_COMMAND' | 'RAW_IO' | 'RAW_IO_RESPONSE';
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
        await initializePyodide(id);
        break;

      case 'PUSH':
      case 'EXEC':
        // Both PUSH and EXEC now use the console's push method
        if (!pyodide || !pyConsole) throw new Error('Pyodide not initialized');
        currentExecutionId = id;
        try {
          await executePush(id!, payload.code);
        } finally {
          currentExecutionId = undefined;
        }
        break;

      case 'PLR_COMMAND':
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
        if (!pyodide || !pyConsole) throw new Error('Pyodide not initialized');
        try {
          // Use Console.complete() - returns (completions: list[str], start: int)
          const resultProxy = pyConsole.complete(payload.code);
          const result = resultProxy.toJs();
          resultProxy.destroy();

          // result is [completions_list, start_index]
          const completions = result[0] || [];
          const matches = completions.map((name: string) => ({
            name,
            type: 'unknown',
            description: ''
          }));
          postMessage({ type: 'COMPLETE_RESULT', id, payload: { matches } });
        } catch (err: any) {
          console.error('Completion error:', err);
          postMessage({ type: 'COMPLETE_RESULT', id, payload: { matches: [] } });
        }
        break;

      case 'SIGNATURES':
        // PyodideConsole doesn't have built-in signature help
        // We can try to use Jedi if available, or return empty
        if (!pyodide) throw new Error('Pyodide not initialized');
        try {
          const bridge = pyodide.pyimport('web_bridge');
          const signaturesProxy = bridge.get_signatures(payload.code);
          const signatures = signaturesProxy.toJs();
          signaturesProxy.destroy();
          postMessage({ type: 'SIGNATURE_RESULT', id, payload: { signatures } });
        } catch (err: any) {
          // Signature help is optional, just return empty
          postMessage({ type: 'SIGNATURE_RESULT', id, payload: { signatures: [] } });
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

// Expose callbacks for Python to call
(self as any).handlePythonOutput = (type: string, content: string) => {
  if (currentExecutionId) {
    postMessage({ type, id: currentExecutionId, payload: content });
  } else {
    // Output without an ID (e.g. background logs)
    // Send as 'stdout'/'stderr' event or log?
    // For specific testability, let's log to console which shows in browser console
    console.log(`[Python ${type}]: ${content}`);

    // Also try to send to main thread if it accepts global messages (optional)
    // But our service maps by ID, so it might be dropped.
  }
};

async function initializePyodide(id?: string) {
  // Load Pyodide with core files from local assets, packages from CDN
  pyodide = await loadPyodide({
    indexURL: 'assets/pyodide/',
    lockFileURL: 'https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide-lock.json'
  });

  // Install micropip for package management
  await pyodide.loadPackage('micropip');

  // Install basic dependencies including PLR and Jedi
  // Note: We use a try-catch for pylabrobot as it might have complex deps
  try {
    const micropip = pyodide.pyimport('micropip');
    await micropip.install(['jedi', 'pylabrobot']);
    console.log('PyLabRobot and Jedi installed successfully');
  } catch (err) {
    console.error('Failed to install PyLabRobot/Jedi:', err);
  }

  // Load WebBridge Python code (for RAW_IO and signature help)
  const response = await fetch('assets/python/web_bridge.py');
  const bridgeCode = await response.text();
  pyodide.FS.writeFile('web_bridge.py', bridgeCode);

  // Create PyodideConsole with stream callbacks
  const consoleCode = `
from pyodide.console import PyodideConsole
import js
import sys

def stdout_callback(s):
    # Use the exposed JS handler
    js.handlePythonOutput("STDOUT", s)

def stderr_callback(s):
    js.handlePythonOutput("STDERR", s)

# Create console with our callbacks
console = PyodideConsole(
    stdout_callback=stdout_callback,
    stderr_callback=stderr_callback
)

# Import web_bridge to make it available
import web_bridge

# Bootstrap the REPL environment (redirects sys.stdout/stderr, auto-imports)
web_bridge.bootstrap_repl(console.globals)

console
`;

  const consoleProxy = await pyodide.runPythonAsync(consoleCode);
  pyConsole = consoleProxy;

  postMessage({ type: 'INIT_COMPLETE', id });
}

async function executePush(id: string, code: string) {
  // PyodideConsole.push() returns a ConsoleFuture
  // For multi-line code, we split by lines and push each
  const lines = code.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    try {
      const futureProxy = pyConsole.push(line);

      const syntaxCheck = futureProxy.syntax_check;

      if (syntaxCheck === 'syntax-error') {
        futureProxy.destroy();
        break;
      }

      if (syntaxCheck === 'complete') {
        const resultProxy = await futureProxy;

        if (resultProxy !== undefined && resultProxy !== null) {
          const formatted = String(resultProxy);
          if (formatted && formatted !== 'None' && formatted !== 'undefined') {
            // result output
            postMessage({ type: 'STDOUT', id, payload: formatted + '\n' });
          }
        }

        if (typeof resultProxy?.destroy === 'function') {
          resultProxy.destroy();
        }
      }

      futureProxy.destroy();

    } catch (err: any) {
      console.error('Execution error:', err);
      // Get full Python traceback using traceback.format_exc()
      let errorMessage = '';
      try {
        const tracebackCode = `
import sys
import traceback
_tb = traceback.format_exc()
# If no exception is active, format_exc returns 'NoneType: None\\n'
_tb if _tb and _tb.strip() != 'NoneType: None' else str(sys.exc_info()[1]) if sys.exc_info()[1] else ''
`;
        const tracebackProxy = pyodide.runPython(tracebackCode);
        errorMessage = String(tracebackProxy);
        if (typeof tracebackProxy?.destroy === 'function') {
          tracebackProxy.destroy();
        }
      } catch {
        // Fallback to basic error string
        errorMessage = '';
      }

      // If we couldn't get a Python traceback, use the JS error
      if (!errorMessage || errorMessage.trim() === '') {
        errorMessage = String(err);
      }

      postMessage({ type: 'STDERR', id, payload: errorMessage + '\n' });
    }
  }

  postMessage({ type: 'EXEC_COMPLETE', id, payload: null });
}
