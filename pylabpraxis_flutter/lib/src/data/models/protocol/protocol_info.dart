// FILE: lib/src/data/models/protocol/protocol_info.dart
// Purpose: Defines the basic information for a protocol.

import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_info.freezed.dart';
part 'protocol_info.g.dart';

// Enum for protocol complexity, mirroring the TypeScript union type.
enum ProtocolComplexity { low, medium, high }

@freezed
abstract class ProtocolInfo with _$ProtocolInfo {
  const factory ProtocolInfo({
    // Mandatory fields
    required String name,
    required String path,
    required String description,

    // Optional fields from TypeScript model
    String? version,
    @JsonKey(name: 'last_modified') DateTime? lastModified,
    List<String>? tags,
    String? author,
    String? license,
    @JsonKey(name: 'created_date') DateTime? createdDate,
    String? category,
    Map<String, dynamic>? metadata,
    @JsonKey(name: 'is_favorite') bool? isFavorite,
    @JsonKey(name: 'run_count') int? runCount,
    @JsonKey(name: 'average_rating') double? averageRating,
    @JsonKey(name: 'estimated_duration')
    String? estimatedDuration, // Could be parsed into Duration later
    ProtocolComplexity? complexity,
    @JsonKey(name: 'icon_url') String? iconUrl,
  }) = _ProtocolInfo;

  // Factory constructor for creating a new ProtocolInfo instance from a map.
  // This is used for deserializing JSON data.
  factory ProtocolInfo.fromJson(Map<String, dynamic> json) =>
      _$ProtocolInfoFromJson(json);
}
