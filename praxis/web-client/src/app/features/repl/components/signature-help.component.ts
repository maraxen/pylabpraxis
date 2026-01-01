import {
  Component,
  Input,
  Output,
  EventEmitter,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { SignatureInfo } from '../../../core/services/repl-runtime.interface';

/**
 * Floating signature help popup for the REPL.
 * Displays function signatures with highlighted current parameter.
 */
@Component({
  selector: 'app-signature-help',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="signature-popup"
      [style.left.px]="x"
      [style.top.px]="y"
      *ngIf="signatures.length > 0"
    >
      @for (sig of signatures; track sig.name; let i = $index) {
        <div class="signature">
          <span class="function-name">{{ sig.name }}</span>
          <span class="params">(
            @for (param of sig.params; track param; let j = $index) {
              <span
                class="param"
                [class.current]="j === sig.index"
              >{{ param }}{{ j < sig.params.length - 1 ? ', ' : '' }}</span>
            }
          )</span>
        </div>
        @if (sig.docstring) {
          <div class="docstring">{{ sig.docstring | slice:0:200 }}{{ (sig.docstring?.length || 0) > 200 ? '...' : '' }}</div>
        }
      }
    </div>
  `,
  styles: [`
    .signature-popup {
      position: absolute;
      z-index: 9999;
      background: var(--mat-sys-surface-container-high);
      border: 1px solid var(--mat-sys-outline);
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
      padding: 8px 12px;
      max-width: 500px;
      font-size: 13px;
      font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
      color: var(--mat-sys-on-surface);
    }

    .signature {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
    }

    .function-name {
      color: #dcdcaa;
      font-weight: 500;
    }

    .params {
      color: var(--mat-sys-on-surface-variant);
    }

    .param {
      color: var(--mat-sys-on-surface-variant);
    }

    .param.current {
      color: var(--mat-sys-primary);
      font-weight: 600;
      text-decoration: underline;
    }

    .docstring {
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px solid var(--mat-sys-outline-variant);
      color: var(--mat-sys-on-surface-variant);
      font-size: 11px;
      font-family: system-ui, sans-serif;
      white-space: pre-wrap;
    }
  `]
})
export class SignatureHelpComponent {
  @Input() signatures: SignatureInfo[] = [];
  @Input() x = 0;
  @Input() y = 0;

  @Output() closed = new EventEmitter<void>();

  close(): void {
    this.closed.emit();
  }
}
