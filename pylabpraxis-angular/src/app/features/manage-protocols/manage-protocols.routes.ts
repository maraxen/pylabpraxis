import { Routes } from '@angular/router';

// Import the new authGuard from the main app.routes.ts file
// The path '../..' navigates up from 'features/manage-protocols/' to 'app/'
import { authGuard } from '../../app.routes';

// Import the components used in this feature module
import { ProtocolDashboardComponent } from './pages/protocol-dashboard/protocol-dashboard.component';
import { RunNewProtocolComponent } from './pages/run-new-protocol/run-new-protocol.component';
import { ProtocolRunHistoryComponent } from './pages/protocol-run-history/protocol-run-history.component';

export const MANAGE_PROTOCOLS_ROUTES: Routes = [
  {
    path: '', // Base path for this feature module (e.g., resolves to /protocols)
    component: ProtocolDashboardComponent,
    title: 'Manage Protocols - PylabPraxis',
    canActivate: [authGuard] // Apply the new authGuard
  },
  {
    path: 'run-new', // Child route (e.g., resolves to /protocols/run-new)
    component: RunNewProtocolComponent,
    title: 'Run New Protocol - PylabPraxis',
    canActivate: [authGuard] // Apply the new authGuard
  },
  {
    path: 'history', // Child route (e.g., resolves to /protocols/history)
    component: ProtocolRunHistoryComponent,
    title: 'Protocol Run History - PylabPraxis',
    canActivate: [authGuard] // Apply the new authGuard
  }
  // Add more child routes for manage-protocols here if needed,
  // ensuring to apply the authGuard if they require authentication.
];
