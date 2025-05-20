part of 'protocols_discovery_bloc.dart';

// Using Freezed for immutable state classes
@freezed
sealed class ProtocolsDiscoveryState with _$ProtocolsDiscoveryState {
  /// Initial state, typically before any loading has begun.
  const factory ProtocolsDiscoveryState.initial() = ProtocolsDiscoveryInitial;

  /// State indicating that protocols are currently being loaded.
  const factory ProtocolsDiscoveryState.loading() = ProtocolsDiscoveryLoading;

  /// State indicating that protocols have been successfully loaded.
  /// Contains the list of [ProtocolInfo] objects.
  const factory ProtocolsDiscoveryState.loaded({
    required List<ProtocolInfo> protocols,
  }) = ProtocolsDiscoveryLoaded;

  /// State indicating that an error occurred while loading protocols.
  /// Contains an error [message].
  const factory ProtocolsDiscoveryState.error({required String message}) =
      ProtocolsDiscoveryError;
}
