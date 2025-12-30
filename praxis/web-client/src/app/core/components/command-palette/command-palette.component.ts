import { Component, OnInit, AfterViewInit, inject, signal, computed, ViewChild, ElementRef, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { toSignal } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, switchMap, map } from 'rxjs/operators';
import { of, combineLatest } from 'rxjs';
import { CommandRegistryService, Command } from '../../services/command-registry.service';
import { AssetSearchService } from '../../../features/assets/services/asset-search.service';

@Component({
  selector: 'app-command-palette',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatInputModule,
    MatListModule,
    MatIconModule,
    MatDividerModule,
  ],
  template: `
    <div class="command-palette-container">
      <div class="search-header">
        <mat-icon>search</mat-icon>
        <input
          #searchInput
          [formControl]="searchControl"
          placeholder="Type a command or search..."
          autoFocus
          (keydown)="handleKeyDown($event)"
        />
        <span class="esc-hint">ESC to close</span>
      </div>

      <mat-divider></mat-divider>

      <mat-action-list class="command-list" #commandList>
        @for (command of filteredCommands(); track command.id; let i = $index) {
          <button
            mat-list-item
            (click)="execute(command)"
            [class.selected-item]="i === selectedIndex()"
            (mouseenter)="selectedIndex.set(i)"
            tabindex="-1"
          >
            <mat-icon matListItemIcon>{{ command.icon || 'terminal' }}</mat-icon>
            <div matListItemTitle>{{ command.label }}</div>
            <div matListItemLine class="description">{{ command.description }}</div>
            
            <div matListItemMeta class="meta-container">
              <span class="shortcut-badge" *ngIf="command.shortcut">{{ formatShortcut(command.shortcut) }}</span>
              <div class="category-chip" *ngIf="command.category">
                {{ command.category }}
              </div>
            </div>
          </button>
        } @empty {
          <div class="no-results">No commands found matching your search.</div>
        }
      </mat-action-list>

      <div class="palette-footer">
        <div class="shortcuts">
          <span><kbd>↑↓</kbd> to navigate</span>
          <span><kbd>↵</kbd> to select</span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      background: var(--mat-sys-surface-container-high);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--mat-sys-level5);
    }

    .command-palette-container {
      width: 600px;
      max-width: 90vw;
    }

    .search-header {
      display: flex;
      align-items: center;
      padding: 16px;
      gap: 12px;

      mat-icon {
        color: var(--mat-sys-on-surface-variant);
      }

      input {
        flex: 1;
        background: transparent;
        border: none;
        outline: none;
        color: var(--mat-sys-on-surface);
        font-size: 1.1rem;
        font-family: inherit;

        &::placeholder {
          color: var(--mat-sys-outline);
        }
      }

      .esc-hint {
        font-size: 0.75rem;
        color: var(--mat-sys-outline);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
    }

    .command-list {
      max-height: 400px;
      overflow-y: auto;
      padding: 8px 0;

      .selected-item {
        /* Distinct background */
        background-color: var(--mat-sys-secondary-container) !important;
        position: relative;
        
        /* Side bar indicator */
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 0;
          bottom: 0;
          width: 4px;
          background-color: var(--mat-sys-on-secondary-container); 
          border-radius: 0 4px 4px 0;
        }

        /* Ensure text contrast is correct */
        &, .mat-mdc-list-item-title, .mat-icon {
           color: var(--mat-sys-on-secondary-container) !important;
           font-weight: 500; /* Make text slightly bolder */
        }
        
        mat-icon {
          color: var(--mat-sys-on-secondary-container) !important;
        }

        /* Ensure description also has correct contrast, maybe slightly diminished */
        .description {
          color: var(--mat-sys-on-secondary-container) !important;
          opacity: 0.8;
        }
      }

      .description {
        font-size: 0.85rem;
        color: var(--mat-sys-on-surface-variant);
      }

      .meta-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
      }

      .shortcut-badge {
        font-size: 0.7rem;
        font-weight: 600;
        background: var(--mat-sys-surface-container);
        color: var(--mat-sys-on-surface-variant);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid var(--mat-sys-outline-variant);
        font-family: monospace;
      }

      .category-chip {
        font-size: 0.7rem;
        background: var(--mat-sys-surface-container-low);
        padding: 2px 8px;
        border-radius: 4px;
        color: var(--mat-sys-outline);
        text-transform: uppercase;
      }
    }

    .no-results {
      padding: 32px;
      text-align: center;
      color: var(--mat-sys-outline);
    }

    .palette-footer {
      padding: 12px 16px;
      background: var(--mat-sys-surface-container-low);
      border-top: 1px solid var(--mat-sys-outline-variant);

      .shortcuts {
        display: flex;
        gap: 16px;
        font-size: 0.75rem;
        color: var(--mat-sys-outline);

        kbd {
          background: var(--mat-sys-surface-container);
          padding: 2px 4px;
          border-radius: 3px;
          border: 1px solid var(--mat-sys-outline-variant);
          font-family: monospace;
        }
      }
    }
  `],
})
export class CommandPaletteComponent implements OnInit, AfterViewInit {
  private dialogRef = inject(MatDialogRef<CommandPaletteComponent>);
  private registry = inject(CommandRegistryService);
  private assetSearchService = inject(AssetSearchService);
  private platformId = inject(PLATFORM_ID);

