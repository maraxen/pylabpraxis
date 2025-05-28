import 'package:file_picker/file_picker.dart';
import 'package:praxis_lab_management/src/data/models/protocol/file_upload_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_prepare_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_run_command.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_status_response.dart';
import 'package:praxis_lab_management/src/data/models/protocol/run_command_response.dart';

/// Abstract interface for protocol-related API services.
abstract class ProtocolApiService {
  /// Discovers available protocols from the backend.
  Future<List<ProtocolInfo>> discoverProtocols();

  /// Fetches detailed information for a specific protocol.
  Future<ProtocolDetails> getProtocolDetails({required String protocolPath});

  /// Fetches available deck layouts from the backend.
  Future<List<String>> getDeckLayouts();

  /// Uploads a new deck layout file to the backend.
  Future<FileUploadResponse> uploadDeckFile({required PlatformFile file});

  /// Uploads a new protocol configuration file to the backend.
  Future<FileUploadResponse> uploadConfigFile({required PlatformFile file});

  /// Fetches JSONSchema for a protocol's parameters.
  Future<Map<String, dynamic>> getProtocolSchema({
    required String protocolPath,
  });

  /// Lists all running/active protocols (or runs).
  /// Backend `GET /api/protocols/` returns List<String> of protocol names.
  /// This might need adjustment if the goal is to list "runs" with more details.
  Future<List<String>> listRunningProtocols();

  /// Gets the status of a specific protocol run.
  /// Assumes an endpoint like GET /api/protocols/runs/{runGuid} or similar exists.
  Future<ProtocolStatusResponse> getProtocolRunStatus({
    required String runGuid,
  });

  /// Sends a control command (PAUSE, RESUME, CANCEL) to a specific protocol run.
  Future<RunCommandResponse> sendProtocolRunCommand({
    required String runGuid,
    required ProtocolRunCommand command,
  });

  /// Prepares a protocol for execution with the given configuration.
  Future<ProtocolPrepareResponse> prepareProtocol({
    required ProtocolPrepareRequest request,
  });

  /// Starts the execution of a previously prepared protocol.
  /// The backend `POST /start` takes the config from `/prepare` response.
  /// It returns `ProtocolStatus` which is `name` and `status`.
  /// `ProtocolStatusResponse` should be compatible with this.
  Future<ProtocolStatusResponse> startProtocol({
    required Map<String, dynamic> preparedConfig,
  });
}
