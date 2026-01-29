export type ViewType = 'card' | 'list' | 'table' | 'accordion';

export interface SelectOption {
    label: string;
    value: any;
    icon?: string;
    count?: number;
    disabled?: boolean;
}

export interface ActiveFilter<T = unknown> {
    filterId: string;
    label: string;
    values: T[];
    displayText: string;
}

export type FilterOption = SelectOption;

export interface FilterConfig {
    key: string;
    label: string;
    /** 
     * Filter type. 
     * Note: 'chips' is deprecated and will be mapped to 'multiselect'
     */
    type: 'multiselect' | 'select' | 'toggle' | 'chips';

    options?: FilterOption[];
    allowInvert?: boolean;
    defaultValue?: any;
    icon?: string;           // NEW: Icon for the filter chip
    pinned?: boolean;        // NEW: If true, show inline in bar (not in "+ Add Filter")
    urlParam?: string;       // NEW: Override URL param name (defaults to key)
}

export type SortOption = SelectOption;

export interface ViewControlsState {
    viewType: ViewType;
    groupBy: string | null;
    filters: Record<string, any[]>; // Standardized to any[]
    sortBy: string;
    sortOrder: 'asc' | 'desc';
    search: string;
    resultCount?: number;   // NEW: Current matching item count
}

export interface ViewControlsConfig {
    // Available view types (default: all)
    viewTypes?: ViewType[];

    // Available group-by options
    groupByOptions?: SelectOption[];

    // Available filter configurations
    filters?: FilterConfig[];

    // Available sort options
    sortOptions?: SortOption[];

    // localStorage key for persistence
    storageKey?: string;

    // Initial values
    defaults?: Partial<ViewControlsState>;

    enableUrlSync?: boolean;          // NEW: Sync state to URL query params
    urlParamPrefix?: string;          // NEW: Prefix for URL params (e.g., "filter_")
    showResultCount?: boolean;        // NEW: Display matching item count
    collapseMobileAt?: number;        // NEW: Breakpoint for mobile collapse (default: 768)
}
