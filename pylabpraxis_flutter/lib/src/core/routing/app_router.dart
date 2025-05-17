import 'package:flutter/material.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/protocols/presentation/screens/protocols_screen.dart';
import '../../features/assetManagement/presentation/screens/assetManagement_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';
// Import other screens as they are created, e.g., login, protocol_details etc.

class AppRouter {
  // Route names
  static const String home = '/';
  static const String protocols = '/protocols';
  static const String assetManagement = '/assetManagement';
  static const String settings = '/settings';
  // Add more route names here
  // static const String login = '/login';
  // static const String protocolDetails = '/protocol-details'; // Example with parameter

  // Private constructor to prevent instantiation
  AppRouter._();

  static Route<dynamic> generateRoute(RouteSettings settings) {
    // final args = settings.arguments; // Use if passing arguments

    switch (settings.name) {
      case AppRouter.home:
        return MaterialPageRoute(builder: (_) => const HomeScreen());
      case AppRouter.protocols:
        return MaterialPageRoute(builder: (_) => const ProtocolsScreen());
      case AppRouter.assetManagement:
        // Assuming you have a screen for asset management
        return MaterialPageRoute(builder: (_) => const AssetManagementScreen());
      case AppRouter.settings:
        return MaterialPageRoute(builder: (_) => const SettingsScreen());
      // case login:
      //   return MaterialPageRoute(builder: (_) => const LoginScreen());
      // case protocolDetails:
      //   if (args is String) { // Example: expecting a protocol ID as string
      //     return MaterialPageRoute(builder: (_) => ProtocolDetailsScreen(protocolId: args));
      //   }
      //   return _errorRoute('Invalid arguments for ${settings.name}');
      default:
        return _errorRoute('Unknown route: ${settings.name}');
    }
  }

  static Route<dynamic> _errorRoute(String message) {
    return MaterialPageRoute(
      builder:
          (_) => Scaffold(
            appBar: AppBar(title: const Text('Error')),
            body: Center(child: Text('ROUTE ERROR: $message')),
          ),
    );
  }
}
