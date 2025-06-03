import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/data/models/deck_layout_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_definition_catalog_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_instance_orm.dart';
import 'package:praxis_lab_management/src/data/models/managed_device_orm.dart';
import 'package:praxis_lab_management/src/data/services/asset_api_service.dart';
import 'package:praxis_lab_management/src/core/network/dio_client.dart';
import 'package:praxis_lab_management/src/core/error/exceptions.dart';

// Generate mocks for DioClient and Dio
@GenerateMocks([DioClient, Dio])
import 'asset_api_service_impl_test.mocks.dart';

void main() {
  late MockDioClient mockDioClient;
  late MockDio mockDio;
  late AssetApiServiceImpl assetApiService;

  setUp(() {
    mockDio = MockDio();
    mockDioClient = MockDioClient();
    when(mockDioClient.dio).thenReturn(mockDio);
    assetApiService = AssetApiServiceImpl(mockDioClient);
  });

  group('ManagedDeviceOrm - CRUD and Actions', () {
    final deviceJson = {
      'name': 'Test Device 1',
      'type': 'robot',
      'metadata': {'info': 'test info'},
      'is_available': true,
      'description': 'A test device',
    };
    final deviceOrm = ManagedDeviceOrm.fromJson(deviceJson);

    // getDevices
    group('getDevices', () {
      test('returns list of ManagedDeviceOrm on success', () async {
        final responseData = [deviceJson, deviceJson];
        when(mockDio.get('/api/assets/types/machine')).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: '/api/assets/types/machine'),
            data: responseData,
            statusCode: 200,
          ),
        );

        final result = await assetApiService.getDevices();

        expect(result, isA<List<ManagedDeviceOrm>>());
        expect(result.length, 2);
        expect(result[0].name, deviceOrm.name);
        verify(mockDio.get('/api/assets/types/machine')).called(1);
      });

      test('throws ApiException on API error', () async {
        when(mockDio.get('/api/assets/types/machine')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/api/assets/types/machine'),
            response: Response(
              requestOptions: RequestOptions(path: '/api/assets/types/machine'),
              statusCode: 404,
            ),
          ),
        );
        expect(
          () => assetApiService.getDevices(),
          throwsA(isA<ApiException>()),
        );
      });

      test('throws DataParsingException on parsing error', () async {
        when(mockDio.get('/api/assets/types/machine')).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: '/api/assets/types/machine'),
            data: {'wrong_data': 'format'}, // Malformed data
            statusCode: 200,
          ),
        );
        expect(
          () => assetApiService.getDevices(),
          throwsA(isA<DataParsingException>()),
        );
      });
    });

    // createDevice
    group('createDevice', () {
      test('returns ManagedDeviceOrm on success', () async {
        when(
          mockDio.post('/api/assets/machine', data: anyNamed('data')),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: '/api/assets/machine'),
            data: deviceJson,
            statusCode: 200,
          ),
        );

        final result = await assetApiService.createDevice(deviceOrm);

        expect(result, isA<ManagedDeviceOrm>());
        expect(result.name, deviceOrm.name);
        verify(
          mockDio.post('/api/assets/machine', data: anyNamed('data')),
        ).called(1);
      });

      test('throws ApiException on API error', () async {
        when(
          mockDio.post('/api/assets/machine', data: anyNamed('data')),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/api/assets/machine'),
            response: Response(
              requestOptions: RequestOptions(path: '/api/assets/machine'),
              statusCode: 500,
            ),
          ),
        );
        expect(
          () => assetApiService.createDevice(deviceOrm),
          throwsA(isA<ApiException>()),
        );
      });
    });

    // getDeviceById
    group('getDeviceById', () {
      test('returns ManagedDeviceOrm on success', () async {
        when(mockDio.get('/api/assets/${deviceOrm.name}')).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/assets/${deviceOrm.name}',
            ),
            data: deviceJson,
            statusCode: 200,
          ),
        );

        final result = await assetApiService.getDeviceById(deviceOrm.name);

        expect(result, isA<ManagedDeviceOrm>());
        expect(result.name, deviceOrm.name);
        verify(mockDio.get('/api/assets/${deviceOrm.name}')).called(1);
      });

      test('throws ApiException on 404 error', () async {
        when(mockDio.get('/api/assets/unknownDevice')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/api/assets/unknownDevice'),
            response: Response(
              requestOptions: RequestOptions(path: '/api/assets/unknownDevice'),
              statusCode: 404,
            ),
          ),
        );
        expect(
          () => assetApiService.getDeviceById('unknownDevice'),
          throwsA(isA<ApiException>()),
        );
      });
    });

    // updateDevice
    group('updateDevice', () {
      test('returns ManagedDeviceOrm on success', () async {
        when(
          mockDio.put(
            '/api/assets/machine/${deviceOrm.name}',
            data: anyNamed('data'),
          ),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/assets/machine/${deviceOrm.name}',
            ),
            data: deviceJson, // Assuming update returns the updated device
            statusCode: 200,
          ),
        );

        final result = await assetApiService.updateDevice(
          deviceOrm.name,
          deviceOrm,
        );

        expect(result, isA<ManagedDeviceOrm>());
        expect(result.name, deviceOrm.name);
        verify(
          mockDio.put(
            '/api/assets/machine/${deviceOrm.name}',
            data: anyNamed('data'),
          ),
        ).called(1);
      });
    });

    // deleteDevice
    group('deleteDevice', () {
      test('completes successfully on 200 or 204', () async {
        when(
          mockDio.delete('/api/assets/machine/${deviceOrm.name}'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/assets/machine/${deviceOrm.name}',
            ),
            statusCode: 204, // No Content
          ),
        );
        await expectLater(
          assetApiService.deleteDevice(deviceOrm.name),
          completes,
        );
        verify(
          mockDio.delete('/api/assets/machine/${deviceOrm.name}'),
        ).called(1);
      });
    });

    // Device Actions (connect, initialize, disconnect)
    group('_executeDeviceAction', () {
      const deviceId = 'testDevice123';
      test('connectDevice calls _executeDeviceAction with "connect"', () async {
        when(
          mockDio.post(
            '/api/workcell/devices/$deviceId/execute_action',
            data: anyNamed('data'),
          ),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/workcell/devices/$deviceId/execute_action',
            ),
            statusCode: 200,
          ),
        );
        await assetApiService.connectDevice(deviceId);
        verify(
          mockDio.post(
            '/api/workcell/devices/$deviceId/execute_action',
            data:
                '"{\\"action\\":\\"connect\\"}"', // verify specific JSON payload
          ),
        ).called(1);
      });

      test(
        'initializeDevice calls _executeDeviceAction with "initialize"',
        () async {
          when(
            mockDio.post(
              '/api/workcell/devices/$deviceId/execute_action',
              data: anyNamed('data'),
            ),
          ).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(
                path: '/api/workcell/devices/$deviceId/execute_action',
              ),
              statusCode: 200,
            ),
          );
          await assetApiService.initializeDevice(deviceId);
          verify(
            mockDio.post(
              '/api/workcell/devices/$deviceId/execute_action',
              data: '"{\\"action\\":\\"initialize\\"}"',
            ),
          ).called(1);
        },
      );

      test(
        'disconnectDevice calls _executeDeviceAction with "disconnect"',
        () async {
          when(
            mockDio.post(
              '/api/workcell/devices/$deviceId/execute_action',
              data: anyNamed('data'),
            ),
          ).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(
                path: '/api/workcell/devices/$deviceId/execute_action',
              ),
              statusCode: 200,
            ),
          );
          await assetApiService.disconnectDevice(deviceId);
          verify(
            mockDio.post(
              '/api/workcell/devices/$deviceId/execute_action',
              data: '"{\\"action\\":\\"disconnect\\"}"',
            ),
          ).called(1);
        },
      );

      test('_executeDeviceAction throws ApiException on API error', () async {
        when(
          mockDio.post(
            '/api/workcell/devices/$deviceId/execute_action',
            data: anyNamed('data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: '/api/workcell/devices/$deviceId/execute_action',
            ),
            response: Response(
              requestOptions: RequestOptions(
                path: '/api/workcell/devices/$deviceId/execute_action',
              ),
              statusCode: 500,
            ),
          ),
        );
        expect(
          () => assetApiService.connectDevice(deviceId),
          throwsA(isA<ApiException>()),
        );
      });
    });
  });

  group('ResourceDefinitionCatalogOrm - CRUD', () {
    final resourceDefJson = {
      'pylabrobot_definition_name': 'test_plate',
      'python_fqn': 'pylabrobot.resources.Plate',
      'size_x_mm': 127.0,
      'size_y_mm': 85.0,
      'size_z_mm': 14.0,
      'plr_category': 'plate',
      'model': 'TestModel123',
      // other fields as needed by your model ...
    };
    final resourceDefOrm = ResourceDefinitionCatalogOrm.fromJson(
      resourceDefJson,
    );
    final assetResponseJsonForResourceDef = {
      'name': resourceDefOrm.pylabrobotDefinitionName,
      'type': 'resource', // or 'resource' depending on implementation
      'metadata': resourceDefJson, // The full resource definition
      'is_available': true,
      'description': resourceDefOrm.description,
    };

    group('getResourceDefinitions', () {
      test('returns list of ResourceDefinitionCatalogOrm on success', () async {
        // Assumes /api/assets/types/resource returns AssetResponse which needs mapping
        final responseData = [
          assetResponseJsonForResourceDef,
          assetResponseJsonForResourceDef,
        ];
        when(mockDio.get('/api/assets/types/resource')).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: '/api/assets/types/resource'),
            data: responseData,
            statusCode: 200,
          ),
        );

        final result = await assetApiService.getResourceDefinitions();

        expect(result, isA<List<ResourceDefinitionCatalogOrm>>());
        expect(result.length, 2);
        expect(
          result[0].pylabrobotDefinitionName,
          resourceDefOrm.pylabrobotDefinitionName,
        );
        verify(mockDio.get('/api/assets/types/resource')).called(1);
      });

      test(
        'throws DataParsingException on incorrect metadata structure',
        () async {
          final malformedAssetResponse = {
            'name': 'bad_def',
            'type': 'resource',
            'metadata': "not_a_map", // Incorrect metadata
            'is_available': true,
          };
          when(mockDio.get('/api/assets/types/resource')).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(
                path: '/api/assets/types/resource',
              ),
              data: [malformedAssetResponse],
              statusCode: 200,
            ),
          );
          expect(
            () => assetApiService.getResourceDefinitions(),
            throwsA(isA<DataParsingException>()),
          );
        },
      );
    });

    group('createResourceDefinition', () {
      test('returns ResourceDefinitionCatalogOrm on success', () async {
        // Assumes /api/assets/resource returns AssetResponse which needs mapping
        when(
          mockDio.post('/api/assets/resource', data: anyNamed('data')),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: '/api/assets/resource'),
            data:
                assetResponseJsonForResourceDef, // Backend returns AssetResponse
            statusCode: 200,
          ),
        );

        final result = await assetApiService.createResourceDefinition(
          resourceDefOrm,
        );

        expect(result, isA<ResourceDefinitionCatalogOrm>());
        expect(
          result.pylabrobotDefinitionName,
          resourceDefOrm.pylabrobotDefinitionName,
        );
        verify(
          mockDio.post('/api/assets/resource', data: anyNamed('data')),
        ).called(1);
      });
    });

    // Update and Delete are placeholders, so testing them might be limited
    // to verifying the call and mock error handling for now.
    group('updateResourceDefinition (placeholder)', () {
      test(
        'throws ApiException as it is a placeholder for non-existent endpoint',
        () async {
          // Simulate Dio throwing an error when a non-existent endpoint is called
          when(
            mockDio.put(
              '/api/assets/resource_definitions/some_id',
              data: anyNamed('data'),
            ),
          ).thenThrow(
            createDioError(
              statusCode: 501,
              path: '/api/assets/resource_definitions/some_id',
            ),
          );
          expect(
            () => assetApiService.updateResourceDefinition(
              "some_id",
              resourceDefOrm,
            ),
            throwsA(isA<ApiException>()),
          );
        },
      );
    });

    group('deleteResourceDefinition (placeholder)', () {
      test(
        'throws ApiException as it is a placeholder for non-existent endpoint',
        () async {
          when(
            mockDio.delete('/api/assets/resource_definitions/some_id'),
          ).thenThrow(
            createDioError(
              statusCode: 501,
              path: '/api/assets/resource_definitions/some_id',
            ),
          );
          expect(
            () => assetApiService.deleteResourceDefinition("some_id"),
            throwsA(isA<ApiException>()),
          );
        },
      );
    });
  });

  group('ResourceInstanceOrm - CRUD', () {
    final inventoryDataJson = {
      'praxis_inventory_schema_version': '1.0',
      'consumable_state': 'new',
    };
    final resourceInstanceJson = {
      'id': 1,
      'user_assigned_name': 'Test LW Instance 1',
      'pylabrobot_definition_name': 'test_plate_def',
      'properties_json':
          inventoryDataJson, // This contains the inventory details
      'current_status': 'AVAILABLE_IN_STORAGE',
      'workspaceId':
          'ws1', // Assuming workspaceId is part of your frontend model
    };
    final resourceInstanceOrm = ResourceInstanceOrm.fromJson(
      resourceInstanceJson,
    );

    group('getResourceInstances (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        when(mockDio.get('/api/assets/resource_instances')).thenThrow(
          createDioError(
            statusCode: 501,
            path: '/api/assets/resource_instances',
          ),
        );
        expect(
          () => assetApiService.getResourceInstances(),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('createResourceInstance (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        when(
          mockDio.post(
            '/api/assets/resource_instances',
            data: anyNamed('data'),
          ),
        ).thenThrow(
          createDioError(
            statusCode: 501,
            path: '/api/assets/resource_instances',
          ),
        );
        expect(
          () => assetApiService.createResourceInstance(resourceInstanceOrm),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('getResourceInstanceById', () {
      test(
        'returns ResourceInstanceOrm (from inventory data) on success',
        () async {
          final instanceId =
              resourceInstanceOrm.id!
                  .toString(); // Assuming ID is non-null for a created instance
          when(
            mockDio.get('/api/assets/resource_instances/$instanceId/inventory'),
          ).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(
                path: '/api/assets/resource_instances/$instanceId/inventory',
              ),
              data: inventoryDataJson,
              statusCode: 200,
            ),
          );

          final result = await assetApiService.getResourceInstanceById(
            instanceId,
          );

          expect(result, isA<ResourceInstanceOrm>());
          expect(
            result.id.toString(),
            instanceId,
          ); // Compare string IDs if one is string
          expect(
            result.inventoryData?.consumableState,
            inventoryDataJson['consumable_state'],
          );
          expect(result.userAssignedName, 'Instance $instanceId (Inventory)');
          verify(
            mockDio.get('/api/assets/resource_instances/$instanceId/inventory'),
          ).called(1);
        },
      );

      test(
        'throws ApiException on API error for getResourceInstanceById',
        () async {
          final instanceId = resourceInstanceOrm.id!.toString();
          when(
            mockDio.get('/api/assets/resource_instances/$instanceId/inventory'),
          ).thenThrow(
            createDioError(
              statusCode: 404,
              path: '/api/assets/resource_instances/$instanceId/inventory',
            ),
          );
          expect(
            () => assetApiService.getResourceInstanceById(instanceId),
            throwsA(isA<ApiException>()),
          );
        },
      );
    });

    group('updateResourceInstance', () {
      test(
        'returns ResourceInstanceOrm with updated inventory on success',
        () async {
          final instanceId = resourceInstanceOrm.id!.toString();
          final updatedInventoryJson = {
            ...inventoryDataJson,
            'consumable_state': 'used',
            'last_updated_at': DateTime.now().toIso8601String(),
          };

          // Ensure the resourceInstanceOrm being updated has non-null inventoryData
          final updatableInstance =
              resourceInstanceOrm.inventoryData == null
                  ? ResourceInstanceOrm.fromJson({
                    ...resourceInstanceJson,
                    'properties_json': inventoryDataJson,
                  })
                  : resourceInstanceOrm;

          when(
            mockDio.put(
              '/api/assets/resource_instances/$instanceId/inventory',
              data: anyNamed('data'),
            ),
          ).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(
                path: '/api/assets/resource_instances/$instanceId/inventory',
              ),
              data: updatedInventoryJson,
              statusCode: 200,
            ),
          );

          final result = await assetApiService.updateResourceInstance(
            instanceId,
            updatableInstance,
          );

          expect(result, isA<ResourceInstanceOrm>());
          expect(result.id.toString(), instanceId);
          expect(
            result.inventoryData?.consumableState,
            updatedInventoryJson['consumable_state'],
          );
          verify(
            mockDio.put(
              '/api/assets/resource_instances/$instanceId/inventory',
              data: anyNamed('data'),
            ),
          ).called(1);
        },
      );

      test(
        'throws ArgumentError if inventoryData is null for updateResourceInstance',
        () async {
          final instanceWithoutInventory = ResourceInstanceOrm(
            id: 2, // Make sure ID is int if comparing with int
            userAssignedName: "No Inventory",
            pylabrobotDefinitionName: "some_def",
            inventoryData: null,
            workspaceId: "ws2", // Ensure all required fields are present
          );
          expect(
            () => assetApiService.updateResourceInstance(
              "2",
              instanceWithoutInventory,
            ),
            throwsA(isA<ArgumentError>()),
          );
        },
      );

      test(
        'throws ApiException on API error for updateResourceInstance',
        () async {
          final instanceId = resourceInstanceOrm.id!.toString();
          final updatableInstance =
              resourceInstanceOrm.inventoryData == null
                  ? ResourceInstanceOrm.fromJson({
                    ...resourceInstanceJson,
                    'properties_json': inventoryDataJson,
                  })
                  : resourceInstanceOrm;

          when(
            mockDio.put(
              '/api/assets/resource_instances/$instanceId/inventory',
              data: anyNamed('data'),
            ),
          ).thenThrow(
            createDioError(
              statusCode: 500,
              path: '/api/assets/resource_instances/$instanceId/inventory',
            ),
          );
          expect(
            () => assetApiService.updateResourceInstance(
              instanceId,
              updatableInstance,
            ),
            throwsA(isA<ApiException>()),
          );
        },
      );
    });

    group('deleteResourceInstance (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        final instanceId = resourceInstanceOrm.id!.toString();
        when(
          mockDio.delete('/api/assets/resource_instances/$instanceId'),
        ).thenThrow(
          createDioError(
            statusCode: 501,
            path: '/api/assets/resource_instances/$instanceId',
          ),
        );
        expect(
          () => assetApiService.deleteResourceInstance(instanceId),
          throwsA(isA<ApiException>()),
        );
      });
    });
  });

  group('DeckLayoutOrm - CRUD (placeholders)', () {
    final slotItemJson = {
      'id': 1,
      'deck_configuration_id': 1,
      'slot_name': 'A1',
      'resource_instance_id': 1,
    };
    final deckLayoutJson = {
      'id': 1, // Ensure ID is int
      'layout_name': 'Test Layout 1',
      'deck_device_id': 1, // Ensure this is int
      'slot_items': [slotItemJson],
      'workspace_id': 'ws1',
    };
    final deckLayoutOrm = DeckLayoutOrm.fromJson(deckLayoutJson);

    group('getDeckLayouts (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        when(mockDio.get('/api/assets/deck_layouts')).thenThrow(
          createDioError(statusCode: 501, path: '/api/assets/deck_layouts'),
        );
        expect(
          () => assetApiService.getDeckLayouts(),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('createDeckLayout (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        when(
          mockDio.post('/api/assets/deck_layouts', data: anyNamed('data')),
        ).thenThrow(
          createDioError(statusCode: 501, path: '/api/assets/deck_layouts'),
        );
        expect(
          () => assetApiService.createDeckLayout(deckLayoutOrm),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('getDeckLayoutById (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        final layoutId = deckLayoutOrm.id!.toString();
        when(mockDio.get('/api/assets/deck_layouts/$layoutId')).thenThrow(
          createDioError(
            statusCode: 501,
            path: '/api/assets/deck_layouts/$layoutId',
          ),
        );
        expect(
          () => assetApiService.getDeckLayoutById(layoutId),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('updateDeckLayout (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        final layoutId = deckLayoutOrm.id!.toString();
        when(
          mockDio.put(
            '/api/assets/deck_layouts/$layoutId',
            data: anyNamed('data'),
          ),
        ).thenThrow(
          createDioError(
            statusCode: 501,
            path: '/api/assets/deck_layouts/$layoutId',
          ),
        );
        expect(
          () => assetApiService.updateDeckLayout(layoutId, deckLayoutOrm),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('deleteDeckLayout (placeholder)', () {
      test('throws ApiException for placeholder endpoint', () async {
        final layoutId = deckLayoutOrm.id!.toString();
        when(mockDio.delete('/api/assets/deck_layouts/$layoutId')).thenThrow(
          createDioError(
            statusCode: 501,
            path: '/api/assets/deck_layouts/$layoutId',
          ),
        );
        expect(
          () => assetApiService.deleteDeckLayout(layoutId),
          throwsA(isA<ApiException>()),
        );
      });
    });
  });
}

// Helper to create a DioException
DioException createDioError({
  required int statusCode,
  required String path,
  String? statusMessage,
}) {
  return DioException(
    requestOptions: RequestOptions(path: path),
    response: Response(
      requestOptions: RequestOptions(path: path),
      statusCode: statusCode,
      statusMessage: statusMessage ?? 'Error $statusCode',
    ),
  );
}
