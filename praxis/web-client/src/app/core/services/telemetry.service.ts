import { Injectable } from '@angular/core';
import { Observable, interval, map, shareReplay } from 'rxjs';

export interface TelemetryPoint {
    timestamp: number;
    value: number;
    label: string;
}

@Injectable({
    providedIn: 'root'
})
export class TelemetryService {
    constructor() { }

    /**
     * Returns an observable that emits random temperature data every second.
     */
    getTemperatureStream(): Observable<TelemetryPoint> {
        return interval(1000).pipe(
            map(() => ({
                timestamp: Date.now(),
                // Random temperature between 20 and 40 degrees
                value: 20 + Math.random() * 20,
                label: 'Temperature (°C)'
            })),
            shareReplay(1)
        );
    }
}
