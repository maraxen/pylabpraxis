import { Component, Input, ChangeDetectionStrategy } from '@angular/core';


@Component({
  selector: 'app-protocol-card-skeleton',
  standalone: true,
  imports: [],
  template: `
    <div class="praxis-card" [class.praxis-card-min]="compact">
      <div class="card-header">
        <div class="flex items-center gap-3 w-full">
          <div class="skeleton-avatar"></div>
          <div class="flex-1">
            <div class="skeleton-title"></div>
            @if (!compact) {
              <div class="skeleton-subtitle"></div>
            }
          </div>
        </div>
      </div>
      @if (!compact) {
        <div class="card-content">
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
        <div class="card-actions">
          <div class="flex gap-2">
            <div class="skeleton-chip"></div>
            <div class="skeleton-chip"></div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    .praxis-card-min {
      min-width: 180px;
      max-width: 220px;
    }
    .skeleton-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }
    .skeleton-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(90deg, var(--mat-sys-surface-container) 25%, var(--mat-sys-surface-container-high) 50%, var(--mat-sys-surface-container) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
    }
    .skeleton-title-area {
      flex: 1;
    }
    .skeleton-title {
      height: 20px;
      width: 60%;
      border-radius: 4px;
      background: linear-gradient(90deg, var(--mat-sys-surface-container) 25%, var(--mat-sys-surface-container-high) 50%, var(--mat-sys-surface-container) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      margin-bottom: 8px;
    }
    .skeleton-subtitle {
      height: 14px;
      width: 40%;
      border-radius: 4px;
      background: linear-gradient(90deg, var(--mat-sys-surface-container) 25%, var(--mat-sys-surface-container-high) 50%, var(--mat-sys-surface-container) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
    }
    .skeleton-content {
      margin-bottom: 16px;
    }
    .skeleton-line {
      height: 14px;
      width: 100%;
      border-radius: 4px;
      background: linear-gradient(90deg, var(--mat-sys-surface-container) 25%, var(--mat-sys-surface-container-high) 50%, var(--mat-sys-surface-container) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      margin-bottom: 8px;
    }
    .skeleton-line.short {
      width: 70%;
    }
    .skeleton-chips {
      display: flex;
      gap: 8px;
    }
    .skeleton-chip {
      height: 24px;
      width: 60px;
      border-radius: 12px;
      background: linear-gradient(90deg, var(--mat-sys-surface-container) 25%, var(--mat-sys-surface-container-high) 50%, var(--mat-sys-surface-container) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolCardSkeletonComponent {
  @Input() compact = false;
}
