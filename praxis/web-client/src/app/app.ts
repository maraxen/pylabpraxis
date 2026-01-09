import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SqliteService } from './core/services/sqlite.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('web-client');

  constructor(private sqlite: SqliteService) {
    // Expose for E2E testing
    (window as any).sqliteService = this.sqlite;
  }
}
