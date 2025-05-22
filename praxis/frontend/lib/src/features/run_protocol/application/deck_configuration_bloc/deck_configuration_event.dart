part of 'deck_configuration_bloc.dart';

@freezed
sealed class DeckConfigurationEvent with _$DeckConfigurationEvent {
  /// Event to fetch the list of available deck layouts from the backend/server.
  const factory DeckConfigurationEvent.fetchAvailableDeckLayouts() =
      FetchAvailableDeckLayouts;

  /// Event triggered when a user selects an existing deck layout from the dropdown.
  /// [layoutName] can be null if the selection is cleared or no layout is chosen.
  const factory DeckConfigurationEvent.deckLayoutSelected({
    String? layoutName,
  }) = DeckLayoutSelected;

  /// Event triggered when a user picks a deck layout file from their device.
  /// [file] is the [PlatformFile] object representing the picked file.
  const factory DeckConfigurationEvent.deckFilePicked({
    required PlatformFile file,
  }) = DeckFilePicked;

  /// Event to clear any current deck layout selection (either from available list or uploaded file).
  const factory DeckConfigurationEvent.clearDeckSelection() =
      ClearDeckSelection;

  /// Event to initialize the BLoC, potentially with pre-existing data if coming back to this step.
  const factory DeckConfigurationEvent.initializeDeckConfiguration({
    String? initialSelectedLayoutName,
    PlatformFile? initialPickedFile,
    List<String>? availableLayouts,
  }) = InitializeDeckConfiguration;
}
