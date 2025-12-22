import { Routes } from '@angular/router';
import { RunProtocolComponent } from './run-protocol.component';
import { LiveDashboardComponent } from './components/live-dashboard.component';

export const RUN_PROTOCOL_ROUTES: Routes = [
  {
    path: '',
    component: RunProtocolComponent
  },
  {
    path: 'live',
    component: LiveDashboardComponent
  }
];