// Defines the contract for interacting with the protocol-related backend APIs.
//
// This abstract class serves as an interface for concrete implementations
// that will handle HTTP requests for discovering protocols, fetching details,
// preparing runs, and starting protocols.

import 'dart:io'; // For File, if used directly for uploads

import 'package:file_picker/file_picker.dart'; // For PlatformFile
import 'package:pylabpraxis_flutter/src/data/models/protocol/deck_layout.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_status_response.dart';

/// Abstract interface for protocol-related API services.
///
/// Implementations of this class will provide methods to interact with the
/// backend API endpoints for managing and executing protocols.
abstract class ProtocolApiService {
  /// Discovers available protocols from the backend.
  ///
  /// Returns a list of [ProtocolInfo] objects, each representing a summary
  /// of an available protocol.
  /// Throws [ApiException] or its subclasses on API errors.
  Future<List<ProtocolInfo>> discoverProtocols();

  /// Fetches detailed information for a specific protocol.
  ///
  /// Parameters:
  ///   [protocolPath] - The unique path or identifier of the protocol.
  ///
  /// Returns a [ProtocolDetails] object containing comprehensive information
  /// about the protocol, including its parameters, assets, and steps.
  /// Throws [ApiException] or its subclasses on API errors.
  Future<ProtocolDetails> getProtocolDetails(String protocolPath);

  /// Fetches available deck layouts from the backend.
  ///
  /// Returns a list of strings, where each string is the name or identifier
  /// of an available deck layout.
  /// Alternatively, this could return `List<DeckLayoutInfo>` if more structured
  /// information about layouts is available from the API.
  /// Throws [ApiException] or its subclasses on API errors.
  Future<List<String>> getDeckLayouts(); // Or Future<List<DeckLayoutInfo>>

  /// Uploads a new deck layout file to the backend.
  ///
  /// Parameters:
  ///   [file] - The deck layout file to upload. This could be a [File] from `dart:io`
  ///            or [PlatformFile] from `file_picker` if using bytes.
  ///
  /// Returns a [DeckLayout] object representing the uploaded and processed layout,
  /// or void if the API doesn't return the full layout on upload.
  /// Throws [ApiException] or its subclasses on API errors.
  Future<DeckLayout> uploadDeckFile({
    required PlatformFile file,
  }); // Or File file

  /// Prepares a protocol for execution with the given configuration.
  ///
  /// Parameters:
  ///   [request] - A [ProtocolPrepareRequest] object containing the protocol path,
  ///               configured parameters, assigned assets, and deck layout information.
  ///
  /// Returns a map representing the prepared configuration from the backend,
  /// which is typically then used to start the protocol. This could also be
  /// a more specific response model like `ProtocolPreparedResponse`.
  /// Throws [ApiException] or its subclasses on API errors.
  Future<Map<String, dynamic>> prepareProtocol({
    required ProtocolPrepareRequest request,
  });

  /// Starts the execution of a previously prepared protocol.
  ///
  /// Parameters:
  ///   [preparedConfig] - The configuration map returned by the `prepareProtocol` call.
  ///
  /// Returns a [ProtocolStatusResponse] object indicating the status of the
  /// initiated protocol run.
  /// Throws [ApiException] or its subclasses on API errors.
  Future<ProtocolStatusResponse> startProtocol({
    required Map<String, dynamic> preparedConfig,
  });
}
