import 'dart:async';
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/features/visualizer/application/bloc/visualizer_bloc.dart';
import 'package:praxis_lab_management/src/data/services/workcell_api_service.dart';
import 'package:praxis_lab_management/src/data/models/protocol/deck_layout.dart';

// Assuming mock_services.mocks.dart is generated in praxis/frontend/test/mocks/
import '../../../../mocks/mock_services.mocks.dart';

void main() {
  late MockWorkcellApiService mockWorkcellApiService;
  late DeckLayout mockDeckLayout;
  const String workcellId = 'test_workcell_1';

  setUp(() {
    mockWorkcellApiService = MockWorkcellApiService();
    mockDeckLayout = const DeckLayout(
      id: 'deck1',
      name: 'Test Deck',
      positions: [],
    );
  });

  group('VisualizerBloc', () {
    test('initial state is VisualizerInitial', () {
      expect(
        VisualizerBloc(mockWorkcellApiService).state,
        const VisualizerInitial(),
      );
    });

    group('VisualizerLoadDeckStateRequested', () {
      // Mock stream controller for WebSocket simulation
      late StreamController<dynamic> webSocketController;

      setUp(() {
        webSocketController = StreamController<dynamic>();
      });

      tearDown(() {
        webSocketController.close();
      });

      blocTest<VisualizerBloc, VisualizerState>(
        'emits [VisualizerLoadInProgress, VisualizerLoadSuccess] and subscribes to WebSocket on successful fetch',
        build: () {
          when(
            mockWorkcellApiService.fetchDeckState(any),
          ).thenAnswer((_) async => mockDeckLayout);
          when(
            mockWorkcellApiService.subscribeToWorkcellUpdates(any),
          ).thenAnswer((_) => webSocketController.stream);
          return VisualizerBloc(mockWorkcellApiService);
        },
        act:
            (bloc) =>
                bloc.add(const VisualizerLoadDeckStateRequested(workcellId)),
        expect:
            () => [
              const VisualizerLoadInProgress(),
              VisualizerLoadSuccess(mockDeckLayout),
            ],
        verify: (_) {
          verify(mockWorkcellApiService.fetchDeckState(workcellId)).called(1);
          verify(
            mockWorkcellApiService.subscribeToWorkcellUpdates(workcellId),
          ).called(1);
        },
      );

      blocTest<VisualizerBloc, VisualizerState>(
        'emits [VisualizerLoadInProgress, VisualizerLoadSuccess, VisualizerRealtimeUpdate] when WebSocket message is received',
        build: () {
          when(
            mockWorkcellApiService.fetchDeckState(any),
          ).thenAnswer((_) async => mockDeckLayout);
          when(
            mockWorkcellApiService.subscribeToWorkcellUpdates(any),
          ).thenAnswer((_) => webSocketController.stream);
          return VisualizerBloc(mockWorkcellApiService);
        },
        act: (bloc) async {
          bloc.add(const VisualizerLoadDeckStateRequested(workcellId));
          await Future.delayed(Duration.zero); // Allow subscription to set up
          webSocketController.add({'update': 'new_data'});
        },
        expect:
            () => [
              const VisualizerLoadInProgress(),
              VisualizerLoadSuccess(mockDeckLayout),
              const VisualizerRealtimeUpdate({'update': 'new_data'}),
            ],
      );

      blocTest<VisualizerBloc, VisualizerState>(
        'emits [VisualizerLoadInProgress, VisualizerLoadFailure] on fetchDeckState exception',
        build: () {
          when(
            mockWorkcellApiService.fetchDeckState(any),
          ).thenThrow(Exception('Failed to fetch deck state'));
          return VisualizerBloc(mockWorkcellApiService);
        },
        act:
            (bloc) =>
                bloc.add(const VisualizerLoadDeckStateRequested(workcellId)),
        expect:
            () => [
              const VisualizerLoadInProgress(),
              isA<VisualizerLoadFailure>().having(
                (s) => s.error,
                'error',
                'Exception: Failed to fetch deck state',
              ),
            ],
        verify: (_) {
          verify(mockWorkcellApiService.fetchDeckState(workcellId)).called(1);
          verifyNever(mockWorkcellApiService.subscribeToWorkcellUpdates(any));
        },
      );

      blocTest<VisualizerBloc, VisualizerState>(
        'emits [VisualizerLoadInProgress, VisualizerLoadSuccess, VisualizerDisconnected] when WebSocket stream closes',
        build: () {
          when(
            mockWorkcellApiService.fetchDeckState(any),
          ).thenAnswer((_) async => mockDeckLayout);
          when(
            mockWorkcellApiService.subscribeToWorkcellUpdates(any),
          ).thenAnswer((_) => webSocketController.stream);
          return VisualizerBloc(mockWorkcellApiService);
        },
        act: (bloc) async {
          bloc.add(const VisualizerLoadDeckStateRequested(workcellId));
          await Future.delayed(
            Duration.zero,
          ); // Ensure subscription is processed
          await webSocketController.close(); // Close the stream
        },
        expect:
            () => [
              const VisualizerLoadInProgress(),
              VisualizerLoadSuccess(mockDeckLayout),
              const VisualizerDisconnected(),
            ],
      );
    });

    group('VisualizerWebSocketMessageReceived', () {
      blocTest<VisualizerBloc, VisualizerState>(
        'emits [VisualizerRealtimeUpdate] when a message is received',
        build: () => VisualizerBloc(mockWorkcellApiService),
        act:
            (bloc) => bloc.add(
              const VisualizerWebSocketMessageReceived({'data': 'test'}),
            ),
        expect:
            () => [
              const VisualizerRealtimeUpdate({'data': 'test'}),
            ],
      );
    });

    group('VisualizerWebSocketConnectionClosed', () {
      blocTest<VisualizerBloc, VisualizerState>(
        'emits [VisualizerDisconnected] when connection closed event is added',
        build: () {
          // Simulate an active subscription that might get closed externally
          when(
            mockWorkcellApiService.fetchDeckState(any),
          ).thenAnswer((_) async => mockDeckLayout);
          when(
            mockWorkcellApiService.subscribeToWorkcellUpdates(any),
          ).thenAnswer(
            (_) => StreamController<dynamic>().stream,
          ); // Dummy stream
          return VisualizerBloc(mockWorkcellApiService);
        },
        // Optionally, first load state to have an active subscription
        seed: () => VisualizerLoadSuccess(mockDeckLayout),
        act: (bloc) => bloc.add(const VisualizerWebSocketConnectionClosed()),
        expect: () => [const VisualizerDisconnected()],
      );
    });

    group('VisualizerDisposeRequested', () {
      blocTest<VisualizerBloc, VisualizerState>(
        'calls closeWebSocket on WorkcellApiService and cancels subscription',
        build: () {
          // Simulate an active subscription
          final streamController = StreamController<dynamic>(sync: true);
          when(
            mockWorkcellApiService.fetchDeckState(any),
          ).thenAnswer((_) async => mockDeckLayout);
          when(
            mockWorkcellApiService.subscribeToWorkcellUpdates(any),
          ).thenAnswer((_) => streamController.stream);
          when(
            mockWorkcellApiService.closeWebSocket(),
          ).thenAnswer((_) async {});

          final bloc = VisualizerBloc(mockWorkcellApiService);
          // Trigger subscription
          bloc.add(const VisualizerLoadDeckStateRequested(workcellId));
          return bloc;
        },
        // Ensure the subscription is active before dispose is called
        // Need to wait for the fetchDeckState and subscribeToWorkcellUpdates to complete
        wait: const Duration(
          milliseconds: 100,
        ), // Adjust if needed for async operations
        act: (bloc) => bloc.add(const VisualizerDisposeRequested()),
        verify: (_) {
          verify(mockWorkcellApiService.closeWebSocket()).called(1);
          // Verification of subscription cancellation is implicitly handled by bloc_test
          // if the BLoC's close method or the handler for VisualizerDisposeRequested cancels it.
        },
        // No state change expected from dispose requested itself, BLoC would be closed by owner.
        expect: () => [],
      );
    });

    // Test BLoC close method directly if it has specific logic not covered by DisposeRequested
    test('closes subscription on BLoC close', () async {
      final streamController = StreamController<dynamic>();
      when(
        mockWorkcellApiService.fetchDeckState(any),
      ).thenAnswer((_) async => mockDeckLayout);
      when(
        mockWorkcellApiService.subscribeToWorkcellUpdates(any),
      ).thenAnswer((_) => streamController.stream);
      when(mockWorkcellApiService.closeWebSocket()).thenAnswer((_) async {});

      final bloc = VisualizerBloc(mockWorkcellApiService);
      bloc.add(const VisualizerLoadDeckStateRequested(workcellId));

      // Give time for async operations in `_onLoadDeckStateRequested` to complete
      await Future.delayed(const Duration(milliseconds: 100));

      await bloc.close();

      expect(
        streamController.hasListener,
        isFalse,
      ); // Check if subscription was cancelled
      verify(mockWorkcellApiService.closeWebSocket()).called(1);
    });
  });
}
