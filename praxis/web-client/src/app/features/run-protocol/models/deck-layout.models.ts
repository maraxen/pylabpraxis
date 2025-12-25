export interface DeckResource {
    name: string;
    type: 'plate' | 'tip_rack' | 'other';
    color?: string;
    category?: string;
}

export interface DeckSlot {
    id: string;
    x: number;
    y: number;
    width: number;
    height: number;
    resource?: DeckResource;
}

export interface DeckLayout {
    width: number;
    height: number;
    slots: DeckSlot[];
}
