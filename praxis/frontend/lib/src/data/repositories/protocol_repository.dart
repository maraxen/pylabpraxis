// Defines the contract for protocol-related data operations.
//
// This abstract class serves as an interface for concrete repository
// implementations that will interact with data sources (like ProtocolApiService)
// to fetch and manage protocol information.

// For File
import 'package:file_picker/file_picker.dart'; // For PlatformFile
import 'package:praxis_lab_management/src/data/models/protocol/deck_layout.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_status_response.dart';
import 'package:praxis_lab_management/src/data/services/protocol_api_service.dart'; // Import ProtocolApiService

/// Abstract interface for protocol repositories.
///
/// Repositories coordinate data operations between data sources (e.g., API services)
/// and the application's business logic (e.g., BLoCs).
abstract class ProtocolRepository {
  Future<List<ProtocolInfo>> discoverProtocols();
  Future<ProtocolDetails> getProtocolDetails(String protocolPath);
  Future<List<String>> getDeckLayouts();
  Future<DeckLayout> uploadDeckFile({required PlatformFile file});
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
      // Log or handle specific exceptions if needed before rethrowing
      rethrow; // Propagate the exception (already an AppException or similar)
    }
  }

  @override
  Future<ProtocolDetails> getProtocolDetails(String protocolPath) async {
    try {
      return await _protocolApiService.getProtocolDetails(
        protocolPath: protocolPath,
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
  Future<DeckLayout> uploadDeckFile({required PlatformFile file}) async {
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
      return await _protocolApiService.prepareProtocol(request: request);
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
