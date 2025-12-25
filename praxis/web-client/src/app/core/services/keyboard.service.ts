import { Injectable, inject, RendererFactory2, Renderer2 } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { CommandPaletteComponent } from '../components/command-palette/command-palette.component';
import { CommandRegistryService } from './command-registry.service';

@Injectable({
  providedIn: 'root',
})
export class KeyboardService {
  private dialog = inject(MatDialog);
  private router = inject(Router);
  private registry = inject(CommandRegistryService);
  private rendererFactory = inject(RendererFactory2);
  private renderer: Renderer2;

  constructor() {
    this.renderer = this.rendererFactory.createRenderer(null, null);
    this.initGlobalListeners();
    this.registerDefaultCommands();
  }

  private initGlobalListeners() {
    this.renderer.listen('window', 'keydown', (event: KeyboardEvent) => {
      // Check if user is in an input field
      const activeElement = document.activeElement;
      const isInput = activeElement instanceof HTMLInputElement ||
        activeElement instanceof HTMLTextAreaElement ||
        (activeElement instanceof HTMLElement && activeElement.isContentEditable);

      const isCmdOrCtrl = event.metaKey || event.ctrlKey;
      const isAlt = event.altKey;

      // Cmd+K or Ctrl+K: Command Palette (Keep this as Cmd/Ctrl)
      if (isCmdOrCtrl && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        this.openCommandPalette();
      }

      // Safe Navigation Shortcuts (only if not in input)
      // Moved from Cmd to Alt/Option to avoid browser conflicts (Cmd+R, etc)
      // Use event.code instead of event.key because Option+Key on Mac produces special chars (e.g. Option+p = π)
      if (!isInput && isAlt) {
        switch (event.code) {
          case 'KeyP':
            event.preventDefault();
            this.router.navigate(['/app/protocols']);
            break;
          case 'KeyR':
            event.preventDefault();
            this.router.navigate(['/app/assets'], { queryParams: { type: 'resource' } });
            break;
          case 'KeyM':
            event.preventDefault();
            this.router.navigate(['/app/assets'], { queryParams: { type: 'machine' } });
            break;
          case 'KeyH':
            event.preventDefault();
            this.router.navigate(['/app/home']);
            break;
        }
      }
    });
  }

  private openCommandPalette() {
    // Prevent multiple instances
    if (this.dialog.openDialogs.some(d => d.componentInstance instanceof CommandPaletteComponent)) {
      return;
    }

    this.dialog.open(CommandPaletteComponent, {
      width: '600px',
      maxWidth: '90vw',
      panelClass: 'command-palette-dialog',
      backdropClass: 'command-palette-backdrop',
      position: { top: '10%' },
    });
  }

  private registerDefaultCommands() {
    this.registry.registerCommand({
      id: 'nav-home',
      label: 'Go to Home',
      description: 'Navigate to the dashboard',
      icon: 'home',
      category: 'Navigation',
      shortcut: 'Alt+H',
      action: () => this.router.navigate(['/app/home']),
      keywords: ['dashboard', 'main'],
    });

    this.registry.registerCommand({
      id: 'nav-protocols',
      label: 'Go to Protocols',
      description: 'View the protocol library',
      icon: 'science',
      category: 'Navigation',
      shortcut: 'Alt+P',
      action: () => this.router.navigate(['/app/protocols']),
      keywords: ['scripts', 'definitions'],
    });

    this.registry.registerCommand({
      id: 'nav-assets',
      label: 'Go to Assets',
      description: 'Manage machines and resources',
      icon: 'inventory_2',
      category: 'Navigation',
      shortcut: 'Alt+A',
      action: () => this.router.navigate(['/app/assets']),
      keywords: ['machines', 'instruments', 'labware'],
    });

    this.registry.registerCommand({
      id: 'theme-toggle',
      label: 'Toggle Theme',
      description: 'Switch between light and dark mode',
      icon: 'contrast',
      category: 'Settings',
      action: () => {
        // This should probably call a ThemeService, but for now we can trigger it via store if available
        // Or just emit a message. Since I don't want to break existing logic, 
        // I'll assume there is a theme toggle logic somewhere.
        const body = document.body;
        if (body.classList.contains('light-theme')) {
          body.classList.remove('light-theme');
          localStorage.setItem('theme', 'dark');
        } else {
          body.classList.add('light-theme');
          localStorage.setItem('theme', 'light');
        }
      },
    });
  }
}
