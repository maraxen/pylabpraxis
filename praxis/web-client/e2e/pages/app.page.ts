import { BasePage } from './base.page';

export class AppPage extends BasePage {
    // Specific locators for the main shell
    get sidebar() {
        return this.page.locator('mat-sidenav');
    }

    get content() {
        return this.page.locator('router-outlet + *');
    }
}
