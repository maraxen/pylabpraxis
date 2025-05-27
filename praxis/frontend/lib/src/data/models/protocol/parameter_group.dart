import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_constraints.dart';

part 'parameter_group.freezed.dart';
part 'parameter_group.g.dart';

@freezed
sealed class ParameterGroup with _$ParameterGroup {
  const factory ParameterGroup({
    required String name,
    String? displayName,
    String? description,
    @Default([]) List<ParameterDefinition> parameters,
  }) = _ParameterGroup;

  factory ParameterGroup.fromJson(Map<String, dynamic> json) =>
      _$ParameterGroupFromJson(json);
}

// Extension for creating parameter groups from a list of ParameterDefinitions
extension ParameterDefinitionListExtension on List<ParameterDefinition> {
  /// Organizes parameters into groups based on their 'group' property
  /// Parameters without a group are placed in a 'default' group
  List<ParameterGroup> organizeIntoGroups() {
    final Map<String, List<ParameterDefinition>> groupMap = {};

    // Sort parameters into groups
    for (var param in this) {
      final groupName = param.config.group ?? 'default';
      if (!groupMap.containsKey(groupName)) {
        groupMap[groupName] = [];
      }
      groupMap[groupName]!.add(param);
    }

    // Convert grouped map to list of ParameterGroup objects
    return groupMap.entries.map((entry) {
      return ParameterGroup(
        name: entry.key,
        displayName: entry.key != 'default' ? entry.key : 'Default',
        parameters: entry.value,
      );
    }).toList();
  }
}

// Extension to add helper methods to ProtocolDetails
extension ProtocolDetailsParameterExtension on ProtocolDetails {
  /// Converts parameters map to list of ParameterDefinition objects
  List<ParameterDefinition> get parameterDefinitions {
    return (parameters as Map<String, dynamic>).entries.map((entry) {
      if (entry.value is ParameterConfig) {
        return ParameterDefinition(
          name: entry.key,
          config: entry.value as ParameterConfig,
        );
      } else {
        // Handle case where value is a Map or other type
        final value = entry.value;
        final displayName =
            value is Map
                ? value['displayName'] as String? ?? entry.key
                : entry.key;
        final defaultValue = value is Map ? value['defaultValue'] : null;

        return ParameterDefinition(
          name: entry.key,
          displayName: displayName,
          defaultValue: defaultValue,
          config:
              value is ParameterConfig
                  ? value
                  : ParameterConfig(
                    type:
                        value is Map
                            ? value['type'] as String? ?? 'string'
                            : 'string',
                    displayName: displayName,
                    constraints:
                        value is Map
                            ? ParameterConstraints.fromJson(
                              value['constraints'] as Map<String, dynamic>,
                            )
                            : null,
                  ),
        );
      }
    }).toList();
  }

  /// Generates parameter groups from the individual parameters
  List<ParameterGroup> get derivedParameterGroups {
    return parameterDefinitions.organizeIntoGroups();
  }
}
