part of 'protocol_parameters_bloc.dart';

@freezed
sealed class ProtocolParametersState with _$ProtocolParametersState {
  const factory ProtocolParametersState.initial() = _ProtocolParametersInitial;
  const factory ProtocolParametersState.loading() = _ProtocolParametersLoading;

  const factory ProtocolParametersState.loaded({
    required ProtocolDetails protocolDetails,
    required RichFormState formState,
    @Default(false)
    bool
    isFormValid, // Overall form validity (all fields valid by their constraints)
    @Default(0.0)
    double
    requiredParametersCompletionPercent, // New: progress of explicitly set required fields
  }) = _ProtocolParametersLoaded;

  const factory ProtocolParametersState.error({required String message}) =
      _ProtocolParametersError;
}
