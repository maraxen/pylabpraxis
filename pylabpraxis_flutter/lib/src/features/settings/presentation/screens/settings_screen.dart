import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  static const String routeName = '/settings'; // Matches AppRouter.settings

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // AppBar is now part of AppShell
      // appBar: AppBar(
      //   title: const Text('Settings'),
      // ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: <Widget>[
          Text(
            'Application Settings',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          ListTile(
            leading: const Icon(Icons.person_outline),
            title: const Text('User Profile'),
            subtitle: const Text('Manage your account details'),
            onTap: () {
              // TODO: Navigate to User Profile Screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('User Profile to be implemented!'),
                ),
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.color_lens_outlined),
            title: const Text('Appearance'),
            subtitle: const Text('Customize theme and display options'),
            onTap: () {
              // TODO: Navigate to Appearance Settings or show a dialog
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Appearance settings to be implemented!'),
                ),
              );
            },
          ),
          SwitchListTile(
            title: const Text('Enable Notifications'),
            value: true, // TODO: Replace with actual setting state
            onChanged: (bool value) {
              // TODO: Update notification setting
            },
            secondary: const Icon(Icons.notifications_active_outlined),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.api_outlined),
            title: const Text('API Configuration'),
            subtitle: const Text('Set up backend connection details'),
            onTap: () {
              // TODO: Navigate to API Configuration Screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('API Configuration to be implemented!'),
                ),
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About PyLabPraxis'),
            subtitle: const Text('Version, licenses, and more'),
            onTap: () {
              // TODO: Show About Dialog or Screen
              showAboutDialog(
                context: context,
                applicationName: 'PyLabPraxis Flutter',
                applicationVersion:
                    '0.1.0 (Dev)', // TODO: Get version dynamically
                applicationLegalese: '© 2024-2025 Your Company Name',
                children: <Widget>[
                  const Padding(
                    padding: EdgeInsets.only(top: 15),
                    child: Text(
                      'Migrating from Angular to Flutter for a better cross-platform experience.',
                    ),
                  ),
                ],
              );
            },
          ),
          ListTile(
            leading: Icon(
              Icons.logout,
              color: Theme.of(context).colorScheme.error,
            ),
            title: Text(
              'Logout',
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
            onTap: () {
              // TODO: Implement Logout logic (call AuthBloc/AuthService)
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Logout functionality to be implemented!'),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
