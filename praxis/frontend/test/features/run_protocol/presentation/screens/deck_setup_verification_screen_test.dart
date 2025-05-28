import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/deck_setup_verification_screen.dart';
import 'package:praxis_lab_management/src/features/visualizer/application/bloc/visualizer_bloc.dart';
import 'package:praxis_lab_management/src/features/visualizer/presentation/screens/visualizer_screen.dart';
import 'package:praxis_lab_management/src/data/models/protocol/deck_layout.dart';
import 'package:praxis_lab_management/src/data/services/workcell_api_service.dart';

// Assuming mock_services.mocks.dart is generated in praxis/frontend/test/mocks/
import '../../../../mocks/mock_services.mocks.dart';

// Mock VisualizerBloc
class MockVisualizerBloc extends Mock implements VisualizerBloc {}

class FakeVisualizerState extends Fake implements VisualizerState {}

class FakeVisualizerEvent extends Fake implements VisualizerEvent {}

void main() {
  late MockVisualizerBloc mockVisualizerBloc;
  late MockWorkcellApiService
  mockWorkcellApiService; // Needed by VisualizerBloc

  const String testWorkcellId = 'test_workcell_123';

  setUpAll(() {
    // registerFallbackValue(FakeVisualizerState());
    // registerFallbackValue(FakeVisualizerEvent());
  });

  setUp(() {
    mockVisualizerBloc = MockVisualizerBloc();
    mockWorkcellApiService =
        MockWorkcellApiService(); // VisualizerScreen will create its own bloc, but needs this if we were to mock the bloc provider's create function

    // Default state for VisualizerBloc when VisualizerScreen is pumped
    when(mockVisualizerBloc.state).thenReturn(const VisualizerInitial());
    when(
      mockVisualizerBloc.stream,
    ).thenAnswer((_) => Stream.value(const VisualizerInitial()));

    // If VisualizerScreen's internal BlocProvider creates the bloc,
    // we might need to mock the service that the actual bloc would use.
    // However, VisualizerScreen itself provides the bloc.
    // The DeckSetupVerificationScreen passes workcellId to VisualizerScreen.
    // VisualizerScreen then creates its own BlocProvider for VisualizerBloc.
    // For this test, we can provide the mockVisualizerBloc directly to VisualizerScreenWidget
    // if we were testing VisualizerScreenWidget in isolation.
    // But since we test DeckSetupVerificationScreen, it will instantiate VisualizerScreen,
    // which in turn instantiates its own VisualizerBloc.
    // So, we rely on VisualizerScreen's internal BlocProvider.
    // The VisualizerScreen widget as created previously will instantiate its own VisualizerBloc
    // with a real WorkcellApiServiceImpl(). For a unit test of DeckSetupVerificationScreen,
    // this is an integration point. If WorkcellApiServiceImpl() makes network calls,
    // they should be mocked globally (e.g. via GetIt or passing service).
    // For simplicity here, we assume VisualizerScreen can run with its default setup.
    // A better approach would be to allow injecting the VisualizerBloc/WorkcellApiService
    // into VisualizerScreen for more controlled testing.

    // Given the current structure of VisualizerScreen (it creates its own BlocProvider),
    // we cannot easily inject a mockVisualizerBloc from this test file when testing
    // DeckSetupVerificationScreen.
    // We will rely on finding VisualizerScreen by type.
  });

  Widget createTestableWidget(Widget child) {
    return MaterialApp(
      home: child, // DeckSetupVerificationScreen will be the child
    );
  }

  testWidgets(
    'DeckSetupVerificationScreen displays AppBar, Buttons, and VisualizerScreen',
    (WidgetTester tester) async {
      // For VisualizerScreen to initialize its BLoC correctly without real service calls,
      // we'd ideally mock the WorkcellApiService that its BLoC uses.
      // Since VisualizerScreen creates its own VisualizerBloc with WorkcellApiServiceImpl(),
      // this test becomes more of an integration test for that part.
      // We'll assume the default WorkcellApiServiceImpl() mock behavior (if any was set up globally)
      // or that it can initialize without error for this placeholder visualizer.

      await tester.pumpWidget(
        createTestableWidget(
          const DeckSetupVerificationScreen(workcellId: testWorkcellId),
        ),
      );

      // Verify AppBar title
      expect(find.text('Deck Setup Verification'), findsOneWidget);

      // Verify presence of Back and Continue buttons
      expect(find.text('Back'), findsOneWidget);
      expect(find.text('Continue'), findsOneWidget);

      // Verify that VisualizerScreen is present
      // VisualizerScreen internally has an AppBar with title 'Workcell Visualizer: {workcellId}'
      // and a BlocBuilder.
      expect(find.byType(VisualizerScreen), findsOneWidget);

      // Check for a key element within VisualizerScreen, e.g., its AppBar title
      // This confirms VisualizerScreen is being rendered with the correct workcellId.
      expect(find.text('Workcell Visualizer: $testWorkcellId'), findsOneWidget);
    },
  );
}
