# Agent Prompt: 33_docs_diagram_expand

Examine `.agents/README.md` for development context.

**Status:** ✅ Completed
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Add expand/fullscreen functionality to Mermaid diagrams in the documentation pages.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [docs-page.component.ts](../../../praxis/web-client/src/app/features/docs/components/docs-page.component.ts) | Markdown/diagram rendering |
| [system-topology.component.ts](../../../praxis/web-client/src/app/features/docs/components/system-topology/system-topology.component.ts) | Topology diagram page |

---

## Current Implementation

Diagrams are rendered with fixed min-height and no expansion capability:

```css
.diagram-container { min-height: 400px; }

.mermaid {
  background: linear-gradient(...);
  padding: 32px;
  display: flex;
  justify-content: center;
  overflow-x: auto;
}
```

---

## Required Changes

### 1. Create DiagramOverlayComponent

```typescript
@Component({
  selector: 'app-diagram-overlay',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div class="diagram-overlay" (click)="close()">
      <div class="overlay-content" (click)="$event.stopPropagation()">
        <button mat-icon-button class="close-btn" (click)="close()">
          <mat-icon>close</mat-icon>
        </button>
        <div class="diagram-container" [innerHTML]="diagramHtml()"></div>
      </div>
    </div>
  `,
  styles: [`
    .diagram-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.8);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .overlay-content {
      background: var(--mat-sys-surface);
      border-radius: 16px;
      padding: 24px;
      max-width: 95vw;
      max-height: 95vh;
      overflow: auto;
      position: relative;
    }
    .close-btn {
      position: absolute;
      top: 8px;
      right: 8px;
    }
    .diagram-container {
      min-width: 600px;
    }
  `]
})
export class DiagramOverlayComponent {
  diagramHtml = input.required<string>();

  @Output() closed = new EventEmitter<void>();

  close(): void {
    this.closed.emit();
  }
}
```

### 2. Add Expand Button to Diagram Containers

In `docs-page.component.ts`:

```html
<div class="diagram-wrapper">
  <button mat-icon-button class="expand-btn" (click)="expandDiagram($event)">
    <mat-icon>fullscreen</mat-icon>
  </button>
  <div class="mermaid">
    <!-- diagram content -->
  </div>
</div>
```

```css
.diagram-wrapper {
  position: relative;
}

.expand-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  background: var(--mat-sys-surface-container);
}
```

### 3. Implement expandDiagram Method

```typescript
expandedDiagram = signal<string | null>(null);

expandDiagram(event: Event): void {
  const target = event.target as HTMLElement;
  const wrapper = target.closest('.diagram-wrapper');
  const mermaidDiv = wrapper?.querySelector('.mermaid');

  if (mermaidDiv) {
    this.expandedDiagram.set(mermaidDiv.innerHTML);
  }
}

closeExpanded(): void {
  this.expandedDiagram.set(null);
}
```

### 4. Add Overlay to Template

```html
@if (expandedDiagram()) {
  <app-diagram-overlay
    [diagramHtml]="expandedDiagram()!"
    (closed)="closeExpanded()">
  </app-diagram-overlay>
}
```

---

## Design Guidelines

- Expand button: Semi-transparent, top-right corner
- Overlay: Dark backdrop with centered content
- Close: Click outside or X button
- Support keyboard: Escape key closes overlay
- Preserve diagram styling in expanded view

---

## Testing

1. Expand button visible on all Mermaid diagrams
2. Click expand opens fullscreen overlay
3. Diagram renders correctly at larger size
4. Click outside or X button closes overlay
5. Escape key closes overlay

---

## On Completion

- [x] DiagramOverlayComponent created
- [x] Expand button added to diagram containers
- [x] Overlay rendering works correctly
- [x] Close functionality (click outside, X, Escape)
- [x] Update backlog status
- [x] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 6.1
