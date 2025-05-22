part of 'protocol_start_bloc.dart';

@freezed
sealed class ProtocolStartState with _$ProtocolStartState {
  /// Initial state, before the prepared configuration is loaded.
  const factory ProtocolStartState.initial() = ProtocolStartInitial;

  /// State indicating the prepared configuration is loaded and displayed.
  const factory ProtocolStartState.ready({
    required Map<String, dynamic> preparedConfig,
  }) = ProtocolStartReady;

  /// State indicating that the command to start protocol execution is in progress.
  const factory ProtocolStartState.startingExecution({
    required Map<String, dynamic> preparedConfig,
  }) = ProtocolStartingExecution;

  /// State indicating that the protocol execution started successfully.
  const factory ProtocolStartState.success({
    required ProtocolStatusResponse response,
    required Map<String, dynamic> preparedConfig, // The config that was started
  }) = ProtocolStartSuccess;

  /// State indicating that an error occurred while trying to start the protocol.
  const factory ProtocolStartState.failure({
    required String error,
    required Map<String, dynamic>
    preparedConfig, // The config that failed to start
  }) = ProtocolStartFailure;
}
