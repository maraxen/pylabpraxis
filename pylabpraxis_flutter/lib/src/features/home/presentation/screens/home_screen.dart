import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  static const String routeName = '/'; // Matches AppRouter.home

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // AppBar is now part of AppShell
      // appBar: AppBar(
      //   title: const Text('Home'),
      // ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Welcome to PyLabPraxis!',
              style: Theme.of(context).textTheme.headlineMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Example navigation, though typically handled by BottomNavBar
                // Navigator.pushNamed(context, '/protocols');
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Navigate using bottom bar!')),
                );
              },
              child: const Text('View Protocols (Example)'),
            ),
            const SizedBox(height: 10),
            Text(
              'This is the Home Screen.',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }
}
