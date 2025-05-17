import 'package:flutter/material.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/protocols/presentation/screens/protocols_screen.dart';
import '../../features/assetManagement/presentation/screens/assetManagement_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;

  // List of widgets to display for each tab
  static const List<Widget> _widgetOptions = <Widget>[
    HomeScreen(),
    ProtocolsScreen(),
    AssetManagementScreen(),
    SettingsScreen(),
  ];

  // List of destinations for the BottomNavigationBar
  // These correspond to the _widgetOptions
  static const List<NavigationDestination> _navDestinations = [
    NavigationDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: 'Home',
    ),
    NavigationDestination(
      icon: Icon(Icons.science_outlined),
      selectedIcon: Icon(Icons.science),
      label: 'Protocols',
    ),
    NavigationDestination(
      icon: Icon(Icons.inventory_2_outlined),
      selectedIcon: Icon(Icons.inventory_2),
      label: 'Assets',
    ),
    NavigationDestination(
      icon: Icon(Icons.settings_outlined),
      selectedIcon: Icon(Icons.settings),
      label: 'Settings',
    ),
  ];

  // Titles for the AppBar corresponding to each tab
  static const List<String> _appBarTitles = [
    'PyLabPraxis Home',
    'Manage Protocols',
    'Manage Assets',
    'Settings',
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_appBarTitles[_selectedIndex]),
        // Potentially add actions or leading widgets to AppBar if needed globally
        // actions: [
        //   if (_selectedIndex == 0) // Example: Action only for home screen
        //     IconButton(icon: Icon(Icons.notifications_none), onPressed: () {}),
        // ],
      ),
      body: Center(child: _widgetOptions.elementAt(_selectedIndex)),
      bottomNavigationBar: NavigationBar(
        // backgroundColor: Theme.of(context).colorScheme.surface, // Handled by theme
        // indicatorColor: Theme.of(context).colorScheme.secondaryContainer, // M3 default
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onItemTapped,
        destinations: _navDestinations,
        labelBehavior:
            NavigationDestinationLabelBehavior
                .alwaysShow, // Or onlyShowSelected / alwaysHide
        animationDuration: const Duration(
          milliseconds: 500,
        ), // Smooth transition
      ),
    );
  }
}
