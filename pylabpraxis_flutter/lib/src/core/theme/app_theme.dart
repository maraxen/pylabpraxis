import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// Main color (seed for Material 3)
// Main: #ED7A9B

class AppTheme {
  // Private constructor to prevent instantiation
  AppTheme._();

  // Define the seed color for Material 3 theme generation
  static final Color _seedColor = const Color(0xFFED7A9B);

  // Define the default RobotoFlex variations based on your SCSS
  static const List<FontVariation> _robotoFlexVariations = [
    FontVariation('wght', 400.0),
    FontVariation('wdth', 100.0),
    FontVariation('opsz', 14.0),
    FontVariation('GRAD', 0.0),
    FontVariation('slnt', 0.0),
    FontVariation('XTRA', 468.0),
    FontVariation('YTAS', 750.0),
    FontVariation('YTDE', -203.0),
    FontVariation('YTFI', 738.0),
    FontVariation('YTLC', 514.0),
    FontVariation('YTUC', 712.0),
  ];

  static ThemeData get lightTheme {
    final ColorScheme colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.light,
    );

    // Get the base TextTheme with RobotoFlex family applied by google_fonts
    final baseTextTheme = GoogleFonts.robotoFlexTextTheme(
      ThemeData(brightness: colorScheme.brightness).textTheme,
    );

    final ThemeData robotoFlexTheme = ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,

      // fontFamily is now handled by google_fonts at the TextTheme level
      textTheme: _applyVariationsToTextTheme(baseTextTheme, colorScheme),

