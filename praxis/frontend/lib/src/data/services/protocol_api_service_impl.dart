import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:praxis_lab_management/src/core/error/exceptions.dart';
import 'package:praxis_lab_management/src/core/network/dio_client.dart';
import 'package:praxis_lab_management/src/data/models/protocol/file_upload_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_prepare_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_run_command.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_status_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/run_command_response.dart';

import 'protocol_api_service.dart';

class ProtocolApiServiceImpl implements ProtocolApiService {
  final DioClient _dioClient;

  ProtocolApiServiceImpl({required DioClient dioClient})
    : _dioClient = dioClient;

  Dio get _dio => _dioClient.dio;

  String get _basePath => '/api/protocols'; // Centralized base path

  @override
  Future<List<ProtocolInfo>> discoverProtocols() async {
    try {
      final response = await _dio.get('$_basePath/discover');
      if (response.statusCode == 200 && response.data is List) {
        final List<dynamic> jsonData = response.data as List<dynamic>;
        return jsonData
            .map((item) => ProtocolInfo.fromJson(item as Map<String, dynamic>))
            .toList();
      } else {
        throw ApiException(
          message: 'Failed to discover protocols',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Protocol discovery failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse protocol discovery response: $e',
        s,
      );
    }
  }

  @override
  Future<Map<String, dynamic>> getProtocolDetails({
    // UPDATE return type
    required String protocolPath,
  }) async {
    try {
      final encodedPath = Uri.encodeComponent(protocolPath);
      // Corrected to use query parameter as per backend
      final response = await _dio.get(
        '$_basePath/details',
        queryParameters: {'protocol_path': encodedPath},
      );
      if (response.statusCode == 200 && response.data is Map) {
        return response.data as Map<String, dynamic>; // UPDATE: return raw map
      } else {
        throw ApiException(
          message: 'Failed to get protocol details',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Fetching protocol details failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse protocol details response: $e',
        s,
      );
    }
  }

  @override
  Future<List<String>> getDeckLayouts() async {
    try {
      // Corrected URL
      final response = await _dio.get('$_basePath/deck_layouts');
      if (response.statusCode == 200 && response.data is List) {
        return List<String>.from(response.data as List);
      } else {
        throw ApiException(
          message: 'Failed to get deck layouts',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Fetching deck layouts failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse deck layouts response: $e',
        s,
      );
    }
  }

  Future<FileUploadResponse> _uploadFile(
    String endpoint,
    PlatformFile file,
  ) async {
    try {
      if (file.bytes == null) {
        throw ClientException(message: 'File bytes are null, cannot upload.');
      }
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(file.bytes!, filename: file.name),
      });

      final response = await _dio.post(
        endpoint,
        data: formData,
        options: Options(headers: {'Content-Type': 'multipart/form-data'}),
      );

      if ((response.statusCode == 200 || response.statusCode == 201) &&
          response.data is Map) {
        return FileUploadResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Failed to upload file to $endpoint',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'File upload to $endpoint failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse file upload response from $endpoint: $e',
        s,
      );
    }
  }

  @override
  Future<FileUploadResponse> uploadDeckFile({
    required PlatformFile file,
  }) async {
    // Corrected URL and uses helper
    return _uploadFile('$_basePath/upload_deck_file', file);
  }

  @override
  Future<FileUploadResponse> uploadConfigFile({
    required PlatformFile file,
  }) async {
    return _uploadFile('$_basePath/upload_config_file', file);
  }

  @override
  Future<Map<String, dynamic>> getProtocolSchema({
    required String protocolPath,
  }) async {
    try {
      final encodedPath = Uri.encodeComponent(protocolPath);
      final response = await _dio.get(
        '$_basePath/schema',
        queryParameters: {'protocol_path': encodedPath},
      );
      if (response.statusCode == 200 && response.data is Map) {
        return response.data as Map<String, dynamic>;
      } else {
        throw ApiException(
          message: 'Failed to get protocol schema',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Fetching protocol schema failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse protocol schema response: $e',
        s,
      );
    }
  }

  @override
  Future<List<String>> listRunningProtocols() async {
    try {
      // Backend endpoint is GET /api/protocols/
      final response = await _dio.get('$_basePath/');
      if (response.statusCode == 200 && response.data is List) {
        return List<String>.from(response.data as List);
      } else {
        throw ApiException(
          message: 'Failed to list running protocols',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Listing running protocols failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse list running protocols response: $e',
        s,
      );
    }
  }

  @override
  Future<ProtocolStatusResponse> getProtocolRunStatus({
    required String runGuid,
  }) async {
    try {
      // Corrected endpoint based on analysis: GET /api/protocols/{runGuid}
      // (assuming runGuid is used as {protocol_name} in backend for specific run status)
      // OR a more specific /runs/ endpoint if that's the actual backend structure.
      // Using /api/protocols/{runGuid} as per current backend file.
      final response = await _dio.get('$_basePath/$runGuid');
      if (response.statusCode == 200 && response.data is Map) {
        return ProtocolStatusResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Failed to get protocol run status for $runGuid',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message:
            e.message ?? 'Fetching protocol run status for $runGuid failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse protocol run status response for $runGuid: $e',
        s,
      );
    }
  }

  @override
  Future<RunCommandResponse> sendProtocolRunCommand({
    required String runGuid,
    required ProtocolRunCommand command,
  }) async {
    try {
      // Backend endpoint: POST /api/protocols/{run_guid}/command
      // Backend expects a simple string for command, or Form data.
      // Sending as JSON: {"command": "THE_COMMAND_STRING"}
      final response = await _dio.post(
        '$_basePath/$runGuid/command',
        data: {'command': protocolRunCommandToString(command)},
      );
      if (response.statusCode == 200 && response.data is Map) {
        return RunCommandResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message:
              'Failed to send command ${protocolRunCommandToString(command)} to run $runGuid',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message:
            e.message ??
            'Sending command ${protocolRunCommandToString(command)} to run $runGuid failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse run command response for $runGuid: $e',
        s,
      );
    }
  }

  @override
  Future<ProtocolPrepareResponse> prepareProtocol({
    required ProtocolPrepareRequest request,
  }) async {
    try {
      final response = await _dio.post(
        '$_basePath/prepare',
        data: request.toJson(),
      );
      if (response.statusCode == 200 && response.data is Map) {
        return ProtocolPrepareResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Failed to prepare protocol',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Protocol preparation failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse protocol prepare response: $e',
        s,
      );
    }
  }

  @override
  Future<ProtocolStatusResponse> startProtocol({
    required Map<String, dynamic> preparedConfig,
  }) async {
    try {
      final response = await _dio.post(
        '$_basePath/start',
        data: preparedConfig,
      );
      if (response.statusCode == 200 && response.data is Map) {
        return ProtocolStatusResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Failed to start protocol',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Protocol start failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException(
        'Failed to parse protocol start response: $e',
        s,
      );
    }
  }
}
