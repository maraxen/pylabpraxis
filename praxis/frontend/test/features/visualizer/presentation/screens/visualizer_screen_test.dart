import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/features/visualizer/application/bloc/visualizer_bloc.dart';
import 'package:praxis_lab_management/src/features/visualizer/presentation/screens/visualizer_screen.dart';
import 'package:praxis_lab_management/src/data/models/protocol/deck_layout.dart';
// Required for VisualizerBloc if not mocking create

// MockVisualizerBloc was defined in deck_setup_verification_screen_test,
// but it's better to define mocks per-test-suite or in a shared file if not using build_runner for them.
// For now, we'll assume it's available or re-declare if necessary.
// Re-using from previous test file for now.
import '../../../../mocks/mock_services.mocks.dart'; // For MockWorkcellApiService if needed by VisualizerBloc

class MockVisualizerBlocExt extends Mock implements VisualizerBloc {}

class FakeVisualizerStateExt extends Fake implements VisualizerState {
  @override
  String toString({DiagnosticLevel? minLevel}) {
    return 'FakeVisualizerStateExt';
  }
}

class FakeVisualizerEventExt extends Fake implements VisualizerEvent {
  @override
  String toString({DiagnosticLevel? minLevel}) {
    return 'FakeVisualizerEventExt';
  }
}

