part of 'protocols_discovery_bloc.dart';

// Using Freezed for immutable event classes
@freezed
sealed class ProtocolsDiscoveryEvent with _$ProtocolsDiscoveryEvent {
  /// Event to fetch the list of discovered protocols.
  const factory ProtocolsDiscoveryEvent.fetchDiscoveredProtocols() =
      FetchDiscoveredProtocols;
}
