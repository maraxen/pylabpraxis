part of 'deck_configuration_bloc.dart';

@freezed
sealed class DeckConfigurationState with _$DeckConfigurationState {
  /// Initial state before any layouts are fetched or selected.
  const factory DeckConfigurationState.initial() = DeckConfigurationInitial;

  /// State indicating that available deck layouts are being fetched.
  /// Optionally can carry previous data to avoid UI flicker if desired.
  const factory DeckConfigurationState.loading({
    List<String>? availableLayouts, // Previous list while loading new one
    String? selectedLayoutName,
    PlatformFile? pickedFile,
  }) = DeckConfigurationLoading;

  /// State indicating that deck layout options are loaded and ready for user interaction.
  const factory DeckConfigurationState.loaded({
    required List<String> availableLayouts,
    String? selectedLayoutName,
    PlatformFile? pickedFile,
    @Default(false) bool isSelectionValid,
  }) = DeckConfigurationLoaded;

  /// State indicating an error occurred.
  /// Optionally can carry previous data if error occurred during a refresh.
  const factory DeckConfigurationState.error({
    required String message,
    // List<String>? availableLayoutsOnError,
    // String? selectedLayoutNameOnError,
    // PlatformFile? pickedFileOnError,
  }) = DeckConfigurationError;
}