      // Define component themes
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surfaceContainerHighest,
        foregroundColor: colorScheme.onSurfaceVariant,
        elevation: 0,
        titleTextStyle: GoogleFonts.robotoFlex(
          color: colorScheme.onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w500,
        ).copyWith(
          fontVariations: _robotoFlexVariations,
        ), // Corrected application
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: colorScheme.surfaceContainer,
        indicatorColor: colorScheme.secondaryContainer,
        iconTheme: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return IconThemeData(color: colorScheme.onSecondaryContainer);
          }
          return IconThemeData(color: colorScheme.onSurfaceVariant);
        }),
        labelTextStyle: MaterialStateProperty.resolveWith((states) {
          final baseStyle = GoogleFonts.robotoFlex(
            // Use GoogleFonts.robotoFlex here
            fontSize: 12,
          ).copyWith(
            fontVariations: _robotoFlexVariations,
          ); // Corrected application
          if (states.contains(MaterialState.selected)) {
            return baseStyle.copyWith(
              color: colorScheme.onSurface,
              fontWeight: FontWeight.w500,
            );
          }
          return baseStyle.copyWith(
            color: colorScheme.onSurfaceVariant,
            fontWeight: FontWeight.normal,
          );
        }),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: colorScheme.primary,
          foregroundColor: colorScheme.onPrimary,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          textStyle: GoogleFonts.robotoFlex(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.1,
          ).copyWith(
            fontVariations: _robotoFlexVariations,
          ), // Corrected application
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.outline),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.outline),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.primary, width: 2.0),
        ),
        labelStyle: GoogleFonts.robotoFlex(
          textStyle: TextStyle(color: colorScheme.onSurfaceVariant),
        ).copyWith(
          fontVariations: _robotoFlexVariations,
        ), // Applied to ensure variations
        hintStyle: GoogleFonts.robotoFlex(
          textStyle: TextStyle(
            color: colorScheme.onSurfaceVariant.withOpacity(0.7),
          ),
        ).copyWith(
          fontVariations: _robotoFlexVariations,
        ), // Applied to ensure variations
        filled: true,
        fillColor: colorScheme.surfaceContainerHighest,
      ),
      cardTheme: CardTheme(
        elevation: 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.7)),
        ),
        color: colorScheme.surface,
        surfaceTintColor: colorScheme.surfaceTint,
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 0),
      ),
    );
    // Apply RobotoFlex variations to other InputDecorator's text styles if not inheriting correctly
    return robotoFlexTheme.copyWith(
      inputDecorationTheme: robotoFlexTheme.inputDecorationTheme.copyWith(
        // labelStyle and hintStyle already handled above.
        // If they were based on robotoFlexTheme.textTheme.bodyLarge, this would be one way:
        // labelStyle: robotoFlexTheme.textTheme.bodyLarge?.copyWith(
        //   color: colorScheme.onSurfaceVariant,
        //   fontVariations: _robotoFlexVariations // Already applied by _applyVariationsToTextTheme
        // ),
        // hintStyle: robotoFlexTheme.textTheme.bodyLarge?.copyWith(
        //   color: colorScheme.onSurfaceVariant.withOpacity(0.7),
        //   fontVariations: _robotoFlexVariations // Already applied
        // ),
        helperStyle: GoogleFonts.robotoFlex(
          textStyle: robotoFlexTheme.textTheme.bodySmall?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ).copyWith(fontVariations: _robotoFlexVariations), // Corrected
        errorStyle: GoogleFonts.robotoFlex(
          textStyle: robotoFlexTheme.textTheme.bodySmall?.copyWith(
            color: colorScheme.error,
          ),
        ).copyWith(fontVariations: _robotoFlexVariations), // Corrected
      ),
    );
  }

  static ThemeData get darkTheme {
    final ColorScheme colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.dark,
    );

    final baseTextTheme = GoogleFonts.robotoFlexTextTheme(
      ThemeData(brightness: colorScheme.brightness).textTheme,
    );

    final ThemeData robotoFlexTheme = ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: _applyVariationsToTextTheme(baseTextTheme, colorScheme),
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surfaceContainerHighest,
        foregroundColor: colorScheme.onSurfaceVariant,
        elevation: 0,
        titleTextStyle: GoogleFonts.robotoFlex(
          color: colorScheme.onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w500,
        ).copyWith(fontVariations: _robotoFlexVariations), // Corrected
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: colorScheme.surfaceContainer,
        indicatorColor: colorScheme.secondaryContainer,
        iconTheme: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return IconThemeData(color: colorScheme.onSecondaryContainer);
          }
          return IconThemeData(color: colorScheme.onSurfaceVariant);
        }),
        labelTextStyle: MaterialStateProperty.resolveWith((states) {
          final baseStyle = GoogleFonts.robotoFlex(
            fontSize: 12,
          ).copyWith(fontVariations: _robotoFlexVariations); // Corrected
          if (states.contains(MaterialState.selected)) {
            return baseStyle.copyWith(
              color: colorScheme.onSurface,
              fontWeight: FontWeight.w500,
            );
          }
          return baseStyle.copyWith(
            color: colorScheme.onSurfaceVariant,
            fontWeight: FontWeight.normal,
          );
        }),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: colorScheme.primary,
          foregroundColor: colorScheme.onPrimary,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          textStyle: GoogleFonts.robotoFlex(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.1,
          ).copyWith(fontVariations: _robotoFlexVariations), // Corrected
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.outline),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.outline),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.primary, width: 2.0),
        ),
        labelStyle: GoogleFonts.robotoFlex(
          textStyle: TextStyle(color: colorScheme.onSurfaceVariant),
        ).copyWith(fontVariations: _robotoFlexVariations),
        hintStyle: GoogleFonts.robotoFlex(
          textStyle: TextStyle(
            color: colorScheme.onSurfaceVariant.withOpacity(0.7),
          ),
        ).copyWith(fontVariations: _robotoFlexVariations),
        filled: true,
        fillColor: colorScheme.surfaceContainerHighest,
      ),
      cardTheme: CardTheme(
        elevation: 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.7)),
        ),
        color: colorScheme.surface,
        surfaceTintColor: colorScheme.surfaceTint,
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 0),
      ),
    );
    return robotoFlexTheme.copyWith(
      inputDecorationTheme: robotoFlexTheme.inputDecorationTheme.copyWith(
        helperStyle: GoogleFonts.robotoFlex(
          textStyle: robotoFlexTheme.textTheme.bodySmall?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ).copyWith(fontVariations: _robotoFlexVariations), // Corrected
        errorStyle: GoogleFonts.robotoFlex(
          textStyle: robotoFlexTheme.textTheme.bodySmall?.copyWith(
            color: colorScheme.error,
          ),
        ).copyWith(fontVariations: _robotoFlexVariations), // Corrected
      ),
    );
  }

  // Helper function to apply variations to each style in the TextTheme
  static TextTheme _applyVariationsToTextTheme(
    TextTheme baseTheme,
    ColorScheme colorScheme,
  ) {
    // This function correctly applies variations using .copyWith() on TextStyles
    return baseTheme
        .copyWith(
          displayLarge: baseTheme.displayLarge?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          displayMedium: baseTheme.displayMedium?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          displaySmall: baseTheme.displaySmall?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          headlineLarge: baseTheme.headlineLarge?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          headlineMedium: baseTheme.headlineMedium?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          headlineSmall: baseTheme.headlineSmall?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          titleLarge: baseTheme.titleLarge?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          titleMedium: baseTheme.titleMedium?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          titleSmall: baseTheme.titleSmall?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          bodyLarge: baseTheme.bodyLarge?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          bodyMedium: baseTheme.bodyMedium?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurface,
          ),
          bodySmall: baseTheme.bodySmall?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurfaceVariant,
          ),
          labelLarge: baseTheme.labelLarge?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onPrimary,
          ),
          labelMedium: baseTheme.labelMedium?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurfaceVariant,
          ),
          labelSmall: baseTheme.labelSmall?.copyWith(
            fontVariations: _robotoFlexVariations,
            color: colorScheme.onSurfaceVariant,
          ),
        )
        .apply(
          bodyColor: colorScheme.onSurface,
          displayColor: colorScheme.onSurface,
        );
  }
}
