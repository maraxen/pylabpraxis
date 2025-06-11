part of 'deck_instance_bloc.dart';

@freezed
sealed class DeckInstanceState with _$DeckInstanceState {
  /// Initial state before any layouts are fetched or selected.
  const factory DeckInstanceState.initial() = DeckInstanceInitial;

  /// State indicating that available deck layouts are being fetched.
  /// Optionally can carry previous data to avoid UI flicker if desired.
  const factory DeckInstanceState.loading({
    List<String>? availableLayouts, // Previous list while loading new one
    String? selectedLayoutName,
    PlatformFile? pickedFile,
  }) = DeckInstanceLoading;

  /// State indicating that deck layout options are loaded and ready for user interaction.
  const factory DeckInstanceState.loaded({
    required List<String> availableLayouts,
    String? selectedLayoutName,
    PlatformFile? pickedFile,
    @Default(false) bool isSelectionValid,
  }) = DeckInstanceLoaded;

  /// State indicating an error occurred.
  /// Optionally can carry previous data if error occurred during a refresh.
  const factory DeckInstanceState.error({
    required String message,
    // List<String>? availableLayoutsOnError,
    // String? selectedLayoutNameOnError,
    // PlatformFile? pickedFileOnError,
  }) = DeckInstanceError;
}
