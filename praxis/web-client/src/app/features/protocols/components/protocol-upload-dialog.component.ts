
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { AssetService } from '../../assets/services/asset.service'; // Typo? ProtocolService?
import { ProtocolService } from '../services/protocol.service';

@Component({
  selector: 'app-protocol-upload-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule
  ],
  template: `
    <h2 mat-dialog-title>Upload Protocol</h2>
    <mat-dialog-content>
      <div class="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer relative">
        <input type="file" (change)="onFileSelected($event)" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer">
        <mat-icon class="text-4xl text-gray-400 mb-2">cloud_upload</mat-icon>
        <p class="text-sm text-gray-600" *ngIf="!selectedFile">Drag & drop or click to select file</p>
        <p class="text-sm font-semibold text-primary" *ngIf="selectedFile">{{ selectedFile.name }}</p>
      </div>

      <mat-progress-bar *ngIf="uploading" mode="indeterminate" class="mt-4"></mat-progress-bar>
      <p *ngIf="error" class="text-red-500 text-sm mt-2">{{ error }}</p>

    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close [disabled]="uploading">Cancel</button>
      <button mat-flat-button color="primary" [disabled]="!selectedFile || uploading" (click)="upload()">Upload</button>
    </mat-dialog-actions>
  `,
  styles: [`
    mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
    }
  `]
})
export class ProtocolUploadDialogComponent {
  private dialogRef = inject(MatDialogRef<ProtocolUploadDialogComponent>);
  private protocolService = inject(ProtocolService);

  selectedFile: File | null = null;
  uploading = false;
  error: string | null = null;

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.error = null;
    }
  }

  upload() {
    if (!this.selectedFile) return;

    this.uploading = true;
    this.protocolService.uploadProtocol(this.selectedFile).subscribe({
      next: (result) => {
        this.uploading = false;
        this.dialogRef.close(result);
      },
      error: (err) => {
        this.uploading = false;
        this.error = 'Upload failed. Please try again.';
        console.error(err);
      }
    });
  }
}
