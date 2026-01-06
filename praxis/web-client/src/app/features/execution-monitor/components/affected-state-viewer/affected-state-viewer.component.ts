/**
 * Affected State Viewer Component
 *
 * Displays a table of state changes that may have been affected by a failed
 * operation, showing before/after values with visual indicators.
 */
import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { UncertainStateChange } from '../../models/state-resolution.models';

@Component({
    selector: 'app-affected-state-viewer',
    standalone: true,
    imports: [MatIconModule, MatTooltipModule],
    templateUrl: './affected-state-viewer.component.html',
    styleUrl: './affected-state-viewer.component.scss',
})
export class AffectedStateViewerComponent {
    /** List of uncertain state changes to display. */
    @Input() states: UncertainStateChange[] = [];

    /** Whether values are editable. */
    @Input() editable = false;

    /** Current resolved values (for editable mode). */
    @Input() resolvedValues: Record<string, unknown> = {};

    /** Emits when user changes a resolved value. */
    @Output() valueChange = new EventEmitter<{ key: string; value: unknown }>();

    /**
     * Get user-friendly label for property type.
     */
    getPropertyTypeLabel(type: string): string {
        const labels: Record<string, string> = {
            volume: 'Volume (µL)',
            has_liquid: 'Contains Liquid',
            has_tip: 'Has Tip',
            tip_loaded: 'Tip Loaded',
            temperature: 'Temperature (°C)',
            position: 'Position',
            arbitrary: 'State',
        };
        return labels[type] || 'State';
    }

    /**
     * Get icon for property type.
     */
    getPropertyIcon(type: string): string {
        const icons: Record<string, string> = {
            volume: 'water_drop',
            has_liquid: 'opacity',
            has_tip: 'push_pin',
            tip_loaded: 'hardware',
            temperature: 'thermostat',
            position: 'place',
            arbitrary: 'info',
        };
        return icons[type] || 'info';
    }

    /**
     * Format a value for display.
     */
    formatValue(value: unknown): string {
        if (value === null || value === undefined) {
            return '—';
        }
        if (typeof value === 'number') {
            return value.toFixed(2);
        }
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        return String(value);
    }

    /**
     * Get CSS class for change indicator.
     */
    getChangeClass(state: UncertainStateChange): string {
        if (state.expected_value === undefined) {
            return 'change-unknown';
        }
        const current = state.current_value;
        const expected = state.expected_value;

        if (current === expected) {
            return 'change-none';
        }
        if (typeof expected === 'number' && typeof current === 'number') {
            return expected > current ? 'change-increase' : 'change-decrease';
        }
        return 'change-modified';
    }

    /**
     * Get tooltip text for change indicator.
     */
    getChangeTooltip(state: UncertainStateChange): string {
        if (state.expected_value === undefined) {
            return 'Expected value unknown';
        }
        const current = this.formatValue(state.current_value);
        const expected = this.formatValue(state.expected_value);
        return `Before: ${current} → Expected: ${expected}`;
    }

    /**
     * Handle value input change.
     */
    onValueChange(stateKey: string, event: Event): void {
        const input = event.target as HTMLInputElement;
        const rawValue = input.value;

        // Parse value
        let value: unknown = rawValue;
        const numValue = parseFloat(rawValue);
        if (!isNaN(numValue)) {
            value = numValue;
        } else if (rawValue.toLowerCase() === 'true') {
            value = true;
        } else if (rawValue.toLowerCase() === 'false') {
            value = false;
        }

        this.valueChange.emit({ key: stateKey, value });
    }

    /**
     * Get resolved value for a state key.
     */
    getResolvedValue(stateKey: string): unknown {
        return this.resolvedValues[stateKey];
    }
}
