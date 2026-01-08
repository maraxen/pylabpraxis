import { TestBed } from '@angular/core/testing';
import { FilterResultService, FilterOption } from './filter-result.service';

describe('FilterResultService', () => {
    let service: FilterResultService;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(FilterResultService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('computeOptionMetrics', () => {
        interface TestItem {
            category: string;
            value: number;
        }

        const testData: TestItem[] = [
            { category: 'A', value: 1 },
            { category: 'A', value: 2 },
            { category: 'B', value: 3 },
        ];

        const options: FilterOption[] = [
            { label: 'Cat A', value: 'A' },
            { label: 'Cat B', value: 'B' },
            { label: 'Cat C', value: 'C' },
        ];

        it('should compute counts and disabled status correctly', () => {
            const result = service.computeOptionMetrics(
                testData,
                (item, value) => item.category === value,
                options
            );

            expect(result.length).toBe(3);

            // Cat A: 2 matches
            expect(result[0].count).toBe(2);
            expect(result[0].disabled).toBe(false);

            // Cat B: 1 match
            expect(result[1].count).toBe(1);
            expect(result[1].disabled).toBe(false);

            // Cat C: 0 matches
            expect(result[2].count).toBe(0);
            expect(result[2].disabled).toBe(true);
        });

        it('should handle multi-select metrics (delta counting placeholder logic)', () => {
            const result = service.computeOptionMetrics(
                testData,
                (item, value) => item.category === value,
                options,
                ['A'],
                true
            );

            expect(result[0].count).toBe(2);
            expect(result[1].count).toBe(1);
            expect(result[2].count).toBe(0);
        });
    });
});
