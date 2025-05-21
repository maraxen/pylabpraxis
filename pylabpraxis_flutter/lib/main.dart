import 'dart:async'; // For PlatformDispatcher.instance.onError & runZonedGuarded
import 'dart:developer' as developer; // For developer.log

import 'package:flutter/foundation.dart'; // For kDebugMode and PlatformDispatcher
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; // For secure storage
import 'package:get_it/get_it.dart'; // For service locator

// Core imports
import 'src/core/network/dio_client.dart'; // For DioClient
import 'src/core/theme/app_theme.dart';
import 'src/core/routing/app_go_router.dart'; // Import AppGoRouter

// Data Layer Imports (Services & Repositories & Implementations)
import 'src/data/services/auth_service.dart';
import 'src/data/services/auth_service_impl.dart';
import 'src/data/services/protocol_api_service.dart';
import 'src/data/services/protocol_api_service_impl.dart';
import 'src/data/repositories/auth_repository.dart';
import 'src/data/repositories/protocol_repository.dart';

// Feature Layer Imports (BLoCs & Events)
import 'src/features/auth/application/bloc/auth_bloc.dart';

// Import other BLoCs you might provide globally, e.g.:
// import 'src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';

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
    if (kIsWeb) {
      return const FlutterSecureStorage(
        webOptions: WebOptions(
          // IMPORTANT: These are placeholders. Replace with your actual secure keys.
          wrapKey:
              'HfOqhiH1bqQiKhXkL4BAFyKtWkdH_o10PTQflvEY6aM', // REPLACE THIS
          wrapKeyIv: 'ZL3K9IfeCOqdjP+VM6y4aA==', // REPLACE THIS
        ),
      );
    } else {
      return const FlutterSecureStorage();
    }
  });

  // Services
  sl.registerLazySingleton<AuthService>(
    () => AuthServiceImpl(secureStorage: sl<FlutterSecureStorage>()),
  );
  // Assuming DioClient needs AuthService for interceptors.
  // If your DioClient doesn't directly depend on AuthService at construction,
  // you might initialize it differently or pass AuthService later.
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
        return true; // Indicate that the error has been handled
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
            // Add other RepositoryProviders if needed
          ],
          child: MultiBlocProvider(
            providers: [
              BlocProvider<AuthBloc>(
                create:
                    (context) =>
                        AuthBloc(authRepository: context.read<AuthRepository>())
                          ..add(AuthAppStarted()), // Dispatch initial event
              ),
              // Example of another BLoC:
              // BlocProvider<ProtocolsDiscoveryBloc>(
              //   create: (context) => ProtocolsDiscoveryBloc(
              //     protocolRepository: context.read<ProtocolRepository>(),
              //   )..add(ProtocolsLoadStarted()), // Dispatch initial event if needed
              // ),
            ],
            child: const MyApp(), // MyApp will now use GoRouter
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

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late final AppGoRouter _appGoRouter;

  @override
  void initState() {
    super.initState();
    // Initialize AppGoRouter here. It needs AuthBloc, which is available
    // from the context provided by MultiBlocProvider.
    _appGoRouter = AppGoRouter(context.read<AuthBloc>());
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'PyLabPraxis Flutter',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,

      // darkTheme: AppTheme.darkTheme, // Optional: uncomment if you have a dark theme
      // themeMode: ThemeMode.system, // Optional: set theme mode
      routerConfig: _appGoRouter.router, // Use the go_router configuration

      builder: (context, child) {
        // This child is the widget rendered by the router for the current route.
        // We can wrap it with a BlocListener for global Auth state changes.
        return BlocListener<AuthBloc, AuthState>(
          listener: (context, state) {
            developer.log(
              'AuthBloc state changed in MyApp (global listener): ${state.runtimeType}',
              name: 'AuthGlobalListener',
            );
            if (state is AuthFailure) {
              // Show a snackbar for authentication failures
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
            // Handle other global notifications or side effects here if needed
          },
          child: child!, // The router's current page
        );
      },
    );
  }
}
