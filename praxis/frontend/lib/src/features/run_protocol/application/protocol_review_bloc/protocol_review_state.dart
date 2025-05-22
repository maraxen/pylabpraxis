part of 'protocol_review_bloc.dart';

@freezed
sealed class ProtocolReviewState with _$ProtocolReviewState {
  /// Initial state, before review data is loaded.
  const factory ProtocolReviewState.initial() = ProtocolReviewInitial;

  /// State indicating that all collected data is loaded and ready for display.
  const factory ProtocolReviewState.ready({
    required ReviewDataBundle displayData,
  }) = ProtocolReviewReady;

  /// State indicating that the protocol preparation request is in progress.
  /// It holds the data that is being prepared for display continuity.
  const factory ProtocolReviewState.preparationInProgress({
    required ReviewDataBundle reviewData,
  }) = ProtocolPreparationInProgress;

  /// State indicating that the protocol was successfully prepared by the backend.
  const factory ProtocolReviewState.preparationSuccess({
    required Map<String, dynamic> preparedConfig,
    required ReviewDataBundle reviewedData,
  }) = ProtocolPreparationSuccess;

  /// State indicating that protocol preparation failed.
  const factory ProtocolReviewState.preparationFailure({
    required String error,
    required ReviewDataBundle? displayData,
  }) = ProtocolPreparationFailure;
}
