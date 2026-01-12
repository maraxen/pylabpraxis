import { Component, signal, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SqliteService } from './core/services/sqlite.service';
import { ApiConfigService } from './core/services/api-config.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('web-client');
  private apiConfig = inject(ApiConfigService);

  constructor(private sqlite: SqliteService) {
    // Initialize API client configuration
    this.apiConfig.initialize();

    // Expose for E2E testing
    (window as any).sqliteService = this.sqlite;
  }
}
