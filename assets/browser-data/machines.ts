/**
 * Mock machines for browser mode
 */
export const MOCK_MACHINES = [
    {
        accession_id: 'machine-def-sim-lh',
        name: 'Simulated Liquid Handler',
        fqn: 'praxis.simulated.LiquidHandler',
        type: 'liquid_handler',
        category: 'LiquidHandler',
        status: 'AVAILABLE',
        description: 'Generic Simulated Liquid Handler',
        frontend_fqn: 'pylabrobot.liquid_handling.LiquidHandler',
        is_simulated_frontend: true,
        available_simulation_backends: [
            'pylabrobot.liquid_handling.backends.simulation.simulator.SimulatorBackend',
            'pylabrobot.liquid_handling.backends.chatterbox.ChatterBoxBackend'
        ],
        connection_info: {
            backend: 'simulation'
        },
        properties_json: {
            channels: 8,
            deck_positions: 12,
            brand: 'Generic'
        }
    },
    {
        accession_id: 'machine-001',
        name: 'Hamilton STAR (Simulated)',
        fqn: 'pylabrobot.machines.hamilton.STAR',
        type: 'liquid_handler',
        category: 'LiquidHandler',
        status: 'AVAILABLE',
        description: 'Hamilton STAR Liquid Handler - 8 channels',
        frontend_fqn: 'pylabrobot.liquid_handling.LiquidHandler',
        connection_info: {
            backend: 'simulation',
            serial_port: null
        },
        properties_json: {
            channels: 8,
            deck_positions: 10,
            volume_range_ul: [0.5, 1000],
            brand: 'Hamilton'
        }
    },
    {
        accession_id: 'machine-002',
        name: 'Simulated Opentrons OT-2',
        fqn: 'pylabrobot.machines.opentrons.OT2',
        type: 'liquid_handler',
        category: 'LiquidHandler',
        status: 'IN_USE',
        description: 'Opentrons OT-2 Personal Pipetting Robot',
        connection_info: {
            backend: 'simulation',
            ip_address: '192.168.1.100'
        },
        properties_json: {
            channels: 8,
            deck_positions: 11,
            volume_range_ul: [1, 300],
            brand: 'Opentrons'
        }
    },
    {
        accession_id: 'machine-003',
        name: 'Simulated BioTek ELx405',
        fqn: 'pylabrobot.machines.biotek.ELx405',
        type: 'plate_washer',
        category: 'PlateWasher',
        status: 'AVAILABLE',
        description: 'BioTek ELx405 Microplate Washer',
        connection_info: {
            backend: 'simulation'
        },
        properties_json: {
            wash_channels: 8,
            dispense_volume_range: [25, 3000],
            brand: 'BioTek'
        }
    },
    {
        accession_id: 'machine-004',
        name: 'Simulated Tecan Infinite 200',
        fqn: 'pylabrobot.machines.tecan.Infinite200',
        type: 'plate_reader',
        category: 'PlateReader',
        status: 'AVAILABLE',
        description: 'Tecan Infinite 200 PRO Microplate Reader',
        connection_info: {
            backend: 'simulation'
        },
        properties_json: {
            detection_modes: ['absorbance', 'fluorescence', 'luminescence'],
            wavelength_range: [230, 1000],
            brand: 'Tecan'
        }
    }
];
