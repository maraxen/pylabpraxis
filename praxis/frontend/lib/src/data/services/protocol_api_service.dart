// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:file_picker/file_picker.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/file_upload_response.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_prepare_response.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_run_command.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_status_response.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/run_command_response.dart';

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
  Future<Map<String, dynamic>> getProtocolSchema(
      {required String protocolPath});

  /// Lists all running/active protocols (or runs).
  /// Backend `GET /api/protocols/` returns List<String> of protocol names.
  /// This might need adjustment if the goal is to list "runs" with more details.
  Future<List<String>> listRunningProtocols();

  /// Gets the status of a specific protocol run.
  /// Assumes an endpoint like GET /api/protocols/runs/{runGuid} or similar exists.
  Future<ProtocolStatusResponse> getProtocolRunStatus(
      {required String runGuid});

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
