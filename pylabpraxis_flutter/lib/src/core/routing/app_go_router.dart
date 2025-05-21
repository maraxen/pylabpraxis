import 'dart:async'; // Added for StreamSubscription
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart'; // For state.extra type casting

// Auth Feature
import 'package:pylabpraxis_flutter/src/features/auth/application/bloc/auth_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/auth/presentation/screens/login_screen.dart';

// Core App Shell and Main Screens
import 'package:pylabpraxis_flutter/src/core/widgets/app_shell.dart';
import 'package:pylabpraxis_flutter/src/features/home/presentation/screens/home_screen.dart';
import 'package:pylabpraxis_flutter/src/features/protocols/presentation/screens/protocols_screen.dart';
import 'package:pylabpraxis_flutter/src/features/assetManagement/presentation/screens/assetManagement_screen.dart';
import 'package:pylabpraxis_flutter/src/features/settings/presentation/screens/settings_screen.dart';
import 'package:pylabpraxis_flutter/src/features/splash/presentation/screens/splash_screen.dart';

// Run Protocol Workflow Screens
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/run_protocol_workflow_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/parameter_configuration_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/asset_assignment_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/deck_configuration_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/review_and_prepare_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/start_protocol_screen.dart';

// --- Route Names ---
const String homeRouteName = 'home';
const String protocolsRouteName = 'protocols';
const String assetManagementRouteName = 'assetManagement';
const String settingsRouteName = 'settings';

const String parameterConfigurationRouteName = 'parameterConfiguration';
const String assetAssignmentRouteName = 'assetAssignment';
const String deckConfigurationRouteName = 'deckConfiguration';
const String reviewAndPrepareRouteName = 'reviewAndPrepare';
const String startProtocolRouteName = 'startProtocol';

const String beginProtocolWorkflowRouteName = parameterConfigurationRouteName;

// Navigator keys
final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>(
  debugLabel: 'root',
);
final GlobalKey<NavigatorState> _shellNavigatorKey = GlobalKey<NavigatorState>(
  debugLabel: 'shell',
);
final GlobalKey<NavigatorState> _workflowShellNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'workflowShell');

class AppGoRouter {
  final AuthBloc authBloc;
  late final GoRouter router;

