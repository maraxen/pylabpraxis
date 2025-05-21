import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/auth/application/bloc/auth_bloc.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    // Dispatch the AuthAppStarted event to trigger the initial authentication check.
    // The AuthBloc's _onAuthAppStarted handler will manage the loading state
    // and subsequent auth state determination.
    // The go_router's redirect logic will then handle navigation based on the outcome.
    context.read<AuthBloc>().add(AuthAppStarted());
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 20),
            Text('Loading Praxis...'),
          ],
        ),
      ),
    );
  }
}
