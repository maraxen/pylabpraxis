import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mockito/mockito.dart';
import 'package:praxis_lab_management/src/features/assetManagement/application/bloc/asset_management_bloc.dart';
import 'package:praxis_lab_management/src/features/assetManagement/presentation/screens/assetManagement_screen.dart';

// Mock AssetManagementBloc
class MockAssetManagementBloc extends Mock implements AssetManagementBloc {}

// A minimal AssetManagementState for testing initial UI before data load
class FakeAssetManagementState extends Fake implements AssetManagementState {}

class FakeAssetManagementEvent extends Fake implements AssetManagementEvent {}

void main() {
  late MockAssetManagementBloc mockAssetManagementBloc;

  setUpAll(() {
    // Register fallback values for Fake State and Event for bloc_test if needed,
    // but for widget tests directly providing the bloc, this might not be as critical.
    // registerFallbackValue(FakeAssetManagementState());
    // registerFallbackValue(FakeAssetManagementEvent());
  });

  setUp(() {
    mockAssetManagementBloc = MockAssetManagementBloc();
    // Provide a default initial state for the bloc when it's read.
    // The screen expects the bloc to be in a state that can build the UI.
    // For initial display, AssetManagementInitial is fine.
    // If testing LoadSuccess, you'd mock a state with data.
    when(mockAssetManagementBloc.state).thenReturn(
      const AssetManagementLoadSuccess(
        // Or AssetManagementInitial() if UI doesn't depend on data for tabs
        machines: [],
        resourceDefinitions: [],
        resourceInstances: [],
        deckLayouts: [],
      ),
    );
    // If your BLoC uses a stream for state changes that the widget might listen to,
    // you might need to mock that too, though often for simple UI tests,
    // just mocking the initial `state` getter is enough.
    when(mockAssetManagementBloc.stream).thenAnswer(
      (_) => Stream.value(
        const AssetManagementLoadSuccess(
          // Keep it consistent with .state
          machines: [],
          resourceDefinitions: [],
          resourceInstances: [],
          deckLayouts: [],
        ),
      ),
    );
  });

  Widget createTestableWidget(Widget child) {
    return MaterialApp(
      home: BlocProvider<AssetManagementBloc>.value(
        value: mockAssetManagementBloc,
        child: child,
      ),
    );
  }

  testWidgets('AssetManagementScreen displays AppBar and Tabs correctly', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      createTestableWidget(const AssetManagementScreen()),
    );

    // Verify AppBar title
    expect(find.text('Asset Management'), findsOneWidget);

    // Verify Tab texts
    expect(find.text('Instruments'), findsOneWidget);
    expect(find.text('Resource Instances'), findsOneWidget);
    expect(find.text('Resource Definitions'), findsOneWidget);

    // Verify initial tab content (Placeholder texts)
    // This assumes the first tab ('Instruments') is active by default.
    expect(find.text('Instruments Tab Content'), findsOneWidget);
    expect(
      find.text('Resource Instances Tab Content'),
      findsNothing,
    ); // Not visible initially
    expect(
      find.text('Resource Definitions Tab Content'),
      findsNothing,
    ); // Not visible initially

    // Simulate tapping the 'Resource Instances' tab
    await tester.tap(find.text('Resource Instances'));
    await tester.pumpAndSettle(); // Let animations and transitions finish

    expect(find.text('Instruments Tab Content'), findsNothing);
    expect(find.text('Resource Instances Tab Content'), findsOneWidget);
    expect(find.text('Resource Definitions Tab Content'), findsNothing);

    // Simulate tapping the 'Resource Definitions' tab
    await tester.tap(find.text('Resource Definitions'));
    await tester.pumpAndSettle();

    expect(find.text('Instruments Tab Content'), findsNothing);
    expect(find.text('Resource Instances Tab Content'), findsNothing);
    expect(find.text('Resource Definitions Tab Content'), findsOneWidget);
  });
}
