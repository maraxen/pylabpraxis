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
      position: fixed;
      z-index: 9999;
      background: var(--mat-sys-surface-container-high);
      border: 1px solid var(--mat-sys-outline);
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
      max-height: 200px;
      overflow-y: auto;
      min-width: 200px;
      max-width: 400px;
    }

    .completion-list {
      list-style: none;
      margin: 0;
      padding: 4px 0;
    }

    .completion-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      cursor: pointer;
      font-size: 13px;
      font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
      color: var(--mat-sys-on-surface);
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
    }

    .type-function { color: #ab82ff; }
    .type-class { color: #4ec9b0; }
    .type-module { color: #dcdcaa; }
    .type-instance { color: #9cdcfe; }
    .type-keyword { color: #569cd6; }
    .type-param { color: #9cdcfe; }
    .type-statement { color: #c586c0; }
    .type-unknown { color: var(--mat-sys-on-surface-variant); }

    .completion-name {
      flex-shrink: 0;
    }

    .completion-description {
      color: var(--mat-sys-on-surface-variant);
      font-size: 11px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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
