import 'package:flutter/material.dart';

// Screen Imports
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/protocols/presentation/screens/protocols_screen.dart';
import '../../features/assetManagement/presentation/screens/assetManagement_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';
// Import the LoginScreen (adjust path if necessary if it's different from the one created previously)
import '../../features/auth/presentation/screens/login_screen.dart';
// Import other screens as they are created, e.g., protocol_details etc.

class AppRouter {
  // Route names
  static const String home =
      '/'; // Typically the initial screen within AppShell
  static const String login = '/login'; // Route for the login screen
  static const String protocols = '/protocols';
  static const String assetManagement = '/assetManagement';
  static const String settings = '/settings';
  // static const String protocolDetails = '/protocol-details'; // Example for a route with parameters

  // Private constructor to prevent instantiation
  AppRouter._();

  static Route<dynamic> generateRoute(RouteSettings routeSettings) {
    // final args = routeSettings.arguments; // Use if passing arguments to routes

    switch (routeSettings.name) {
      case AppRouter.home:
        // This route is typically the default screen shown by AppShell once authenticated.
        // The BlocBuilder in main.dart handles showing AppShell vs LoginScreen initially.
        return MaterialPageRoute(builder: (_) => const HomeScreen());

      case AppRouter.login:
        // Route to the LoginScreen.
        // This can be used for explicit navigation to login if needed (e.g., after logout or session expiry).
        return MaterialPageRoute(builder: (_) => const LoginScreen());

      case AppRouter.protocols:
        return MaterialPageRoute(builder: (_) => const ProtocolsScreen());

      case AppRouter.assetManagement:
        return MaterialPageRoute(builder: (_) => const AssetManagementScreen());

      case AppRouter.settings:
        return MaterialPageRoute(builder: (_) => const SettingsScreen());

      // Example for a route that takes arguments:
      // case AppRouter.protocolDetails:
      //   if (args is String) { // Example: expecting a protocol ID as a string
      //     return MaterialPageRoute(builder: (_) => ProtocolDetailsScreen(protocolId: args));
      //   }
      //   // If arguments are not valid, return an error route
      //   return _errorRoute('Invalid arguments for ${routeSettings.name}');

      default:
        // If the route is unknown, display an error screen.
        return _errorRoute('Unknown route: ${routeSettings.name}');
    }
  }

  static Route<dynamic> _errorRoute(String message) {
    return MaterialPageRoute(
      builder:
          (_) => Scaffold(
            appBar: AppBar(title: const Text('Error'), centerTitle: true),
            body: Center(
              child: Text(
                'ROUTE ERROR: $message',
                style: const TextStyle(color: Colors.red, fontSize: 16),
                textAlign: TextAlign.center,
              ),
            ),
          ),
    );
  }
}
