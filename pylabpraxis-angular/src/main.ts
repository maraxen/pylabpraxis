import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config'; // Import your application configuration
import { AppComponent } from './app/app.component'; // Import your root component

bootstrapApplication(AppComponent, appConfig) // Bootstrap with appConfig
  .catch((err) => console.error(err));
