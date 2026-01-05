/**
 * Asset Icon Definitions
 * 
 * Centralized mapping of resource and machine categories to Material Design icons
 * and custom SVG icons registered in CustomIconRegistryService.
 * Used throughout the application for consistency.
 */

export const RESOURCE_CATEGORY_ICONS: Record<string, string> = {
    // Plates
    'Plate': 'grid_view',
    'plate': 'grid_view',

    // Tips (Using Custom SVG)
    'TipRack': 'tip_rack_custom',
    'tip_rack': 'tip_rack_custom',

    // Liquid Containers
    'Reservoir': 'water_drop',
    'reservoir': 'water_drop',
    'Trough': 'waves',
    'trough': 'waves',

    // Tubes & Flasks (Using Custom SVG/Standard Material)
    'Tube': 'test_tube', // Custom Tube SVG
    'tube': 'test_tube',

    // Carriers & Structure
    'Carrier': 'table_rows', // Better represents linear tracks/carriers
    'carrier': 'table_rows',
    'Deck': 'view_quilt', // Represents a layout of items
    'Lid': 'vertical_align_top', // "On top"
    'lid': 'vertical_align_top',

    // Generic
    'Resource': 'category',
    'resource': 'category',
    'Other': 'category'
};

export const MACHINE_CATEGORY_ICONS: Record<string, string> = {
    'LiquidHandler': 'precision_manufacturing', // It's a robot
    'PlateReader': 'sensors', // Sensing/Reading
    'HeaterShaker': 'microwave', // Heat + Motion often implies this shape
    'Shaker': 'vibration',
    'Centrifuge': 'rotate_right',
    'Thermocycler': 'device_thermostat',
    'TemperatureController': 'thermostat',
    'Incubator': 'wb_sunny', // Warmth
    'Pump': 'water',
    'Fan': 'air',
    'Sealer': 'compress', // Pressing/Sealing
    'Peeler': 'layers_clear', // Removing a layer
    'PowderDispenser': 'grain',
    'Washer': 'local_laundry_service', // Clear metaphor
    'Dispenser': 'format_color_fill',
    'MagneticRack': 'vertical_align_bottom', // Pulls beads down
    'Other': 'smart_toy' // Generic machine
};

/**
 * Get icon for a resource category
 */
export function getResourceCategoryIcon(category: string): string {
    // Handle snake_case or specific variants by checking direct access first, then lower case
    if (RESOURCE_CATEGORY_ICONS[category]) {
        return RESOURCE_CATEGORY_ICONS[category];
    }
    const lower = category.toLowerCase();
    if (RESOURCE_CATEGORY_ICONS[lower]) {
        return RESOURCE_CATEGORY_ICONS[lower];
    }
    return 'category';
}

/**
 * Get icon for a machine category
 */
export function getMachineCategoryIcon(category: string): string {
    if (MACHINE_CATEGORY_ICONS[category]) {
        return MACHINE_CATEGORY_ICONS[category];
    }
    return 'smart_toy';
}
