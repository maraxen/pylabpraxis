import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router'; // For back button or other links

// Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatStepperModule } from '@angular/material/stepper'; // Will be used later
import { MatFormFieldModule } from '@angular/material/form-field'; // For inputs
import { MatInputModule } from '@angular/material/input'; // For inputs
import { MatAutocompleteModule } from '@angular/material/autocomplete'; // For protocol selection
import { ReactiveFormsModule } from '@angular/forms'; // For form handling
import { MatDivider } from '@angular/material/divider';

@Component({
  selector: 'app-run-new-protocol',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule,
    MatAutocompleteModule,
    MatDivider
  ],
  template: `
        <div class="run-protocol-container">
          <header class="page-header">
            <button mat-icon-button routerLink="/protocols" matTooltip="Back to Protocols Dashboard">
              <mat-icon>arrow_back</mat-icon>
            </button>
            <h1>Run New Protocol</h1>
          </header>
          <mat-divider></mat-divider>

          <mat-card class="content-card">
            <mat-card-content>
              <p>Protocol selection, parameter configuration, asset assignment, and review steps will go here.</p>
              <p>(Visual scaffolding - feature under development)</p>

              <mat-form-field appearance="outline" class="protocol-selector-field">
                <mat-label>Select Protocol</mat-label>
                <input type="text"
                       placeholder="Start typing to search protocols..."
                       aria-label="Select Protocol"
                       matInput
                       [matAutocomplete]="auto">
                <mat-autocomplete #auto="matAutocomplete">
                  <mat-option value="Protocol A (Example)">Protocol A (Example)</mat-option>
                  <mat-option value="Protocol B (Example)">Protocol B (Example)</mat-option>
                </mat-autocomplete>
                <mat-icon matSuffix>search</mat-icon>
              </mat-form-field>

              <p style="margin-top: 20px;"><i>Stepper for multi-stage configuration will be added here.</i></p>

            </mat-card-content>
          </mat-card>
        </div>
      `,
  styles: [`
        :host { display: block; padding: 24px; }
        .run-protocol-container { max-width: 1000px; margin: 0 auto; }
        .page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
        .page-header h1 { margin: 0; font-size: 1.8rem; font-weight: 500; }
        .content-card { margin-top: 24px; }
        .protocol-selector-field { width: 100%; margin-top: 20px; }
      `]
})
export class RunNewProtocolComponent {
  // Logic for fetching protocols for autocomplete, form groups, stepper will go here
}
