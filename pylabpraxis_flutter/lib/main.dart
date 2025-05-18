import 'dart:async'; // For PlatformDispatcher.instance.onError & runZonedGuarded
import 'dart:developer' as developer; // For developer.log

import 'package:flutter/foundation.dart'; // For kDebugMode and PlatformDispatcher
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; // For secure storage
import 'package:get_it/get_it.dart'; // For service locator (optional, but good practice)

// Core imports
import 'src/core/network/dio_client.dart'; // For DioClient
import 'src/core/theme/app_theme.dart';
import 'src/core/routing/app_router.dart';
import 'src/core/widgets/app_shell.dart'; // Your main app UI after login

// Data Layer Imports (Services & Repositories & Implementations)
import 'src/data/services/auth_service.dart';
import 'src/data/services/auth_service_impl.dart';
import 'src/data/services/protocol_api_service.dart';
import 'src/data/services/protocol_api_service_impl.dart';
import 'src/data/repositories/auth_repository.dart';
import 'src/data/repositories/protocol_repository.dart';

// Feature Layer Imports (BLoCs & Screens)
import 'src/features/auth/application/bloc/auth_bloc.dart';

// Import the LoginScreen (adjust path if necessary)
import 'src/features/auth/presentation/screens/login_screen.dart';

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
    // To avoid overly verbose logs for complex states, consider logging selectively.
    // For instance, log only the runtimeType of states or specific properties.
    // developer.log(
    //   'Change in ${bloc.runtimeType}: ${change.currentState.runtimeType} -> ${change.nextState.runtimeType}',
    //   name: 'AppBlocObserver',
    // );
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    super.onTransition(bloc, transition);
    // developer.log(
    //   'Transition in ${bloc.runtimeType}: ${transition.event} -> Current: ${transition.currentState.runtimeType}, Next: ${transition.nextState.runtimeType}',
    //   name: 'AppBlocObserver',
    // );
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

// Initialize GetIt service locator instance
final GetIt sl = GetIt.instance;

// Function to setup service locator
Future<void> setupServiceLocator() async {
  // External Packages
  sl.registerLazySingleton<FlutterSecureStorage>(() {
    // Configure FlutterSecureStorage with WebOptions if on web
    if (kIsWeb) {
      return const FlutterSecureStorage(
        // IMPORTANT: Replace these placeholder values with your securely generated,
        // unique, and persistent application-specific keys and IVs.
        // These are used to wrap the encryption key for data stored in LocalStorage.
        // wrapKey should be a Base64 encoded 256-bit (32-byte) key.
        // wrapKeyIv should be a Base64 encoded 128-bit (16-byte) IV.
        // Generate these once (e.g., using a crypto library) and store them securely.
        // DO NOT USE THESE EXAMPLE VALUES IN PRODUCTION.
        webOptions: WebOptions(
          wrapKey:
              'YOUR_APP_SPECIFIC_ENCRYPTION_KEY_BASE64_32BYTES', // REPLACE THIS
          wrapKeyIv:
              'YOUR_APP_SPECIFIC_ENCRYPTION_IV_BASE64_16BYTES', // REPLACE THIS
        ),
      );
    } else {
      // For mobile, default options or platform-specific options can be used.
      return const FlutterSecureStorage(
        // Example: aOptions: AndroidOptions(encryptedSharedPreferences: true),
      );
    }
  });

  // Services
  sl.registerLazySingleton<AuthService>(
    () => AuthServiceImpl(secureStorage: sl<FlutterSecureStorage>()),
  );
  sl.registerLazySingleton<DioClient>(
    () => DioClient(authService: sl<AuthService>()),
  );
  sl.registerLazySingleton<ProtocolApiService>(
    () => ProtocolApiServiceImpl(dioClient: sl<DioClient>()),
  );

  // Repositories
  sl.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(authService: sl<AuthService>()),
  );
  sl.registerLazySingleton<ProtocolRepository>(
    () => ProtocolRepositoryImpl(protocolApiService: sl<ProtocolApiService>()),
  );

  developer.log('Service Locator Initialized', name: 'main');
}

