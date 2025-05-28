import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_config.dart'; // ADD this import
import 'package:praxis_lab_management/src/data/models/protocol/protocol_asset_detail.dart';

part 'protocol_details.freezed.dart';

@freezed
sealed class ProtocolDetails with _$ProtocolDetails {
  const factory ProtocolDetails({
    required String name,
    required String path,
    required String description,
    required Map<String, ParameterConfig> parameters, // UPDATE this line
    required List<ProtocolAssetDetail> assets,
    required bool hasAssets,
    required bool hasParameters,
    required bool requiresConfig,
  }) = _ProtocolDetails;
}

class ParameterGroup {
  final String name;
  final List<ParameterDefinition> parameters;

  ParameterGroup({required this.name, required this.parameters});
}

extension ProtocolDetailsExtension on ProtocolDetails {
  /// Derives a map of [ParameterDefinition]s from the protocol's parameters.
  Map<String, ParameterDefinition> get parameterDefinitions {
    return parameters.map(
      (key, config) => MapEntry(
        key,
        ParameterDefinition(
          name: key,
          displayName: config.displayName ?? key,
          description: config.description,
          defaultValue: config.defaultValue,
          config: config,
        ),
      ),
    );
  }

  List<ParameterGroup> get derivedParameterGroups {
    final groupNames =
        parameters.values
            .map((p) => p.group)
            .where((g) => g != null && g.isNotEmpty)
            .toSet()
            .toList();

    // Create ParameterGroup objects for each group name
    return groupNames.map((groupName) {
      // Find all parameters that belong to this group
      final groupParameters =
          parameterDefinitions.values
              .where((param) => param.config.group == groupName)
              .toList();

      return ParameterGroup(
        name: groupName!, // Safe to use ! here due to the where filter above
        parameters: groupParameters,
      );
    }).toList();
  }
}
