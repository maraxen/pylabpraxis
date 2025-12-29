import { Injectable } from '@angular/core';
import { Observable, interval } from 'rxjs';
import { map } from 'rxjs/operators';

export interface TelemetryData {
  timestamp: Date;
  value: number;
  unit: string;
}

@Injectable({
  providedIn: 'root'
})
export class MockTelemetryService {
  private telemetryData$: Observable<TelemetryData>;

  constructor() {
    this.telemetryData$ = interval(1000).pipe(
      map(() => {
        return {
          timestamp: new Date(),
          value: Math.random() * 100,
          unit: 'C'
        };
      })
    );
  }

  getTelemetryData(): Observable<TelemetryData> {
    return this.telemetryData$;
  }
}
