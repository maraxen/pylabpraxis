/**
 * Mock resources for browser mode
 * Must have resource_definition_accession_id that matches entries with plr_category
 */

// Resource definitions (what AssetSelector uses for filtering)
export const MOCK_RESOURCE_DEFINITIONS = [
    {
        accession_id: 'def-plate-001',
        name: 'Corning 96 Wellplate 360µL Flat',
        fqn: 'pylabrobot.resources.corning_costar.Corning_96_wellplate_360ul_Flat',
        plr_category: 'Plate',
        num_items: 96,
        plate_type: 'flat',
        is_consumable: true,
        default_count: null, // null = infinite
        is_reusable: true,   // can be washed and reused
        properties_json: { wells: 96, volume_ul: 360, brand: 'Corning' }
    },
    {
        accession_id: 'def-plate-002',
        name: 'Greiner 96 Wellplate U-bottom',
        fqn: 'pylabrobot.resources.greiner.Greiner_96_wellplate_U_bottom',
        plr_category: 'Plate',
        num_items: 96,
        plate_type: 'U-bottom',
        is_consumable: true,
        default_count: null,
        is_reusable: true,
        properties_json: { wells: 96, volume_ul: 340, brand: 'Greiner' }
    },
    {
        accession_id: 'def-tiprack-001',
        name: 'Opentrons 96 TipRack 300µL',
        fqn: 'pylabrobot.resources.opentrons.opentrons_96_tiprack_300ul',
        plr_category: 'TipRack',
        num_items: 96,
        tip_volume_ul: 300,
        is_consumable: true,
        default_count: 10,   // limited count
        is_reusable: false,  // tips are single-use
        properties_json: { tips: 96, volume_ul: 300, brand: 'Opentrons' }
    },
    {
        accession_id: 'def-tiprack-002',
        name: 'Opentrons 96 TipRack 20µL',
        fqn: 'pylabrobot.resources.opentrons.opentrons_96_tiprack_20ul',
        plr_category: 'TipRack',
        num_items: 96,
        tip_volume_ul: 20,
        is_consumable: true,
        default_count: null,
        is_reusable: false,
        properties_json: { tips: 96, volume_ul: 20, brand: 'Opentrons' }
    },
    {
        accession_id: 'def-reservoir-001',
        name: 'Agilent 1 Reservoir 290mL',
        fqn: 'pylabrobot.resources.agilent.Agilent_1_reservoir_290ml',
        plr_category: 'Reservoir',
        num_items: 1,
        is_consumable: false,  // reusable lab equipment
        default_count: null,
        is_reusable: true,
        properties_json: { wells: 1, volume_ml: 290, brand: 'Agilent' }
    },
    {
        accession_id: 'def-reservoir-002',
        name: 'Disposable Reagent Reservoir 50mL',
        fqn: 'pylabrobot.resources.generic.disposable_reservoir_50ml',
        plr_category: 'Reservoir',
        num_items: 1,
        is_consumable: true,   // disposable = consumable
        default_count: null,
        is_reusable: false,
        properties_json: { wells: 1, volume_ml: 50, type: 'disposable' }
    },
    {
        accession_id: 'def-carrier-001',
        name: 'Hamilton PLT_CAR_L5AC_A00',
        fqn: 'pylabrobot.resources.hamilton.PLT_CAR_L5AC_A00',
        plr_category: 'Carrier',
        num_items: 5,
        is_consumable: false,
        default_count: null,
        is_reusable: true,
        properties_json: { slots: 5, type: 'plate_carrier', brand: 'Hamilton' }
    },
    {
        accession_id: 'def-carrier-002',
        name: 'Hamilton TIP_CAR_480BC_A00',
        fqn: 'pylabrobot.resources.hamilton.TIP_CAR_480BC_A00',
        plr_category: 'Carrier',
        num_items: 5,
        is_consumable: false,
        default_count: null,
        is_reusable: true,
        properties_json: { slots: 5, type: 'tip_carrier', brand: 'Hamilton' }
    },
    {
        accession_id: 'def-carrier-003',
        name: 'Hamilton TIP_CAR_480BC_HT_A00',
        fqn: 'pylabrobot.resources.hamilton.TIP_CAR_480BC_HT_A00',
        plr_category: 'Carrier',
        num_items: 5,
        is_consumable: false,
        default_count: null,
        is_reusable: true,
        properties_json: { slots: 5, type: 'high_throughput_tip_carrier', brand: 'Hamilton' }
    },
    // Troughs for serial dilution protocol
    {
        accession_id: 'def-trough-001',
        name: 'Hamilton 8-Channel Trough 100mL',
        fqn: 'pylabrobot.resources.hamilton.Hamilton_8ch_trough_100ml',
        plr_category: 'Trough',
        num_items: 1,
        is_consumable: false,
        default_count: null,
        is_reusable: true,
        properties_json: { channels: 8, volume_ml: 100, brand: 'Hamilton' }
    },
    {
        accession_id: 'def-trough-002',
        name: 'Disposable Diluent Trough 200mL',
        fqn: 'pylabrobot.resources.generic.disposable_trough_200ml',
        plr_category: 'Trough',
        num_items: 1,
        is_consumable: true,
        default_count: null,
        is_reusable: false,
        properties_json: { channels: 1, volume_ml: 200, type: 'disposable' }
    }
];

// Resources (actual instances that reference definitions)
export const MOCK_RESOURCES = [
    {
        accession_id: 'res-001',
        name: 'Source Plate A',
        resource_definition_accession_id: 'def-plate-001',
        status: 'AVAILABLE',
        location: 'Deck Position 1',
        properties_json: {}
    },
    {
        accession_id: 'res-002',
        name: 'Destination Plate B',
        resource_definition_accession_id: 'def-plate-001',
        status: 'AVAILABLE',
        location: 'Deck Position 2',
        properties_json: {}
    },
    {
        accession_id: 'res-003',
        name: 'Assay Plate C',
        resource_definition_accession_id: 'def-plate-002',
        status: 'IN_USE',
        location: 'Deck Position 3',
        properties_json: {}
    },
    {
        accession_id: 'res-004',
        name: 'Tip Rack 300µL',
        resource_definition_accession_id: 'def-tiprack-001',
        status: 'AVAILABLE',
        location: 'Deck Position 4',
        properties_json: {}
    },
    {
        accession_id: 'res-005',
        name: 'Tip Rack 20µL',
        resource_definition_accession_id: 'def-tiprack-002',
        status: 'AVAILABLE',
        location: 'Deck Position 5',
        properties_json: {}
    },
    {
        accession_id: 'res-006',
        name: 'Wash Buffer Reservoir',
        resource_definition_accession_id: 'def-reservoir-001',
        status: 'AVAILABLE',
        location: 'Deck Position 6',
        properties_json: {}
    },
    {
        accession_id: 'res-007',
        name: 'Diluent Trough',
        resource_definition_accession_id: 'def-trough-001',
        status: 'AVAILABLE',
        location: 'Deck Position 7',
        properties_json: {}
    },
    {
        accession_id: 'res-008',
        name: 'Disposable Diluent Trough',
        resource_definition_accession_id: 'def-trough-002',
        status: 'AVAILABLE',
        location: 'Deck Position 8',
        properties_json: {}
    }
];
