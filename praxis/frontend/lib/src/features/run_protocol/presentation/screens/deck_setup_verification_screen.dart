import 'package:flutter/material.dart';
import 'package:praxis_lab_management/src/features/visualizer/presentation/screens/visualizer_screen.dart';
// TODO(user): Import ProtocolWorkflowBloc if workcellId is to be sourced from it.
// import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';

class DeckSetupVerificationScreen extends StatelessWidget {
  final String workcellId;

  const DeckSetupVerificationScreen({
    super.key,
    required this.workcellId, // For now, pass workcellId directly.
  });

  // TODO(user): Add routeName if needed for navigation and ensure workcellId is passed via routing or BLoC.

  @override
  Widget build(BuildContext context) {
    // TODO(user): In a real application, workcellId would likely come from a BLoC state,
    // e.g., context.watch<ProtocolWorkflowBloc>().state.currentWorkcellId or similar.
    // final protocolWorkflowBloc = context.watch<ProtocolWorkflowBloc>();
    // final String? currentWorkcellId = protocolWorkflowBloc.state.selectedWorkcellId;
    // if (currentWorkcellId == null) {
    //   return Scaffold(
    //     appBar: AppBar(title: const Text('Error')),
    //     body: const Center(child: Text('Workcell ID not available.')),
    //   );
    // }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Deck Setup Verification'),
        // TODO(user): Consider adding a leading back button if not handled by router or higher-level Scaffold.
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Integrate VisualizerScreen here
            Expanded(
              child: VisualizerScreen(
                workcellId: workcellId,
              ), // Pass the workcellId
            ),
            const SizedBox(height: 16), // Added some spacing
            // TODO(user): Add other UI elements for deck setup verification if needed.
            // For example, a list of required resource vs actual detected resource.
            const SizedBox(height: 16), // Added some spacing
            OverflowBar(
              alignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton(
                  onPressed: () {
                    // TODO(user): Implement Back navigation using ProtocolWorkflowBloc
                    // e.g., context.read<ProtocolWorkflowBloc>().add(const ProtocolWorkflowEvent.previousStepRequested());
                    // Or, if not using a workflow BLoC for navigation control here:
                    // if (Navigator.of(context).canPop()) {
                    //   Navigator.of(context).pop();
                    // }
                    debugPrint(
                      'Back button pressed on DeckSetupVerificationScreen',
                    );
                  },
                  child: const Text('Back'),
                ),
                ElevatedButton(
                  onPressed: () {
                    // TODO(user): Implement Continue navigation or action using ProtocolWorkflowBloc
                    // e.g., context.read<ProtocolWorkflowBloc>().add(const ProtocolWorkflowEvent.deckVerificationCompleted());
                    debugPrint(
                      'Continue button pressed on DeckSetupVerificationScreen',
                    );
                  },
                  child: const Text('Continue'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
