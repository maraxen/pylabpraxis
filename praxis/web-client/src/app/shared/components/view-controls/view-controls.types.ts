export type ViewType = 'card' | 'list' | 'table' | 'accordion';

export interface SelectOption {
    label: string;
    value: any;
    icon?: string;
    count?: number;
    disabled?: boolean;
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
}

export type SortOption = SelectOption;

export interface ViewControlsState {
    viewType: ViewType;
    groupBy: string | null;
    filters: Record<string, any>;
    sortBy: string;
    sortOrder: 'asc' | 'desc';
    search: string;
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
}
