part of 'protocol_start_bloc.dart';

@freezed
sealed class ProtocolStartEvent with _$ProtocolStartEvent {
  /// Event to initialize the Start Protocol Screen with the prepared configuration.
  const factory ProtocolStartEvent.initializeStartScreen({
    required Map<String, dynamic> preparedConfig,
  }) = InitializeStartScreen;

  /// Event to trigger the execution of the protocol.
  const factory ProtocolStartEvent.executeStartProtocol() =
      ExecuteStartProtocol;

  /// Event to reset the BLoC to its initial state.
  const factory ProtocolStartEvent.resetStart() = ResetStart;

  const factory ProtocolStartEvent.loadConfiguration({
    required Map<String, dynamic> preparedConfig,
  }) = LoadConfiguration;

  const factory ProtocolStartEvent.reportError({
    required String error,
    required Map<String, dynamic> preparedConfig,
  }) = ReportError;
}
