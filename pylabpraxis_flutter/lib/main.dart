import 'dart:async'; // For PlatformDispatcher.instance.onError
import 'dart:developer' as developer; // For developer.log

import 'package:flutter/foundation.dart'; // For kDebugMode and PlatformDispatcher
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

// Core imports
import 'src/core/theme/app_theme.dart';
import 'src/core/routing/app_router.dart';
import 'src/core/widgets/app_shell.dart';

// Data Layer Imports (Services & Repositories)
import 'src/data/services/auth_service.dart';
import 'src/data/services/protocol_api_service.dart';
import 'src/data/services/protocol_api_service_impl.dart';
import 'src/data/repositories/auth_repository.dart';
import 'src/data/repositories/protocol_repository.dart';

// Feature Layer Imports (BLoCs)
import 'src/features/auth/application/bloc/auth_bloc.dart';

// Simple BlocObserver for logging BLoC events and transitions
class AppBlocObserver extends BlocObserver {
  @override
  void onCreate(BlocBase bloc) {
    super.onCreate(bloc);
    developer.log('Bloc CREATED: ${bloc.runtimeType}', name: 'AppBlocObserver');
  }

  @override
  void onEvent(Bloc bloc, Object? event) {
    super.onEvent(bloc, event);
    developer.log(
      'Event in ${bloc.runtimeType}: $event',
      name: 'AppBlocObserver',
    );
  }

  @override
  void onChange(BlocBase bloc, Change change) {
    super.onChange(bloc, change);
    developer.log(
      'Change in ${bloc.runtimeType}: ${change.currentState} -> ${change.nextState}',
      name: 'AppBlocObserver',
    );
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    super.onTransition(bloc, transition);
    developer.log(
      'Transition in ${bloc.runtimeType}: ${transition.event} -> ${transition.nextState}',
      name: 'AppBlocObserver',
    );
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    developer.log(
      'Error in ${bloc.runtimeType}: $error',
      name: 'AppBlocObserver',
      error: error,
      stackTrace: stackTrace,
    );
    super.onError(bloc, error, stackTrace);
  }

  @override
  void onClose(BlocBase bloc) {
    super.onClose(bloc);
    developer.log('Bloc CLOSED: ${bloc.runtimeType}', name: 'AppBlocObserver');
  }
}

void main() {
  // This function will run the app with error handling and logging.
  runZonedGuarded<Future<void>>(
    () async {
      // Ensure Flutter bindings are initialized
      WidgetsFlutterBinding.ensureInitialized();

      // Setup BlocObserver
      Bloc.observer = AppBlocObserver();

      // Setup basic error handling for Flutter framework errors
      FlutterError.onError = (FlutterErrorDetails details) {
        // Log the error to the console.
        // In a real app, you might send this to an error reporting service.
        developer.log(
          'Flutter error caught by FlutterError.onError:',
          name: 'FlutterError',
          error: details.exception,
          stackTrace: details.stack,
        );
        // Optionally, display a user-friendly error message in debug mode.
        if (kDebugMode) {
          FlutterError.dumpErrorToConsole(details);
        }
      };

      // Setup basic error handling for other unhandled errors (e.g., async errors)
      PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
        developer.log(
          'Unhandled error caught by PlatformDispatcher.instance.onError:',
          name: 'PlatformError',
          error: error,
          stackTrace: stack,
        );
        // In a real app, report to an error service.
        // Returning true tells Flutter that the error has been handled.
        return true;
      };

      // TODO: Set up more advanced logging (e.g., using the 'logging' package) if needed.
      // TODO: Set up remote error reporting (e.g., Sentry, Firebase Crashlytics) for release builds.

      // Initialize services
      final AuthService authService = AuthServiceImpl();
      final ProtocolApiService protocolApiService = ProtocolApiServiceImpl(
        dioClient: null,
      ); // TODO: Pass a valid DioClient instance

      // Initialize repositories
      final AuthRepository authRepository = AuthRepositoryImpl(
        authService: authService,
      );
      final ProtocolRepository protocolRepository = ProtocolRepositoryImpl(
        protocolApiService: protocolApiService,
      );

      runApp(
        MultiRepositoryProvider(
          providers: [
            RepositoryProvider<AuthRepository>.value(value: authRepository),
            RepositoryProvider<ProtocolRepository>.value(
              value: protocolRepository,
            ),
          ],
          child: MultiBlocProvider(
            providers: [
              BlocProvider<AuthBloc>(
                create:
                    (context) =>
                        AuthBloc(authRepository: context.read<AuthRepository>())
                          ..add(AuthAppStarted()),
              ),
            ],
            child: const MyApp(),
          ),
        ),
      );
    },
    (Object error, StackTrace stack) {
      // This is the zone error handler. Errors caught here are critical.
      developer.log(
        'Unhandled error caught by runZonedGuarded:',
        name: 'ZoneError',
        error: error,
        stackTrace: stack,
      );
      // In a real app, report to an error service.
    },
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
      onGenerateRoute: AppRouter.generateRoute,
      home: const AppShell(),
      builder: (context, child) {
        return BlocListener<AuthBloc, AuthState>(
          listener: (context, state) {
            developer.log(
              'AuthBloc state changed in UI: $state',
              name: 'AuthUIListener',
            );
            if (state is AuthUnauthenticated) {
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
            } else if (state is AuthFailure) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Auth Error: ${state.message}')),
              );
            }
          },
          child: child!,
        );
      },
    );
  }
}
