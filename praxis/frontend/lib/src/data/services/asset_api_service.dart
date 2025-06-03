import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:praxis_lab_management/src/data/models/deck_layout_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_definition_catalog_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_instance_orm.dart';
import 'package:praxis_lab_management/src/data/models/managed_device_orm.dart';
import 'package:praxis_lab_management/src/core/error/exceptions.dart';

import 'package:praxis_lab_management/src/core/network/dio_client.dart';

/// Abstract class for asset API services.
abstract class AssetApiService {
  /// Devices (Instruments)
  Future<List<ManagedDeviceOrm>> getDevices();
  Future<ManagedDeviceOrm> createDevice(ManagedDeviceOrm device);
  Future<ManagedDeviceOrm> getDeviceById(String deviceId);
  Future<ManagedDeviceOrm> updateDevice(
    String deviceId,
    ManagedDeviceOrm device,
  );
  Future<void> deleteDevice(String deviceId);
  Future<void> connectDevice(String deviceId);
  Future<void> initializeDevice(String deviceId);
  Future<void> disconnectDevice(String deviceId);

  /// Resource Definitions (Resource Types)
  Future<List<ResourceDefinitionCatalogOrm>> getResourceDefinitions();
  Future<ResourceDefinitionCatalogOrm> createResourceDefinition(
    ResourceDefinitionCatalogOrm resourceDefinition,
  );
  Future<ResourceDefinitionCatalogOrm> updateResourceDefinition(
    String resourceDefinitionId,
    ResourceDefinitionCatalogOrm resourceDefinition,
  );
  Future<void> deleteResourceDefinition(String resourceDefinitionId);

  /// Resource Instances (Physical Resource Items)
  Future<List<ResourceInstanceOrm>> getResourceInstances();
  Future<ResourceInstanceOrm> createResourceInstance(
    ResourceInstanceOrm resourceInstance,
  );
  Future<ResourceInstanceOrm> getResourceInstanceById(String instanceId);
  Future<ResourceInstanceOrm> updateResourceInstance(
    String instanceId,
    ResourceInstanceOrm resourceInstance,
  );
  Future<void> deleteResourceInstance(String instanceId);

  /// Deck Layouts
  Future<List<DeckLayoutOrm>> getDeckLayouts();
  Future<DeckLayoutOrm> createDeckLayout(DeckLayoutOrm deckLayout);
  Future<DeckLayoutOrm> getDeckLayoutById(String deckLayoutId);
  Future<DeckLayoutOrm> updateDeckLayout(
    String deckLayoutId,
    DeckLayoutOrm deckLayout,
  );
  Future<void> deleteDeckLayout(String deckLayoutId);
}

/// Implementation of [AssetApiService] using Dio.
class AssetApiServiceImpl extends AssetApiService {
  final DioClient _dioClient;

  /// Constructor for [AssetApiServiceImpl].
  AssetApiServiceImpl(this._dioClient);

