/// <reference lib="webworker" />

import { loadPyodide, PyodideInterface } from 'pyodide';

let pyodide: PyodideInterface;

interface PythonMessage {
  type: 'INIT' | 'EXEC' | 'INSTALL';
  id?: string;
  payload?: any;
}

addEventListener('message', async ({ data }: { data: PythonMessage }) => {
  const { type, id, payload } = data;

  try {
    switch (type) {
      case 'INIT':
        // Load Pyodide
        // We use the local assets path served by Angular
        pyodide = await loadPyodide({
          indexURL: 'assets/pyodide/'
        });
        
        // Install micropip for package management
        await pyodide.loadPackage('micropip');
        
        // Load WebBridge Python code
        const response = await fetch('assets/python/web_bridge.py');
        const bridgeCode = await response.text();
        pyodide.FS.writeFile('web_bridge.py', bridgeCode);
        
        postMessage({ type: 'INIT_COMPLETE', id });
        break;

      case 'EXEC':
        if (!pyodide) throw new Error('Pyodide not initialized');
        
        // Capture stdout/stderr?
        // Pyodide allows setting stdout/stderr handlers in loadPyodide or separately.
        // For now, simple return.
        
        const result = await pyodide.runPythonAsync(payload.code);
        postMessage({ type: 'EXEC_COMPLETE', id, payload: result });
        break;

      case 'INSTALL':
        if (!pyodide) throw new Error('Pyodide not initialized');
        const micropip = pyodide.pyimport('micropip');
        await micropip.install(payload.packages);
        postMessage({ type: 'INSTALL_COMPLETE', id });
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
