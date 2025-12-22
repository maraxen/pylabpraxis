import { Routes } from '@angular/router';
import { ProtocolLibraryComponent } from './components/protocol-library/protocol-library.component';
import { ProtocolDetailComponent } from './components/protocol-detail/protocol-detail.component';

export const PROTOCOL_ROUTES: Routes = [
  {
    path: '',
    component: ProtocolLibraryComponent
  },
  {
    path: ':id',
    component: ProtocolDetailComponent
  }
];