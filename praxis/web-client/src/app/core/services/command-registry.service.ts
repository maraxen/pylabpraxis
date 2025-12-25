import { Injectable, signal } from '@angular/core';

export interface Command {
  id: string;
  label: string;
  description?: string;
  icon?: string;
  category?: string;
  action: () => void;
  keywords?: string[];
  shortcut?: string;
}

@Injectable({
  providedIn: 'root',
})
export class CommandRegistryService {
  private _commands = signal<Command[]>([]);
  public commands = this._commands.asReadonly();

  registerCommand(command: Command) {
    this._commands.update((cmds) => [...cmds, command]);
  }

  unregisterCommand(id: string) {
    this._commands.update((cmds) => cmds.filter((c) => c.id !== id));
  }

  executeCommand(id: string) {
    const command = this._commands().find((c) => c.id === id);
    if (command) {
      command.action();
    }
  }
}
