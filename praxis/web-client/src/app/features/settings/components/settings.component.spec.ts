import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SettingsComponent } from './settings.component';
import { AppStore } from '../../../core/store/app.store';
import { OnboardingService } from '@core/services/onboarding.service';
import { TutorialService } from '@core/services/tutorial.service';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('SettingsComponent', () => {
    let component: SettingsComponent;
    let fixture: ComponentFixture<SettingsComponent>;

    // Mocks
    const storeMock = {
        theme: vi.fn(() => 'system'),
        setTheme: vi.fn(),
        maintenanceEnabled: vi.fn(() => true),
        setMaintenanceEnabled: vi.fn()
    };

    const onboardingMock = {
        getTutorialState: vi.fn(() => null),
        clearTutorialState: vi.fn(),
        isDemoModeEnabled: vi.fn(() => false)
    };

    const tutorialMock = {
        start: vi.fn()
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SettingsComponent],
            providers: [
                { provide: AppStore, useValue: storeMock },
                { provide: OnboardingService, useValue: onboardingMock },
                { provide: TutorialService, useValue: tutorialMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(SettingsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should set theme', () => {
        component.setTheme('dark');
        expect(storeMock.setTheme).toHaveBeenCalledWith('dark');
    });

    it('should check for tutorial progress', () => {
        const hasProgress = component.hasTutorialProgress();
        expect(hasProgress).toBe(false);
        expect(onboardingMock.getTutorialState).toHaveBeenCalled();
    });

    it('should resume tutorial', () => {
        component.resumeTutorial();
        expect(tutorialMock.start).toHaveBeenCalledWith(true);
    });

    it('should restart tutorial', () => {
        component.restartTutorial();
        expect(onboardingMock.clearTutorialState).toHaveBeenCalled();
        expect(tutorialMock.start).toHaveBeenCalledWith(false);
    });
});
