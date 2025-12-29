import { Component, ChangeDetectionStrategy, Input, signal, effect, inject, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { PlrDeckData } from '@core/models/plr.models';

@Component({
  selector: 'app-deck-visualizer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="deck-visualizer-wrapper">
      <div class="visualizer-header">
        <h4>Deck Configuration Visualizer</h4>
      </div>

      <div class="iframe-container">
        <iframe
            *ngIf="visualizerUrl"
            [src]="visualizerUrl"
            class="visualizer-frame"
            title="PyLabRobot Visualizer"
            (load)="onIframeLoad($event)">
        </iframe>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .deck-visualizer-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--sys-surface-container-low);
      border-radius: 12px;
      padding: 16px;
      border: 1px solid var(--sys-outline-variant);
    }

    .visualizer-header {
      margin-bottom: 16px;
    }

    .visualizer-header h4 {
      margin: 0;
      color: var(--sys-on-surface);
    }

    .iframe-container {
      flex: 1;
      min-height: 0;
      overflow: hidden;
      border-radius: 8px;
      background: white;
    }

    .visualizer-frame {
      width: 100%;
      height: 100%;
      border: none;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckVisualizerComponent {
  private sanitizer = inject(DomSanitizer);

  // Inputs
  @Input({ required: true }) set layoutData(value: PlrDeckData | null) {
    this.data.set(value);
  }

  // Signals
  data = signal<PlrDeckData | null>(null);
  iframeLoaded = signal(false);
  private iframeWindow: Window | null = null;

  visualizerUrl: SafeResourceUrl;

  constructor() {
    const url = `assets/visualizer-wrapper.html?mode=demo&autoload=false&embedded=true`;
    this.visualizerUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);

    // Effect to update visualizer when data changes
    effect(() => {
      const data = this.data();
      const loaded = this.iframeLoaded();

      if (data && loaded && this.iframeWindow) {
        this.sendDataToVisualizer(data);
      }
    });
  }

  onIframeLoad(event: Event) {
    const iframe = event.target as HTMLIFrameElement;
    this.iframeWindow = iframe.contentWindow;
    this.iframeLoaded.set(true);
  }

  private sendDataToVisualizer(data: PlrDeckData) {
    // Small timeout to ensure visualizer scripts are fully ready to receive
    setTimeout(() => {
      this.iframeWindow?.postMessage({
        type: 'init_visualizer',
        data: data // vis.js expects { resource: ... } structure
      }, '*');
    }, 100);
  }
}
