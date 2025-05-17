import 'package:flutter/material.dart';

class ProtocolsScreen extends StatelessWidget {
  const ProtocolsScreen({super.key});

  static const String routeName = '/protocols'; // Matches AppRouter.protocols

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // AppBar is now part of AppShell
      // appBar: AppBar(
      //   title: const Text('Protocols'),
      // ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.science_outlined,
                size: 80,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: 20),
              Text(
                'Protocols Screen',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 10),
              Text(
                'Here you will manage and run your scientific protocols.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 30),
              ElevatedButton.icon(
                icon: const Icon(Icons.add_circle_outline),
                label: const Text('Run New Protocol'),
                onPressed: () {
                  // TODO: Navigate to the "Run New Protocol" workflow (Phase 3)
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        '"Run New Protocol" flow to be implemented!',
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 10),
              TextButton.icon(
                icon: const Icon(Icons.history_outlined),
                label: const Text('View Run History'),
                onPressed: () {
                  // TODO: Navigate to Protocol Run History
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Run History to be implemented!'),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