  AppGoRouter(this.authBloc) {
    router = GoRouter(
      navigatorKey: _rootNavigatorKey,
      initialLocation: '/splash', // Always start at splash
      debugLogDiagnostics: true,
      refreshListenable: GoRouterRefreshStream(authBloc.stream),
      redirect: (BuildContext context, GoRouterState state) {
        final authState = authBloc.state;
        final uri = state.uri; // This is the full URI go_router is considering
        final currentPath = uri.path; // The path part, e.g. /login, /splash

        // For web (hash strategy), OIDC params are often in the fragment.
        // GoRouter's state.uri often reflects the fragment as its "location".
        // We need to parse parameters from this effective location string.
        String effectiveLocationString = uri.toString();
        if (effectiveLocationString.startsWith('/')) {
          effectiveLocationString = effectiveLocationString.substring(1);
        }

        Map<String, String> effectiveParams = {};
        if (effectiveLocationString.contains('=')) {
          // Basic check for query-like string
          try {
            effectiveParams = Uri.splitQueryString(effectiveLocationString);
          } catch (e) {
            print("Error parsing effectiveLocationString as query string: $e");
          }
        }

        final bool isOidcCallbackUrl =
            effectiveParams.containsKey('state') &&
            (effectiveParams.containsKey('code') ||
                effectiveParams.containsKey('id_token') ||
                effectiveParams.containsKey('session_state'));

        final isAuthenticating =
            authState is AuthInitial || authState is AuthLoading;
        final isAuthenticated = authState is AuthAuthenticated;
        final isUnauthenticated =
            authState is AuthUnauthenticated || authState is AuthFailure;

        print(
          'Redirect Check: AuthState: $authState, CurrentPath: $currentPath, isOidcCallback: $isOidcCallbackUrl, EffectiveLocationParams: $effectiveParams, GoRouter URI: $uri, MatchedLoc: ${state.matchedLocation}',
        );

        // Scenario 1: AuthBloc is currently working (AuthInitial or AuthLoading)
        if (isAuthenticating) {
          if (isOidcCallbackUrl) {
            print(
              'OIDC callback detected during auth processing (AuthInitial/AuthLoading). No redirect from router.',
            );
            return null; // Allow AuthBloc to process the OIDC callback URL
          }
          if (authState is AuthLoading && currentPath == '/login') {
            print(
              'AuthLoading on /login (OIDC redirect likely in progress). No redirect from router.',
            );
            return null;
          }
          if (currentPath != '/splash') {
            print(
              'Authenticating (not OIDC callback/initiation from login), not on splash. Redirecting to /splash.',
            );
            return '/splash';
          }
          print(
            'Authenticating, on splash or OIDC callback/initiation being handled. No redirect from this block.',
          );
          return null;
        }

        // Scenario 2: User is authenticated
        if (isAuthenticated) {
          if (currentPath == '/login' ||
              currentPath == '/splash' ||
              isOidcCallbackUrl) {
            // Also handle if somehow authenticated on callback URL
            print(
              'Authenticated. Redirecting from $currentPath (or OIDC callback) to /home.',
            );
            return '/home';
          }
          print(
            'Authenticated. Not on login/splash/OIDC callback. No redirect.',
          );
          return null;
        }

        // Scenario 3: User is unauthenticated (AuthUnauthenticated or AuthFailure)
        if (isUnauthenticated) {
          if (isOidcCallbackUrl) {
            print(
              'OIDC callback processed, but result is Unauthenticated/Failure. Redirecting to /login.',
            );
            return '/login';
          }
          if (currentPath == '/splash') {
            print('Unauthenticated. On splash. Redirecting to /login.');
            return '/login';
          }
          if (currentPath != '/login') {
            print(
              'Unauthenticated (not OIDC callback). Not on login (and not splash). Redirecting to /login.',
            );
            return '/login';
          }
          print('Unauthenticated. On login. No redirect from this block.');
          return null;
        }

        print('No redirect conditions met. Path: $currentPath');
        return null;
      },
      routes: <RouteBase>[
        GoRoute(
          path: '/splash',
          name: 'splash',
          builder: (BuildContext context, GoRouterState state) {
            return const SplashScreen();
          },
        ),
        GoRoute(
          path: '/login',
          name: 'login',
          builder: (BuildContext context, GoRouterState state) {
            return const LoginScreen();
          },
        ),
        ShellRoute(
          navigatorKey: _shellNavigatorKey,
          builder: (BuildContext context, GoRouterState state, Widget child) {
            return AppShell(child: child);
          },
          routes: <RouteBase>[
            GoRoute(
              path: '/home',
              name: homeRouteName,
              pageBuilder:
                  (context, state) =>
                      const NoTransitionPage(child: HomeScreen()),
            ),
            GoRoute(
              path: '/protocols',
              name: protocolsRouteName,
              pageBuilder:
                  (context, state) =>
                      const NoTransitionPage(child: ProtocolsScreen()),
            ),
            GoRoute(
              path: '/asset-management',
              name: assetManagementRouteName,
              pageBuilder:
                  (context, state) =>
                      const NoTransitionPage(child: AssetManagementScreen()),
            ),
            GoRoute(
              path: '/settings',
              name: settingsRouteName,
              pageBuilder:
                  (context, state) =>
                      const NoTransitionPage(child: SettingsScreen()),
            ),
          ],
        ),
        ShellRoute(
          navigatorKey: _workflowShellNavigatorKey,
          builder: (BuildContext context, GoRouterState state, Widget child) {
            final protocolInfo = state.extra as ProtocolInfo?;
            return RunProtocolWorkflowScreen(
              protocolInfo: protocolInfo,
              child: child,
            );
          },
          routes: <RouteBase>[
            GoRoute(
              path: '/run-protocol-workflow/parameters',
              name: parameterConfigurationRouteName,
              builder: (BuildContext context, GoRouterState state) {
                return const ParameterConfigurationScreen();
              },
            ),
            GoRoute(
              path: '/run-protocol-workflow/assets',
              name: assetAssignmentRouteName,
              builder: (BuildContext context, GoRouterState state) {
                return const AssetAssignmentScreen();
              },
            ),
            GoRoute(
              path: '/run-protocol-workflow/deck',
              name: deckConfigurationRouteName,
              builder: (BuildContext context, GoRouterState state) {
                return const DeckConfigurationScreen();
              },
            ),
            GoRoute(
              path: '/run-protocol-workflow/review',
              name: reviewAndPrepareRouteName,
              builder: (BuildContext context, GoRouterState state) {
                return const ReviewAndPrepareScreen();
              },
            ),
            GoRoute(
              path: '/run-protocol-workflow/start',
              name: startProtocolRouteName,
              builder: (BuildContext context, GoRouterState state) {
                return const StartProtocolScreen();
              },
            ),
          ],
        ),
      ],
      errorBuilder:
          (context, state) => Scaffold(
            appBar: AppBar(title: const Text('Page Not Found')),
            body: Center(
              child: Text(
                'Oops! Page not found: ${state.error?.message} from path ${state.uri}',
              ),
            ),
          ),
    );
  }
}

class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(Stream<dynamic> stream) {
    notifyListeners();
    _subscription = stream.asBroadcastStream().listen(
      (dynamic _) => notifyListeners(),
    );
  }

  late final StreamSubscription<dynamic> _subscription;

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}
