export interface TransferLog {
    accession_id: string;
    run_accession_id: string;
    timestamp: string;
    well: string;
    volume_transferred: number;
    cumulative_volume: number;
    temperature?: number;
    pressure?: number;
}

export class SeededRandom {
    private seed: number;

    constructor(seed: number) {
        this.seed = seed;
    }

    next(): number {
        const x = Math.sin(this.seed++) * 10000;
        return x - Math.floor(x);
    }

    range(min: number, max: number): number {
        return min + this.next() * (max - min);
    }

    // Gaussian-ish distribution using Box-Muller transform
    gaussian(mean: number, std: number): number {
        const u1 = this.next() || 0.0001; // Avoid 0
        const u2 = this.next() || 0.0001;
        const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
        return z * std + mean;
    }
}

export interface ProtocolProfile {
    name: string;
    wellCount: number;
    volumeRange: [number, number];
    pointsPerWell: [number, number];
    tempMean: number;
    tempStd: number;
    pressureMean: number;
    pressureStd: number;
    isStepWise?: boolean;
}

const PROFILES: Record<string, ProtocolProfile> = {
    'PCR Prep': {
        name: 'PCR Prep',
        wellCount: 96,
        volumeRange: [10, 50],
        pointsPerWell: [10, 20],
        tempMean: 4.0,
        tempStd: 0.5,
        pressureMean: 101.3,
        pressureStd: 0.1,
        isStepWise: true
    },
    'Cell Culture Feed': {
        name: 'Cell Culture Feed',
        wellCount: 24,
        volumeRange: [100, 250],
        pointsPerWell: [5, 12],
        tempMean: 37.0,
        tempStd: 0.2,
        pressureMean: 101.3,
        pressureStd: 0.05,
        isStepWise: true
    },
    'Daily Maintenance': {
        name: 'Daily Maintenance',
        wellCount: 12,
        volumeRange: [50, 100],
        pointsPerWell: [20, 40],
        tempMean: 22.0,
        tempStd: 1.0,
        pressureMean: 101.0,
        pressureStd: 0.5,
        isStepWise: false
    }
};

export class MockDataGenerator {
    static generateForRun(runId: string, protocolName: string, startTime: Date): TransferLog[] {
        const profile = this.getProfile(protocolName);
        const seed = this.hashCode(runId + protocolName);
        const rng = new SeededRandom(seed);
        const logs: TransferLog[] = [];

        const wells = this.generateWellList(profile.wellCount);

        wells.forEach(well => {
            let cumulative = 0;
            const numPoints = Math.floor(rng.range(profile.pointsPerWell[0], profile.pointsPerWell[1]));

            for (let i = 0; i < numPoints; i++) {
                const volume = rng.range(profile.volumeRange[0], profile.volumeRange[1]);
                cumulative += volume;

                // Organic temperature: some noise + slight drift or stability
                const temperature = rng.gaussian(profile.tempMean, profile.tempStd);
                const pressure = rng.gaussian(profile.pressureMean, profile.pressureStd);

                // Space points out by 1-5 minutes
                const timeOffset = i * rng.range(1, 5) * 60 * 1000;
                const timestamp = new Date(startTime.getTime() + timeOffset);

                logs.push({
                    accession_id: `log-${runId.slice(0, 4)}-${well}-${i}`,
                    run_accession_id: runId,
                    timestamp: timestamp.toISOString(),
                    well,
                    volume_transferred: Math.round(volume * 10) / 10,
                    cumulative_volume: Math.round(cumulative * 10) / 10,
                    temperature: Math.round(temperature * 100) / 100,
                    pressure: Math.round(pressure * 100) / 100
                });
            }
        });

        return logs;
    }

    private static getProfile(name: string): ProtocolProfile {
        if (name.includes('PCR')) return PROFILES['PCR Prep'];
        if (name.includes('Feed') || name.includes('Culture') || name.includes('Dilution')) return PROFILES['Cell Culture Feed'];
        return PROFILES['Daily Maintenance'];
    }

    private static generateWellList(count: number): string[] {
        const wells: string[] = [];
        const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
        const cols = 12;

        for (let i = 0; i < count; i++) {
            const rowIdx = Math.floor(i / cols);
            const colIdx = (i % cols) + 1;
            if (rowIdx < rows.length) {
                wells.push(`${rows[rowIdx]}${colIdx}`);
            }
        }
        return wells;
    }

    private static hashCode(str: string): number {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash);
    }
}
