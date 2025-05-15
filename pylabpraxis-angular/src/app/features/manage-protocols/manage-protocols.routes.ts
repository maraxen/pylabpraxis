import { Routes } from '@angular/router';
import { autoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';

// Import the components
import { ProtocolDashboardComponent } from './pages/protocol-dashboard/protocol-dashboard.component';
import { RunNewProtocolComponent } from './pages/run-new-protocol.component';
import { ProtocolRunHistoryComponent } from './pages/protocol-run-history.component';

export const MANAGE_PROTOCOLS_ROUTES: Routes = [
  {
    path: '', // Base path for this feature module (e.g., /protocols)
    component: ProtocolDashboardComponent,
    title: 'Manage Protocols - PylabPraxis',
    canActivate: [autoLoginPartialRoutesGuard]
  },
  {
    path: 'run-new', // Child route: /protocols/run-new
    component: RunNewProtocolComponent,
    title: 'Run New Protocol - PylabPraxis',
    canActivate: [autoLoginPartialRoutesGuard]
  },
  {
    path: 'history', // Child route: /protocols/history
    component: ProtocolRunHistoryComponent,
    title: 'Protocol Run History - PylabPraxis',
    canActivate: [autoLoginPartialRoutesGuard]
  }
  // Add more child routes for manage-protocols here if needed
];
