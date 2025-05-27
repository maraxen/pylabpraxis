// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mockito/mockito.dart';
import 'package:pylabpraxis_flutter/src/features/assetManagement/application/bloc/asset_management_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/assetManagement/presentation/screens/assetManagement_screen.dart';
import 'package:praxis_data/praxis_data.dart'; // For ORM models

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
      const AssetManagementLoadSuccess( // Or AssetManagementInitial() if UI doesn't depend on data for tabs
        devices: [],
        labwareDefinitions: [],
        labwareInstances: [],
        deckLayouts: [],
      ),
    );
    // If your BLoC uses a stream for state changes that the widget might listen to,
    // you might need to mock that too, though often for simple UI tests,
    // just mocking the initial `state` getter is enough.
    when(mockAssetManagementBloc.stream).thenAnswer((_) => Stream.value(
      const AssetManagementLoadSuccess( // Keep it consistent with .state
        devices: [],
        labwareDefinitions: [],
        labwareInstances: [],
        deckLayouts: [],
      ),
    ));
  });

  Widget createTestableWidget(Widget child) {
    return MaterialApp(
      home: BlocProvider<AssetManagementBloc>.value(
        value: mockAssetManagementBloc,
        child: child,
      ),
    );
  }

  testWidgets('AssetManagementScreen displays AppBar and Tabs correctly',
      (WidgetTester tester) async {
    await tester.pumpWidget(createTestableWidget(const AssetManagementScreen()));

    // Verify AppBar title
    expect(find.text('Asset Management'), findsOneWidget);

    // Verify Tab texts
    expect(find.text('Instruments'), findsOneWidget);
    expect(find.text('Labware Instances'), findsOneWidget);
    expect(find.text('Labware Definitions'), findsOneWidget);

    // Verify initial tab content (Placeholder texts)
    // This assumes the first tab ('Instruments') is active by default.
    expect(find.text('Instruments Tab Content'), findsOneWidget);
    expect(find.text('Labware Instances Tab Content'), findsNothing); // Not visible initially
    expect(find.text('Labware Definitions Tab Content'), findsNothing); // Not visible initially

    // Simulate tapping the 'Labware Instances' tab
    await tester.tap(find.text('Labware Instances'));
    await tester.pumpAndSettle(); // Let animations and transitions finish

    expect(find.text('Instruments Tab Content'), findsNothing);
    expect(find.text('Labware Instances Tab Content'), findsOneWidget);
    expect(find.text('Labware Definitions Tab Content'), findsNothing);

    // Simulate tapping the 'Labware Definitions' tab
    await tester.tap(find.text('Labware Definitions'));
    await tester.pumpAndSettle();

    expect(find.text('Instruments Tab Content'), findsNothing);
    expect(find.text('Labware Instances Tab Content'), findsNothing);
    expect(find.text('Labware Definitions Tab Content'), findsOneWidget);
  });
}
