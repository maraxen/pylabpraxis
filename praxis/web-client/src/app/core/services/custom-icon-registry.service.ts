import { Injectable, inject } from '@angular/core';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';

@Injectable({
    providedIn: 'root'
})
export class CustomIconRegistryService {
    private iconRegistry = inject(MatIconRegistry);
    private sanitizer = inject(DomSanitizer);

    init() {
        this.registerCustomIcons();
    }

    private registerCustomIcons() {
        // Tip Rack (Simple grid of circles)
        this.iconRegistry.addSvgIconLiteral(
            'tip_rack_custom',
            this.sanitizer.bypassSecurityTrustHtml(`
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="6" cy="6" r="2" fill="currentColor"/>
          <circle cx="12" cy="6" r="2" fill="currentColor"/>
          <circle cx="18" cy="6" r="2" fill="currentColor"/>
          <circle cx="6" cy="12" r="2" fill="currentColor"/>
          <circle cx="12" cy="12" r="2" fill="currentColor"/>
          <circle cx="18" cy="12" r="2" fill="currentColor"/>
          <circle cx="6" cy="18" r="2" fill="currentColor"/>
          <circle cx="12" cy="18" r="2" fill="currentColor"/>
          <circle cx="18" cy="18" r="2" fill="currentColor"/>
        </svg>
      `)
        );

        // Erlenmeyer Flask
        this.iconRegistry.addSvgIconLiteral(
            'erlenmeyer',
            this.sanitizer.bypassSecurityTrustHtml(`
        <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
           <path d="M14,6V5.5C14,4.12 12.88,3 11.5,3C10.12,3 9,4.12 9,5.5V6L3,18V20H20V18L14,6M11,5.5C11,5.22 11.22,5 11.5,5C11.78,5 12,5.22 12,5.5V7H11V5.5M16.92,18H6.08L10,10.16V8H13V10.16L16.92,18Z" />
        </svg>
      `)
        );

        // Test Tube
        this.iconRegistry.addSvgIconLiteral(
            'test_tube',
            this.sanitizer.bypassSecurityTrustHtml(`
               <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                 <path d="M7,2H17V4H16V17A5,5 0 0,1 11,22A5,5 0 0,1 6,17V4H5V2H7Z" />
               </svg>
             `)
        );
    }
}
