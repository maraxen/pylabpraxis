/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TipStateSnapshot } from './TipStateSnapshot';
/**
 * Complete state snapshot at a point in time.
 */
export type StateSnapshot = {
    tips?: TipStateSnapshot;
    liquids?: Record<string, Record<string, number>>;
    on_deck?: Array<string>;
    raw_plr_state?: (Record<string, any> | null);
};

