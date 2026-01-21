# Theme Manifest Format for Praxis

This document outlines the proposed format for user-installable themes in the Praxis web client.

## 1. Theme Manifest Schema (`theme.json`)

The `theme.json` file is the core of a Praxis theme. It's a JSON file that defines the theme's metadata and its visual properties.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Praxis Theme Manifest",
  "description": "A manifest file for a Praxis UI theme.",
  "type": "object",
  "properties": {
    "name": {
      "description": "The name of the theme.",
      "type": "string"
    },
    "author": {
      "description": "The author of the theme.",
      "type": "string"
    },
    "version": {
      "description": "The version of the theme. Must be a valid semantic version.",
      "type": "string",
      "pattern": "^(0|[1-9]\\\\d*)\\\\.(0|[1-9]\\\\d*)\\\\.(0|[1-9]\\\\d*)(?:-((?:0|[1-9]\\\\d*|\\\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\\\.(?:0|[1-9]\\\\d*|\\\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\\\+([0-9a-zA-Z-]+(?:\\\\.[0-9a-zA-Z-]+)*))?$"
    },
    "description": {
      "description": "A brief description of the theme.",
      "type": "string"
    },
    "theme": {
      "type": "object",
      "properties": {
        "type": {
          "description": "Specifies whether the theme is light or dark.",
          "type": "string",
          "enum": ["light", "dark"]
        },
        "colors": {
          "type": "object",
          "properties": {
            "primary": { "type": "string", "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$" },
            "secondary": { "type": "string", "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$" },
            "tertiary": { "type": "string", "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$" },
            "warn": { "type": "string", "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$" }
          },
          "required": ["primary", "secondary", "tertiary", "warn"]
        },
        "glassmorphism": {
          "type": "object",
          "properties": {
            "background": { "type": "string" },
            "border": { "type": "string" }
          },
          "required": ["background", "border"]
        },
        "typography": {
          "type": "object",
          "properties": {
            "fontFamily": { "type": "string" }
          },
          "required": ["fontFamily"]
        },
        "density": {
          "type": "object",
          "properties": {
            "scale": {
              "type": "integer",
              "minimum": -3,
              "maximum": 0
            }
          },
          "required": ["scale"]
        }
      },
      "required": ["type", "colors", "glassmorphism", "typography", "density"]
    }
  },
  "required": ["name", "author", "version", "description", "theme"]
}
```

## 2. CSS Variable Mapping

The properties defined in the `theme.json` manifest will be dynamically applied to the application's root element (`:root`) as CSS variables. The existing `styles.scss` is already set up to consume these variables, allowing for runtime theme changes without a full page reload.

| Manifest Property                | CSS Variable / DOM Style         | Notes                                                                                             |
| -------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------- |
| `theme.colors.primary`           | `--primary-color`                | Overrides the primary color used in the Angular Material theme.                                     |
| `theme.colors.secondary`         | `--secondary-color`              | Overrides the secondary color.                                                                    |
| `theme.colors.tertiary`          | `--tertiary-color`               | Overrides the tertiary color.                                                                     |
| `theme.colors.warn`              | `--warn-color`                   | Overrides the warn/error color.                                                                   |
| `theme.glassmorphism.background` | `--glass-bg`                     | Defines the background color and opacity for glassmorphism effects.                               |
| `theme.glassmorphism.border`     | `--glass-border`                 | Defines the border for glassmorphism effects.                                                     |
| `theme.typography.fontFamily`    | `--font-family`                  | This will be applied to the `<body>` tag.                                                         |
| `theme.density.scale`            | N/A                              | This will be handled by a `ThemeService` that applies a class to the body, corresponding to a pre-generated set of density styles. |

The `theme.type` (`light` or `dark`) property will be used to toggle a class on the `body` element (e.g., `theme-dark` or `theme-light`), ensuring that the correct base styles from Angular Material are applied before the custom overrides.

## 3. Installation and Loading Mechanism

The following describes the proposed user flow and technical implementation for managing themes.

### User Flow

1.  **Theme Installation**: A user can install a new theme by providing a URL to a `theme.json` file or by uploading the file directly. Installed themes will be stored in the browser's `localStorage`.
2.  **Theme Switching**: In the application's settings, the user will be presented with a list of installed themes. Selecting a theme will apply it immediately.
3.  **Theme Preview**: As the user selects different themes from the list, the UI will update in real-time to preview the changes before the user navigates away from the settings page.

### Technical Implementation

A `ThemeService` in Angular will be responsible for:
-   **Loading and Parsing**: Fetching the `theme.json` file from a URL or reading it from a file upload, then parsing and validating it against the schema.
-   **Storing Themes**: Saving the theme manifests to `localStorage` as an array of JSON objects.
-   **Applying Themes**: When a theme is selected, the `ThemeService` will:
    -   Update the CSS variables on the `:root` element by iterating over the `colors` and `glassmorphism` properties in the manifest.
    -   Set the `font-family` on the `<body>` element.
    -   Apply the appropriate `theme-light` or `theme-dark` class to the `<body>`.
    -   Apply the appropriate density class to the `<body>`.
-   **Managing the Active Theme**: The `ThemeService` will keep track of the currently active theme and ensure it's applied on application startup.

## 4. Default Theme Variants

Praxis will come with a set of default themes that will be bundled with the application and loaded on first launch.

-   **Praxis Light (Default)**: The current default theme.
    -   `type`: "light"
    -   `primary`: "#ED7A9B" (Rose Pompadour)
    -   `secondary`: "#F0E68C" (Khaki)
    -   `tertiary`: "#73A9C2" (Moonstone Blue)
    -   `warn`: "#B22222" (Firebrick)
    -   `glassmorphism.background`: "rgba(255, 255, 255, 0.7)"
    -   `glassmorphism.border`: "1px solid rgba(255, 255, 255, 0.3)"
-   **Praxis Dark**: A dark version of the default theme.
    -   `type`: "dark"
    -   `primary`: "#ED7A9B"
    -   `secondary`: "#BDB76B" (Dark Khaki)
    -   `tertiary`: "#73A9C2"
    -   `warn`: "#CD5C5C" (Indian Red)
    -   `glassmorphism.background`: "rgba(30, 30, 30, 0.7)"
    -   `glassmorphism.border`: "1px solid rgba(255, 255, 255, 0.1)"
-   **High Contrast**: An accessible theme with higher contrast ratios.
    -   `type`: "light"
    -   `primary`: "#000000"
    -   `secondary`: "#FFFF00"
    -   `tertiary`: "#0000FF"
    -   `warn`: "#FF0000"
    -   `glassmorphism.background`: "rgba(255, 255, 255, 0.95)"
    -   `glassmorphism.border`: "1px solid #000000"

## 5. Example Theme Manifest

Here is a complete example of a `theme.json` file for a custom "Oceanic" theme.

```json
{
  "name": "Oceanic",
  "author": "Jules",
  "version": "1.0.0",
  "description": "A cool blue and green theme.",
  "theme": {
    "type": "light",
    "colors": {
      "primary": "#008B8B",
      "secondary": "#98FB98",
      "tertiary": "#8FBC8F",
      "warn": "#FF6347"
    },
    "glassmorphism": {
      "background": "rgba(240, 255, 255, 0.7)",
      "border": "1px solid rgba(0, 139, 139, 0.3)"
    },
    "typography": {
      "fontFamily": "'Verdana', sans-serif"
    },
    "density": {
      "scale": -1
    }
  }
}
```
