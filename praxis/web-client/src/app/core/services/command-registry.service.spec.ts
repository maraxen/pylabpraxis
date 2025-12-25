import { TestBed } from '@angular/core/testing';
import { CommandRegistryService, Command } from './command-registry.service';

describe('CommandRegistryService', () => {
  let service: CommandRegistryService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CommandRegistryService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should register a command', () => {
    const command: Command = {
      id: 'test',
      label: 'Test Command',
      action: vi.fn(),
    };
    service.registerCommand(command);
    expect(service.commands()).toContain(command);
  });

  it('should unregister a command', () => {
    const command: Command = {
      id: 'test',
      label: 'Test Command',
      action: vi.fn(),
    };
    service.registerCommand(command);
    service.unregisterCommand('test');
    expect(service.commands()).not.toContain(command);
  });

  it('should execute a command by id', () => {
    const action = vi.fn();
    const command: Command = {
      id: 'test',
      label: 'Test Command',
      action,
    };
    service.registerCommand(command);
    service.executeCommand('test');
    expect(action).toHaveBeenCalled();
  });
});
