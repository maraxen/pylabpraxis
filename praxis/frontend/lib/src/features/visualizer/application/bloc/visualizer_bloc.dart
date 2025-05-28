import 'dart:async';
import 'package:bloc/bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/deck_layout.dart';
import 'package:praxis_lab_management/src/data/services/workcell_api_service.dart';
import 'package:flutter/foundation.dart'; // For debugPrint

part 'visualizer_bloc.freezed.dart';

class VisualizerBloc extends Bloc<VisualizerEvent, VisualizerState> {
  final WorkcellApiService _workcellApiService;
  StreamSubscription<dynamic>? _workcellSubscription;

  VisualizerBloc(this._workcellApiService) : super(const VisualizerInitial()) {
    on<VisualizerLoadDeckStateRequested>(_onLoadDeckStateRequested);
    on<VisualizerWebSocketMessageReceived>(_onWebSocketMessageReceived);
    on<VisualizerWebSocketConnectionClosed>(_onWebSocketConnectionClosed);
    on<VisualizerDisposeRequested>(_onDisposeRequested);
  }

  Future<void> _onLoadDeckStateRequested(
    VisualizerLoadDeckStateRequested event,
    Emitter<VisualizerState> emit,
  ) async {
    emit(const VisualizerLoadInProgress());
    try {
      final deckLayout = await _workcellApiService.fetchDeckState(
        event.workcellId,
      );
      emit(VisualizerLoadSuccess(deckLayout));

      // Cancel any existing subscription before starting a new one
      await _workcellSubscription?.cancel();
      _workcellSubscription = _workcellApiService
          .subscribeToWorkcellUpdates(event.workcellId)
          .listen(
            (message) {
              add(VisualizerWebSocketMessageReceived(message));
            },
            onError: (error) {
              // Handle WebSocket errors if necessary, e.g., add a specific event
              debugPrint('VisualizerBloc: WebSocket error: $error');
              add(const VisualizerWebSocketConnectionClosed());
            },
            onDone: () {
              add(const VisualizerWebSocketConnectionClosed());
            },
          );
    } catch (e) {
      emit(VisualizerLoadFailure(e.toString()));
    }
  }

  void _onWebSocketMessageReceived(
    VisualizerWebSocketMessageReceived event,
    Emitter<VisualizerState> emit,
  ) {
    // Assuming the message is already the updated DeckLayout or relevant data
    // In a real scenario, you might parse event.message and potentially merge
    // it with existing state or transform it into a DeckLayout object.
    if (event.message is Map<String, dynamic>) {
      // Try to parse as DeckLayout if it's a map, otherwise pass as is
      try {
        // This is a placeholder. The actual message might not be a full DeckLayout.
        // It might be a partial update that needs to be applied to the current state.
        // For now, we'll assume the message *could* be a new DeckLayout.
        // Or, more simply, just pass the raw message for the UI to interpret.
        // final updatedDeckLayout = DeckLayout.fromJson(event.message as Map<String, dynamic>);
        // emit(VisualizerRealtimeUpdate(updatedDeckLayout));
        emit(VisualizerRealtimeUpdate(event.message));
        debugPrint(
          'VisualizerBloc: Realtime update received: ${event.message}',
        );
      } catch (e) {
        debugPrint(
          'VisualizerBloc: Error parsing WebSocket message: $e. Message: ${event.message}',
        );
        // Optionally emit a specific error state or just log
      }
    } else {
      // If the message is not a map, pass it directly.
      // The UI or a subsequent processing step will need to handle its type.
      emit(VisualizerRealtimeUpdate(event.message));
      debugPrint(
        'VisualizerBloc: Realtime update (non-map) received: ${event.message}',
      );
    }
  }

  void _onWebSocketConnectionClosed(
    VisualizerWebSocketConnectionClosed event,
    Emitter<VisualizerState> emit,
  ) {
    debugPrint('VisualizerBloc: WebSocket connection closed.');
    emit(const VisualizerDisconnected());
    _workcellSubscription?.cancel(); // Ensure subscription is cancelled
    _workcellSubscription = null;
  }

  Future<void> _onDisposeRequested(
    VisualizerDisposeRequested event,
    Emitter<VisualizerState> emit,
  ) async {
    debugPrint('VisualizerBloc: Dispose requested.');
    await _workcellSubscription?.cancel();
    _workcellSubscription = null;
    await _workcellApiService.closeWebSocket();
    // No specific state to emit on dispose, BLoC will be closed by its owner.
  }

  @override
  Future<void> close() {
    debugPrint(
      'VisualizerBloc: Closing BLoC, cancelling subscription and closing WebSocket.',
    );
    _workcellSubscription?.cancel();
    _workcellApiService.closeWebSocket(); // Ensure WebSocket is closed
    return super.close();
  }
}

/// Events for VisualizerBloc
@freezed
abstract class VisualizerEvent with _$VisualizerEvent {
  const factory VisualizerEvent.loadDeckStateRequested(String workcellId) =
      VisualizerLoadDeckStateRequested;
  const factory VisualizerEvent.webSocketMessageReceived(dynamic message) =
      VisualizerWebSocketMessageReceived;
  const factory VisualizerEvent.webSocketConnectionClosed() =
      VisualizerWebSocketConnectionClosed;
  const factory VisualizerEvent.disposeRequested() = VisualizerDisposeRequested;
}

/// States for VisualizerBloc
@freezed
abstract class VisualizerState with _$VisualizerState {
  const factory VisualizerState.initial() = VisualizerInitial;
  const factory VisualizerState.loadInProgress() = VisualizerLoadInProgress;
  const factory VisualizerState.loadSuccess(DeckLayout deckLayout) =
      VisualizerLoadSuccess;
  const factory VisualizerState.loadFailure(String error) =
      VisualizerLoadFailure;
  // For RealtimeUpdate, using 'dynamic' to be flexible with what WebSocket sends.
  // Could be a specific model if the WebSocket message structure is fixed.
  const factory VisualizerState.realtimeUpdate(dynamic updatedData) =
      VisualizerRealtimeUpdate;
  const factory VisualizerState.disconnected() = VisualizerDisconnected;
}
