import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import Shepherd from 'shepherd.js';
import { OnboardingService } from './onboarding.service';
import { MatDialog } from '@angular/material/dialog';

@Injectable({ providedIn: 'root' })
export class TutorialService {
    private onboarding = inject(OnboardingService);
    private router = inject(Router);
    private dialog = inject(MatDialog);
    private tour: any;

    constructor() {
        this.tour = new Shepherd.Tour({
            useModalOverlay: true,
            defaultStepOptions: {
                classes: 'praxis-tutorial-step shadow-lg rounded-xl',
                scrollTo: { behavior: 'smooth', block: 'center' },
                cancelIcon: { enabled: true },
                buttons: [
                    {
                        text: 'Back',
                        action: this.back.bind(this),
                        classes: 'mat-mdc-button'
                    },
                    {
                        text: 'Next',
                        action: this.next.bind(this),
                        classes: 'mat-mdc-raised-button mat-primary'
                    }
                ]
            }
        });

        this.initSteps();

        // Event listeners
        this.tour.on('show', (evt: any) => {
            const stepId = evt.step.id;
            this.onboarding.saveTutorialStep(stepId);
        });
        this.tour.on('complete', () => this.onComplete());
        // On cancel, keep the saved step so user can resume later
        this.tour.on('cancel', () => {
            // State is already saved on 'show', so nothing to do
            // User can resume from Settings -> Restart Tutorial
        });
    }

    start(resume: boolean = false) {
        if (resume) {
            const state = this.onboarding.getTutorialState();
            if (state && state.stepId) {
                this.tour.show(state.stepId);
                return;
            }
        }

        // Start fresh
        this.onboarding.startTutorialSession();
        this.tour.start();
    }

    next() {
        this.tour.next();
    }

    back() {
        this.tour.back();
    }

    /**
     * Skip to the next section of the tutorial.
     * Sections: Assets (2-4), Protocols (5-6), Run (7-9), REPL (10-11), Settings (12-13)
     */
    skipSection() {
        const currentStepId = this.tour.getCurrentStep()?.id;
        const sectionMap: Record<string, string> = {
            'intro': 'nav-assets',
            'nav-assets': 'nav-protocols',
            'assets-machines': 'nav-protocols',
            'assets-resources': 'nav-protocols',
            'nav-protocols': 'nav-run',
            'protocols-import': 'nav-run',
            'nav-run': 'nav-playground',
            'run-step-protocol': 'nav-playground',
            'run-step-params': 'nav-playground',
            'run-step-machine': 'nav-playground',
            'run-step-assets': 'nav-playground',
            'run-step-deck': 'nav-playground',
            'nav-playground': 'nav-settings',
            'playground-term': 'nav-settings',
            'nav-settings': 'settings-finish',
            'settings-finish': 'settings-finish'
        };
        const nextSection = sectionMap[currentStepId] || 'settings-finish';
        this.tour.show(nextSection);
    }

