import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/repositories/protocol_repository.dart';

part 'protocols_discovery_event.dart';
part 'protocols_discovery_state.dart';
part 'protocols_discovery_bloc.freezed.dart';

/// BLoC responsible for managing the state of protocol discovery.
/// It fetches protocols from the [ProtocolRepository] and emits states
/// corresponding to the loading process, success, or failure.
class ProtocolsDiscoveryBloc
    extends Bloc<ProtocolsDiscoveryEvent, ProtocolsDiscoveryState> {
  final ProtocolRepository _protocolRepository;

  ProtocolsDiscoveryBloc({required ProtocolRepository protocolRepository})
    : _protocolRepository = protocolRepository,
      super(const ProtocolsDiscoveryState.initial()) {
    on<FetchDiscoveredProtocols>(_onFetchDiscoveredProtocols);
  }

  /// Handles the [FetchDiscoveredProtocols] event.
  ///
  /// Emits [ProtocolsDiscoveryLoading] state, then attempts to fetch protocols.
  /// If successful, emits [ProtocolsDiscoveryLoaded] with the fetched protocols.
  /// If an error occurs, emits [ProtocolsDiscoveryError] with an error message.
  Future<void> _onFetchDiscoveredProtocols(
    FetchDiscoveredProtocols event,
    Emitter<ProtocolsDiscoveryState> emit,
  ) async {
    emit(const ProtocolsDiscoveryState.loading());
    try {
      final protocols = await _protocolRepository.discoverProtocols();
      emit(ProtocolsDiscoveryState.loaded(protocols: protocols));
    } catch (e) {
      emit(
        ProtocolsDiscoveryState.error(
          message: 'Failed to fetch protocols: ${e.toString()}',
        ),
      );
    }
  }
}
