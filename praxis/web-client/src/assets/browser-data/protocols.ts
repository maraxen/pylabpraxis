/**
 * Mock protocol definitions for browser mode
 * Format matches ProtocolDefinition interface from protocol.models.ts
 */
export const MOCK_PROTOCOLS = [
    {
        accession_id: '11111111-1111-1111-1111-111111111111',
        name: 'PCR Prep (96-well)',
        description: 'Transfers master mix and primers to a 96-well plate for PCR amplification.',
        version: '1.0.0',
        is_top_level: true,
        category: 'Molecular Biology',
        source_file_path: 'praxis/protocol/protocols/pcr_prep.py',
        module_name: 'praxis.protocol.protocols.pcr_prep',
        function_name: 'run_pcr_prep',
        fqn: 'praxis.protocol.protocols.pcr_prep.run_pcr_prep',
        tags: ['pcr', 'molecular-biology', '96-well'],
        deprecated: false,
        parameters: [
            {
                name: 'volume_ul',
                type_hint: 'float',
                fqn: 'builtins.float',
                is_deck_param: false,
                optional: false,
                default_value_repr: '25.0',
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
        name: 'Cell Culture Feed (24-well)',
        description: 'Aspirates old media and adds fresh growth media to a 24-well cell culture plate.',
        version: '1.0.0',
        is_top_level: true,
        category: 'Cell Culture',
        source_file_path: 'praxis/protocol/protocols/cell_feed.py',
        module_name: 'praxis.protocol.protocols.cell_feed',
        function_name: 'cell_culture_feed',
        fqn: 'praxis.protocol.protocols.cell_feed.cell_culture_feed',
        tags: ['cell-culture', 'maintenance', '24-well'],
        deprecated: false,
        parameters: [
            {
                name: 'media_volume_ul',
                type_hint: 'float',
                fqn: 'builtins.float',
                is_deck_param: false,
                optional: true,
                default_value_repr: '500.0',
                description: 'Volume of fresh media per well',
                constraints: { min_value: 100, max_value: 2000 },
            }
        ],
        assets: [
            {
                accession_id: 'asset-sd-plate',
                name: 'plate',
                fqn: 'pylabrobot.resources.Plate',
                type_hint_str: 'pylabrobot.resources.Plate',
                optional: false,
                description: 'Plate for cell culture',
                constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} },
                location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] }
            }
        ]
    },
    {
        accession_id: '33333333-3333-3333-3333-333333333333',
        name: 'Daily System Maintenance',
        description: 'Standard maintenance protocol including tip-seal check and system priming.',
        version: '2.0.1',
        is_top_level: true,
        category: 'Maintenance',
        source_file_path: 'praxis/protocol/protocols/maintenance.py',
        module_name: 'praxis.protocol.protocols.maintenance',
        function_name: 'run_maintenance',
        fqn: 'praxis.protocol.protocols.maintenance.run_maintenance',
        tags: ['maintenance', 'calibration'],
        deprecated: false,
        parameters: [
            {
                name: 'wash_cycles',
                type_hint: 'int',
                fqn: 'builtins.int',
                is_deck_param: false,
                optional: true,
                default_value_repr: '2',
                description: 'Number of wash cycles',
                constraints: { min_value: 1, max_value: 5 },
            }
        ],
        assets: []
    }
];
