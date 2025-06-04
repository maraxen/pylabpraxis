import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/features/assetManagement/application/bloc/asset_management_bloc.dart';
import 'package:praxis_lab_management/src/data/models/managed_machine_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_definition_catalog_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_instance_orm.dart';
import 'package:praxis_lab_management/src/data/models/deck_layout_orm.dart';

// Assuming mock_services.mocks.dart is generated in praxis/frontend/test/mocks/
import '../../../../mocks/mock_services.mocks.dart';

void main() {
  late MockAssetApiService mockAssetApiService;

  setUp(() {
    mockAssetApiService = MockAssetApiService();
  });

  group('AssetManagementBloc', () {
    final machine1 = ManagedDeviceOrm(
      name: 'Device 1',
      type: 'machineType1',
      metadata: {},
      isAvailable: true,
    );
    final resourceDef1 = ResourceDefinitionCatalogOrm(
      pylabrobotDefinitionName:
          'lwDef1', // TODO: replace with actual definition name
      pythonFqn: 'com.praxis.resource.ResourceDef1',
    );
    final resourceInstance1 = ResourceInstanceOrm(
      userAssignedName: 'Resource Instance 1',
      pylabrobotDefinitionName: resourceDef1.pylabrobotDefinitionName,
    );
    final deckLayout1 = DeckLayoutOrm(
      id: 1,
      layoutName: 'Deck Layout 1',
      deckDeviceId: 1,
      workspaceId: 'workspace1',
    );

    final List<ManagedDeviceOrm> mockDevices = [machine1];
    final List<ResourceDefinitionCatalogOrm> mockResourceDefinitions = [
      resourceDef1,
    ];
    final List<ResourceInstanceOrm> mockResourceInstances = [resourceInstance1];
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
            mockAssetApiService.getResourceDefinitions(),
          ).thenAnswer((_) async => mockResourceDefinitions);
          when(
            mockAssetApiService.getResourceInstances(),
          ).thenAnswer((_) async => mockResourceInstances);
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
                machines: mockDevices,
                resourceDefinitions: mockResourceDefinitions,
                resourceInstances: mockResourceInstances,
                deckLayouts: mockDeckLayouts,
              ),
            ],
        verify: (_) {
          verify(mockAssetApiService.getDevices()).called(1);
          verify(mockAssetApiService.getResourceDefinitions()).called(1);
          verify(mockAssetApiService.getResourceInstances()).called(1);
          verify(mockAssetApiService.getDeckLayouts()).called(1);
        },
      );

      blocTest<AssetManagementBloc, AssetManagementState>(
        'emits [AssetManagementLoadInProgress, AssetManagementLoadFailure] when AssetApiService.getDevices throws an exception',
        build: () {
          when(
            mockAssetApiService.getDevices(),
          ).thenThrow(Exception('Failed to fetch machines'));
          // Mock other calls if they would happen before the failing one
          when(
            mockAssetApiService.getResourceDefinitions(),
          ).thenAnswer((_) async => mockResourceDefinitions);
          when(
            mockAssetApiService.getResourceInstances(),
          ).thenAnswer((_) async => mockResourceInstances);
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
                'Exception: Failed to fetch machines',
              ),
            ],
        verify: (_) {
          verify(mockAssetApiService.getDevices()).called(1);
          // Other calls might not happen if getDevices fails early and the bloc doesn't catch individually
        },
      );
    });

    group('AddDeviceStarted', () {
      final newDevice = ManagedDeviceOrm(
        name: 'New Device',
        type: 'newDeviceType',
        metadata: {},
        isAvailable: true,
      );
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
            mockAssetApiService.getResourceDefinitions(),
          ).thenAnswer((_) async => mockResourceDefinitions);
          when(
            mockAssetApiService.getResourceInstances(),
          ).thenAnswer((_) async => mockResourceInstances);
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
                machines: [newDevice],
                resourceDefinitions: mockResourceDefinitions,
                resourceInstances: mockResourceInstances,
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
          ).thenThrow(Exception('Failed to create machine'));
          return AssetManagementBloc(mockAssetApiService);
        },
        act: (bloc) => bloc.add(AddDeviceStarted(newDevice)),
        expect:
            () => [
              const AssetManagementUpdateInProgress(),
              isA<AssetManagementUpdateFailure>().having(
                (s) => s.error,
                'error',
                'Exception: Failed to create machine',
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
