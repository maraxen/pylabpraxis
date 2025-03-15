import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react';
import {
  buttonRecipe,
  tabsRecipe,
  cardRecipe,
  fieldsetRecipe,
  fieldRecipe,
  selectRecipe,
  inputRecipe,
  containerRecipe
} from '@recipes/index';


const customConfig = defineConfig({
  conditions: {
    light: '[data-color-mode=light] &',
    dark: '[data-color-mode=dark] &',
  },
  theme: {
    keyframes: {
      shakeX: {
        "0%": { transform: "translateX(0)" },
        "25%": { transform: "translateX(5px)" },
        "50%": { transform: "translateX(-5px)" },
        "75%": { transform: "translateX(5px)" },
        "100%": { transform: "translateX(0)" },
      },
    },
    tokens: {
      colors: {
        brand: {
          50: { value: '#F7EDF2' },  // Lightest pink
          100: { value: '#EFCFE3' }, // Light pink
          200: { value: '#EA9AB2' }, // Medium pink
          300: { value: '#E27396' }, // Rose Pompadour
          400: { value: '#DC5880' }, // Darker rose
          500: { value: '#CB2A5D' }, // Deep rose
          600: { value: '#B33860' }, // Darker
          700: { value: '#A9234D' }, // Even darker
          800: { value: '#771836' }, // Very dark
          900: { value: '#440E1F' }, // Darkest
        },
        accent: {
          50: { value: '#F0F7F7' },  // Lightest blue
          100: { value: '#B3DEE2' }, // Light blue
          200: { value: '#9FD5DA' }, // Medium light blue
          300: { value: '#8BCCD2' }, // Medium blue
          400: { value: '#779FA1' }, // Moonstone
          500: { value: '#638D8F' }, // Deeper moonstone
          600: { value: '#4F7B7D' }, // Dark moonstone
          700: { value: '#3B696B' }, // Darker moonstone
          800: { value: '#275759' }, // Very dark moonstone
          900: { value: '#134547' }, // Darkest moonstone
        },
      },
      animations: {
        shake: { value: "shakeX 0.3s" },
      },
    },
    semanticTokens: {
      colors: {
        "app.bg": {
          value: {
            _light: "white",
            _dark: "gray.900"
          }
        },
        "app.text": {
          value: {
            _light: "{colors.brand.700}",
            _dark: "{colors.brand.200}"
          }
        },
        brand: {
          solid: {
            value: {
              _light: '{colors.brand.500}',
              _dark: '{colors.brand.300}'
            }
          },
          contrast: {
            value: {
              _light: 'white',
              _dark: '{colors.brand.900}'
            }
          },
          fg: {
            value: {
              _light: '{colors.brand.700}',
              _dark: '{colors.brand.200}'
            }
          },
          muted: {
            value: {
              _light: '{colors.brand.100}',
              _dark: '{colors.brand.800}'
            }
          },
          subtle: {
            value: {
              _light: '{colors.brand.50}',
              _dark: '{colors.brand.900}'
            }
          },
          emphasized: {
            value: {
              _light: '{colors.brand.600}',
              _dark: '{colors.brand.300}'
            }
          },
          focusRing: {
            value: {
              _light: '{colors.brand.500}',
              _dark: '{colors.brand.400}'
            }
          },
        },
        accent: {
          solid: {
            value: {
              _light: '{colors.accent.500}',
              _dark: '{colors.accent.300}'
            }
          },
          contrast: {
            value: {
              _light: 'white',
              _dark: '{colors.accent.900}'
            }
          },
          fg: {
            value: {
              _light: '{colors.accent.700}',
              _dark: '{colors.accent.200}'
            }
          },
          muted: {
            value: {
              _light: '{colors.accent.100}',
              _dark: '{colors.accent.800}'
            }
          },
          subtle: {
            value: {
              _light: '{colors.accent.50}',
              _dark: '{colors.accent.900}'
            }
          },
          emphasized: {
            value: {
              _light: '{colors.accent.600}',
              _dark: '{colors.accent.300}'
            }
          },
          focusRing: {
            value: {
              _light: '{colors.accent.500}',
              _dark: '{colors.accent.400}'
            }
          },
        },
        default: {
          color: {
            value: {
              _light: "{colors.brand.700}",
              _dark: "{colors.brand.200}"
            }
          },
          background: {
            value: {
              _light: "white",
              _dark: "{colors.gray.800}"
            }
          },
          border: {
            value: {
              _light: "{colors.brand.200}",
              _dark: "{colors.brand.700}"
            }
          },
        },
        button: {
          background: {
            value: {
              _light: "{colors.brand.500}",
              _dark: "{colors.brand.300}"
            }
          },
          color: {
            value: {
              _light: "white",
              _dark: "{colors.brand.900}"
            }
          },
          hover: {
            value: {
              _light: "{colors.brand.600}",
              _dark: "{colors.brand.400}"
            }
          },
        }
      },
    },

    slotRecipes: {
      tabs: tabsRecipe,
      card: cardRecipe,
      fieldset: fieldsetRecipe,
      field: fieldRecipe,
      select: selectRecipe
    },
    recipes: {
      button: buttonRecipe,
      input: inputRecipe,
      container: containerRecipe

    },
  },
});

export const system = createSystem(defaultConfig, customConfig);

export default system;
