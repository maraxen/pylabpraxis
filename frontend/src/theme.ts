import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react';
import { buttonRecipe } from './recipes/button.recipe';
import { tabsRecipe } from './recipes/tabs.recipe';
import { cardRecipe } from './recipes/card.recipe';
import { fieldsetRecipe } from './recipes/fieldset.recipe';
import { fieldRecipe } from './recipes/field.recipe';
import { selectRecipe } from './recipes/select.recipe';
import { inputRecipe } from './recipes/input.recipe';

const customConfig = defineConfig({
  conditions: {
    light: '[data-color-mode=light] &',
    dark: '[data-color-mode=dark] &',
  },
  theme: {
    tokens: {
      colors: {
        brand: {
          50: { value: '#EFCFE3' },  // Mimi Pink
          100: { value: '#EA9AB2' }, // Amaranth pink
          300: { value: '#E27396' }, // Rose Pompadour
          500: { value: '#E27396' }, // Rose Pompadour - Primary
          600: { value: '#779FA1' }, // Moonstone
          700: { value: '#B3DEE2' }, // Light blue
          900: { value: '#779FA1' }, // Moonstone
        },
        accent: {
          50: { value: '#F0F7F7' },  // Lightest
          100: { value: '#B3DEE2' }, // Light blue
          200: { value: '#9FD5DA' }, // Light blue darker
          300: { value: '#8BCCD2' }, // Between
          400: { value: '#779FA1' }, // Moonstone
          500: { value: '#779FA1' }, // Moonstone - Primary
          600: { value: '#688C8E' }, // Darker Moonstone
          700: { value: '#59797B' }, // Even darker
          800: { value: '#4A6668' }, // Much darker
          900: { value: '#3B5355' }, // Darkest
        },
      },
    },
    semanticTokens: {
      colors: {
        "app.bg": { value: { _light: "white", _dark: "gray.900" } },
        "app.text": { value: { _light: "{colors.brand.300}", _dark: "{colors.brand.700}" } },
        brand: {
          solid: { value: '{colors.brand.500}' },
          contrast: { value: 'white' },
          fg: { value: '{colors.brand.700}' },
          muted: { value: '{colors.brand.100}' },
          subtle: { value: '{colors.brand.50}' },
          emphasized: { value: '{colors.brand.300}' },
          focusRing: { value: '{colors.brand.500}' },
        },
        accent: {
          solid: { value: '{colors.accent.500}' },
          contrast: { value: 'white' },
          fg: { value: '{colors.accent.700}' },
          muted: { value: '{colors.accent.100}' },
          subtle: { value: '{colors.accent.50}' },
          emphasized: { value: '{colors.accent.300}' },
          focusRing: { value: '{colors.accent.500}' },
        },
        default: {
          color: { value: "{colors.brand.300}" },
          background: { value: "white" },
          border: { value: "{colors.brand.100}" },
        },
        button: {
          background: { value: "{colors.brand.300}" },
          color: { value: "white" },
          hover: { value: "{colors.brand.500}" },
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
    },
  },
});

export const system = createSystem(defaultConfig, customConfig);

export default system;
