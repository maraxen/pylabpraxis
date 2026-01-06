import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface FilterOption {
    label: string;
    value: any;
    count?: number;
    disabled?: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class FilterResultService {

    /**
     * Computes availability of options based on current data and other applied filters
     * This is a utility method that components can use
     */
    computeOptionAvailability<T>(
        allData: T[],
        filterFn: (item: T, value: any) => boolean,
        options: FilterOption[]
    ): FilterOption[] {
        return options.map(option => {
            const MATCH_COUNT = allData.filter(item => filterFn(item, option.value)).length;
            return {
                ...option,
                count: MATCH_COUNT,
                disabled: MATCH_COUNT === 0
            };
        });
    }
}
