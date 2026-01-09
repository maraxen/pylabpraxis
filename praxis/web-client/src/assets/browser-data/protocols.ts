/**
 * Mock protocol definitions for browser mode
 * Format matches ProtocolDefinition interface from protocol.models.ts
 */
export const MOCK_PROTOCOLS = [
    {
        accession_id: '11111111-1111-1111-1111-111111111111',
        name: 'Simple Liquid Transfer',
        description: 'Transfers liquid from a source plate to a destination plate using a liquid handler.',
        version: '1.0.0',
        is_top_level: true,
        category: 'Liquid Handling',
        source_file_path: 'praxis/protocol/protocols/simple_transfer.py',
        module_name: 'praxis.protocol.protocols.simple_transfer',
        function_name: 'run_simple_transfer',
        fqn: 'praxis.protocol.protocols.simple_transfer.run_simple_transfer',
        tags: ['liquid-handling', 'basic'],
        deprecated: false,
        parameters: [
            {
                name: 'volume_ul',
                type_hint: 'float',
                fqn: 'builtins.float',
                is_deck_param: false,
                optional: false,
                default_value_repr: '100.0',
                description: 'Volume to transfer in microliters',
                constraints: { min_value: 1, max_value: 1000 },
            }
        ],
        assets: [
            {
                accession_id: 'asset-1',
                name: 'source_plate',
                fqn: 'pylabrobot.resources.Plate',
                type_hint_str: 'pylabrobot.resources.Plate',
                optional: false,
                description: 'Source plate containing liquid to transfer',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            },
            {
                accession_id: 'asset-2',
                name: 'destination_plate',
                fqn: 'pylabrobot.resources.Plate',
                type_hint_str: 'pylabrobot.resources.Plate',
                optional: false,
                description: 'Destination plate to receive liquid',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            }
        ]
    },
    {
        accession_id: '22222222-2222-2222-2222-222222222222',
        name: 'Serial Dilution',
        description: 'Performs a serial dilution across columns of a 96-well plate. Adds diluent to all wells, then transfers sample serially.',
        version: '1.0.0',
        is_top_level: true,
        category: 'Assay Prep',
        source_file_path: 'praxis/protocol/protocols/serial_dilution.py',
        module_name: 'praxis.protocol.protocols.serial_dilution',
        function_name: 'serial_dilution',
        fqn: 'praxis.protocol.protocols.serial_dilution.serial_dilution',
        tags: ['browser-mode', 'dilution', 'assay'],
        deprecated: false,
        parameters: [
            {
                name: 'start_row',
                type_hint: 'str',
                fqn: 'builtins.str',
                is_deck_param: false,
                optional: true,
                default_value_repr: "'A'",
                description: 'Starting row letter (A-H)',
                constraints: {},
            },
            {
                name: 'num_dilutions',
                type_hint: 'int',
                fqn: 'builtins.int',
                is_deck_param: false,
                optional: true,
                default_value_repr: '8',
                description: 'Number of dilution steps',
                constraints: { min_value: 1, max_value: 12 },
            },
            {
                name: 'sample_volume_ul',
                type_hint: 'float',
                fqn: 'builtins.float',
                is_deck_param: false,
                optional: true,
                default_value_repr: '100.0',
                description: 'Volume of sample to transfer between wells',
                constraints: { min_value: 1, max_value: 1000 },
            },
            {
                name: 'diluent_volume_ul',
                type_hint: 'float',
                fqn: 'builtins.float',
                is_deck_param: false,
                optional: true,
                default_value_repr: '100.0',
                description: 'Volume of diluent to add to each well',
                constraints: { min_value: 1, max_value: 1000 },
            },
            {
                name: 'dilution_factor',
                type_hint: 'float',
                fqn: 'builtins.float',
                is_deck_param: false,
                optional: true,
                default_value_repr: '2.0',
                description: 'Dilution factor per step (e.g., 2 for 1:2 dilution)',
                constraints: { min_value: 1.1, max_value: 10 },
            }
        ],
        assets: [
            {
                accession_id: 'asset-sd-plate',
                name: 'plate',
                fqn: 'pylabrobot.resources.Plate',
                type_hint_str: 'pylabrobot.resources.Plate',
                optional: false,
                description: 'Plate for serial dilution',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            },
            {
                accession_id: 'asset-sd-tiprack',
                name: 'tip_rack',
                fqn: 'pylabrobot.resources.TipRack',
                type_hint_str: 'pylabrobot.resources.TipRack',
                optional: false,
                description: 'Tip rack for liquid handling',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            },
            {
                accession_id: 'asset-sd-trough',
                name: 'diluent_trough',
                fqn: 'pylabrobot.resources.Trough',
                type_hint_str: 'pylabrobot.resources.Trough',
                optional: false,
                description: 'Trough containing diluent',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            }
        ]
    },
    {
        accession_id: '33333333-3333-3333-3333-333333333333',
        name: 'Plate Preparation',
        description: 'Prepares a 96-well plate with reagents for an assay, including washing and priming steps.',
        version: '2.0.1',
        is_top_level: true,
        category: 'Assay Prep',
        source_file_path: 'praxis/protocol/protocols/plate_preparation.py',
        module_name: 'praxis.protocol.protocols.plate_preparation',
        function_name: 'run_plate_preparation',
        fqn: 'praxis.protocol.protocols.plate_preparation.run_plate_preparation',
        tags: ['plate-prep', 'assay', 'washing'],
        deprecated: false,
        parameters: [
            {
                name: 'wash_cycles',
                type_hint: 'int',
                fqn: 'builtins.int',
                is_deck_param: false,
                optional: true,
                default_value_repr: '3',
                description: 'Number of wash cycles',
                constraints: { min_value: 1, max_value: 10 },
            }
        ],
        assets: [
            {
                accession_id: 'asset-4',
                name: 'assay_plate',
                fqn: 'pylabrobot.resources.Plate',
                type_hint_str: 'pylabrobot.resources.Plate',
                optional: false,
                description: 'Target assay plate',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            },
            {
                accession_id: 'asset-5',
                name: 'wash_buffer',
                fqn: 'pylabrobot.resources.Reservoir',
                type_hint_str: 'pylabrobot.resources.Reservoir',
                optional: false,
                description: 'Wash buffer reservoir',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            },
            {
                accession_id: 'asset-6',
                name: 'reagent',
                fqn: 'pylabrobot.resources.Reservoir',
                type_hint_str: 'pylabrobot.resources.Reservoir',
                optional: false,
                description: 'Primary reagent reservoir',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            }
        ]
    }
];
