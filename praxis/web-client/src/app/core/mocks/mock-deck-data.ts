export const MOCK_DECK_DATA = {
    resource: {
        name: "deck",
        type: "HamiltonSTARDeck",
        location: { x: 0, y: 0, z: 0, type: "Coordinate" },
        size_x: 1200,
        size_y: 600,
        size_z: 100,
        children: [
            {
                name: "plate_1",
                type: "Plate",
                location: { x: 100, y: 100, z: 0, type: "Coordinate" },
                size_x: 127.76,
                size_y: 85.48,
                size_z: 14.5,
                num_items_x: 12,
                num_items_y: 8,
                children: [] // Wells would go here, simplified for now
            },
            {
                name: "tip_rack_1",
                type: "TipRack",
                location: { x: 300, y: 100, z: 0, type: "Coordinate" },
                size_x: 127.76,
                size_y: 85.48,
                size_z: 60,
                num_items_x: 12,
                num_items_y: 8,
                children: []
            }
        ],
        num_rails: 30
    },
    state: {}
};

// Generates wells for a plate to make it look realistic
function generateWells(plateName: string, startX: number, startY: number) {
    const wells = [];
    const wellSpacing = 9.0;
    const wellSize = 7.0;
    for (let i = 0; i < 12; i++) {
        for (let j = 0; j < 8; j++) {
            wells.push({
                name: `${plateName}_well_${i}_${j}`,
                type: "Well",
                location: {
                    x: 14 + i * wellSpacing,
                    y: 11 + j * wellSpacing,
                    z: 0,
                    type: "Coordinate"
                },
                size_x: wellSize,
                size_y: wellSize,
                size_z: 10,
                max_volume: 300,
                volume: 0,
                cross_section_type: "circle",
                children: []
            });
        }
    }
    return wells;
}

// Populate children
MOCK_DECK_DATA.resource.children[0].children = generateWells("plate_1", 100, 100) as any;
