import { Component, ChangeDetectionStrategy, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { environment } from '@env/environment';

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
        title="PyLabRobot Visualizer">
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
    const wsPort = '2121'; 
    const fsPort = '1337';

    const url = `/assets/visualizer-wrapper.html?ws_port=${wsPort}&fs_port=${fsPort}`;
    this.visualizerUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}