// FILE: lib/src/data/models/protocol/protocol_hardware.dart
// Purpose: Defines hardware requirements or configurations for the protocol.
// Corresponds to: ProtocolHardware in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_hardware.freezed.dart';
part 'protocol_hardware.g.dart';

@freezed
abstract class ProtocolHardware with _$ProtocolHardware {
  const factory ProtocolHardware({
    // Name of the hardware component (e.g., 'pipette_p300_single', 'temperature_module').
    required String name,
    // Type of hardware (e.g., 'pipette', 'module', 'robot_arm').
    required String type,
    // Specific configuration or settings for this hardware.
    // e.g., { 'mount': 'left', 'model': 'GEN2' }
    Map<String, dynamic>? configuration,
    // Indicates if this hardware is mandatory for the protocol.
    @Default(true) bool required,
    // Optional human-readable description or purpose.
    String? description,
  }) = _ProtocolHardware;

  // Factory constructor for deserializing JSON.
  factory ProtocolHardware.fromJson(Map<String, dynamic> json) =>
      _$ProtocolHardwareFromJson(json);
}
