// FILE: lib/src/data/models/protocol/protocol_step.dart
// Purpose: Defines the structure for a single step within a protocol.
// Corresponds to: ProtocolStep in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';
// Import other necessary models if ProtocolStep references them
// For example, if 'parameters' uses ParameterConfig, it would be imported here.
// import './parameter_config.dart';

part 'protocol_step.freezed.dart';
part 'protocol_step.g.dart';

@freezed
abstract class ProtocolStep with _$ProtocolStep {
  const factory ProtocolStep({
    // Unique identifier for the step.
    required String id,
    // Human-readable name or title of the step.
    required String name,
    // Detailed description of what happens in this step.
    String? description,
    // The command or function to be executed in this step.
    // e.g., 'aspirate', 'dispense', 'incubate', 'custom_script'.
    required String command,
    // Parameters specific to this command.
    // Structure will depend on the command; using Map<String, dynamic> for flexibility.
    // This might later be refined to use specific parameter types if commands are well-defined.
    Map<String, dynamic>? arguments,
    // Estimated duration for this step (e.g., "PT5M" for 5 minutes).
    @JsonKey(name: 'estimated_duration') String? estimatedDuration,
    // Order of execution.
    int? order,
    // Conditions under which this step should be skipped.
    String? skipConditions, // Could be a more structured condition object later
    // IDs of previous steps this step depends on.
    List<String>? dependencies,
    // Resources or assets required or used in this step.
    List<String>?
    resources, // e.g., names of assets defined in ProtocolDetails.assets
    // Visual representation or notes for the UI.
    Map<String, dynamic>? uiHints,
  }) = _ProtocolStep;

  // Factory constructor for deserializing JSON.
  factory ProtocolStep.fromJson(Map<String, dynamic> json) =>
      _$ProtocolStepFromJson(json);
}
