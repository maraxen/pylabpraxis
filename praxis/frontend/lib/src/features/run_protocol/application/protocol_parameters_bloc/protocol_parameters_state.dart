// File: lib/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_state.dart
part of 'protocol_parameters_bloc.dart'; // Ensures this is part of the BLoC's library

@freezed
sealed class ProtocolParametersState with _$ProtocolParametersState {
  const factory ProtocolParametersState.initial() =
      ProtocolParametersInitial; // Changed: _ProtocolParametersInitial -> ProtocolParametersInitial
  const factory ProtocolParametersState.loading() =
      ProtocolParametersLoading; // Changed: _ProtocolParametersLoading -> ProtocolParametersLoading

  const factory ProtocolParametersState.loaded({
    required ProtocolDetails protocolDetails,
    required RichFormState formState,
    @Default(false) bool isFormValid,
    @Default(0.0) double requiredParametersCompletionPercent,
  }) =
      ProtocolParametersLoaded; // Changed: _ProtocolParametersLoaded -> ProtocolParametersLoaded

  const factory ProtocolParametersState.error({required String message}) =
      ProtocolParametersError; // Changed: _ProtocolParametersError -> ProtocolParametersError
}
