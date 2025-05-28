import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/features/assetManagement/application/bloc/asset_management_bloc.dart';
import 'package:praxis_lab_management/src/data/services/asset_api_service.dart';
import 'package:praxis_data/praxis_data.dart'; // For ORM models

// Assuming mock_services.mocks.dart is generated in praxis/frontend/test/mocks/
import '../../../../mocks/mock_services.mocks.dart';

void main() {
  late MockAssetApiService mockAssetApiService;

  setUp(() {
    mockAssetApiService = MockAssetApiService();
  });

  group('AssetManagementBloc', () {
    final device1 = ManagedDeviceOrm(id: 'device1', name: 'Device 1');
    final labwareDef1 = LabwareDefinitionCatalogOrm(
      id: 'lwDef1',
      name: 'Labware Def 1',
    );
    final labwareInstance1 = LabwareInstanceOrm(
      id: 'lwInstance1',
      labwareDefinitionId: 'lwDef1',
    );
    final deckLayout1 = DeckLayoutOrm(id: 'deck1', name: 'Deck 1');

    final List<ManagedDeviceOrm> mockDevices = [device1];
    final List<LabwareDefinitionCatalogOrm> mockLabwareDefinitions = [
      labwareDef1,
    ];
    final List<LabwareInstanceOrm> mockLabwareInstances = [labwareInstance1];
    final List<DeckLayoutOrm> mockDeckLayouts = [deckLayout1];

    test('initial state is AssetManagementInitial', () {
      expect(
        AssetManagementBloc(mockAssetApiService).state,
        const AssetManagementInitial(),
      );
    });

    group('AssetManagementLoadStarted', () {
      blocTest<AssetManagementBloc, AssetManagementState>(
        'emits [AssetManagementLoadInProgress, AssetManagementLoadSuccess] when AssetApiService returns data successfully',
        build: () {
          when(
            mockAssetApiService.getDevices(),
          ).thenAnswer((_) async => mockDevices);
          when(
            mockAssetApiService.getLabwareDefinitions(),
          ).thenAnswer((_) async => mockLabwareDefinitions);
          when(
            mockAssetApiService.getLabwareInstances(),
          ).thenAnswer((_) async => mockLabwareInstances);
          when(
            mockAssetApiService.getDeckLayouts(),
          ).thenAnswer((_) async => mockDeckLayouts);
          return AssetManagementBloc(mockAssetApiService);
        },
        act: (bloc) => bloc.add(const AssetManagementLoadStarted()),
        expect:
            () => [
              const AssetManagementLoadInProgress(),
              AssetManagementLoadSuccess(
                devices: mockDevices,
                labwareDefinitions: mockLabwareDefinitions,
                labwareInstances: mockLabwareInstances,
                deckLayouts: mockDeckLayouts,
              ),
            ],
        verify: (_) {
          verify(mockAssetApiService.getDevices()).called(1);
          verify(mockAssetApiService.getLabwareDefinitions()).called(1);
          verify(mockAssetApiService.getLabwareInstances()).called(1);
          verify(mockAssetApiService.getDeckLayouts()).called(1);
        },
      );

      blocTest<AssetManagementBloc, AssetManagementState>(
        'emits [AssetManagementLoadInProgress, AssetManagementLoadFailure] when AssetApiService.getDevices throws an exception',
        build: () {
          when(
            mockAssetApiService.getDevices(),
          ).thenThrow(Exception('Failed to fetch devices'));
          // Mock other calls if they would happen before the failing one
          when(
            mockAssetApiService.getLabwareDefinitions(),
          ).thenAnswer((_) async => mockLabwareDefinitions);
          when(
            mockAssetApiService.getLabwareInstances(),
          ).thenAnswer((_) async => mockLabwareInstances);
          when(
            mockAssetApiService.getDeckLayouts(),
          ).thenAnswer((_) async => mockDeckLayouts);
          return AssetManagementBloc(mockAssetApiService);
        },
        act: (bloc) => bloc.add(const AssetManagementLoadStarted()),
        expect:
            () => [
              const AssetManagementLoadInProgress(),
              isA<AssetManagementLoadFailure>().having(
                (s) => s.error,
                'error',
                'Exception: Failed to fetch devices',
              ),
            ],
        verify: (_) {
          verify(mockAssetApiService.getDevices()).called(1);
          // Other calls might not happen if getDevices fails early and the bloc doesn't catch individually
        },
      );
    });

    group('AddDeviceStarted', () {
      final newDevice = ManagedDeviceOrm(id: 'newDevice', name: 'New Device');
      blocTest<AssetManagementBloc, AssetManagementState>(
        'emits [AssetManagementUpdateInProgress, AssetManagementUpdateSuccess, AssetManagementLoadInProgress, AssetManagementLoadSuccess] when createDevice is successful',
        build: () {
          when(
            mockAssetApiService.createDevice(any),
          ).thenAnswer((_) async => newDevice);
          // For the subsequent load
          when(
            mockAssetApiService.getDevices(),
          ).thenAnswer((_) async => [newDevice]); // Assume it's now in the list
          when(
            mockAssetApiService.getLabwareDefinitions(),
          ).thenAnswer((_) async => mockLabwareDefinitions);
          when(
            mockAssetApiService.getLabwareInstances(),
          ).thenAnswer((_) async => mockLabwareInstances);
          when(
            mockAssetApiService.getDeckLayouts(),
          ).thenAnswer((_) async => mockDeckLayouts);
          return AssetManagementBloc(mockAssetApiService);
        },
        act: (bloc) => bloc.add(AddDeviceStarted(newDevice)),
        expect:
            () => [
              const AssetManagementUpdateInProgress(),
              const AssetManagementUpdateSuccess(),
              const AssetManagementLoadInProgress(), // Due to add(AssetManagementLoadStarted())
              AssetManagementLoadSuccess(
                devices: [newDevice],
                labwareDefinitions: mockLabwareDefinitions,
                labwareInstances: mockLabwareInstances,
                deckLayouts: mockDeckLayouts,
              ),
            ],
        verify: (_) {
          verify(mockAssetApiService.createDevice(newDevice)).called(1);
          verify(mockAssetApiService.getDevices()).called(1); // From the reload
        },
      );

      blocTest<AssetManagementBloc, AssetManagementState>(
        'emits [AssetManagementUpdateInProgress, AssetManagementUpdateFailure] when createDevice throws an exception',
        build: () {
          when(
            mockAssetApiService.createDevice(any),
          ).thenThrow(Exception('Failed to create device'));
          return AssetManagementBloc(mockAssetApiService);
        },
        act: (bloc) => bloc.add(AddDeviceStarted(newDevice)),
        expect:
            () => [
              const AssetManagementUpdateInProgress(),
              isA<AssetManagementUpdateFailure>().having(
                (s) => s.error,
                'error',
                'Exception: Failed to create device',
              ),
            ],
        verify: (_) {
          verify(mockAssetApiService.createDevice(newDevice)).called(1);
        },
      );
    });
    // TODO(user): Add similar tests for other modification events (Update, Delete for each asset type)
  });
}
