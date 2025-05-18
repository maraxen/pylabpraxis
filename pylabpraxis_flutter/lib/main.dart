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
import 'src/core/widgets/app_shell.dart';

// Data Layer Imports (Services & Repositories & Implementations)
import 'src/data/services/auth_service.dart';
import 'src/data/services/auth_service_impl.dart';
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
    // Avoid logging overly verbose states if they are complex
    // Consider logging only specific parts or using a custom toString if needed.
    // developer.log(
    //   'Change in ${bloc.runtimeType}: ${change.currentState} -> ${change.nextState}',
    //   name: 'AppBlocObserver',
    // );
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    super.onTransition(bloc, transition);
    // developer.log(
    //   'Transition in ${bloc.runtimeType}: ${transition.event} -> ${transition.nextState}',
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
  sl.registerLazySingleton<FlutterSecureStorage>(
    () => const FlutterSecureStorage(
      // Optional: Configure AndroidOptions and IOSOptions for FlutterSecureStorage
      // aOptions: AndroidOptions(encryptedSharedPreferences: true),
    ),
  );

  // Services
  // Register AuthService (AuthServiceImpl depends on FlutterSecureStorage)
  sl.registerLazySingleton<AuthService>(
    () => AuthServiceImpl(secureStorage: sl<FlutterSecureStorage>()),
  );

  // Register DioClient (DioClient depends on AuthService)
  sl.registerLazySingleton<DioClient>(
    () => DioClient(authService: sl<AuthService>()),
  );

  // Register ProtocolApiService (ProtocolApiServiceImpl depends on DioClient)
  sl.registerLazySingleton<ProtocolApiService>(
    () => ProtocolApiServiceImpl(dioClient: sl<DioClient>()),
  );

  // Repositories
  // Register AuthRepository (AuthRepositoryImpl depends on AuthService)
  sl.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(authService: sl<AuthService>()),
  );

  // Register ProtocolRepository (ProtocolRepositoryImpl depends on ProtocolApiService)
  sl.registerLazySingleton<ProtocolRepository>(
    () => ProtocolRepositoryImpl(protocolApiService: sl<ProtocolApiService>()),
  );

  developer.log('Service Locator Initialized', name: 'main');
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

      // Setup basic error handling for other unhandled errors
      PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
        developer.log(
          'Unhandled error caught by PlatformDispatcher.instance.onError:',
          name: 'PlatformError',
          error: error,
          stackTrace: stack,
        );
        return true; // Mark as handled
      };

      // Initialize Service Locator
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
            // You can also provide services directly if needed by UI and not through a BLoC/Repo
            // Provider<AuthService>.value(value: sl<AuthService>()),
          ],
          child: MultiBlocProvider(
            providers: [
              BlocProvider<AuthBloc>(
                create:
                    (context) => AuthBloc(
                      authRepository: context.read<AuthRepository>(),
                      // Or: authRepository: sl<AuthRepository>(), if not using context.read
                    )..add(AuthAppStarted()), // Dispatch initial event
              ),
              // Add other BLoCs here as needed
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
      // darkTheme: AppTheme.darkTheme, // Optional: define a dark theme
      // themeMode: ThemeMode.system, // Optional: follow system theme
      onGenerateRoute: AppRouter.generateRoute,
      // Start with AppShell which handles initial auth state checking or splash screen
      home: const AppShell(),
      builder: (context, child) {
        // BlocListener for global Auth state changes (e.g., showing SnackBars)
        return BlocListener<AuthBloc, AuthState>(
          listener: (context, state) {
            developer.log(
              'AuthBloc state changed in UI (MyApp builder): $state',
              name: 'AuthUIListener',
            );
            // Example: Show a snackbar on auth failure
            if (state is AuthFailure) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Authentication Error: ${state.message}'),
                  backgroundColor: Colors.red,
                ),
              );
            }
            // You might navigate or show other global UI feedback here
          },
          child: child!,
        );
      },
    );
  }
}
