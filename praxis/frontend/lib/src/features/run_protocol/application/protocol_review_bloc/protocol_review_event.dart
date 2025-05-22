part of 'protocol_review_bloc.dart';

@freezed
sealed class ProtocolReviewEvent with _$ProtocolReviewEvent {
  /// Event to load all collected data for review.
  const factory ProtocolReviewEvent.loadReviewData({
    required ReviewDataBundle reviewData,
  }) = LoadReviewData;

  /// Event to request the preparation of the protocol with the backend.
  const factory ProtocolReviewEvent.prepareProtocolRequested() =
      PrepareProtocolRequested;

  /// Event to reset the BLoC to its initial state.
  const factory ProtocolReviewEvent.resetReview() = ResetReview;
}
