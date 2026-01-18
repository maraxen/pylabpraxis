/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Type of machine backend implementation.
 *
 * Used to distinguish between different types of backends:
 * - REAL_HARDWARE: Connects to a physical device
 * - SIMULATOR: PLR visualizer/simulator
 * - CHATTERBOX: Print-only, no hardware connection
 * - MOCK: For testing purposes only
 */
export type BackendTypeEnum = 'real_hardware' | 'simulator' | 'chatterbox' | 'mock';
