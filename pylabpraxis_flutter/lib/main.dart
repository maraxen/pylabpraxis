import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

// Core imports
import 'src/core/theme/app_theme.dart';
import 'src/core/routing/app_router.dart';
import 'src/core/widgets/app_shell.dart';

// Data Layer Imports (Services & Repositories)
import 'src/data/services/auth_service.dart';
import 'src/data/services/protocol_api_service.dart';
import 'src/data/repositories/auth_repository.dart' as auth;
import 'src/data/repositories/protocol_repository.dart' as protocol;

// Feature Layer Imports (BLoCs)
import 'src/features/auth/application/bloc/auth_bloc.dart';
// TODO: Import other BLoCs as they are created

void main() {
  // Ensure Flutter bindings are initialized, especially if using async operations before runApp
  WidgetsFlutterBinding.ensureInitialized();

  // TODO: Set up logging, error reporting (e.g., Sentry), etc.

  // Initialize services
  // In a real app, these might take configurations or other dependencies
  final AuthService authService = AuthServiceImpl();
  final ProtocolApiService protocolApiService = ProtocolApiServiceImpl();

  // Initialize repositories with their service dependencies
  final auth.AuthRepository authRepository = auth.AuthRepositoryImpl(
    authService: authService,
  );
  final protocol.ProtocolRepository protocolRepository =
      protocol.ProtocolRepositoryImpl(protocolApiService: protocolApiService);

  runApp(
    // Provide repositories to the widget tree so BLoCs can access them
    MultiRepositoryProvider(
      providers: [
        RepositoryProvider<auth.AuthRepository>.value(value: authRepository),
        RepositoryProvider<protocol.ProtocolRepository>.value(
          value: protocolRepository,
        ),
        // Add other RepositoryProviders here
      ],
      child: MultiBlocProvider(
        // Provide global BLoCs
        providers: [
          BlocProvider<AuthBloc>(
            create:
                (context) => AuthBloc(
                  // BLoCs can read repositories provided above them in the tree
                  authRepository: context.read<auth.AuthRepository>(),
                )..add(AuthAppStarted()), // Initial event to check auth status
          ),
          // Add other global BlocProviders here
          // e.g., BlocProvider<AppConfigBloc>(create: (_) => AppConfigBloc()..add(LoadConfig())),
        ],
        child: const MyApp(),
      ),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PyLabPraxis Flutter',
      debugShowCheckedModeBanner: false,

      theme: AppTheme.lightTheme,

      // darkTheme: AppTheme.darkTheme,
      // themeMode: ThemeMode.system,
      onGenerateRoute: AppRouter.generateRoute,
      home: const AppShell(),

      // Example of a global BlocListener for auth state changes
      builder: (context, child) {
        return BlocListener<AuthBloc, AuthState>(
          listener: (context, state) {
            print('AuthBloc state changed: $state'); // For debugging
            if (state is AuthUnauthenticated) {
              // Example: Navigate to a login screen if you had one
              // This is a simple example; complex navigation might be handled differently
              // For instance, AppShell itself could react to AuthState
              // if (ModalRoute.of(context)?.settings.name != AppRouter.login) { // Avoid pushing if already there
              //   Navigator.of(context).pushNamedAndRemoveUntil(AppRouter.login, (route) => false);
              // }
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('User is unauthenticated (Placeholder).'),
                ),
              );
            } else if (state is AuthAuthenticated) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('User is authenticated (Placeholder).'),
                ),
              );
              // Potentially navigate away from login screen if user was on it
            } else if (state is AuthFailure) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Auth Error: ${state.message}')),
              );
            }
          },
          child: child!, // The rest of your app
        );
      },
    );
  }
}
