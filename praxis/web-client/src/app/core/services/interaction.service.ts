import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { firstValueFrom } from 'rxjs';
import { InteractionDialogComponent } from '../../shared/components/interaction-dialog/interaction-dialog.component';

@Injectable({
  providedIn: 'root'
})
export class InteractionService {
  constructor(private dialog: MatDialog) {}

  async handleInteraction(request: any): Promise<any> {
    const dialogRef = this.dialog.open(InteractionDialogComponent, {
      data: request,
      disableClose: true // Force user to interact with the dialog
    });

    return await firstValueFrom(dialogRef.afterClosed());
  }
}
