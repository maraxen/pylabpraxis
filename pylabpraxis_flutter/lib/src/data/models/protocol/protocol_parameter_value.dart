// FILE: lib/src/data/models/protocol/protocol_parameter_value.dart
// Purpose: Represents the actual value of a configured parameter.
// This is a simple wrapper for now, might be expanded if values have more metadata.
// Corresponds to: ProtocolParameterValue in protocol.models.ts (which is `any`)
// For Dart, we often use `dynamic` for `any`, but if parameters always resolve
// to simple types or lists/maps of simple types, we can be more specific.
// Using dynamic for now to match `any`.

// No specific freezed class needed if it's just `dynamic`.
// However, if we want to enforce a structure for how parameters are stored,
// we might define a union type or a class here.
// For now, we'll assume parameters are stored as their direct Dart equivalents
// (String, int, double, bool, List<dynamic>, Map<String, dynamic>).
// If ProtocolParameterValue had a more defined structure in TypeScript,
// we would model it here.
//
// Example: if ProtocolParameterValue could be one of a few types
// @freezed
// abstract class ProtocolParameterValue with _$ProtocolParameterValue {
//   const factory ProtocolParameterValue.stringValue(String value) = StringValue;
//   const factory ProtocolParameterValue.intValue(int value) = IntValue;
//   // ... and so on
// }
// For now, direct Dart types will be used for parameter values.
