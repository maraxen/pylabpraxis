// lib/src/features/auth/presentation/screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'dart:developer' as developer;

// Assuming AuthBloc and its events/states are in this path or similar
import '../../application/bloc/auth_bloc.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login - PyLabPraxis'),
        automaticallyImplyLeading: false, // No back button on login screen
      ),
      body: BlocListener<AuthBloc, AuthState>(
        listener: (context, state) {
          // Listener for navigation or global messages if needed from login screen itself
          // For example, if AuthFailure should show a dialog specifically on this screen
          if (state is AuthFailure) {
            // The global listener in MyApp might already handle this with a SnackBar
            developer.log(
              'AuthFailure detected in LoginScreen listener: ${state.message}',
              name: 'LoginScreen',
            );
            // Optionally, show a dialog or a more prominent error on the login screen itself
            // ScaffoldMessenger.of(context).showSnackBar(
            //   SnackBar(
            //     content: Text('Login Error: ${state.message}'),
            //     backgroundColor: Colors.red,
            //   ),
            // );
          }
        },
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                Text(
                  'Welcome to PyLabPraxis',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 30),
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (context, state) {
                    if (state is AuthLoading) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    return ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        textStyle: const TextStyle(fontSize: 18),
                      ),
                      onPressed: () {
                        developer.log(
                          'Sign In button pressed, dispatching AuthSignInRequested',
                          name: 'LoginScreen',
                        );
                        // Dispatch sign-in event to AuthBloc
                        context.read<AuthBloc>().add(AuthSignInRequested());
                      },
                      child: const Text('Sign In with Keycloak'),
                    );
                  },
                ),
                const SizedBox(height: 10),
                // Display error message from AuthFailure state if not handled globally
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (context, state) {
                    if (state is AuthFailure) {
                      return Padding(
                        padding: const EdgeInsets.only(top: 16.0),
                        child: Text(
                          'Error: ${state.message}',
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Colors.red,
                            fontSize: 16,
                          ),
                        ),
                      );
                    }
                    return const SizedBox.shrink(); // No error, show nothing
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