  searchControl = new FormControl('');
  searchQuery = toSignal(this.searchControl.valueChanges, { initialValue: '' });

  selectedIndex = signal(0);
  isMac = signal(false);

  @ViewChild('searchInput') searchInput!: ElementRef;
  @ViewChild('commandList', { read: ElementRef }) commandList!: ElementRef;

  filteredCommands = toSignal(
    this.searchControl.valueChanges.pipe(
      startWith(''),
      debounceTime(200),
      distinctUntilChanged(),
      switchMap(query => {
        const normalized = (query || '').toLowerCase();

        // Filter static commands
        const staticCommands = this.registry.commands().filter(c =>
          !normalized ||
          c.label.toLowerCase().includes(normalized) ||
          c.description?.toLowerCase().includes(normalized) ||
          c.category?.toLowerCase().includes(normalized) ||
          c.keywords?.some(k => k.toLowerCase().includes(normalized))
        );

        if (!normalized || normalized.length < 2) {
          return of(staticCommands);
        }

        // Search assets and merge
        return this.assetSearchService.search(normalized).pipe(
          map(assetCommands => [...staticCommands, ...assetCommands]),
          startWith(staticCommands)
        );
      })
    ),
    { initialValue: [] }
  );

  ngOnInit() {
    this.searchControl.valueChanges.subscribe(() => {
      this.selectedIndex.set(0);
    });

    if (isPlatformBrowser(this.platformId)) {
      this.isMac.set(navigator.userAgent.includes('Mac'));
    }
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.searchInput?.nativeElement?.focus();
    });
  }

  handleKeyDown(event: KeyboardEvent) {
    // Stop propagation to prevent global listeners (e.g. KeyboardService) from reacting
    event.stopPropagation();

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.moveSelection(1);
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.moveSelection(-1);
        break;
      case 'Enter':
        event.preventDefault();
        this.executeSelected();
        break;
      case 'Escape':
        event.preventDefault();
        this.dialogRef.close();
        break;
    }
  }

  moveSelection(delta: number) {
    const count = this.filteredCommands().length;
    if (count === 0) return;

    this.selectedIndex.update(current => {
      const next = (current + delta + count) % count;
      this.scrollToItem(next);
      return next;
    });
  }

  scrollToItem(index: number) {
    setTimeout(() => {
      const listEl = this.commandList?.nativeElement;
      if (listEl) {
        // Find the button at the specific index
        // Since we use @for, the children should be in order
        // However, mat-action-list might inject other elements? 
        // Best to select by class or just children
        const buttons = listEl.querySelectorAll('button[mat-list-item]');
        const selectedEl = buttons[index] as HTMLElement;

        if (selectedEl) {
          selectedEl.scrollIntoView({ block: 'nearest' });
        }
      }
    });
  }

  executeSelected() {
    const commands = this.filteredCommands();
    if (commands.length > 0) {
      this.execute(commands[this.selectedIndex()]);
    }
  }

  execute(command: Command) {
    this.dialogRef.close();
    command.action();
  }

  formatShortcut(shortcut: string): string {
    if (!shortcut) return '';
    if (this.isMac()) {
      return shortcut
        .replace('Alt', '⌥')
        .replace('Control', '⌃')
        .replace('Ctrl', '⌃')
        .replace('Shift', '⇧')
        .replace('Meta', '⌘')
        .replace('Cmd', '⌘');
    }
    return shortcut;
  }
}
