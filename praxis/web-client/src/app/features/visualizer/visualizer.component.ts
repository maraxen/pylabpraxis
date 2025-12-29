import { Component, ChangeDetectionStrategy, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';


@Component({
  selector: 'app-visualizer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="visualizer-container">
      <iframe 
        *ngIf="visualizerUrl" 
        [src]="visualizerUrl" 
        class="visualizer-frame"
        title="PyLabRobot Visualizer"
        (load)="onIframeLoad($event)">
      </iframe>
      <div *ngIf="!visualizerUrl" class="error">
        Unable to load visualizer URL.
      </div>
    </div>
  `,
  styles: [`
    .visualizer-container {
      height: 100%;
      width: 100%;
      display: flex;
      flex-direction: column;
    }
    .visualizer-frame {
      flex: 1;
      border: none;
      width: 100%;
      height: 100%;
    }
    .error {
      padding: 20px;
      color: red;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VisualizerComponent implements OnInit {
  private sanitizer = inject(DomSanitizer);
  visualizerUrl: SafeResourceUrl | null = null;

  ngOnInit() {
    // In demo mode, we use the wrapper which listens for postMessage
    const wsPort = '2121';
    const fsPort = '1337';

    const url = `assets/visualizer-wrapper.html?ws_port=${wsPort}&fs_port=${fsPort}&mode=demo`;
    this.visualizerUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  onIframeLoad(event: Event) {
    // PostMessage logic can be added here if we want to dynamic update
    // For now, mode=demo in the URL handles loading the mock data.
    console.log('Visualizer iframe loaded');
  }
}