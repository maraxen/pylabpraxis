import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:file_picker/file_picker.dart';
// Assuming ProtocolRepository can fetch deck layouts.
// If not, a dedicated DeckRepository might be needed.
import 'package:praxis_lab_management/src/data/repositories/protocol_repository.dart';

part 'deck_instance_event.dart';
part 'deck_instance_state.dart';
part 'deck_instance_bloc.freezed.dart';

class DeckInstanceBloc extends Bloc<DeckInstanceEvent, DeckInstanceState> {
  // TODO: Replace with a specific repository if ProtocolRepository doesn't handle deck layouts.
  final ProtocolRepository _protocolRepository;

  DeckInstanceBloc({required ProtocolRepository protocolRepository})
    : _protocolRepository = protocolRepository,
      super(const DeckInstanceState.initial()) {
    on<InitializeDeckInstance>(_onInitializeDeckInstance);
    on<FetchAvailableDeckLayouts>(_onFetchAvailableDeckLayouts);
    on<DeckLayoutSelected>(_onDeckLayoutSelected);
    on<DeckFilePicked>(_onDeckFilePicked);
    on<ClearDeckSelection>(_onClearDeckSelection);
  }

  void _onInitializeDeckInstance(
    InitializeDeckInstance event,
    Emitter<DeckInstanceState> emit,
  ) {
    List<String> layouts = event.availableLayouts ?? [];
    bool isValid =
        (event.initialSelectedLayoutName != null &&
            event.initialSelectedLayoutName!.isNotEmpty) ||
        event.initialPickedFile != null;

    // If layouts are provided, directly go to loaded state.
    // Otherwise, if no initial selection, stay initial to trigger fetch later.
    if (layouts.isNotEmpty ||
        event.initialSelectedLayoutName != null ||
        event.initialPickedFile != null) {
      emit(
        DeckInstanceState.loaded(
          availableLayouts: layouts,
          selectedLayoutName: event.initialSelectedLayoutName,
          pickedFile: event.initialPickedFile,
          isSelectionValid: isValid,
        ),
      );
    } else {
      emit(const DeckInstanceState.initial());
      // Optionally, if this init implies a fresh start, trigger fetch:
      // add(const FetchAvailableDeckLayouts());
    }
  }

  Future<void> _onFetchAvailableDeckLayouts(
    FetchAvailableDeckLayouts event,
    Emitter<DeckInstanceState> emit,
  ) async {
    // Preserve current selection if any, while loading new list
    String? currentSelectedLayout;
    PlatformFile? currentPickedFile;
    List<String> existingLayouts = []; // To revert to on error if needed

    final currentState = state; // Capture current state before emitting loading
    if (currentState is DeckInstanceLoaded) {
      currentSelectedLayout = currentState.selectedLayoutName;
      currentPickedFile = currentState.pickedFile;
      existingLayouts = currentState.availableLayouts;
    }

    emit(const DeckInstanceState.loading());
    try {
      // TODO: Implement _protocolRepository.getAvailableDeckLayouts()
      // This is a placeholder for actual API call.
      // final layouts = await _protocolRepository.getAvailableDeckLayouts();
      await Future.delayed(
        const Duration(milliseconds: 700),
      ); // Simulate network delay
      final layouts = [
        'Default Layout Alpha',
        'Standard Setup Beta',
        'Custom Rig Gamma',
        'Empty Deck',
      ];

      String? finalSelectedLayout = currentSelectedLayout;
      PlatformFile? finalPickedFile = currentPickedFile;

      // After fetching, if a picked file exists, it takes precedence.
      if (finalPickedFile != null) {
        finalSelectedLayout = null; // Picked file overrides dropdown selection
      } else if (finalSelectedLayout != null &&
          !layouts.contains(finalSelectedLayout)) {
        // If previously selected layout is no longer in the new list, clear it.
        finalSelectedLayout = null;
      }

      emit(
        DeckInstanceState.loaded(
          availableLayouts: layouts,
          selectedLayoutName: finalSelectedLayout,
          pickedFile: finalPickedFile, // Keep picked file if it was there
          isSelectionValid:
              (finalSelectedLayout != null && finalSelectedLayout.isNotEmpty) ||
              finalPickedFile != null,
        ),
      );
    } catch (e) {
      // On error, emit error state, potentially with the old data if available
      emit(
        DeckInstanceState.error(
          message: 'Failed to fetch deck layouts: ${e.toString()}',
          // You could add fields to DeckInstanceError to hold previous valid data:
          // previousAvailableLayouts: existingLayouts,
          // previousSelectedLayoutName: currentSelectedLayout,
          // previousPickedFile: currentPickedFile,
        ),
      );
    }
  }

  void _onDeckLayoutSelected(
    DeckLayoutSelected event,
    Emitter<DeckInstanceState> emit,
  ) {
    // This event should only be processed if the BLoC is in a loaded state
    // or an error state where availableLayouts might still be relevant.
    final currentState = state;
    List<String> availableLayouts = [];

    if (currentState is DeckInstanceLoaded) {
      availableLayouts = currentState.availableLayouts;
    } else if (currentState is DeckInstanceError) {
      // If in error state, you might want to use previously known layouts if your error state carries them.
      // For now, assume if not loaded, availableLayouts is empty or from a default.
      // This scenario (selecting while not loaded) should ideally be prevented by UI.
    }

    emit(
      DeckInstanceState.loaded(
        availableLayouts:
            availableLayouts, // Preserve the list of available layouts
        selectedLayoutName: event.layoutName,
        pickedFile:
            null, // Clear picked file if a layout is selected from dropdown
        isSelectionValid:
            event.layoutName != null && event.layoutName!.isNotEmpty,
      ),
    );
  }

  void _onDeckFilePicked(
    DeckFilePicked event,
    Emitter<DeckInstanceState> emit,
  ) {
    List<String> currentAvailable = [];
    final currentState = state;
    if (currentState is DeckInstanceLoaded) {
      currentAvailable = currentState.availableLayouts;
    } else if (currentState is DeckInstanceError) {
      // Potentially use layouts from error state if it carries them
    }

    emit(
      DeckInstanceState.loaded(
        availableLayouts: currentAvailable,
        pickedFile: event.file,
        selectedLayoutName: null,
        isSelectionValid: true,
      ),
    );
  }

  void _onClearDeckSelection(
    ClearDeckSelection event,
    Emitter<DeckInstanceState> emit,
  ) {
    List<String> currentAvailable = [];
    final currentState = state;
    if (currentState is DeckInstanceLoaded) {
      currentAvailable = currentState.availableLayouts;
    } else if (currentState is DeckInstanceError) {
      // If clearing from an error state, you might want to retain the available layouts list
      // if your error state was designed to hold it.
    }
    // Always transition to a 'loaded' state with selections cleared,
    // preserving the list of available layouts if known.
    emit(
      DeckInstanceState.loaded(
        availableLayouts: currentAvailable,
        selectedLayoutName: null,
        pickedFile: null,
        isSelectionValid: false,
      ),
    );
  }
}
