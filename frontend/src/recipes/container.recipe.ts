import { defineRecipe } from '@chakra-ui/react';

export const containerRecipe = defineRecipe({
  className: 'chakra-container',
  base: {
    position: 'relative',
    width: '100%',
    maxWidth: '8xl',
    mx: 'auto',
    px: { base: '4', md: '6', lg: '8' },
    borderWidth: '1px',
    borderRadius: 'md',
    transition: 'all 0.2s',
    bg: { base: 'brand.50', _dark: 'brand.900' },
    borderColor: { base: 'brand.200', _dark: 'brand.700' },
  },
  variants: {
    centerContent: {
      true: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      },
    },
    fluid: {
      true: {
        maxWidth: 'full',
      },
    },
    solid: {
      true: {
        bg: { base: 'brand.50', _dark: 'brand.900' },
        borderColor: { base: 'brand.200', _dark: 'brand.700' },
        '&:hover': {
          borderColor: { base: 'brand.300', _dark: 'brand.600' },
          bg: { base: 'brand.100', _dark: 'brand.800' },
        }
      }
    },
    subtle: {
      true: {
        bg: { base: 'whiteAlpha.500', _dark: 'blackAlpha.300' },
        borderColor: { base: 'brand.100', _dark: 'brand.800' },
        '&:hover': {
          borderColor: { base: 'brand.200', _dark: 'brand.700' },
        }
      }
    }
  }
});
