import 'dart:async'; // For StreamSubscription
import 'dart:developer' as developer; // For developer.log
import 'package:flutter/foundation.dart' show kIsWeb; // For kIsWeb check
import 'package:web/web.dart' hide Text;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart'; // For state.extra type casting

// Auth Feature
import 'package:praxis_lab_management/src/features/auth/application/bloc/auth_bloc.dart';
import 'package:praxis_lab_management/src/features/auth/presentation/screens/login_screen.dart';

// Core App Shell and Main Screens
import 'package:praxis_lab_management/src/core/widgets/app_shell.dart';
import 'package:praxis_lab_management/src/features/home/presentation/screens/home_screen.dart';
import 'package:praxis_lab_management/src/features/protocols/presentation/screens/protocols_screen.dart';
import 'package:praxis_lab_management/src/features/assetManagement/presentation/screens/assetManagement_screen.dart';
import 'package:praxis_lab_management/src/features/settings/presentation/screens/settings_screen.dart';
import 'package:praxis_lab_management/src/features/splash/presentation/screens/splash_screen.dart';

// Run Protocol Workflow Screens
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/run_protocol_workflow_screen.dart';
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/parameter_configuration_screen.dart';
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/asset_assignment_screen.dart';
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/deck_configuration_screen.dart';
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/review_and_prepare_screen.dart';
import 'package:praxis_lab_management/src/features/run_protocol/presentation/screens/start_protocol_screen.dart';

// --- Route Names ---
const String homeRouteName = 'home';
const String protocolsRouteName = 'protocols';
const String assetManagementRouteName = 'assetManagement';
const String settingsRouteName = 'settings';
const String splashRouteName = 'splash';
const String loginRouteName = 'login';

