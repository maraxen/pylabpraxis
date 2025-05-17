import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart'; // Import google_fonts

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    const String appName = 'PyLabPraxis Flutter';
    const Color seedColor = Color(0xFFED7A9B); // Your main app seed color

    // --- Base TextThemes ---
    // Retrieve the default Material 3 text theme for light and dark brightness
    final TextTheme defaultLightTextTheme = ThemeData.light().textTheme;
    final TextTheme defaultDarkTextTheme = ThemeData.dark().textTheme;

    // --- Apply Roboto Flex ---
    // Apply Roboto Flex to the default light text theme
    final TextTheme robotoFlexLightTextTheme = GoogleFonts.robotoFlexTextTheme(
      defaultLightTextTheme,
    ).copyWith(
      // You can override specific styles here if needed.
      // For example, if you want titleLarge to always be a specific weight:
      // titleLarge: GoogleFonts.robotoFlex(
      //   fontSize: defaultLightTextTheme.titleLarge?.fontSize, // Keep M3 size
      //   fontWeight: FontWeight.w500, // Explicit weight
      //   letterSpacing: defaultLightTextTheme.titleLarge?.letterSpacing, // Keep M3 spacing
      //   color: defaultLightTextTheme.titleLarge?.color, // Keep M3 color
      // ),
    );

    // Apply Roboto Flex to the default dark text theme
    final TextTheme robotoFlexDarkTextTheme = GoogleFonts.robotoFlexTextTheme(
      defaultDarkTextTheme,
    ).copyWith(
      // Ensure text colors are suitable for dark backgrounds if not already handled
      // The google_fonts textTheme applicators usually handle this well.
      // Example of explicit color override if needed for dark theme:
      // bodyMedium: GoogleFonts.robotoFlex(
      //     fontSize: defaultDarkTextTheme.bodyMedium?.fontSize,
      //     fontWeight: defaultDarkTextTheme.bodyMedium?.fontWeight,
      //     color: Colors.white70 // An example explicit color
      // ),
    );

    // Define Light Theme directly
    final ThemeData lightTheme = ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: seedColor,
        brightness: Brightness.light,
      ),
      textTheme: robotoFlexLightTextTheme,
      // You can also define component themes directly here:
      // elevatedButtonTheme: ...,
      // appBarTheme: ...,
    );

    // Define Dark Theme directly
    final ThemeData darkTheme = ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: seedColor,
        brightness: Brightness.dark,
      ),
      textTheme: robotoFlexDarkTextTheme,
      // Component themes for dark mode
      // appBarTheme: ...,
    );

    return MaterialApp(
      title: appName,
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: ThemeMode.system,
      home: const MyHomePage(title: appName),
    );
  }
}

class MyHomePage extends StatelessWidget {
  final String title;
  static const Color seedColor = Color(0xFFED7A9B);

  const MyHomePage({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    final ColorScheme colorScheme = Theme.of(context).colorScheme;
    final TextTheme textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          title,
          // Example of using a specific text style
          style: textTheme.titleLarge?.copyWith(color: colorScheme.onPrimary),
        ),
        backgroundColor: colorScheme.primary,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Text(
                'Welcome to PyLabPraxis!',
                style: textTheme.displaySmall, // Uses Roboto Flex
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8.0),
                color: colorScheme.secondaryContainer,
                child: Text(
                  'Font: Roboto Flex. Seed: #${seedColor.value.toRadixString(16).substring(2).toUpperCase()}',
                  style: textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSecondaryContainer,
                  ), // Uses Roboto Flex
                ),
              ),
              const SizedBox(height: 30),
              ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: colorScheme.onPrimary,
                ),
                // Button text will also use Roboto Flex via default ButtonStyle or TextTheme.labelLarge
                child: Text('Primary Action', style: textTheme.labelLarge),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: () {},
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: colorScheme.primary),
                  foregroundColor: colorScheme.primary,
                ),
                child: Text('Secondary Action', style: textTheme.labelLarge),
              ),
              const SizedBox(height: 20),
              Card(
                elevation: 2,
                color: colorScheme.surfaceContainerHighest,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    'This is a Card widget using Roboto Flex.',
                    style: textTheme.bodyLarge?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ), // Uses Roboto Flex
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        tooltip: 'Action',
        backgroundColor: colorScheme.tertiary,
        foregroundColor: colorScheme.onTertiary,
        child: const Icon(Icons.add_task_rounded),
      ),
    );
  }
}
