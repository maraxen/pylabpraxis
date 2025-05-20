import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_status_response.dart';
import 'package:pylabpraxis_flutter/src/data/repositories/protocol_repository.dart';

part 'protocol_start_event.dart';
part 'protocol_start_state.dart';
part 'protocol_start_bloc.freezed.dart';

class ProtocolStartBloc extends Bloc<ProtocolStartEvent, ProtocolStartState> {
  final ProtocolRepository _protocolRepository;

  ProtocolStartBloc({required ProtocolRepository protocolRepository})
    : _protocolRepository = protocolRepository,
      super(const ProtocolStartState.initial()) {
    on<InitializeStartScreen>(_onInitializeStartScreen);
    on<ExecuteStartProtocol>(_onExecuteStartProtocol);
    on<ResetStart>(_onResetStart);
  }

  void _onInitializeStartScreen(
    InitializeStartScreen event,
    Emitter<ProtocolStartState> emit,
  ) {
    emit(ProtocolStartState.ready(preparedConfig: event.preparedConfig));
  }

  Future<void> _onExecuteStartProtocol(
    ExecuteStartProtocol event,
    Emitter<ProtocolStartState> emit,
  ) async {
    Map<String, dynamic>? configToExecute;

    // Get config from the current state, which should be Ready or Failure
    final currentState = state; // Capture current state
    if (currentState is ProtocolStartReady) {
      configToExecute = currentState.preparedConfig;
    } else if (currentState is ProtocolStartFailure) {
      configToExecute = currentState.preparedConfig;
    }

    if (configToExecute == null) {
      emit(
        const ProtocolStartState.failure(
          error: 'Cannot start protocol: Prepared configuration not available.',
          preparedConfig: {},
        ),
      );
      return;
    }

    emit(ProtocolStartState.startingExecution(preparedConfig: configToExecute));
    try {
      final response = await _protocolRepository.startProtocol(
        preparedConfig: configToExecute,
      );
      emit(
        ProtocolStartState.success(
          response: response,
          preparedConfig: configToExecute,
        ),
      );
    } catch (e) {
      emit(
        ProtocolStartState.failure(
          error: 'Failed to start protocol execution: ${e.toString()}',
          preparedConfig: configToExecute,
        ),
      );
    }
  }

  void _onResetStart(ResetStart event, Emitter<ProtocolStartState> emit) {
    emit(const ProtocolStartState.initial());
  }
}
