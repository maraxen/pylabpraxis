import 'package:flutter/material.dart';

class AssetManagementScreen extends StatelessWidget {
  const AssetManagementScreen({super.key});

  static const String routeName =
      '/assetManagement'; // Matches AppRouter.assetManagement

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // AppBar is now part of AppShell
      // appBar: AppBar(
      //   title: const Text('Assets'),
      // ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.inventory_2_outlined,
                size: 80,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: 20),
              Text(
                'Assets Screen',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 10),
              Text(
                'Manage your laboratory assets and consumables here.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              // TODO: Add asset management UI elements (list, add, edit)
            ],
          ),
        ),
      ),
    );
  }
}
