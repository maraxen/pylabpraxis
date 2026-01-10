/**
 * Canonical PLR Category definitions.
 *
 * This is the SINGLE SOURCE OF TRUTH for PLR categories used throughout the frontend.
 * These map directly to the `category` attribute on PyLabRobot classes.
 *
 * IMPORTANT: This file is generated from praxis/backend/models/enums/plr_category.py
 * Keep these in sync! Any changes should be made to the Python source first.
 */

export enum PLRCategory {
  // Resource categories
  PLATE = 'Plate',
  TIP_RACK = 'TipRack',
  TROUGH = 'Trough',
  CARRIER = 'Carrier',
  TUBE = 'Tube',
  TUBE_RACK = 'TubeRack',
  CONTAINER = 'Container',
  LID = 'Lid',
  DECK = 'Deck',

  // Machine frontend categories
  LIQUID_HANDLER = 'LiquidHandler',
  PLATE_READER = 'PlateReader',
  HEATER_SHAKER = 'HeaterShaker',
  SHAKER = 'Shaker',
  TEMPERATURE_CONTROLLER = 'TemperatureController',
  CENTRIFUGE = 'Centrifuge',
  THERMOCYCLER = 'Thermocycler',
  PUMP = 'Pump',
  INCUBATOR = 'Incubator',

  // Machine backend categories (less common in asset requirements)
  LIQUID_HANDLER_BACKEND = 'LiquidHandlerBackend',
  PLATE_READER_BACKEND = 'PlateReaderBackend',
  HEATER_SHAKER_BACKEND = 'HeaterShakerBackend',
  SHAKER_BACKEND = 'ShakerBackend',
  TEMPERATURE_CONTROLLER_BACKEND = 'TemperatureControllerBackend',
  CENTRIFUGE_BACKEND = 'CentrifugeBackend',
  THERMOCYCLER_BACKEND = 'ThermocyclerBackend',
  PUMP_BACKEND = 'PumpBackend',
  INCUBATOR_BACKEND = 'IncubatorBackend',
}

export const RESOURCE_CATEGORIES: ReadonlySet<PLRCategory> = new Set([
  PLRCategory.PLATE,
  PLRCategory.TIP_RACK,
  PLRCategory.TROUGH,
  PLRCategory.CARRIER,
  PLRCategory.TUBE,
  PLRCategory.TUBE_RACK,
  PLRCategory.CONTAINER,
  PLRCategory.LID,
  PLRCategory.DECK,
]);

export const MACHINE_CATEGORIES: ReadonlySet<PLRCategory> = new Set([
  PLRCategory.LIQUID_HANDLER,
  PLRCategory.PLATE_READER,
  PLRCategory.HEATER_SHAKER,
  PLRCategory.SHAKER,
  PLRCategory.TEMPERATURE_CONTROLLER,
  PLRCategory.CENTRIFUGE,
  PLRCategory.THERMOCYCLER,
  PLRCategory.PUMP,
  PLRCategory.INCUBATOR,
]);

export const BACKEND_CATEGORIES: ReadonlySet<PLRCategory> = new Set([
  PLRCategory.LIQUID_HANDLER_BACKEND,
  PLRCategory.PLATE_READER_BACKEND,
  PLRCategory.HEATER_SHAKER_BACKEND,
  PLRCategory.SHAKER_BACKEND,
  PLRCategory.TEMPERATURE_CONTROLLER_BACKEND,
  PLRCategory.CENTRIFUGE_BACKEND,
  PLRCategory.THERMOCYCLER_BACKEND,
  PLRCategory.PUMP_BACKEND,
  PLRCategory.INCUBATOR_BACKEND,
]);

/**
 * Check if a category is a resource category.
 */
export function isResourceCategory(category: string): boolean {
  return RESOURCE_CATEGORIES.has(category as PLRCategory);
}

/**
 * Check if a category is a machine category.
 */
export function isMachineCategory(category: string): boolean {
  return MACHINE_CATEGORIES.has(category as PLRCategory);
}

/**
 * Check if a category is a backend category.
 */
export function isBackendCategory(category: string): boolean {
  return BACKEND_CATEGORIES.has(category as PLRCategory);
}
