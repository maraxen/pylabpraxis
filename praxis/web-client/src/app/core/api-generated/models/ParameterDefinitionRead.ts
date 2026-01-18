/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for reading a ParameterDefinition.
 */
export type ParameterDefinitionRead = {
    accession_id: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    updated_at?: (string | null);
    /**
     * The name of the parameter
     */
    name?: string;
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * The type hint of the parameter
     */
    type_hint?: string;
    /**
     * The fully qualified name of the parameter
     */
    fqn?: string;
    is_deck_param?: boolean;
    /**
     * Whether the parameter is optional
     */
    optional?: boolean;
    /**
     * String representation of default value
     */
    default_value_repr?: (string | null);
    /**
     * Description of the parameter
     */
    description?: (string | null);
    field_type?: (string | null);
    is_itemized?: boolean;
    linked_to?: (string | null);
};