void main() {
  late MockVisualizerBlocExt mockVisualizerBloc;
  // This service is used by the VisualizerScreen when it creates its own VisualizerBloc.
  // For more controlled unit tests of VisualizerScreenWidget, we'd inject the bloc directly.
  late MockWorkcellApiService mockWorkcellApiService;

  const String testWorkcellId = 'vis_test_workcell_1';
  final DeckLayout testDeckLayout = const DeckLayout(
    id: 'deck1',
    name: 'Test Deck',
    positions: [],
  );

  setUpAll(() {
    // registerFallbackValue(FakeVisualizerStateExt());
    // registerFallbackValue(FakeVisualizerEventExt());
  });

  setUp(() {
    mockVisualizerBloc = MockVisualizerBlocExt();
    mockWorkcellApiService =
        MockWorkcellApiService(); // Initialize the mock service

    // When VisualizerScreen creates VisualizerBloc, it uses WorkcellApiServiceImpl().
    // To control tests, we often provide the BLoC directly.
    // The current VisualizerScreen widget provides its own BLoC.
    // So, we test VisualizerScreenWidget by providing the mock BLoC.
  });

  Widget createTestableVisualizerScreenWidget({
    required VisualizerState initialState,
  }) {
    // Ensure the bloc is in the desired initial state for each test case
    when(mockVisualizerBloc.state).thenReturn(initialState);
    when(
      mockVisualizerBloc.stream,
    ).thenAnswer((_) => Stream.value(initialState));

    return MaterialApp(
      home: BlocProvider<VisualizerBloc>.value(
        value: mockVisualizerBloc,
        // VisualizerScreenWidget is the one that consumes the bloc
        child: const VisualizerScreenWidget(workcellId: testWorkcellId),
      ),
    );
  }

  testWidgets(
    'VisualizerScreenWidget shows loading indicator for LoadInProgress state',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        createTestableVisualizerScreenWidget(
          initialState: const VisualizerLoadInProgress(),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.byType(DeckVisualizer), findsNothing);
    },
  );

  testWidgets(
    'VisualizerScreenWidget shows error message for LoadFailure state',
    (WidgetTester tester) async {
      const errorMessage = 'Failed to load deck';
      await tester.pumpWidget(
        createTestableVisualizerScreenWidget(
          initialState: const VisualizerLoadFailure(errorMessage),
        ),
      );

      expect(find.textContaining(errorMessage), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(find.byType(DeckVisualizer), findsNothing);
    },
  );

  testWidgets(
    'VisualizerScreenWidget shows DeckVisualizer for LoadSuccess state',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        createTestableVisualizerScreenWidget(
          initialState: VisualizerLoadSuccess(testDeckLayout),
        ),
      );

      expect(find.byType(DeckVisualizer), findsOneWidget);
      // Verify the DeckVisualizer received the correct data (indirectly, by checking a text element if DeckPainter showed ID)
      // For now, just finding by type is sufficient.
      expect(
        find.textContaining('Deck Area Placeholder'),
        findsOneWidget,
      ); // From DeckPainter
      expect(find.byType(CircularProgressIndicator), findsNothing);
    },
  );

  testWidgets(
    'VisualizerScreenWidget shows DeckVisualizer for RealtimeUpdate state',
    (WidgetTester tester) async {
      final updatedData = {
        'update': 'some_realtime_data',
        'deckId': testDeckLayout.id,
      };
      await tester.pumpWidget(
        createTestableVisualizerScreenWidget(
          initialState: VisualizerRealtimeUpdate(updatedData),
        ),
      );

      expect(find.byType(DeckVisualizer), findsOneWidget);
      expect(
        find.textContaining('Deck Area Placeholder'),
        findsOneWidget,
      ); // From DeckPainter
      // Check if part of the updatedData is displayed by DeckPainter
      expect(
        find.textContaining(updatedData.toString().substring(0, 50)),
        findsOneWidget,
      );
      expect(find.byType(CircularProgressIndicator), findsNothing);
    },
  );

  testWidgets(
    'VisualizerScreenWidget shows disconnected message for Disconnected state',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        createTestableVisualizerScreenWidget(
          initialState: const VisualizerDisconnected(),
        ),
      );

      expect(find.textContaining('WebSocket disconnected'), findsOneWidget);
      expect(find.byType(DeckVisualizer), findsNothing);
    },
  );

  testWidgets(
    'VisualizerScreenWidget dispatches event on initState and dispose',
    (WidgetTester tester) async {
      // This test focuses on VisualizerScreenWidget's lifecycle interaction with the BLoC.
      when(mockVisualizerBloc.state).thenReturn(const VisualizerInitial());
      when(
        mockVisualizerBloc.stream,
      ).thenAnswer((_) => Stream.value(const VisualizerInitial()));

      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<VisualizerBloc>.value(
            value: mockVisualizerBloc,
            child: const VisualizerScreenWidget(workcellId: testWorkcellId),
          ),
        ),
      );

      // Verify that VisualizerLoadDeckStateRequested was added on initState
      verify(
        mockVisualizerBloc.add(
          const VisualizerLoadDeckStateRequested(testWorkcellId),
        ),
      ).called(1);

      // Simulate widget disposal
      await tester.pumpWidget(
        Container(),
      ); // Replace with empty container to dispose

      // Verify that VisualizerDisposeRequested was added on dispose
      verify(
        mockVisualizerBloc.add(const VisualizerDisposeRequested()),
      ).called(1);
    },
  );

  // Test for the VisualizerScreen wrapper (which provides the BLoC)
  testWidgets('VisualizerScreen provides VisualizerBloc to VisualizerScreenWidget', (
    WidgetTester tester,
  ) async {
    // This test is more about checking the BlocProvider setup in VisualizerScreen.
    // We need to mock the WorkcellApiService that VisualizerBloc (created by VisualizerScreen) will use.
    when(
      mockWorkcellApiService.fetchDeckState(any),
    ).thenAnswer((_) async => testDeckLayout);
    when(
      mockWorkcellApiService.subscribeToWorkcellUpdates(any),
    ).thenAnswer((_) => const Stream.empty()); // Empty stream for simplicity

    // It's tricky to test the BlocProvider directly without also testing the child.
    // Instead, we can ensure VisualizerScreenWidget receives a bloc and tries to use it.
    // We'll test that VisualizerScreenWidget (child of VisualizerScreen's BlocProvider)
    // makes its initial call.

    // To really test this, we'd need a way to swap out WorkcellApiServiceImpl
    // or use a service locator pattern that can be configured for tests.
    // For now, we'll trust that VisualizerScreen sets up its BlocProvider correctly.
    // A simple check is that it renders without crashing and finds the AppBar from VisualizerScreenWidget.

    await tester.pumpWidget(
      MaterialApp(
        // Provide the mocked service if it were using GetIt or similar for service location.
        // For now, VisualizerScreen directly instantiates WorkcellApiServiceImpl.
        // This makes this specific test less of a unit test and more of an integration.
        home: VisualizerScreen(workcellId: testWorkcellId),
      ),
    );

    // Check if the AppBar from VisualizerScreenWidget is present
    expect(find.text('Workcell Visualizer: $testWorkcellId'), findsOneWidget);
    // Check for loading indicator, as the real bloc will be created and will initially be loading
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle(); // Allow bloc to load

    // After loading (mocked service returns data), DeckVisualizer should appear
    expect(find.byType(DeckVisualizer), findsOneWidget);
  });
}
