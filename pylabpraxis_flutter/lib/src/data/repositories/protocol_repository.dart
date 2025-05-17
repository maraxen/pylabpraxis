// lib/src/data/repositories/protocol_repository.dart

import '../services/protocol_api_service.dart';

// Interface for Protocol Repository
abstract class ProtocolRepository {
  Future<List<String>> getDiscoveredProtocols();
  // Add other methods that BLoCs will use
}

// Implementation of ProtocolRepository
class ProtocolRepositoryImpl implements ProtocolRepository {
  final ProtocolApiService _protocolApiService;

  ProtocolRepositoryImpl({required ProtocolApiService protocolApiService})
    : _protocolApiService = protocolApiService;

  @override
  Future<List<String>> getDiscoveredProtocols() =>
      _protocolApiService.discoverProtocols();
}
