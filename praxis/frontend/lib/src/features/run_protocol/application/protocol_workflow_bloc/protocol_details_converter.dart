import 'package:json_annotation/json_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_config.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_asset_detail.dart';

class ProtocolDetailsConverter
    implements JsonConverter<ProtocolDetails?, Map<String, dynamic>?> {
  const ProtocolDetailsConverter();

  /// Deserializes a JSON map into a [ProtocolDetails] object.
  @override
  ProtocolDetails? fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      return null;
    }

    // Manually parse the 'parameters' map from the persisted JSON
    final parametersMap = <String, ParameterConfig>{};
    if (json['parameters'] is Map) {
      (json['parameters'] as Map<String, dynamic>).forEach((key, value) {
        // ParameterConfig is serializable, so we can use its fromJson factory
        parametersMap[key] = ParameterConfig.fromJson(
          value as Map<String, dynamic>,
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

    return ProtocolDetails(
      name: json['name'] as String,
      path: json['path'] as String,
      description: json['description'] as String,
      parameters: parametersMap,
      assets: assetsList,
      hasAssets: json['hasAssets'] as bool,
      hasParameters: json['hasParameters'] as bool,
      requiresConfig: json['requiresConfig'] as bool,
    );
  }

  /// Serializes a [ProtocolDetails] object into a JSON map.
  @override
  Map<String, dynamic>? toJson(ProtocolDetails? object) {
    if (object == null) {
      return null;
    }
    return {
      'name': object.name,
      'path': object.path,
      'description': object.description,
      // ParameterConfig has a .toJson() method from its generated .g.dart file
      'parameters': object.parameters.map(
        (key, value) => MapEntry(key, value.toJson()),
      ),
      // ProtocolAssetDetail also has a .toJson() method
      'assets': object.assets.map((e) => e.toJson()).toList(),
      'hasAssets': object.hasAssets,
      'hasParameters': object.hasParameters,
      'requiresConfig': object.requiresConfig,
    };
  }
}
