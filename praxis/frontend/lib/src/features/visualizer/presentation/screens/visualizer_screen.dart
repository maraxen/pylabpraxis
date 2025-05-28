import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:praxis_lab_management/src/data/services/workcell_api_service.dart';
import 'package:praxis_lab_management/src/features/visualizer/application/bloc/visualizer_bloc.dart';

// TODO(user): Consider moving DeckVisualizer and DeckPainter to a separate file
// in praxis/frontend/lib/src/features/visualizer/presentation/widgets/

/// CustomPainter to draw the deck layout.
class DeckPainter extends CustomPainter {
  final dynamic
  deckData; // Can be DeckLayout or Map<String, dynamic> from WebSocket

  DeckPainter({required this.deckData});

  @override
  void paint(Canvas canvas, Size size) {
    final paint =
        Paint()
          ..color = Colors.blueGrey
          ..style = PaintingStyle.fill;

    // Draw a simple placeholder rectangle for the deck area
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paint);

    final textPainter = TextPainter(
      text: TextSpan(
        text:
            'Deck Area Placeholder\nData: ${deckData.toString().substring(0, (deckData.toString().length > 100) ? 100 : deckData.toString().length)}...', // Show partial data
        style: const TextStyle(color: Colors.white, fontSize: 14),
      ),
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout(minWidth: 0, maxWidth: size.width);
    textPainter.paint(
      canvas,
      Offset(0, size.height / 2 - textPainter.height / 2),
    );

    // TODO(user): Implement detailed drawing logic based on deckData
    // This will involve iterating through positions, labware, etc.
    // and drawing them accordingly.
  }

  @override
  bool shouldRepaint(covariant DeckPainter oldDelegate) {
    // Repaint if the deck data has changed.
    // This might need a more sophisticated comparison for complex objects.
    return oldDelegate.deckData != deckData;
  }
}

/// StatelessWidget to render the deck using CustomPaint and DeckPainter.
class DeckVisualizer extends StatelessWidget {
  final dynamic deckLayoutData; // DeckLayout or Map from WebSocket

  const DeckVisualizer({super.key, required this.deckLayoutData});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return CustomPaint(
          size: Size(
            constraints.maxWidth,
            constraints.maxHeight,
          ), // Occupy available space
          painter: DeckPainter(deckData: deckLayoutData),
        );
      },
    );
  }
}

/// StatefulWidget for the main visualizer screen.
class VisualizerScreenWidget extends StatefulWidget {
  final String workcellId;

  const VisualizerScreenWidget({super.key, required this.workcellId});

  @override
  State<VisualizerScreenWidget> createState() => _VisualizerScreenWidgetState();
}

class _VisualizerScreenWidgetState extends State<VisualizerScreenWidget> {
  @override
  void initState() {
    super.initState();
    // Request initial deck state load when the widget is initialized.
    context.read<VisualizerBloc>().add(
      VisualizerLoadDeckStateRequested(widget.workcellId),
    );
  }

  @override
  void dispose() {
    // Notify the BLoC that this widget is being disposed.
    context.read<VisualizerBloc>().add(const VisualizerDisposeRequested());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Workcell Visualizer: ${widget.workcellId}')),
      body: BlocBuilder<VisualizerBloc, VisualizerState>(
        builder: (context, state) {
          return switch (state) {
            VisualizerInitial() => const Center(
              child: CircularProgressIndicator(),
            ),
            VisualizerLoadInProgress() => const Center(
              child: CircularProgressIndicator(),
            ),
            VisualizerLoadFailure(error: final error) => Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  'Error loading deck state: $error',
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            VisualizerLoadSuccess(deckLayout: final deckLayout) =>
              DeckVisualizer(deckLayoutData: deckLayout),
            VisualizerRealtimeUpdate(updatedData: final updatedData) =>
              DeckVisualizer(deckLayoutData: updatedData),
            VisualizerDisconnected() => const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'WebSocket disconnected. Real-time updates paused.',
                  style: TextStyle(color: Colors.orange),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            // TODO: Handle this case.
            VisualizerState() => throw UnimplementedError(),
          };
        },
      ),
    );
  }
}

/// A convenience widget that provides the VisualizerBloc to VisualizerScreenWidget.
class VisualizerScreen extends StatelessWidget {
  final String workcellId;

  const VisualizerScreen({super.key, required this.workcellId});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create:
          (context) => VisualizerBloc(
            WorkcellApiServiceImpl(),
          ), // Direct instantiation for now
      child: VisualizerScreenWidget(workcellId: workcellId),
    );
  }
}
