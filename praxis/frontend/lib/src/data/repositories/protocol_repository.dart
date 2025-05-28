import 'package:file_picker/file_picker.dart';
import 'package:praxis_lab_management/src/data/models/protocol/file_upload_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_status_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_config.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_asset_detail.dart';
import 'package:praxis_lab_management/src/data/services/protocol_api_service.dart';

abstract class ProtocolRepository {
  Future<List<ProtocolInfo>> discoverProtocols();
  Future<ProtocolDetails> getProtocolDetails(String protocolPath);
  Future<List<String>> getDeckLayouts();
  Future<FileUploadResponse> uploadDeckFile({required PlatformFile file});
  Future<Map<String, dynamic>> prepareProtocol({
    required ProtocolPrepareRequest request,
  });
  Future<ProtocolStatusResponse> startProtocol({
    required Map<String, dynamic> preparedConfig,
  });
}

/// Concrete implementation of [ProtocolRepository].
///
/// This class uses a [ProtocolApiService] to fetch and manage protocol data
/// from the backend.
class ProtocolRepositoryImpl implements ProtocolRepository {
  final ProtocolApiService _protocolApiService;

  ProtocolRepositoryImpl({required ProtocolApiService protocolApiService})
    : _protocolApiService = protocolApiService;

  @override
  Future<List<ProtocolInfo>> discoverProtocols() async {
    try {
      return await _protocolApiService.discoverProtocols();
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<ProtocolDetails> getProtocolDetails(String protocolPath) async {
    try {
      final json = await _protocolApiService.getProtocolDetails(
        protocolPath: protocolPath,
      );

      // Manually parse the 'parameters' map from the raw JSON
      final parametersMap = <String, ParameterConfig>{};
      if (json['parameters'] is Map) {
        (json['parameters'] as Map<String, dynamic>).forEach((key, value) {
          final paramDetailJson = value as Map<String, dynamic>;
          parametersMap[key] = ParameterConfig(
            type: paramDetailJson['paramType'] as String,
            isRequired: paramDetailJson['isRequired'] as bool? ?? false,
            description: paramDetailJson['description'] as String?,
            defaultValue:
                paramDetailJson['default'] ?? paramDetailJson['defaultValue'],
            displayName: paramDetailJson['displayName'] as String?,
            units: paramDetailJson['units'] as String?,
          );
        });
      }

      // Manually parse the 'assets' list
      final assetsList = <ProtocolAssetDetail>[];
      if (json['assets'] is List) {
        assetsList.addAll(
          (json['assets'] as List).map(
            (assetJson) =>
                ProtocolAssetDetail.fromJson(assetJson as Map<String, dynamic>),
          ),
        );
      }

      // Construct and return the new ProtocolDetails domain model
      return ProtocolDetails(
        name: json['name'] as String,
        path: json['path'] as String,
        description: json['description'] as String,
        parameters: parametersMap,
        assets: assetsList,
        hasAssets: json['has_assets'] as bool? ?? assetsList.isNotEmpty,
        hasParameters:
            json['has_parameters'] as bool? ?? parametersMap.isNotEmpty,
        requiresConfig: json['requires_config'] as bool? ?? true,
      );
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<List<String>> getDeckLayouts() async {
    try {
      return await _protocolApiService.getDeckLayouts();
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<FileUploadResponse> uploadDeckFile({
    required PlatformFile file,
  }) async {
    try {
      return await _protocolApiService.uploadDeckFile(file: file);
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>> prepareProtocol({
    required ProtocolPrepareRequest request,
  }) async {
    try {
      final response = await _protocolApiService.prepareProtocol(
        request: request,
      );
      return response.config;
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<ProtocolStatusResponse> startProtocol({
    required Map<String, dynamic> preparedConfig,
  }) async {
    try {
      return await _protocolApiService.startProtocol(
        preparedConfig: preparedConfig,
      );
    } catch (e) {
      rethrow;
    }
  }
}
