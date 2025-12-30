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
import { ReplRuntime, ReplOutput } from '../../core/services/repl-runtime.interface';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-repl',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  template: `
    <div class="repl-container">
      <mat-card class="repl-card">
        <div class="repl-header">
          <mat-icon>terminal</mat-icon>
          <h2>PyLabRobot REPL ({{ modeLabel() }})</h2>
        </div>
        <div class="repl-terminal-wrapper" #terminalContainer>
          <div #terminalElement></div>
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
    }
  `]
})
export class ReplComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('terminalElement', { static: true }) terminalElement!: ElementRef;
  @ViewChild('terminalContainer', { static: true }) terminalContainer!: ElementRef;

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

  modeLabel = this.modeService.modeLabel;

  constructor() {
    // Sync terminal theme with app theme
    effect(() => {
      const theme = this.store.theme();
      if (this.terminal) {
        const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
        this.terminal.options.theme = {
          background: isDark ? '#0a0a0c' : '#f8fafc',
          foreground: isDark ? '#e0e0e0' : '#0f172a',
          cursor: isDark ? '#cd4d6e' : '#ed7a9b',
          selectionBackground: isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)',
        };
      }
    });
  }

  ngOnInit() {
    this.runtime = this.modeService.isBrowserMode()
      ? this.pythonRuntime
      : this.backendRepl;
  }

  ngAfterViewInit() {
    this.initTerminal();
    this.connectRuntime();
  }

  private initTerminal() {
    const theme = this.store.theme();
    const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    this.terminal = new Terminal({
      cursorBlink: true,
      theme: {
        background: isDark ? '#0a0a0c' : '#f8fafc',
        foreground: isDark ? '#e0e0e0' : '#0f172a',
        cursor: isDark ? '#cd4d6e' : '#ed7a9b',
      },
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      fontSize: 13,
      scrollback: 2000,
      convertEol: true
    });

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

      // Enter key
      if (keyCode === 13) {
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

  private handleTabCompletion() {
    const tokenMatch = this.inputBuffer.match(/[a-zA-Z_][a-zA-Z0-9_.]*$/);
    const token = tokenMatch ? tokenMatch[0] : '';

    this.runtime.getCompletions(token, this.inputBuffer.length).then(matches => {
      if (matches.length === 1) {
        const completion = matches[0];
        if (token && completion.startsWith(token)) {
          const suffix = completion.slice(token.length);
          this.inputBuffer += suffix;
          this.terminal.write(suffix);
        }
      } else if (matches.length > 1) {
        this.terminal.writeln('');
        this.terminal.writeln('\x1b[90m' + matches.join('  ') + '\x1b[0m');
        this.terminal.write('\x1b[1;32m>>> \x1b[0m');
        this.terminal.write(this.inputBuffer);
      }
    });
  }

  private connectRuntime() {
    this.subscription.add(
      this.runtime.connect().subscribe({
        next: () => {
          this.terminal.writeln('\x1b[90m# Runtime connected and ready.\x1b[0m\r\n');
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
          if (output.type === 'stdout' || output.type === 'stderr') {
            this.terminal.write(output.content.replace(/\n/g, '\r\n'));
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

  ngOnDestroy() {
    this.subscription.unsubscribe();
    this.runtime.disconnect();
    if (this.terminal) {
      this.terminal.dispose();
    }
  }
}
