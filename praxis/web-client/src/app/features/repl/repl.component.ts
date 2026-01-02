import { Component, ElementRef, OnInit, OnDestroy, ViewChild, inject, AfterViewInit, effect, NgZone, ChangeDetectorRef } from '@angular/core';
import { AppStore } from '../../core/store/app.store';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { ModeService } from '../../core/services/mode.service';
import { PythonRuntimeService } from '../../core/services/python-runtime.service';
import { BackendReplService } from '../../core/services/backend-repl.service';
import { ReplRuntime, ReplOutput, CompletionItem, SignatureInfo, ReplacementVariable } from '../../core/services/repl-runtime.interface';
import { Subscription } from 'rxjs';
import { CompletionPopupComponent } from './components/completion-popup.component';
import { SignatureHelpComponent } from './components/signature-help.component';

@Component({
  selector: 'app-repl',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatSidenavModule,
    MatListModule,
    MatSnackBarModule,
    CompletionPopupComponent,
    SignatureHelpComponent
  ],
  template: `
    <div class="repl-container">
      <mat-drawer-container class="repl-drawer-container">
        <!-- Variable Sidebar -->
        <mat-drawer #drawer mode="side" [(opened)]="isSidebarOpen" position="end" class="variables-drawer">
          <div class="drawer-header">
            <h3>Variables</h3>
            <button mat-icon-button (click)="loadVariables()" matTooltip="Refresh Variables">
              <mat-icon>refresh</mat-icon>
            </button>
          </div>
          <mat-list>
            @for (v of variables; track v.name) {
              <mat-list-item>
                <div class="variable-item">
                  <span class="var-name" matTooltip="{{v.type}}">{{ v.name }}</span>
                  <span class="var-value">{{ v.value }}</span>
                </div>
              </mat-list-item>
            }
            @if (variables.length === 0) {
              <div class="empty-state">No variables defined</div>
            }
          </mat-list>
        </mat-drawer>

        <!-- Main Content -->
        <mat-drawer-content class="repl-main-content">
          <mat-card class="repl-card">
            <!-- Menu Bar -->
            <div class="repl-header">
              <div class="header-title">
                <mat-icon>terminal</mat-icon>
                <h2>PyLabRobot REPL ({{ modeLabel() }})</h2>
              </div>
              
              <div class="header-actions">
                <button mat-icon-button (click)="restartKernel()" matTooltip="Restart Kernel">
                  <mat-icon>restart_alt</mat-icon>
                </button>
                <button mat-icon-button (click)="clearTerminal()" matTooltip="Clear Output">
                  <mat-icon>delete_sweep</mat-icon>
                </button>
                <!--- <button mat-icon-button (click)="loadProtocol()" matTooltip="Load Protocol (Coming Soon)" disabled>
                  <mat-icon>file_open</mat-icon>
                </button> -->
                <button mat-icon-button (click)="saveSession()" matTooltip="Save Session to Protocol" [disabled]="history.length === 0">
                  <mat-icon>save</mat-icon>
                </button>
                <button mat-icon-button (click)="isSidebarOpen = !isSidebarOpen" matTooltip="Toggle Variables">
                  <mat-icon>data_object</mat-icon>
                </button>
              </div>
            </div>

            <!-- Terminal -->
            <div class="repl-terminal-wrapper" #terminalContainer>
              <div #terminalElement></div>
              <app-completion-popup
                [items]="completionItems"
                [x]="popupX"
                [y]="popupY"
                (selected)="onCompletionSelected($event)"
                (closed)="closeCompletionPopup()"
                #completionPopup
              ></app-completion-popup>
              <app-signature-help
                [signatures]="signatureItems"
                [x]="popupX"
                [y]="popupY"
                (closed)="closeSignatureHelp()"
              ></app-signature-help>
            </div>
          </mat-card>
        </mat-drawer-content>
      </mat-drawer-container>
    </div>
  `,
  styles: [`
    .repl-container {
      height: 100%;
      width: 100%;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
    }
    .repl-drawer-container {
      height: 100%;
      background: transparent;
    }
    .repl-main-content {
      padding: 16px;
      display: flex;
      flex-direction: column;
      overflow: hidden; /* Prevent scrolling on content wrapper */
    }
    .variables-drawer {
      width: 250px;
      padding: 0;
      background: var(--mat-sys-surface-container);
      border-left: 1px solid var(--mat-sys-outline-variant);
    }
    .drawer-header {
      padding: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
    }
    .drawer-header h3 {
      margin: 0;
      font-size: 1rem;
      font-weight: 500;
    }
    .variable-item {
      display: flex;
      flex-direction: column;
      width: 100%;
      overflow: hidden;
    }
    .var-name {
      font-family: monospace;
      font-weight: bold;
      color: var(--mat-sys-primary);
    }
    .var-value {
      font-family: monospace;
      font-size: 0.8rem;
      color: var(--mat-sys-on-surface-variant);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .empty-state {
      padding: 16px;
      color: var(--mat-sys-on-surface-variant);
      text-align: center;
      font-style: italic;
    }

    .repl-card {
      height: 100%;
      display: flex;
      flex-direction: column;
      padding: 0; 
      background: var(--mat-sys-surface-container);
      border: 1px solid var(--mat-sys-outline-variant);
      color: var(--mat-sys-on-surface);
      border-radius: 8px;
      overflow: hidden;
    }
    .repl-header {
      display: flex;
      align-items: center;
      justify-content: space-between; /* Space between title and actions */
      padding: 8px 16px;
      background: var(--mat-sys-surface-container-high);
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      flex-shrink: 0;
    }
    .header-title {
       display: flex;
       align-items: center;
       gap: 12px;
    }
    .repl-header mat-icon {
      color: var(--mat-sys-primary);
    }
    .repl-header h2 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 500;
    }
    .header-actions {
      display: flex;
      gap: 8px;
    }

    .repl-terminal-wrapper {
      flex-grow: 1;
      overflow: hidden; /* Terminal handles scrolling */
      background: var(--mat-sys-surface-container-low);
      padding: 8px;
      position: relative; /* For popup positioning */
      display: flex; /* Ensure terminal fills */
    }
    /* Target the terminal container div */
    .repl-terminal-wrapper > div:first-child {
        width: 100%;
        height: 100%;
    }
  `]
})
export class ReplComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('terminalElement', { static: true }) terminalElement!: ElementRef;
  @ViewChild('terminalContainer', { static: true }) terminalContainer!: ElementRef;
  @ViewChild('completionPopup') completionPopupComponent?: CompletionPopupComponent;

  private modeService = inject(ModeService);
  private pythonRuntime = inject(PythonRuntimeService);
  private backendRepl = inject(BackendReplService);
  private store = inject(AppStore);
  private ngZone = inject(NgZone);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);

  private terminal!: Terminal;
  private fitAddon!: FitAddon;
  private runtime!: ReplRuntime;
  private subscription = new Subscription();
  private inputBuffer = '';
  private isExecuting = false;

  // History management
  history: string[] = [];
  private historyIndex = -1;
  private currentBufferBackup = '';

  // Popup state
  completionItems: CompletionItem[] = [];
  signatureItems: SignatureInfo[] = [];
  popupX = 0;
  popupY = 0;
  private currentToken = '';

  // Variables
  variables: ReplacementVariable[] = [];
  isSidebarOpen = true;

  modeLabel = this.modeService.modeLabel;

  constructor() {
    // Sync terminal theme with app theme
    effect(() => {
      const theme = this.store.theme();
      this.updateTerminalTheme(theme);
    });
  }

  ngOnInit() {
    this.runtime = this.modeService.isBrowserMode()
      ? this.pythonRuntime
      : this.backendRepl;

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (this.store.theme() === 'system') {
        this.updateTerminalTheme('system');
      }
    });

    // Subscribe to variables if available
    if (this.runtime.variables$) {
      this.subscription.add(
        this.runtime.variables$.subscribe(vars => {
          this.ngZone.run(() => {
            this.variables = vars;
          });
        })
      );
    }
  }

  ngAfterViewInit() {
    this.initTerminal();
    this.connectRuntime();
    this.cdr.detectChanges();
  }

  private updateTerminalTheme(theme: string) {
    if (!this.terminal) return;

    const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    // Dark theme colors (matching App's dark theme)
    const darkTheme = {
      background: '#1e1e2d', // mat-sys-surface-container
      foreground: '#ffffff', // mat-sys-on-surface
      cursor: '#ED7A9B',     // primary
      selectionBackground: 'rgba(237, 122, 155, 0.3)',
      black: '#000000',
      red: '#cf6679',
      green: '#a3be8c',
      yellow: '#ebcb8b',
      blue: '#88c0d0',
      magenta: '#b48ead',
      cyan: '#8fbcbb',
      white: '#e5e9f0',
      brightBlack: '#4c566a',
      brightRed: '#bf616a',
      brightGreen: '#a3be8c',
      brightYellow: '#ebcb8b',
      brightBlue: '#81a1c1',
      brightMagenta: '#b48ead',
      brightCyan: '#8fbcbb',
      brightWhite: '#eceff4'
    };

    // Light theme colors (matching App's light theme)
    const lightTheme = {
      background: '#fffdf5', // mat-sys-surface-container
      foreground: '#020617', // mat-sys-on-surface (slate 950)
      cursor: '#ED7A9B',
      selectionBackground: 'rgba(237, 122, 155, 0.2)',
      black: '#3b4252',
      red: '#bf616a',
      green: '#a3be8c',
      yellow: '#ebcb8b',
      blue: '#81a1c1',
      magenta: '#b48ead',
      cyan: '#8fbcbb',
      white: '#d8dee9',
      brightBlack: '#4c566a',
      brightRed: '#bf616a',
      brightGreen: '#a3be8c',
      brightYellow: '#ebcb8b',
      brightBlue: '#81a1c1',
      brightMagenta: '#b48ead',
      brightCyan: '#8fbcbb',
      brightWhite: '#eceff4'
    };

    this.terminal.options.theme = isDark ? darkTheme : lightTheme;
  }

  private initTerminal() {
    this.terminal = new Terminal({
      cursorBlink: true,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      fontSize: 14,
      scrollback: 2000,
      convertEol: true,
      allowProposedApi: true
    });

    // Apply initial theme
    this.updateTerminalTheme(this.store.theme());

    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    this.terminal.open(this.terminalElement.nativeElement);
    this.fitAddon.fit();

    this.printWelcome();

    this.terminal.onKey(({ key, domEvent }) => {
      const { keyCode, shiftKey, ctrlKey, metaKey } = domEvent;

      if (this.isExecuting) return;

      // Handle Completion Popup Navigation
      if (this.completionItems.length > 0) {
        if (keyCode === 38) { // Up
          domEvent.preventDefault();
          this.completionPopupComponent?.moveSelection(-1);
          return;
        }
        if (keyCode === 40) { // Down
          domEvent.preventDefault();
          this.completionPopupComponent?.moveSelection(1);
          return;
        }
        if (keyCode === 13 || keyCode === 9) { // Enter or Tab
          domEvent.preventDefault();
          this.completionPopupComponent?.emitSelection();
          return;
        }
        if (keyCode === 27) { // Escape
          domEvent.preventDefault();
          this.closeCompletionPopup();
          return;
        }
        // Any other key closes popup (for now, or we could filter)
        this.closeCompletionPopup();
        // Fall through to process the key normally
      }

      // Handle Signature Popup
      if (this.signatureItems.length > 0) {
        if (keyCode === 27) { // Escape
          domEvent.preventDefault();
          this.closeSignatureHelp();
          return;
        }
        // Let other keys pass through, but maybe update signature lookup if needed
      }

      // Enter key
      if (keyCode === 13) {
        if (this.signatureItems.length > 0) this.closeSignatureHelp();

        if (shiftKey) {
          this.inputBuffer += '\n';
          this.terminal.write('\r\n\x1b[90m... \x1b[0m');
        } else {
          this.terminal.write('\r\n');
          this.executeCode();
        }
        return;
      }

      // Backspace
      if (keyCode === 8) {
        if (this.inputBuffer.length > 0) {
          this.inputBuffer = this.inputBuffer.slice(0, -1);
          this.terminal.write('\b \b');
          if (this.signatureItems.length > 0) this.closeSignatureHelp();
        }
        return;
      }

      // Up Arrow (History)
      if (keyCode === 38) {
        if (this.history.length > 0 && this.historyIndex < this.history.length - 1) {
          if (this.historyIndex === -1) {
            this.currentBufferBackup = this.inputBuffer;
          }
          this.historyIndex++;
          this.updateBufferFromHistory();
        }
        return;
      }

      // Down Arrow (History)
      if (keyCode === 40) {
        if (this.historyIndex > -1) {
          this.historyIndex--;
          if (this.historyIndex === -1) {
            this.inputBuffer = this.currentBufferBackup;
          } else {
            this.updateBufferFromHistory();
          }
          this.updateBufferFromHistory(); // Called twice if -1 but guarded
        }
        return;
      }

      // Ctrl + L (Clear)
      if (keyCode === 76 && ctrlKey) {
        this.clearTerminal();
        return;
      }

      // Tab completion
      if (keyCode === 9) {
        domEvent.preventDefault();
        this.handleTabCompletion();
        return;
      }

      // Ignore other control keys
      if (ctrlKey || metaKey || keyCode === 37 || keyCode === 39) {
        return;
      }

      // Standard input
      this.inputBuffer += key;
      this.terminal.write(key);

      // Trigger Signature Help on '('
      if (key === '(') {
        this.handleSignatureHelp();
      } else if (key === ')') {
        this.closeSignatureHelp();
      }
    });

    const resizeObserver = new ResizeObserver(() => {
      if (this.fitAddon) {
        try {
          this.fitAddon.fit();
        } catch (e) {
          // Ignore fit errors if element not visible/sized
        }
      }
    });
    resizeObserver.observe(this.terminalContainer.nativeElement);
  }

  private printWelcome() {
    this.terminal.writeln('\x1b[1;38;5;197mPyLabRobot Interactive REPL\r\n\x1b[0m');
    this.terminal.writeln('  \x1b[90mShift+Enter:\x1b[0m New line');
    this.terminal.writeln('  \x1b[90mCtrl+Enter / Enter:\x1b[0m Execute');
    this.terminal.writeln('  \x1b[90mCtrl+L:\x1b[0m Clear terminal\r\n');
    this.terminal.write('\x1b[1;32m>>> \x1b[0m');
  }

  private updateBufferFromHistory() {
    // Clear current line in terminal
    // Only simple clearing for now, might break if line wraps
    // proper way requires tracking cursor pos
    // But since we just want to clear content relative to prompt...

    // Quick hack: Move cursor to beginning of input start?
    // Not easy without tracking columns.
    // For now, assuming single line history interaction mainly.
    // Or just clear whole line and reprint prompt + buffer.

    // Better strategy for xterm.js:
    // We can use \x1b[2K (erase line) + \r (CR) + Prompt + Input

    this.terminal.write('\x1b[2K\r'); // Clear line and CR
    this.terminal.write('\x1b[1;32m>>> \x1b[0m');

    if (this.historyIndex === -1) {
      this.inputBuffer = this.currentBufferBackup;
    } else {
      this.inputBuffer = this.history[this.historyIndex];
    }
    this.terminal.write(this.inputBuffer);
  }

  private updatePopupPosition() {
    const cursorX = this.terminal.buffer.active.cursorX;
    const cursorY = this.terminal.buffer.active.cursorY;

    const termEl = this.terminalElement.nativeElement;
    const cellWidth = (termEl.clientWidth / this.terminal.cols) || 9;
    const cellHeight = (termEl.clientHeight / this.terminal.rows) || 17;

    // Relative to the terminal wrapper
    this.popupX = (cursorX * cellWidth) + 8;
    this.popupY = ((cursorY + 1) * cellHeight) + 8;

    // Ensure it falls within container
    const containerWidth = this.terminalContainer.nativeElement.clientWidth;
    if (this.popupX > containerWidth - 250) {
      this.popupX = containerWidth - 260; // align left of edge
    }
  }

  private handleTabCompletion() {
    const tokenMatch = this.inputBuffer.match(/[a-zA-Z_][a-zA-Z0-9_.]*$/);
    this.currentToken = tokenMatch ? tokenMatch[0] : '';

    const fullSource = this.inputBuffer;
    const cursorPosition = this.inputBuffer.length;

    this.runtime.getCompletions(fullSource, cursorPosition).then(matches => {
      this.ngZone.run(() => {
        if (matches.length === 0) {
          return;
        }

        if (matches.length === 1) {
          this.applyCompletion(matches[0]);
        } else {
          this.completionItems = matches;
          this.updatePopupPosition();
        }
      });
    }).catch(err => {
      // Completion error
    });
  }

  private handleSignatureHelp() {
    if (!this.runtime.getSignatures) return;

    this.runtime.getSignatures(this.inputBuffer, this.inputBuffer.length).then(signatures => {
      this.ngZone.run(() => {
        if (signatures && signatures.length > 0) {
          this.signatureItems = signatures;
          this.updatePopupPosition();
          this.popupY -= 40;
        }
      });
    });
  }

  onCompletionSelected(item: CompletionItem) {
    this.applyCompletion(item);
    this.closeCompletionPopup();
  }

  private applyCompletion(item: CompletionItem) {
    let suffix = '';
    const name = item.name;

    if (this.currentToken && name.startsWith(this.currentToken)) {
      suffix = name.slice(this.currentToken.length);
    } else if (!this.currentToken) {
      suffix = name;
    }

    if (suffix) {
      this.inputBuffer += suffix;
      this.terminal.write(suffix);
    }
  }

  closeCompletionPopup() {
    this.completionItems = [];
  }

  closeSignatureHelp() {
    this.signatureItems = [];
  }

  private connectRuntime() {
    this.subscription.add(
      this.runtime.connect().subscribe({
        next: () => {
          this.terminal.writeln('\x1b[90m# Runtime connected and ready.\x1b[0m\r\n');
          this.terminal.write('\x1b[1;32m>>> \x1b[0m');
        },
        error: (err) => {
          this.terminal.writeln(`\r\n\x1b[1;31mConnection Error: ${err}\x1b[0m`);
        }
      })
    );
  }

  private executeCode() {
    const code = this.inputBuffer.trim();
    if (!code) {
      this.terminal.write('\x1b[1;32m>>> \x1b[0m');
      return;
    }

    // Add to history
    this.history.unshift(code);
    if (this.history.length > 100) this.history.pop();
    this.historyIndex = -1;

    this.isExecuting = true;
    this.inputBuffer = '';

    this.subscription.add(
      this.runtime.execute(code).subscribe({
        next: (output: ReplOutput) => {
          if (output.type === 'stdout') {
            this.terminal.write(output.content.replace(/\n/g, '\r\n'));
          } else if (output.type === 'stderr') {
            this.terminal.write('\x1b[1;31m' + output.content.replace(/\n/g, '\r\n') + '\x1b[0m');
          } else if (output.type === 'result') {
            if (output.content !== undefined && output.content !== null && output.content !== 'None') {
              this.terminal.writeln(`\x1b[1;36m${output.content}\x1b[0m`);
            }
            this.terminal.write('\x1b[1;32m>>> \x1b[0m');
          } else if (output.type === 'error') {
            this.terminal.writeln(`\r\n\x1b[1;31mError: ${output.content}\x1b[0m`);
            this.terminal.write('\x1b[1;32m>>> \x1b[0m');
          }
        },
        error: (err) => {
          this.terminal.writeln(`\r\n\x1b[1;31mSystem Error: ${err}\x1b[0m`);
          this.terminal.write('\x1b[1;32m>>> \x1b[0m');
          this.isExecuting = false;
        },
        complete: () => {
          this.isExecuting = false;
        }
      })
    );
  }

  clearTerminal() {
    this.terminal.clear();
    this.printWelcome();
    this.inputBuffer = '';
  }

  restartKernel() {
    if (this.runtime.restart) {
      this.runtime.restart().subscribe(() => {
        this.clearTerminal();
        this.terminal.writeln('\x1b[90m# Runtime restarted.\x1b[0m\r\n');
        this.terminal.write('\x1b[1;32m>>> \x1b[0m');
      });
    } else {
      // Fallback for environment without explicit restart (e.g. browser)
      // Maybe just reload page? Or just clear.
      this.clearTerminal();
      this.terminal.writeln('\x1b[90m# Restart not supported in this mode.\x1b[0m\r\n');
      this.terminal.write('\x1b[1;32m>>> \x1b[0m');
    }
  }

  saveSession() {
    if (this.modeService.isBrowserMode()) {
      this.snackBar.open('Save not supported in Browser Demo mode', 'Close', { duration: 3000 });
      return;
    }

    const backend = this.runtime as BackendReplService;
    if (backend.saveSession) {
      // Pass history in reverse chronological order (oldest first) ?
      // Backend implementation expects FE order. FE stores newest first [0].
      // Service should pass it as is, Backend reverses it.
      // Wait, backend logic was: `for line in reversed(request.history):`
      // If we send [Newest, ..., Oldest], then reversed is [Oldest, ... Newest].
      // Correct.
      backend.saveSession(this.history).subscribe({
        next: (res) => {
          this.snackBar.open(`Session saved as ${res.filename}`, 'Close', { duration: 5000 });
        },
        error: (err) => {
          this.snackBar.open('Failed to save session', 'Close', { duration: 5000 });
          console.error(err);
        }
      });
    }
  }

  loadVariables() {
    // Trigger a variable refresh?
    // Currently the backend pushes updates on EXEC.
    // We could add a `GET_VARS` command if needed, but for now just executing empty entry might work?
    // Or just rely on auto-updates.
    // Let's implement a dummy exec or just leave it for now.
    if (!this.isExecuting) {
      this.runtime.execute('').subscribe();
    }
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
    this.runtime.disconnect();
    if (this.terminal) {
      this.terminal.dispose();
    }
  }
}
