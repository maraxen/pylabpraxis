export const inputStyles = {
  width: '100%',
  display: 'block',
  border: '1px solid',
  borderColor: { base: 'brand.100', _dark: 'brand.700' },
  bg: { base: 'white', _dark: 'whiteAlpha.50' },
  _hover: {
    borderColor: { base: 'brand.200', _dark: 'brand.600' },
  },
  _focus: {
    zIndex: 1,
    borderColor: { base: 'brand.300', _dark: 'brand.500' },
    boxShadow: '0 0 0 3px var(--chakra-colors-brand-300)',
  },
};

export const selectStyles = {
  ...inputStyles,
  _invalid: {
    borderColor: 'red.500',
  }
};

export const checkboxStyles = {
  colorScheme: 'brand',
  size: 'md',
  _hover: {
    borderColor: { base: 'brand.200', _dark: 'brand.600' },
  },
};

export const formControlStyles = {
  mb: 4,
};