    private initSteps() {
        // Step 1: Dashboard
        this.addStep({
            id: 'intro',
            title: 'Welcome to Praxis',
            text: 'This is your dashboard overview. See active runs and system status at a glance.',
            attachTo: { element: '[data-tour-id="dashboard-root"]', on: 'center' },
            route: '/app/home',
            buttons: [{ text: 'Start Tour', action: this.next.bind(this), classes: 'mat-mdc-raised-button mat-primary' }]
        });

        // Step 2: Assets Navigation
        this.addStep({
            id: 'nav-assets',
            title: 'Asset Management',
            text: 'Click here to manage your lab inventory, machines, and resources.',
            attachTo: { element: '[data-tour-id="nav-assets"]', on: 'right' },
            advanceOn: { selector: '[data-tour-id="nav-assets"]', event: 'click' }
        });

        // Step 3: Machines Tab
        this.addStep({
            id: 'assets-machines',
            title: 'Machines (Liquid Handlers)',
            text: 'Here you can define machines like Hamilton STAR or Opentrons Flex. Click "Add Machine" to register a new device.',
            attachTo: { element: '[data-tour-id="add-asset-btn"]', on: 'bottom' },
            route: '/app/assets',
            queryParams: { type: 'machine' },
            waitFor: '[data-tour-id="machine-list"]',
            advanceOn: { selector: '[data-tour-id="add-asset-btn"]', event: 'click' }
        });

        // Step 4: Resources Tab
        this.addStep({
            id: 'assets-resources',
            title: 'Labware Resources',
            text: 'Switch to the Resources tab to manage plates, tips, and other labware.',
            attachTo: { element: '[data-tour-id="resource-list"]', on: 'center' },
            route: '/app/assets',
            queryParams: { type: 'resource' },
            waitFor: '[data-tour-id="resource-list"]'
        });

        // Step 5: Protocols Navigation
        this.addStep({
            id: 'nav-protocols',
            title: 'Protocols',
            text: 'Click here to access your protocol library.',
            attachTo: { element: '[data-tour-id="nav-protocols"]', on: 'right' },
            advanceOn: { selector: '[data-tour-id="nav-protocols"]', event: 'click' }
        });

        // Step 6: Import Protocol
        this.addStep({
            id: 'protocols-import',
            title: 'Import Protocols',
            text: 'Upload your Python protocol files (.py) here to make them available for execution.<br><br><em><strong>Note:</strong> Protocol upload is not yet available in Browser Mode as it requires server-side inspection. A solution is in development.</em>',
            attachTo: { element: '[data-tour-id="import-protocol-btn"]', on: 'bottom' },
            route: '/app/protocols',
            waitFor: '[data-tour-id="protocol-table"]'
        });

        // Step 7: Run Navigation
        this.addStep({
            id: 'nav-run',
            title: 'Run Protocol',
            text: 'Ready to experiment? Click here to start the execution wizard.',
            attachTo: { element: '[data-tour-id="nav-run"]', on: 'right' },
            advanceOn: { selector: '[data-tour-id="nav-run"]', event: 'click' }
        });

        // Step 8: Run Wizard - Step 1
        this.addStep({
            id: 'run-step-protocol',
            title: '1. Select Protocol',
            text: 'First, select the protocol you want to run from your library.',
            attachTo: { element: '[data-tour-id="run-step-label-protocol"]', on: 'bottom' },
            route: '/app/run',
            waitFor: '[data-tour-id="run-step-protocol"]'
        });

        // Step 9: Run Wizard - Step 2
        this.addStep({
            id: 'run-step-params',
            title: '2. Configure Parameters',
            text: 'Next, you will configure any runtime parameters defined in your protocol script.',
            attachTo: { element: '[data-tour-id="run-step-label-params"]', on: 'bottom' }
        });

        // Step 10: Run Wizard - Step 3
        this.addStep({
            id: 'run-step-machine',
            title: '3. Select Machine',
            text: 'Then, choose an available robot for execution.',
            attachTo: { element: '[data-tour-id="run-step-label-machine"]', on: 'bottom' }
        });

        // Step 11: Run Wizard - Step 4
        this.addStep({
            id: 'run-step-assets',
            title: '4. Map Assets',
            text: 'You will need to map the protocol\'s labware requirements to your actual inventory.',
            attachTo: { element: '[data-tour-id="run-step-label-assets"]', on: 'bottom' }
        });

        // Step 12: Run Wizard - Step 5
        this.addStep({
            id: 'run-step-deck',
            title: '5. Deck Setup',
            text: 'Finally, verify the deck layout visually before starting the run.',
            attachTo: { element: '[data-tour-id="run-step-label-deck"]', on: 'bottom' }
        });

        // Step 10: Playground Navigation
        this.addStep({
            id: 'nav-playground',
            title: 'Playground',
            text: 'For direct control and testing, use the Python Playground (REPL).',
            attachTo: { element: '[data-tour-id="nav-playground"]', on: 'right' },
            advanceOn: { selector: '[data-tour-id="nav-playground"]', event: 'click' }
        });

        // Step 11: Playground Notebook (JupyterLite)
        this.addStep({
            id: 'playground-term',
            title: 'Playground Notebook',
            text: 'This is a full JupyterLite environment running in your browser. You can control hardware directly using PyLabRobot commands.',
            attachTo: { element: '[data-tour-id="repl-notebook"]', on: 'center' },
            route: '/app/playground',
            waitFor: '[data-tour-id="repl-notebook"]'
        });

        // Step 12: Settings Navigation
        this.addStep({
            id: 'nav-settings',
            title: 'Settings',
            text: 'Finally, let\'s look at your preferences.',
            attachTo: { element: '[data-tour-id="nav-settings"]', on: 'right' },
            advanceOn: { selector: '[data-tour-id="nav-settings"]', event: 'click' }
        });

        // Step 13: Finish
        this.addStep({
            id: 'settings-finish',
            title: 'You\'re All Set!',
            text: 'You can toggle themes, enable "Infinite Consumables" for easier simulation, or manage your preferences anytime from here.',
            attachTo: { element: '[data-tour-id="settings-onboarding"]', on: 'top' },
            route: '/app/settings',
            buttons: [{ text: 'Finish', action: this.onComplete.bind(this), classes: 'mat-mdc-raised-button mat-primary' }]
        });
    }

    private addStep(config: any) {
        const stepConfig: any = {
            id: config.id,
            title: config.title,
            text: config.text,
            attachTo: config.attachTo,
            buttons: config.buttons || [
                { text: 'Back', action: this.back.bind(this), classes: 'mat-mdc-button' },
                { text: 'Skip Section', action: this.skipSection.bind(this), classes: 'mat-mdc-button' },
                { text: 'Next', action: this.next.bind(this), classes: 'mat-mdc-raised-button mat-primary' }
            ]
        };

        if (config.advanceOn) {
            stepConfig.advanceOn = config.advanceOn;
        }

        if (config.route) {
            stepConfig.beforeShowPromise = () => {
                return new Promise((resolve) => {
                    this.router.navigate([config.route], { queryParams: config.queryParams || {} })
                        .then(() => {
                            if (config.waitFor) {
                                // Simple poll for element
                                const interval = setInterval(() => {
                                    if (document.querySelector(config.waitFor)) {
                                        clearInterval(interval);
                                        resolve(null);
                                    }
                                }, 100);
                                // Timeout fallback
                                setTimeout(() => {
                                    clearInterval(interval);
                                    resolve(null);
                                }, 3000);
                            } else {
                                setTimeout(() => resolve(null), 500); // Default wait for route transition
                            }
                        });
                });
            };
        }

        this.tour.addStep(stepConfig);
    }

    private onComplete() {
        this.onboarding.markTutorialComplete();
        this.onboarding.clearTutorialState();
        this.tour.complete();
    }
}
