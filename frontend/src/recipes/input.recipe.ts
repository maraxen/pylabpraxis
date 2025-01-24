import { defineRecipe } from '@chakra-ui/react'

export const inputRecipe = defineRecipe({
  className: 'input',
  base: {
    w: '100%',
    minW: 0,
    outline: 'none',
    position: 'relative',
    appearance: 'none',
    transitionProperty: 'common',
    transitionDuration: 'normal',
    _disabled: {
      opacity: 0.4,
      cursor: 'not-allowed',
    },
  },
  variants: {
    visual: {
      outline: {
        border: '1px solid',
        borderColor: { base: 'brand.100', _dark: 'brand.700' },
        bg: { base: 'white', _dark: 'whiteAlpha.50' },
        _hover: {
          borderColor: { base: 'brand.200', _dark: 'brand.600' },
        },
        _focus: {
          zIndex: 1,
          borderColor: { base: 'brand.300', _dark: 'brand.500' },
          boxShadow: '0 0 0 1px var(--chakra-colors-brand-300)',
        },
      },
      filled: {
        border: '2px solid',
        borderColor: 'transparent',
        bg: { base: 'gray.100', _dark: 'whiteAlpha.50' },
        _hover: {
          bg: { base: 'gray.200', _dark: 'whiteAlpha.100' },
        },
        _focus: {
          bg: { base: 'white', _dark: 'whiteAlpha.200' },
          borderColor: { base: 'brand.300', _dark: 'brand.500' },
        },
      },
    },
    size: {
      sm: { px: '3', h: '8', fontSize: 'sm', borderRadius: 'sm' },
      md: { px: '4', h: '10', fontSize: 'md', borderRadius: 'md' },
      lg: { px: '4', h: '12', fontSize: 'lg', borderRadius: 'lg' },
    }
  },
  defaultVariants: {
    visual: 'outline',
    size: 'md',
  },
})


