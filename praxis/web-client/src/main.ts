import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import { PlotlyService } from 'angular-plotly.js';

// Plotly is loaded globally via angular.json scripts (window.Plotly)
// Configure angular-plotly.js to use the global reference
PlotlyService.setPlotly((window as any).Plotly);

import { environment } from './environments/environment';
import { GlobalInjector } from './app/core/utils/global-injector';

// Pre-bootstrap configuration checks
if ((environment as any).browserMode) {
  console.log('[main.ts] Detected Browser Mode from environment. Setting localStorage flag.');
  localStorage.setItem('praxis_mode', 'browser');
}

bootstrapApplication(App, appConfig)
  .then((appRef) => {
    GlobalInjector.set(appRef.injector);
  })
  .catch((err) => console.error(err));

