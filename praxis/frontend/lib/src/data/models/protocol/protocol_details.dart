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

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_parameter_detail.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_asset_detail.dart';

part 'protocol_details.freezed.dart';
part 'protocol_details.g.dart';

@freezed
class ProtocolDetails with _$ProtocolDetails {
  const factory ProtocolDetails({
    required String name,
    required String path,
    required String description,
    required Map<String, ProtocolParameterDetail> parameters,
    required List<ProtocolAssetDetail> assets,
    required bool hasAssets,
    required bool hasParameters,
    // Corresponds to 'requires_config' in backend.
    // Based on backend logic: `not (bool(parameters) or bool(assets))`,
    // this field is true if there are NO parameters AND NO assets.
    // Consider renaming to 'isSimple' or 'requiresNoConfiguration' for clarity if appropriate.
    required bool requiresConfig,
  }) = _ProtocolDetails;

  factory ProtocolDetails.fromJson(Map<String, dynamic> json) =>
      _$ProtocolDetailsFromJson(json);
}
