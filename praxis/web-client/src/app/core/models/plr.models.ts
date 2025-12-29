export interface PlrLocation {
    x: number;
    y: number;
    z: number;
    type?: string; // "Coordinate"
}

export interface PlrResource {
    name: string;
    type: string;
    location: PlrLocation;
    size_x: number;
    size_y: number;
    size_z: number;
    children: PlrResource[];
    color?: string; // Optional override
    // Specific to certain types
    num_rails?: number;
    num_items_x?: number;
    num_items_y?: number;
    max_volume?: number;
    volume?: number;
    cross_section_type?: string;
}

export interface PlrState {
    [resourceName: string]: any;
}

export interface PlrDeckData {
    resource: PlrResource;
    state: PlrState;
}