// Workflow Route Names (already defined in your provided code)
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
      initialLocation: '/splash',
      debugLogDiagnostics: true,
      refreshListenable: GoRouterRefreshStream(authBloc.stream),
      redirect: (BuildContext context, GoRouterState state) {
        final authState = authBloc.state;
        final goRouterUri = state.uri;
        final currentPath = goRouterUri.path;
        // --- OIDC Callback Detection ---
        bool isOidcCallbackUrl = false;
        Map<String, String> oidcParamsFromSource = {};

        final bool pathIsSplash = currentPath == '/splash';
        developer.log('Current path: $currentPath, isSplash: $pathIsSplash');
        developer.log('GoRouter URI: $goRouterUri');
        final bool hasStateInQuery = goRouterUri.queryParameters.containsKey(
          'state',
        );
        final bool hasCodeInQuery = goRouterUri.queryParameters.containsKey(
          'code',
        );
        final bool hasErrorInQuery = goRouterUri.queryParameters.containsKey(
          'error',
        );

        developer.log(
          'OIDC Callback detection on /splash: hasStateInQuery=$hasStateInQuery, hasCodeInQuery=$hasCodeInQuery, hasErrorInQuery=$hasErrorInQuery',
        );

        if (kIsWeb && pathIsSplash) {
          developer.log(
            'Web detected as current platform. Checking for OIDC callback on /splash.',
          );
          if (hasStateInQuery && (hasCodeInQuery || hasErrorInQuery)) {
            isOidcCallbackUrl = true;
            oidcParamsFromSource = goRouterUri.queryParameters;
            developer.log(
              'OIDC Callback (Auth Code Flow) detected on /splash via GoRouter query parameters: $oidcParamsFromSource',
            );
          } else {
            // Fallback to check browser fragment if query params are missing,
            // though with response_type=code, they should be in query.
            final String browserHash = window.location.hash;
            if (browserHash.startsWith('#')) {
              final String fragmentString = browserHash.substring(1);
              if (fragmentString.isNotEmpty) {
                try {
                  final browserFragmentParams = Uri.splitQueryString(
                    fragmentString,
                  );
                  final bool hasOidcParamsInFragment =
                      browserFragmentParams.containsKey('state') &&
                      (browserFragmentParams.containsKey('id_token') ||
                          browserFragmentParams.containsKey('access_token') ||
                          browserFragmentParams.containsKey('code') ||
                          browserFragmentParams.containsKey(
                            'session_state',
                          )); // Keycloak often includes session_state
                  final bool hasOidcErrorInFragment = browserFragmentParams
                      .containsKey('error');

                  if (hasOidcParamsInFragment || hasOidcErrorInFragment) {
                    isOidcCallbackUrl = true;
                    oidcParamsFromSource = browserFragmentParams;
                  }
                  developer.log(
                    'OIDC Callback (Auth Code Flow) detected on /splash via browser fragment: $browserFragmentParams',
                  );
                  developer.log(
                    'OIDC Callback check on /splash via direct browser fragment: hash="$browserHash", parsed=$browserFragmentParams, isOidcCallbackUrl=$isOidcCallbackUrl',
                    name: "AppGoRouter",
                  );
                } catch (e) {
                  developer.log(
                    "Error parsing browser hash for OIDC check: $e",
                    name: "AppGoRouter",
                  );
                }
              }
            }
          }
        }
        // --- End OIDC Callback Detection ---

        final isAuthenticated = authState is AuthAuthenticated;
        final isUnauthenticated =
            authState is AuthUnauthenticated || authState is AuthFailure;
        final isAuthInitialOrLoading =
            authState is AuthInitial || authState is AuthLoading;

        // Rule 1: If this IS an OIDC callback URL (on /splash with OIDC params in query/fragment)
        // This rule is paramount to let AuthService process the callback.
        if (isOidcCallbackUrl) {
          // If authentication has ALREADY completed successfully (e.g. very fast processing), go to home.
          if (isAuthenticated) {
            developer.log(
              'OIDC callback on /splash, already authenticated. Redirecting to /home.',
              name: 'AppGoRouter',
            );
            return '/home';
          }
          // If OIDC processing resulted in a definitive failure reported by AuthBloc.
          if (authState is AuthFailure) {
            developer.log(
              'OIDC callback on /splash, resulted in AuthFailure. Redirecting to /login.',
              name: 'AppGoRouter',
            );
            return '/login';
          }
          // Otherwise (AuthInitial, AuthLoading, or even an initial AuthUnauthenticated from AuthAppStarted's first pass
          // *before* OIDC processing from AuthService init completes and updates the stream), STAY ON /splash.
          developer.log(
            'OIDC callback on /splash. AuthState is ${authState.runtimeType}. Waiting for OIDC processing to complete via AuthService. No redirect from router.',
            name: 'AppGoRouter',
          );
          return null;
        }

        if (isAuthInitialOrLoading) {
          if (currentPath != '/splash') {
            developer.log(
              'Authenticating (AuthInitial/AuthLoading, not OIDC callback), not on /splash. Redirecting to /splash.',
              name: 'AppGoRouter',
            );
            return '/splash';
          }
          developer.log(
            'Authenticating on /splash (AuthInitial/AuthLoading, not an OIDC callback). Waiting for AuthBloc. No redirect.',
            name: 'AppGoRouter',
          );
          return null; // Stay on splash
        }

        // Rule 3: User is definitively Authenticated (and it was not an OIDC callback URL we just processed under Rule 1)
        if (isAuthenticated) {
          if (currentPath == '/login' || currentPath == '/splash') {
            // Splash is no longer an auth pending page if not OIDC callback
            developer.log(
              'Authenticated (not via immediate OIDC callback). Redirecting from $currentPath to /home.',
              name: 'AppGoRouter',
            );
            return '/home';
          }
          developer.log(
            'Authenticated. Not on login/splash. No redirect.',
            name: 'AppGoRouter',
          );
          return null; // Already on a protected route
        }

        // Rule 4: User is definitively Unauthenticated (AuthUnauthenticated or AuthFailure, and not an OIDC callback URL)
        if (isUnauthenticated) {
          // AuthUnauthenticated or AuthFailure
          if (currentPath != '/login') {
            developer.log(
              'Unauthenticated (not an OIDC callback). Not on /login. Current path: $currentPath. Redirecting to /login.',
              name: 'AppGoRouter',
            );
            return '/login';
          }
          developer.log(
            'Unauthenticated. On /login. No redirect.',
            name: 'AppGoRouter',
          );
          return null; // Already on login screen
        }

        developer.log(
          'No redirect conditions met by AppGoRouter (should not happen). Current path: $currentPath',
          name: 'AppGoRouter',
        );
        return null;
      },
      routes: <RouteBase>[
        GoRoute(
          path: '/splash',
          name: splashRouteName,
          builder: (BuildContext context, GoRouterState state) {
            return const SplashScreen();
          },
        ),
        GoRoute(
          path: '/login',
          name: loginRouteName,
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
          parentNavigatorKey: _rootNavigatorKey,
          builder: (BuildContext context, GoRouterState state, Widget child) {
            final protocolInfo = state.extra as ProtocolInfo?;
            return RunProtocolWorkflowScreen(
              protocolInfo: protocolInfo,
              child: child,
            );
          },
          routes: <RouteBase>[
            GoRoute(
              path:
                  '/run-protocol-workflow/parameters', // Base path for this step
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
                'Oops! Page not found: ${state.error?.message ?? 'Unknown error'} at path ${state.uri}',
              ),
            ),
          ),
    );
  }
}

// GoRouterRefreshStream class remains the same
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
