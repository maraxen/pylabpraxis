import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart'; // For later BLoC integration
// import 'package:provider/provider.dart'; // If using Provider for DI

// Core imports
import 'src/core/theme/app_theme.dart';
import 'src/core/routing/app_router.dart';
import 'src/core/widgets/app_shell.dart'; // Import the AppShell

// TODO: Import services for DI (AuthService, ProtocolService, etc.)
// import 'src/data/services/auth_service.dart';
// import 'src/data/services/protocol_api_service.dart';
// import 'src/repositories/auth_repository.dart';
// import 'src/repositories/protocol_repository.dart';

// TODO: Import global BLoCs if any (e.g., AuthBloc)
// import 'src/features/auth/application/auth_bloc.dart';

void main() {
  // TODO: Ensure Flutter bindings are initialized if using async operations before runApp
  // WidgetsFlutterBinding.ensureInitialized();

  // TODO: Set up logging, error reporting (e.g., Sentry), etc.

  // TODO: Set up dependency injection (e.g., GetIt, Provider, or manual)
  // Example with manual setup for now, replace with a proper DI solution
  // final authService = AuthService(/* dio client, secure_storage */);
  // final protocolApiService = ProtocolApiService(/* dio client */);
  // final authRepository = AuthRepository(authService);
  // final protocolRepository = ProtocolRepository(protocolApiService);

  runApp(
    // TODO: Wrap with MultiRepositoryProvider if using BLoC for DI of repositories
    // MultiRepositoryProvider(
    //   providers: [
    //     RepositoryProvider.value(value: authRepository),
    //     RepositoryProvider.value(value: protocolRepository),
    //   ],
    //   child: MultiBlocProvider( // For providing global BLoCs
    //     providers: [
    //       // BlocProvider<AuthBloc>(
    //       //   create: (context) => AuthBloc(authRepository: context.read<AuthRepository>())..add(AuthAppStarted()),
    //       // ),
    //       // Add other global BLoCs here
    //     ],
    //     child: const MyApp(),
    //   ),
    // ),
    const MyApp(), // Simplified for now, will add providers later
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PyLabPraxis Flutter',
      debugShowCheckedModeBanner: false, // Disable debug banner
      // Theme configuration
      theme: AppTheme.lightTheme,
      // darkTheme: AppTheme.darkTheme, // Uncomment if dark theme is implemented
      // themeMode: ThemeMode.system, // Or ThemeMode.light, ThemeMode.dark

      // Routing configuration
      // initialRoute: AppRouter.home, // Or a splash/login screen if you have one
      onGenerateRoute:
          AppRouter
              .generateRoute, // Use if you need to pass args or have complex logic
      // The home will be our AppShell which handles the main navigation structure
      home: const AppShell(),

      // For BLoC state observation (optional, good for debugging)
      // builder: (context, child) {
      //   return BlocListener<AuthBloc, AuthState>( // Example global BLoC listener
      //     listener: (context, state) {
      //       if (state is AuthUnauthenticated) {
      //         // Navigate to login or handle unauthenticated state
      //         // Navigator.of(context).pushNamedAndRemoveUntil(AppRouter.login, (route) => false);
      //       } else if (state is AuthAuthenticated) {
      //         // Potentially navigate to home or handle authenticated state
      //       }
      //     },
      //     child: child!,
      //   );
      // },
    );
  }
}
