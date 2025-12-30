import { Component, Input, computed, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-sparkline',
    standalone: true,
    imports: [CommonModule],
    template: `
    <svg [attr.viewBox]="viewBox()" class="sparkline-svg" preserveAspectRatio="none">
      <path [attr.d]="pathCheck()" [attr.stroke]="color" fill="none" class="sparkline-path" />
      <circle *ngIf="lastPoint()" [attr.cx]="lastPoint()?.x" [attr.cy]="lastPoint()?.y" r="3" [attr.fill]="color" />
    </svg>
  `,
    styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }
    .sparkline-svg {
      width: 100%;
      height: 100%;
      overflow: visible;
    }
    .sparkline-path {
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
      vector-effect: non-scaling-stroke; 
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class SparklineComponent {
    @Input({ required: true }) data: number[] = [];
    @Input() color: string = 'var(--mat-sys-primary)';
    @Input() width: number = 100;
    @Input() height: number = 30;

    viewBox = computed(() => `0 0 ${this.width} ${this.height}`);

    pathCheck = computed(() => {
        if (!this.data || this.data.length < 2) return '';
        return this.generatePath(this.data);
    });

    lastPoint = computed(() => {
        if (!this.data || this.data.length === 0) return null;
        const { x, y } = this.calculatePoint(this.data.length - 1, this.data[this.data.length - 1], this.data);
        return { x, y };
    });

    private generatePath(data: number[]): string {
        const points = data.map((val, index) => {
            const { x, y } = this.calculatePoint(index, val, data);
            return `${x},${y}`;
        });
        return `M ${points.join(' L ')}`;
    }

    private calculatePoint(index: number, val: number, data: number[]) {
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;

        // X is distributed evenly
        const x = (index / (data.length - 1)) * this.width;

        // Y is normalized and inverted (SVG coords)
        // Add some padding to avoid clipping at extremities
        const padding = 2;
        const availableHeight = this.height - (padding * 2);
        const normalizedVal = (val - min) / range;
        const y = this.height - padding - (normalizedVal * availableHeight);

        return { x, y };
    }
}
