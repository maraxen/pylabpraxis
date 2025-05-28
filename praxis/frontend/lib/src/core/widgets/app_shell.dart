import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart'; // Import go_router
// Import your BLoCs if AppShell needs to interact with them directly,
// though navigation is now handled by go_router.
// import 'package:flutter_bloc/flutter_bloc.dart';
// import 'package:praxis_lab_management/src/features/auth/application/bloc/auth_bloc.dart';

class AppShell extends StatefulWidget {
  final Widget child; // This child will be the screen for the selected tab

  const AppShell({required this.child, super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  // No longer need to manage _selectedIndex for navigation control here,
  // go_router will handle which child to display based on the current route.
  // However, we still need it to set the correct active tab in BottomNavigationBar.

  int _calculateSelectedIndex(BuildContext context) {
    final String location = GoRouterState.of(context).uri.toString();
    if (location.startsWith('/home')) {
      return 0;
    }
    if (location.startsWith('/protocols')) {
      return 1;
    }
    if (location.startsWith('/asset-management')) {
      return 2;
    }
    if (location.startsWith('/settings')) {
      return 3;
    }
    return 0; // Default to home
  }

  void _onItemTapped(int index, BuildContext context) {
    switch (index) {
      case 0:
        context.goNamed('home');
        break;
      case 1:
        context.goNamed('protocols');
        break;
      case 2:
        context.goNamed('assetManagement');
        break;
      case 3:
        context.goNamed('settings');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final selectedIndex = _calculateSelectedIndex(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('PylabPraxis'),
        // Example: Add a logout button if desired, using AuthBloc
        // actions: [
        //   IconButton(
        //     icon: const Icon(Icons.logout),
        //     onPressed: () {
        //       context.read<AuthBloc>().add(AuthSignOutRequested());
        //       // GoRouter's redirect logic will handle navigation to /login
        //     },
        //   ),
        // ],
      ),
      body: widget.child, // Display the child widget passed by ShellRoute
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.science_outlined),
            activeIcon: Icon(Icons.science),
            label: 'Protocols',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.inventory_2_outlined),
            activeIcon: Icon(Icons.inventory_2),
            label: 'Assets',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
        currentIndex: selectedIndex,
        selectedItemColor: Theme.of(context).colorScheme.primary,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true, // Optional: to always show labels
        type:
            BottomNavigationBarType
                .fixed, // Ensures all items are visible and have labels
        onTap: (index) => _onItemTapped(index, context),
      ),
    );
  }
}
