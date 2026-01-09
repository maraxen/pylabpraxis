import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WelcomeDialogComponent } from './welcome-dialog.component';
import { MatDialogRef } from '@angular/material/dialog';
import { OnboardingService } from '@core/services/onboarding.service';
import { ModeService } from '@core/services/mode.service';
import { TutorialService } from '@core/services/tutorial.service';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('WelcomeDialogComponent', () => {
    let component: WelcomeDialogComponent;
    let fixture: ComponentFixture<WelcomeDialogComponent>;

    // Mocks
    const dialogRefMock = {
        close: vi.fn()
    };

    const onboardingMock = {
        hasCompletedOnboarding: vi.fn(() => false),
        markOnboardingComplete: vi.fn(),
    };

    const modeServiceMock = {
        isBrowserMode: vi.fn(() => false)
    };

    const tutorialMock = {
        start: vi.fn()
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [WelcomeDialogComponent],
            providers: [
                { provide: MatDialogRef, useValue: dialogRefMock },
                { provide: OnboardingService, useValue: onboardingMock },
                { provide: ModeService, useValue: modeServiceMock },
                { provide: TutorialService, useValue: tutorialMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(WelcomeDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should start tutorial and close dialog', () => {
        component.startTutorial();
        expect(onboardingMock.markOnboardingComplete).toHaveBeenCalled();
        expect(dialogRefMock.close).toHaveBeenCalled();
        expect(tutorialMock.start).toHaveBeenCalled();
    });

    it('should skip and close dialog', () => {
        component.skip();
        expect(onboardingMock.markOnboardingComplete).toHaveBeenCalled();
        expect(dialogRefMock.close).toHaveBeenCalled();
    });
});
