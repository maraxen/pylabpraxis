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

// Workflow Step Sub-Routes (now top-level names for direct navigation into the shell)
// The ShellRoute builder will handle the ProtocolInfo passed as 'extra'
const String parameterConfigurationRouteName = 'parameterConfiguration';
const String assetAssignmentRouteName = 'assetAssignment';
const String deckConfigurationRouteName = 'deckConfiguration';
const String reviewAndPrepareRouteName = 'reviewAndPrepare';
const String startProtocolRouteName = 'startProtocol';

// This name can be used by ProtocolsScreen to target the first step of the workflow.
// It should match the name of the GoRoute for the first step (e.g., parameterConfigurationRouteName).
const String beginProtocolWorkflowRouteName = parameterConfigurationRouteName;

// Navigator keys
final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>(
  debugLabel: 'root',
);
final GlobalKey<NavigatorState> _shellNavigatorKey = GlobalKey<NavigatorState>(
  debugLabel: 'shell',
); // For main AppShell
final GlobalKey<NavigatorState> _workflowShellNavigatorKey =
    GlobalKey<NavigatorState>(
      debugLabel: 'workflowShell',
    ); // For Workflow Shell

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
        final currentLocation = state.uri.toString();
        final isAuthenticating =
            authState is AuthInitial || authState is AuthLoading;
        final isAuthenticated = authState is AuthAuthenticated;
        final isUnauthenticated =
            authState is AuthUnauthenticated || authState is AuthFailure;

        print(
          'Redirect Check: AuthState: $authState, Location: $currentLocation, MatchedLocation: ${state.matchedLocation}',
        ); // TODO: Remove in production and move to logging

        if (isAuthenticating && currentLocation != '/splash') {
          print('Redirecting to /splash (auth initial/loading)');
          return '/splash';
        }
        if (currentLocation == '/splash' && !isAuthenticating) {
          if (isAuthenticated) {
            print('Redirecting from /splash to /home (authenticated)');
            return '/home';
          } else {
            print(
              'Redirecting from /splash to /login (unauthenticated/failure)',
            );
            return '/login';
          }
        }

        if (isAuthenticated) {
          if (currentLocation == '/login') {
            print('Redirecting to /home (authenticated on login page)');
            return '/home';
          }
        } else if (isUnauthenticated) {
          // Allow /splash and /login for unauthenticated users.
          // For any other route, redirect to login.
          if (currentLocation != '/login' && currentLocation != '/splash') {
            print(
              'Redirecting to /login (unauthenticated, not on login/splash)',
            );
            return '/login';
          }
        }

        print('No redirection needed for $currentLocation');
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
        // Main App Shell
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
        // Protocol Workflow ShellRoute
        // This ShellRoute wraps all steps of the protocol workflow.
        // Navigation to '/run-protocol-workflow/parameters' (or other steps)
        // will render RunProtocolWorkflowScreen with the specific step screen as its child.
        ShellRoute(
          navigatorKey: _workflowShellNavigatorKey,
          builder: (BuildContext context, GoRouterState state, Widget child) {
            // RunProtocolWorkflowScreen will act as the shell for the steps.
            // It needs to receive the ProtocolInfo passed from ProtocolsScreen.
            // 'state.extra' here comes from the GoRoute that matched (e.g., parameters, assets).
            final protocolInfo = state.extra as ProtocolInfo?;
            return RunProtocolWorkflowScreen(
              protocolInfo: protocolInfo,
              child: child, // The current step's screen
            );
          },
          routes: <RouteBase>[
            GoRoute(
              path:
                  '/run-protocol-workflow/parameters', // Full path for the first step
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
              child: Text('Oops! Page not found: ${state.error?.message}'),
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
