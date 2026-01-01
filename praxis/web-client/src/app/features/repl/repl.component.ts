import { Component, ElementRef, OnInit, OnDestroy, ViewChild, inject, AfterViewInit, effect } from '@angular/core';
import { AppStore } from '../../core/store/app.store';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { ModeService } from '../../core/services/mode.service';
import { PythonRuntimeService } from '../../core/services/python-runtime.service';
import { BackendReplService } from '../../core/services/backend-repl.service';
import { ReplRuntime, ReplOutput, CompletionItem, SignatureInfo } from '../../core/services/repl-runtime.interface';
import { Subscription } from 'rxjs';
import { CompletionPopupComponent } from './components/completion-popup.component';
import { SignatureHelpComponent } from './components/signature-help.component';

@Component({
  selector: 'app-repl',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, CompletionPopupComponent, SignatureHelpComponent],
  template: `
    <div class="repl-container">
      <mat-card class="repl-card">
        <div class="repl-header">
          <mat-icon>terminal</mat-icon>
          <h2>PyLabRobot REPL ({{ modeLabel() }})</h2>
        </div>
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
    </div>
  `,
  styles: [`
    .repl-container {
      padding: 16px;
      height: 100%;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
    }
    .repl-card {
      height: 100%;
      display: flex;
      flex-direction: column;
      padding: 16px;
      background: var(--mat-sys-surface-container);
      border: 1px solid var(--mat-sys-outline-variant);
      color: var(--mat-sys-on-surface);
      border-radius: 8px;
    }
    .repl-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      flex-shrink: 0;
    }
    .repl-header mat-icon {
      color: var(--mat-sys-primary);
    }
    .repl-header h2 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 500;
    }
    .repl-terminal-wrapper {
      flex-grow: 1;
      overflow: hidden;
      background: var(--mat-sys-surface-container-low);
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 4px;
      padding: 8px;
      position: relative; /* For popup positioning */
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

  private terminal!: Terminal;
  private fitAddon!: FitAddon;
  private runtime!: ReplRuntime;
  private subscription = new Subscription();
  private inputBuffer = '';
  private isExecuting = false;

  // History management
  private history: string[] = [];
  private historyIndex = -1;
  private currentBufferBackup = '';

  // Popup state
  completionItems: CompletionItem[] = [];
  signatureItems: SignatureInfo[] = [];
  popupX = 0;
  popupY = 0;
  private currentToken = '';

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
  }

  ngAfterViewInit() {
    this.initTerminal();
    this.connectRuntime();
  }

  private updateTerminalTheme(theme: string) {
    if (!this.terminal) return;

    const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    // Explicitly set background to transparent to let container background show through if needed, 
    // or set specific colors matching our app theme.
    // We use the CSS variables effectively where possible, but xterm needs hex strings.

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

    this.terminal.writeln('\x1b[1;38;5;197mPyLabRobot Interactive REPL\r\n\x1b[0m');
    this.terminal.writeln('  \x1b[90mShift+Enter:\x1b[0m New line');
    this.terminal.writeln('  \x1b[90mCtrl+Enter / Enter:\x1b[0m Execute');
    this.terminal.writeln('  \x1b[90mCtrl+L:\x1b[0m Clear terminal\r\n');
    this.terminal.write('\x1b[1;32m>>> \x1b[0m');

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
        this.terminal.clear();
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

    window.addEventListener('resize', () => {
      if (this.fitAddon) this.fitAddon.fit();
    });
  }

  private updateBufferFromHistory() {
    // Clear current line in terminal
    const currentLen = this.inputBuffer.length;
    for (let i = 0; i < currentLen; i++) {
      this.terminal.write('\b \b');
    }

    if (this.historyIndex === -1) {
      this.inputBuffer = this.currentBufferBackup;
    } else {
      this.inputBuffer = this.history[this.historyIndex];
    }
    this.terminal.write(this.inputBuffer);
  }

  private updatePopupPosition() {
    // Estimate cursor position in pixels
    // xterm doesn't give public pixel coordinates cleanly, so we estimate
    const cursorX = this.terminal.buffer.active.cursorX;
    const cursorY = this.terminal.buffer.active.cursorY;

    // Get dimensions of a cell
    const termEl = this.terminalElement.nativeElement;
    // Fallback estimates if measurements fail
    const cellWidth = (termEl.clientWidth / this.terminal.cols) || 9;
    const cellHeight = (termEl.clientHeight / this.terminal.rows) || 17;

    this.popupX = (cursorX * cellWidth) + 16; // + left padding
    this.popupY = ((cursorY + 1) * cellHeight) + 8; // + top padding + 1 line down

    // Ensure it doesn't go off screen (basic check)
    const containerWidth = this.terminalContainer.nativeElement.clientWidth;
    if (this.popupX > containerWidth - 200) {
      this.popupX = containerWidth - 220;
    }
  }

  private handleTabCompletion() {
    // Extract the token being completed (for filtering/replacing)
    const tokenMatch = this.inputBuffer.match(/[a-zA-Z_][a-zA-Z0-9_.]*$/);
    this.currentToken = tokenMatch ? tokenMatch[0] : '';
    console.log('Completing token:', this.currentToken);

    // Pass full source code for context-aware completions (Jedi needs full context)
    const fullSource = this.inputBuffer;
    const cursorPosition = this.inputBuffer.length;

    this.runtime.getCompletions(fullSource, cursorPosition).then(matches => {
      console.log('Matches:', matches);
      if (matches.length === 0) {
        return;
      }

      if (matches.length === 1) {
        // Single match - auto-complete immediately
        this.applyCompletion(matches[0]);
      } else {
        // Multiple matches - show popup
        this.completionItems = matches;
        this.updatePopupPosition();
      }
    }).catch(err => {
      console.error('Completion error:', err);
    });
  }

  private handleSignatureHelp() {
    if (!this.runtime.getSignatures) return;

    this.runtime.getSignatures(this.inputBuffer, this.inputBuffer.length).then(signatures => {
      if (signatures && signatures.length > 0) {
        this.signatureItems = signatures;
        this.updatePopupPosition();
        // Adjust Y up for signature help (above line)
        this.popupY -= 40;
      }
    });
  }

  onCompletionSelected(item: CompletionItem) {
    console.log('Selection made:', item);
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

    console.log('Applying completion:', { name, currentToken: this.currentToken, suffix });

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
            this.terminal.scrollToBottom();
          } else if (output.type === 'stderr') {
            // Red color for stderr
            this.terminal.write('\x1b[1;31m' + output.content.replace(/\n/g, '\r\n') + '\x1b[0m');
            this.terminal.scrollToBottom();
          } else if (output.type === 'result') {
            if (output.content !== undefined && output.content !== null && output.content !== 'None') {
              this.terminal.writeln(`\x1b[1;36m${output.content}\x1b[0m`);
            }
            this.terminal.write('\x1b[1;32m>>> \x1b[0m');
            this.terminal.scrollToBottom();
          } else if (output.type === 'error') {
            this.terminal.writeln(`\r\n\x1b[1;31mError: ${output.content}\x1b[0m`);
            this.terminal.write('\x1b[1;32m>>> \x1b[0m');
            this.terminal.scrollToBottom();
          }
        },
        error: (err) => {
          this.terminal.writeln(`\r\n\x1b[1;31mSystem Error: ${err}\x1b[0m`);
          this.terminal.write('\x1b[1;32m>>> \x1b[0m');
          this.terminal.scrollToBottom();
          this.isExecuting = false;
        },
        complete: () => {
          this.isExecuting = false;
        }
      })
    );
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
    this.runtime.disconnect();
    if (this.terminal) {
      this.terminal.dispose();
    }
  }
}