  /// Devices (Instruments)
  @override
  Future<List<ManagedDeviceOrm>> getDevices() async {
    try {
      final response = await _dioClient.dio.get('/api/assets/types/machine');
      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> jsonData = response.data as List<dynamic>;
        return jsonData
            .map(
              (item) => ManagedDeviceOrm.fromJson(item as Map<String, dynamic>),
            )
            .toList();
      } else {
        throw ApiException(
          message: 'Failed to load devices: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      // Handle Dio specific errors (network, timeout, etc.)
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      // Handle errors in parsing JSON
      throw DataParsingException('Error parsing device data: ${e.message}');
    } catch (e) {
      // Handle any other errors
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ManagedDeviceOrm> createDevice(ManagedDeviceOrm device) async {
    try {
      // The backend expects MachineCreationRequest model
      // which includes name, machineType, backend, description, params.
      // We need to adapt ManagedDeviceOrm to this structure.
      final requestBody = {
        'name': device.name,
        'machineType': device.type,
        // 'backend': null, // Assuming no specific backend for now, can be added if needed
        'description': device.description,
        'params':
            device
                .metadata, // Assuming metadata in ManagedDeviceOrm maps to params
      };
      final response = await _dioClient.dio.post(
        '/api/assets/machine',
        data: jsonEncode(requestBody),
      );
      if (response.statusCode == 200 && response.data != null) {
        return ManagedDeviceOrm.fromJson(response.data as Map<String, dynamic>);
      } else {
        throw ApiException(
          message:
              'Failed to create device: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ManagedDeviceOrm> getDeviceById(String deviceId) async {
    try {
      final response = await _dioClient.dio.get('/api/assets/$deviceId');
      if (response.statusCode == 200 && response.data != null) {
        return ManagedDeviceOrm.fromJson(response.data as Map<String, dynamic>);
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Device not found: $deviceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to get device $deviceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing device data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ManagedDeviceOrm> updateDevice(
    String deviceId,
    ManagedDeviceOrm device,
  ) async {
    try {
      // Assuming a PUT request to /api/assets/machine/{deviceId}
      // The backend assets.py doesn't have this, so this is a placeholder.
      // The request body structure might need to align with MachineCreationRequest
      // or a new MachineUpdateRequest model if defined in backend.
      final requestBody = device.toJson(); // Send full device data for update
      final response = await _dioClient.dio.put(
        '/api/assets/machine/$deviceId',
        data: jsonEncode(requestBody),
      );
      if (response.statusCode == 200 && response.data != null) {
        return ManagedDeviceOrm.fromJson(response.data as Map<String, dynamic>);
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Device not found for update: $deviceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to update device $deviceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<void> deleteDevice(String deviceId) async {
    try {
      // Assuming a DELETE request to /api/assets/machine/{deviceId}
      // The backend assets.py doesn't have this, so this is a placeholder.
      final response = await _dioClient.dio.delete(
        '/api/assets/machine/$deviceId',
      );
      if (response.statusCode == 200 || response.statusCode == 204) {
        // 204 No Content is also a success
        return;
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Device not found for deletion: $deviceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to delete device $deviceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  Future<void> _executeDeviceAction(String deviceId, String action) async {
    try {
      final response = await _dioClient.dio.post(
        '/api/workcell/devices/$deviceId/execute_action',
        data: jsonEncode({'action': action}),
      );
      // Assuming 200 or 202 (Accepted) for successful action submission
      if (response.statusCode == 200 || response.statusCode == 202) {
        // Depending on the backend, response.data might contain action status.
        // For now, we assume no specific data is returned or needed by the frontend.
        return;
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Device not found for action $action: $deviceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to execute $action for device $deviceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(
        message: 'API request failed for $action: ${e.message}',
      );
    } catch (e) {
      throw UnknownException(
        'An unknown error occurred during $action: ${e.toString()}',
      );
    }
  }

  @override
  Future<void> connectDevice(String deviceId) async {
    await _executeDeviceAction(deviceId, 'connect');
  }

  @override
  Future<void> initializeDevice(String deviceId) async {
    await _executeDeviceAction(deviceId, 'initialize');
  }

  @override
  Future<void> disconnectDevice(String deviceId) async {
    await _executeDeviceAction(deviceId, 'disconnect');
  }

  /// Resource Definitions (Resource Types)
  @override
  Future<List<ResourceDefinitionCatalogOrm>> getResourceDefinitions() async {
    try {
      // Using /api/assets/types/resource as per AssetResponse structure.
      // This assumes 'resource' type assets are resource definitions and
      // their 'metadata' field contains the ResourceDefinitionCatalogOrm data.
      // This is a significant assumption and might need backend adjustments
      // for a more direct mapping or a dedicated endpoint.
      final response = await _dioClient.dio.get('/api/assets/types/resource');
      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> jsonData = response.data as List<dynamic>;
        return jsonData.map((item) {
          final assetResponse = item as Map<String, dynamic>;
          // Attempting to reconstruct ResourceDefinitionCatalogOrm from AssetResponse
          // 'name' from AssetResponse is assumed to be 'pylabrobot_definition_name'
          // 'metadata' from AssetResponse is assumed to contain the rest of the fields.
          // 'type' from AssetResponse is 'resource'.
          if (assetResponse['metadata'] is Map<String, dynamic>) {
            final metadata = assetResponse['metadata'] as Map<String, dynamic>;
            return ResourceDefinitionCatalogOrm.fromJson({
              ...metadata, // Spread the metadata
              'pylabrobot_definition_name':
                  assetResponse['name'] ??
                  metadata['pylabrobot_definition_name'], // Prioritize name from AssetResponse
              'python_fqn':
                  metadata['python_fqn'] ??
                  'pylabrobot.resources.Resource', // Placeholder if not in metadata
              // Other fields like size_x_mm, plr_category etc., must be in metadata
            });
          } else {
            // If metadata is not what we expect, we might only have partial data.
            // This indicates a mismatch that needs to be resolved (backend or frontend).
            // For now, create with available data or throw a more specific error.
            throw DataParsingException(
              'Resource definition metadata is not in expected format for item: ${assetResponse['name']}',
            );
          }
        }).toList();
      } else {
        throw ApiException(
          message:
              'Failed to load resource definitions: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException(
        'Error parsing resource definition data: ${e.message}',
      );
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ResourceDefinitionCatalogOrm> createResourceDefinition(
    ResourceDefinitionCatalogOrm resourceDefinition,
  ) async {
    try {
      // Using POST /api/assets/resource as per available backend endpoints.
      // Mapping ResourceDefinitionCatalogOrm to ResourceCreationRequest.
      // This is an approximation. A dedicated endpoint would be better.
      final requestBody = {
        'name':
            resourceDefinition
                .pylabrobotDefinitionName, // Maps to ResourceCreationRequest.name
        'resourceType':
            resourceDefinition.plrCategory ??
            'resource_definition', // Maps to ResourceCreationRequest.resourceType
        'description': resourceDefinition.description,
        'params':
            resourceDefinition.toJson(), // Pass the full resource def as params
      };
      final response = await _dioClient.dio.post(
        '/api/assets/resource',
        data: jsonEncode(requestBody),
      );
      if (response.statusCode == 200 && response.data != null) {
        // The response is AssetResponse. We need to reconstruct ResourceDefinitionCatalogOrm.
        // This assumes the backend, upon creating a resource of this type,
        // stores the 'params' (which was our resourceDefinition.toJson())
        // into the 'metadata' of the created asset, and returns it.
        final assetResponse = response.data as Map<String, dynamic>;
        if (assetResponse['metadata'] is Map<String, dynamic>) {
          final metadata = assetResponse['metadata'] as Map<String, dynamic>;
          // Ensure pylabrobot_definition_name from original request is used if not in metadata explicitly
          return ResourceDefinitionCatalogOrm.fromJson({
            ...metadata,
            'pylabrobot_definition_name':
                assetResponse['name'] ??
                resourceDefinition.pylabrobotDefinitionName,
          });
        } else {
          throw DataParsingException(
            'Created resource definition response metadata is not in expected format.',
          );
        }
      } else {
        throw ApiException(
          message:
              'Failed to create resource definition: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ResourceDefinitionCatalogOrm> updateResourceDefinition(
    String resourceDefinitionId, // This should be pylabrobot_definition_name
    ResourceDefinitionCatalogOrm resourceDefinition,
  ) async {
    try {
      // Placeholder: Backend endpoint /api/assets/resource_definitions/{resourceDefinitionId} does not exist.
      // Assuming a standard PUT request if it were implemented.
      final response = await _dioClient.dio.put(
        '/api/assets/resource_definitions/$resourceDefinitionId',
        data: jsonEncode(resourceDefinition.toJson()),
      );
      if (response.statusCode == 200 && response.data != null) {
        return ResourceDefinitionCatalogOrm.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else if (response.statusCode == 404) {
        throw ApiException(
          message:
              'Resource definition not found for update: $resourceDefinitionId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to update resource definition $resourceDefinitionId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<void> deleteResourceDefinition(String resourceDefinitionId) async {
    try {
      // Placeholder: Backend endpoint /api/assets/resource_definitions/{resourceDefinitionId} does not exist.
      // Assuming a standard DELETE request if it were implemented.
      final response = await _dioClient.dio.delete(
        '/api/assets/resource_definitions/$resourceDefinitionId',
      );
      if (response.statusCode == 200 || response.statusCode == 204) {
        return;
      } else if (response.statusCode == 404) {
        throw ApiException(
          message:
              'Resource definition not found for deletion: $resourceDefinitionId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to delete resource definition $resourceDefinitionId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  /// Resource Instances (Physical Resource Items)
  @override
  Future<List<ResourceInstanceOrm>> getResourceInstances() async {
    try {
      // Placeholder: Backend endpoint /api/assets/resource_instances does not exist.
      // Assuming a standard GET request returning a list if it were implemented.
      final response = await _dioClient.dio.get(
        '/api/assets/resource_instances',
      );
      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> jsonData = response.data as List<dynamic>;
        return jsonData
            .map(
              (item) =>
                  ResourceInstanceOrm.fromJson(item as Map<String, dynamic>),
            )
            .toList();
      } else {
        throw ApiException(
          message:
              'Failed to load resource instances: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException(
        'Error parsing resource instance data: ${e.message}',
      );
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ResourceInstanceOrm> createResourceInstance(
    ResourceInstanceOrm resourceInstance,
  ) async {
    try {
      // Placeholder: Backend endpoint /api/assets/resource_instances does not exist.
      // Assuming a standard POST request if it were implemented.
      final response = await _dioClient.dio.post(
        '/api/assets/resource_instances',
        data: jsonEncode(resourceInstance.toJson()),
      );
      if (response.statusCode == 200 ||
          response.statusCode == 201 && response.data != null) {
        // 201 Created
        return ResourceInstanceOrm.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message:
              'Failed to create resource instance: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ResourceInstanceOrm> getResourceInstanceById(String instanceId) async {
    try {
      // Using GET /api/assets/resource_instances/{instanceId}/inventory
      // This endpoint returns ResourceInventoryDataOut.
      // The ResourceInstanceOrm.fromJson factory is designed to handle this by
      // populating inventoryData and potentially leaving other fields null/default.
      final response = await _dioClient.dio.get(
        '/api/assets/resource_instances/$instanceId/inventory',
      );
      if (response.statusCode == 200 && response.data != null) {
        // We need to construct a ResourceInstanceOrm. Since the endpoint only returns inventory,
        // other details like user_assigned_name, pylabrobot_definition_name might be missing.
        // The FromJson factory for ResourceInstanceOrm will need to be robust to this.
        // We'll pass the instanceId to be potentially used as 'id' or part of 'user_assigned_name' if needed.
        Map<String, dynamic> jsonData = response.data as Map<String, dynamic>;

        // It's possible the backend returns just the inventory data. We might need to wrap this
        // or ensure ResourceInstanceOrm.fromJson can handle it.
        // For now, assume ResourceInstanceOrm.fromJson can handle a map that primarily contains inventory fields.
        // A more complete solution might involve creating a temporary ResourceInstanceOrm
        // with a default name/type if they are not part of the response.
        return ResourceInstanceOrm.fromJson({
          'id': int.tryParse(instanceId), // Attempt to use instanceId as the ID
          'user_assigned_name':
              'Instance $instanceId (Inventory)', // Placeholder name
          'pylabrobot_definition_name': 'UnknownType', // Placeholder type
          ...jsonData, // Spread the inventory data
        });
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Resource instance inventory not found: $instanceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to get resource instance inventory $instanceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException(
        'Error parsing resource instance inventory data: ${e.message}',
      );
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<ResourceInstanceOrm> updateResourceInstance(
    String instanceId,
    ResourceInstanceOrm resourceInstance,
  ) async {
    try {
      // Using PUT /api/assets/resource_instances/{instanceId}/inventory
      // The request body should be ResourceInventoryDataIn, which corresponds to resourceInstance.inventoryData.
      if (resourceInstance.inventoryData == null) {
        throw ArgumentError("Inventory data must be provided for update.");
      }
      final response = await _dioClient.dio.put(
        '/api/assets/resource_instances/$instanceId/inventory',
        data: jsonEncode(resourceInstance.inventoryData!.toJson()),
      );
      if (response.statusCode == 200 && response.data != null) {
        // The response is ResourceInventoryDataOut.
        // We update the inventoryData of the passed resourceInstance and return it.
        final updatedInventoryData = ResourceInventoryData.fromJson(
          response.data as Map<String, dynamic>,
        );
        return ResourceInstanceOrm(
          id: resourceInstance.id ?? int.tryParse(instanceId),
          userAssignedName: resourceInstance.userAssignedName,
          pylabrobotDefinitionName: resourceInstance.pylabrobotDefinitionName,
          lotNumber: resourceInstance.lotNumber,
          expiryDate: resourceInstance.expiryDate,
          dateAddedToInventory: resourceInstance.dateAddedToInventory,
          currentStatus:
              resourceInstance
                  .currentStatus, // Status might change based on inventory
          statusDetails: resourceInstance.statusDetails,
          currentDeckSlotName: resourceInstance.currentDeckSlotName,
          locationDeviceId: resourceInstance.locationDeviceId,
          physicalLocationDescription:
              resourceInstance.physicalLocationDescription,
          inventoryData: updatedInventoryData, // Key update here
          isPermanentFixture: resourceInstance.isPermanentFixture,
          currentProtocolRunGuid: resourceInstance.currentProtocolRunGuid,
          createdAt: resourceInstance.createdAt,
          updatedAt:
              updatedInventoryData.lastUpdatedAt ??
              resourceInstance.updatedAt, // Use from response if available
          workspaceId: resourceInstance.workspaceId,
        );
      } else if (response.statusCode == 404) {
        throw ApiException(
          message:
              'Resource instance inventory not found for update: $instanceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to update resource instance inventory $instanceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<void> deleteResourceInstance(String instanceId) async {
    try {
      // Placeholder: Backend endpoint /api/assets/resource_instances/{instanceId} does not exist.
      // Assuming a standard DELETE request if it were implemented.
      final response = await _dioClient.dio.delete(
        '/api/assets/resource_instances/$instanceId',
      );
      if (response.statusCode == 200 || response.statusCode == 204) {
        // 204 No Content
        return;
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Resource instance not found for deletion: $instanceId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to delete resource instance $instanceId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  /// Deck Layouts
  @override
  Future<List<DeckLayoutOrm>> getDeckLayouts() async {
    try {
      // Placeholder: Backend endpoint /api/assets/deck_layouts does not exist.
      // Assuming a standard GET request returning a list if it were implemented.
      final response = await _dioClient.dio.get('/api/assets/deck_layouts');
      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> jsonData = response.data as List<dynamic>;
        return jsonData
            .map((item) => DeckLayoutOrm.fromJson(item as Map<String, dynamic>))
            .toList();
      } else {
        throw ApiException(
          message:
              'Failed to load deck layouts: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException(
        'Error parsing deck layout data: ${e.message}',
      );
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<DeckLayoutOrm> createDeckLayout(DeckLayoutOrm deckLayout) async {
    try {
      // Placeholder: Backend endpoint /api/assets/deck_layouts does not exist.
      // Assuming a standard POST request if it were implemented.
      final response = await _dioClient.dio.post(
        '/api/assets/deck_layouts',
        data: jsonEncode(deckLayout.toJson()),
      );
      if ((response.statusCode == 200 || response.statusCode == 201) &&
          response.data != null) {
        // 201 Created
        return DeckLayoutOrm.fromJson(response.data as Map<String, dynamic>);
      } else {
        throw ApiException(
          message:
              'Failed to create deck layout: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<DeckLayoutOrm> getDeckLayoutById(String deckLayoutId) async {
    try {
      // Placeholder: Backend endpoint /api/assets/deck_layouts/{deckLayoutId} does not exist.
      // Assuming a standard GET request if it were implemented.
      final response = await _dioClient.dio.get(
        '/api/assets/deck_layouts/$deckLayoutId',
      );
      if (response.statusCode == 200 && response.data != null) {
        return DeckLayoutOrm.fromJson(response.data as Map<String, dynamic>);
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Deck layout not found: $deckLayoutId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to get deck layout $deckLayoutId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException(
        'Error parsing deck layout data: ${e.message}',
      );
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<DeckLayoutOrm> updateDeckLayout(
    String deckLayoutId,
    DeckLayoutOrm deckLayout,
  ) async {
    try {
      // Placeholder: Backend endpoint /api/assets/deck_layouts/{deckLayoutId} does not exist.
      // Assuming a standard PUT request if it were implemented.
      final response = await _dioClient.dio.put(
        '/api/assets/deck_layouts/$deckLayoutId',
        data: jsonEncode(deckLayout.toJson()),
      );
      if (response.statusCode == 200 && response.data != null) {
        return DeckLayoutOrm.fromJson(response.data as Map<String, dynamic>);
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Deck layout not found for update: $deckLayoutId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to update deck layout $deckLayoutId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } on FormatException catch (e) {
      throw DataParsingException('Error parsing response data: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }

  @override
  Future<void> deleteDeckLayout(String deckLayoutId) async {
    try {
      // Placeholder: Backend endpoint /api/assets/deck_layouts/{deckLayoutId} does not exist.
      // Assuming a standard DELETE request if it were implemented.
      final response = await _dioClient.dio.delete(
        '/api/assets/deck_layouts/$deckLayoutId',
      );
      if (response.statusCode == 200 || response.statusCode == 204) {
        // 204 No Content
        return;
      } else if (response.statusCode == 404) {
        throw ApiException(
          message: 'Deck layout not found for deletion: $deckLayoutId',
          statusCode: 404,
        );
      } else {
        throw ApiException(
          message:
              'Failed to delete deck layout $deckLayoutId: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      throw ApiException(message: 'API request failed: ${e.message}');
    } catch (e) {
      throw UnknownException('An unknown error occurred: ${e.toString()}');
    }
  }
}
