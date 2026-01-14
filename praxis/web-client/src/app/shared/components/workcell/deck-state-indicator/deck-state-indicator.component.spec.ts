import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { DeckStateIndicatorComponent, DeckStateSource } from './deck-state-indicator.component';
import { By } from '@angular/platform-browser';

@Component({
  template: `<app-deck-state-indicator [source]="source" />`,
  standalone: true,
  imports: [DeckStateIndicatorComponent]
})
class TestHostComponent {
  source: DeckStateSource = 'live';
}

describe('DeckStateIndicatorComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let hostComponent: TestHostComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent, DeckStateIndicatorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
  });

  it('should create', () => {
    hostComponent.source = 'live';
    fixture.detectChanges();
    const indicator = fixture.debugElement.query(By.directive(DeckStateIndicatorComponent));
    expect(indicator).toBeTruthy();
  });

  it('should render LIVE state correctly', () => {
    hostComponent.source = 'live';
    fixture.detectChanges();
    
    const badge = fixture.debugElement.query(By.css('.state-indicator'));
    expect(badge.classes['live']).toBe(true);
    expect(badge.nativeElement.textContent).toContain('LIVE');
  });

  it('should render SIMULATED state correctly', () => {
    hostComponent.source = 'simulated';
    fixture.detectChanges();
    
    const badge = fixture.debugElement.query(By.css('.state-indicator'));
    expect(badge.classes['simulated']).toBe(true);
    expect(badge.nativeElement.textContent).toContain('SIMULATED');
  });

  it('should render OFFLINE state for cached source', () => {
    hostComponent.source = 'cached';
    fixture.detectChanges();
    
    const badge = fixture.debugElement.query(By.css('.state-indicator'));
    expect(badge.classes['cached']).toBe(true);
    expect(badge.nativeElement.textContent).toContain('OFFLINE');
  });
  
  it('should render STATIC state for definition source', () => {
    hostComponent.source = 'definition';
    fixture.detectChanges();
    
    const badge = fixture.debugElement.query(By.css('.state-indicator'));
    expect(badge.classes['definition']).toBe(true);
    expect(badge.nativeElement.textContent).toContain('STATIC');
  });
});