void main() {
  runZonedGuarded<Future<void>>(
    () async {
      WidgetsFlutterBinding.ensureInitialized();
      Bloc.observer = AppBlocObserver();

      FlutterError.onError = (FlutterErrorDetails details) {
        developer.log(
          'Flutter error caught by FlutterError.onError:',
          name: 'FlutterError',
          error: details.exception,
          stackTrace: details.stack,
        );
        if (kDebugMode) {
          FlutterError.dumpErrorToConsole(details);
        }
      };

      PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
        developer.log(
          'Unhandled error caught by PlatformDispatcher.instance.onError:',
          name: 'PlatformError',
          error: error,
          stackTrace: stack,
        );
        return true;
      };

      await setupServiceLocator();

      runApp(
        MultiRepositoryProvider(
          providers: [
            RepositoryProvider<AuthRepository>.value(
              value: sl<AuthRepository>(),
            ),
            RepositoryProvider<ProtocolRepository>.value(
              value: sl<ProtocolRepository>(),
            ),
          ],
          child: MultiBlocProvider(
            providers: [
              BlocProvider<AuthBloc>(
                create:
                    (context) =>
                        AuthBloc(authRepository: context.read<AuthRepository>())
                          ..add(
                            AuthAppStarted(),
                          ), // Dispatch initial event to check auth status
              ),
              // Add other BLoCs here
            ],
            child: const MyApp(),
          ),
        ),
      );
    },
    (Object error, StackTrace stack) {
      developer.log(
        'Unhandled error caught by runZonedGuarded:',
        name: 'ZoneError',
        error: error,
        stackTrace: stack,
      );
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
      // darkTheme: AppTheme.darkTheme,
      // themeMode: ThemeMode.system,

      // The onGenerateRoute might still be useful for named routes within AppShell
      // but the initial screen (Login or AppShell) is determined by the BlocBuilder below.
      onGenerateRoute: AppRouter.generateRoute,

      // Use BlocBuilder to determine the initial screen based on AuthState
      home: BlocBuilder<AuthBloc, AuthState>(
        builder: (context, state) {
          developer.log(
            'AuthBloc state changed in MyApp (home builder): ${state.runtimeType}',
            name: 'MyAppHomeBuilder',
          );
          if (state is AuthAuthenticated) {
            // User is signed in, show the main app shell
            return const AppShell();
          } else if (state is AuthUnauthenticated || state is AuthFailure) {
            // User is not signed in, or an auth error occurred that led to unauthenticated state
            // Show the login screen. AuthFailure might also be handled by the listener below
            // to show a snackbar, but here we ensure LoginScreen is shown.
            return const LoginScreen();
          } else {
            // AuthInitial, AuthLoading
            // Show a loading indicator while checking auth status or processing login/logout
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
        },
      ),
      builder: (context, child) {
        // BlocListener for global Auth state changes (e.g., showing SnackBars for errors)
        // This child will be the widget returned by 'home' (LoginScreen, AppShell, or Loading).
        return BlocListener<AuthBloc, AuthState>(
          listener: (context, state) {
            developer.log(
              'AuthBloc state changed in MyApp (global listener): ${state.runtimeType}',
              name: 'AuthGlobalListener',
            );
            if (state is AuthFailure) {
              // Only show snackbar if not already on LoginScreen or if it's a general auth error
              // The LoginScreen itself might display more specific errors.
              // This global listener is good for errors that occur outside the login flow.
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Authentication Process Error: ${state.message}',
                  ),
                  backgroundColor: Colors.redAccent,
                  duration: const Duration(seconds: 5),
                ),
              );
            }
            // Potentially handle other global notifications or side effects here
          },
          child:
              child!, // child is the widget determined by the `home` BlocBuilder
        );
      },
    );
  }
}
