import {
  Component,
  Input,
  Output,
  EventEmitter,
  HostListener,
  ElementRef,
  OnChanges,
  SimpleChanges,
  inject,
  AfterViewInit,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { CompletionItem } from '../../../core/services/repl-runtime.interface';

/**
 * Floating completion popup for the REPL.
 * Displays completion items with type icons and keyboard navigation.
 */
@Component({
  selector: 'app-completion-popup',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div
      class="completion-popup"
      [style.left.px]="x"
      [style.top.px]="y"
      *ngIf="items.length > 0"
      #popup
    >
      <ul class="completion-list" role="listbox">
        @for (item of items; track item.name; let i = $index) {
          <li
            class="completion-item"
            [class.selected]="i === selectedIndex"
            (click)="selectItem(i)"
            role="option"
            [attr.aria-selected]="i === selectedIndex"
          >
            <mat-icon class="type-icon" [class]="'type-' + item.type">
              {{ getIconForType(item.type) }}
            </mat-icon>
            <span class="completion-name">{{ item.name }}</span>
            @if (item.description) {
              <span class="completion-description">{{ item.description }}</span>
            }
          </li>
        }
      </ul>
    </div>
  `,
  styles: [`
    .completion-popup {
      position: absolute;
      z-index: 9999;
      background: var(--mat-sys-surface-container-high);
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 8px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      max-height: 250px;
      overflow-y: auto;
      min-width: 240px;
      max-width: 500px;
      display: flex;
      flex-direction: column;
    }

    .completion-list {
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .completion-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 13px;
      font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
      color: var(--mat-sys-on-surface);
      border-bottom: 1px solid transparent;
      transition: background 0.1s;
    }

    .completion-item:hover {
      background: var(--mat-sys-surface-container-highest);
    }

    .completion-item.selected {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
    }

    .type-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .type-function { color: #b794f6; }
    .type-class { color: #f6c177; }
    .type-module { color: #ebbcba; }
    .type-instance { color: #9ccfd8; }
    .type-keyword { color: #eb6f92; }
    .type-param { color: #31748f; }
    .type-statement { color: #c4a7e7; }
    .type-unknown { color: var(--mat-sys-on-surface-variant); }

    .completion-name {
      flex-shrink: 0;
      font-weight: 500;
    }

    .completion-description {
      color: var(--mat-sys-on-surface-variant);
      font-size: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-left: auto; /* Push to right */
      padding-left: 16px;
      font-style: italic;
      opacity: 0.8;
    }
    
    .completion-item.selected .completion-description {
        color: var(--mat-sys-on-primary-container);
        opacity: 0.8;
    }
  `]
})
export class CompletionPopupComponent implements OnChanges, AfterViewInit {
  @ViewChild('popup') popupRef?: ElementRef<HTMLDivElement>;

  @Input() items: CompletionItem[] = [];
  @Input() x = 0;
  @Input() y = 0;

  @Output() selected = new EventEmitter<CompletionItem>();
  @Output() closed = new EventEmitter<void>();

  selectedIndex = 0;

  private iconMap: Record<string, string> = {
    function: 'functions',
    class: 'class',
    module: 'folder',
    instance: 'data_object',
    keyword: 'code',
    param: 'input',
    statement: 'code',
    unknown: 'help_outline',
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['items'] && this.items.length > 0) {
      this.selectedIndex = 0;
    }
  }

  ngAfterViewInit(): void {
    // Focus management if needed
  }

  getIconForType(type: string): string {
    return this.iconMap[type] || this.iconMap['unknown'];
  }

  selectItem(index: number): void {
    this.selectedIndex = index;
    this.emitSelection();
  }

  moveSelection(delta: number): void {
    if (this.items.length === 0) return;
    this.selectedIndex = (this.selectedIndex + delta + this.items.length) % this.items.length;
    this.scrollToSelected();
  }

  emitSelection(): void {
    if (this.items.length > 0 && this.selectedIndex >= 0) {
      this.selected.emit(this.items[this.selectedIndex]);
    }
  }

  close(): void {
    this.closed.emit();
  }

  private scrollToSelected(): void {
    const popup = this.popupRef?.nativeElement;
    if (!popup) return;

    const selectedEl = popup.querySelector('.completion-item.selected') as HTMLElement;
    if (selectedEl) {
      selectedEl.scrollIntoView({ block: 'nearest' });
    }
  }
}
