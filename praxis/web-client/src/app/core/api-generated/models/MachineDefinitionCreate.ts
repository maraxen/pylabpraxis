/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
/**
 * Schema for creating a MachineDefinition.
 */
export type MachineDefinitionCreate = {
    /**
     * The unique accession ID of the record.
     */
    accession_id?: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    updated_at?: (string | null);
    /**
     * An optional name for the record.
     */
    name: string;
    /**
     * Fully qualified name
     */
    fqn: string;
    /**
     * Description of the machine type
     */
    description?: (string | null);
    /**
     * PyLabRobot category
     */
    plr_category?: (string | null);
    /**
     * Category of the machine
     */
    machine_category?: MachineCategoryEnum;
    material?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    /**
     * Size in X dimension (mm)
     */
    size_x_mm?: (number | null);
    /**
     * Size in Y dimension (mm)
     */
    size_y_mm?: (number | null);
    /**
     * Size in Z dimension (mm)
     */
    size_z_mm?: (number | null);
    /**
     * Whether this machine has a deck
     */
    has_deck?: boolean;
    /**
     * PLR frontend class FQN
     */
    frontend_fqn?: (string | null);
};

