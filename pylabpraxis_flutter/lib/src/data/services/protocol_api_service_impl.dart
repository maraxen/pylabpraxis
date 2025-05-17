// Concrete implementation of the [ProtocolApiService] using Dio for HTTP communication.
//
// This class handles the actual API calls to the backend for protocol-related
// operations, including error handling and data parsing.

import 'dart:io'; // For File, if used for uploads
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart'; // For PlatformFile
import 'package:pylabpraxis_flutter/src/core/error/exceptions.dart';
import 'package:pylabpraxis_flutter/src/core/network/dio_client.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/deck_layout.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_status_response.dart';
import 'protocol_api_service.dart'; // The interface

class ProtocolApiServiceImpl implements ProtocolApiService {
  final DioClient _dioClient;

  ProtocolApiServiceImpl({required DioClient dioClient})
    : _dioClient = dioClient;

  Dio get _dio => _dioClient.dio;

  @override
  Future<List<ProtocolInfo>> discoverProtocols() async {
    try {
      final response = await _dio.get('/protocols/discover');
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
      // The ErrorInterceptor in DioClient should convert DioException
      // to a subclass of AppException. If it reaches here as DioException,
      // it means something was not caught by the interceptor or it's a new type.
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
  Future<ProtocolDetails> getProtocolDetails(String protocolPath) async {
    try {
      // Ensure the path is properly encoded if it contains special characters
      final encodedPath = Uri.encodeComponent(protocolPath);
      final response = await _dio.get('/protocols/details/$encodedPath');

      if (response.statusCode == 200 && response.data is Map) {
        return ProtocolDetails.fromJson(response.data as Map<String, dynamic>);
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
      final response = await _dio.get('/decks/layouts');
      if (response.statusCode == 200 && response.data is List) {
        // Assuming the API returns a list of strings (layout names/paths)
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

  @override
  Future<DeckLayout> uploadDeckFile({required PlatformFile file}) async {
    try {
      if (file.bytes == null) {
        throw ClientException(message: 'File bytes are null, cannot upload.');
      }
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(
          file.bytes!,
          filename: file.name,
          // You might need to specify contentType depending on backend requirements
          // contentType: MediaType('application', 'json'), // Example
        ),
      });

      final response = await _dio.post(
        '/decks/upload',
        data: formData,
        options: Options(
          headers: {
            // Dio might set this automatically for FormData, but can be explicit
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      if (response.statusCode == 200 ||
          response.statusCode == 201 && response.data is Map) {
        // Assuming the backend returns the created/updated DeckLayout object
        return DeckLayout.fromJson(response.data as Map<String, dynamic>);
      } else {
        throw ApiException(
          message: 'Failed to upload deck file',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.error is AppException) throw e.error as AppException;
      throw ApiException(
        message: e.message ?? 'Deck file upload failed',
        statusCode: e.response?.statusCode,
        stackTrace: e.stackTrace,
      );
    } catch (e, s) {
      throw DataParsingException('Failed to parse deck upload response: $e', s);
    }
  }

  @override
  Future<Map<String, dynamic>> prepareProtocol({
    required ProtocolPrepareRequest request,
  }) async {
    try {
      final response = await _dio.post(
        '/protocols/prepare',
        data: request.toJson(),
      );
      if (response.statusCode == 200 && response.data is Map) {
        return response.data as Map<String, dynamic>;
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
        '/protocols/start',
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
