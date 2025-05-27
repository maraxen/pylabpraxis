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

part 'protocol_parameter_detail.freezed.dart';
part 'protocol_parameter_detail.g.dart';

@freezed
class ProtocolParameterDetail with _$ProtocolParameterDetail {
  const factory ProtocolParameterDetail({
    required String type,
    required bool required,
    dynamic defaultValue, // 'default' is a reserved keyword in Dart
    String? description,
    Map<String, dynamic>? constraints,
  }) = _ProtocolParameterDetail;

  factory ProtocolParameterDetail.fromJson(Map<String, dynamic> json) {
    // Handle 'default' keyword conflict
    final Map<String, dynamic> updatedJson = Map.from(json);
    if (json.containsKey('default')) {
      updatedJson['defaultValue'] = json['default'];
      updatedJson.remove('default');
    }
    return _$ProtocolParameterDetailFromJson(updatedJson);
  }
}
