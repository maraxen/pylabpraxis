/**
 * Resource Category and Property Tooltips
 *
 * Provides explanatory tooltips for resource-related chips and badges
 * throughout the application.
 */

export const CATEGORY_TOOLTIPS: Record<string, string> = {
    'Plate': 'Microplates with wells for holding samples. Available in 96, 384, or 1536-well formats.',
    'TipRack': 'Disposable pipette tips organized in a rack. Tips are consumed during liquid handling.',
    'Reservoir': 'Single or multi-channel containers for reagents. Typically used for buffers and wash solutions.',
    'Carrier': 'Deck-mounted holders that organize plates, tips, or other labware in fixed positions.',
    'Trough': 'Open containers for bulk liquids. Similar to reservoirs but often larger capacity.',
    'Tube': 'Individual sample tubes (Eppendorf, Falcon, etc.) for storing samples or reagents.',
    'Deck': 'The working surface of a liquid handler where all labware is positioned.',
    'Resource': 'Generic labware item that doesn\'t fit other categories.',
    'Other': 'Miscellaneous labware or equipment.',
};

export const PROPERTY_TOOLTIPS: Record<string, string> = {
    'consumable': 'Items that are used up during protocols. Consumables have a quantity that decreases as they are used (e.g., tips, reagents).',
    'reusable': 'Items that can be washed and used multiple times. Plates and carriers are typically reusable.',
    'top-level': 'Items that sit directly on the deck surface. Non-top-level items are nested inside carriers or other containers.',
    'needs-processing': 'Items that require additional processing before use (e.g., thawing, mixing, or preparation).',
    'infinite': 'Effectively unlimited quantity. The system will not track depletion for this item.',
    'low-stock': 'Quantity is running low. Consider restocking before the next protocol run.',
    'depleted': 'Item has been fully consumed and is no longer available for use.',
    'expired': 'Item has passed its expiration date and should not be used.',
};

export const STATUS_TOOLTIPS: Record<string, string> = {
    'available': 'Ready for use in protocols.',
    'in_use': 'Currently being used by an active protocol run.',
    'busy': 'Reserved for an upcoming operation.',
    'error': 'An error occurred with this item. Check status details.',
    'maintenance': 'Item is undergoing maintenance or calibration.',
};

export const MACHINE_CATEGORY_TOOLTIPS: Record<string, string> = {
    'LiquidHandler': 'Automated pipetting system for precise liquid transfers between containers.',
    'PlateReader': 'Instrument for measuring optical properties (absorbance, fluorescence, luminescence) of samples in plates.',
    'Shaker': 'Device for mixing or agitating plates and containers.',
    'Centrifuge': 'Instrument for separating components by spinning samples at high speed.',
    'Incubator': 'Temperature-controlled chamber for growing cells or running reactions.',
    'Washer': 'Automated plate washer for removing liquids and washing wells.',
    'Dispenser': 'Bulk reagent dispenser for rapid filling of plates.',
    'Sealer': 'Device for applying adhesive seals or heat seals to plates.',
    'Other': 'General laboratory equipment.',
};

/**
 * Get tooltip for a category
 */
export function getCategoryTooltip(category: string): string {
    return CATEGORY_TOOLTIPS[category] || `${category} labware`;
}

/**
 * Get tooltip for a property chip
 */
export function getPropertyTooltip(property: string): string {
    return PROPERTY_TOOLTIPS[property.toLowerCase()] || property;
}

/**
 * Get tooltip for a machine category
 */
export function getMachineCategoryTooltip(category: string): string {
    return MACHINE_CATEGORY_TOOLTIPS[category] || `${category} equipment`;
}
