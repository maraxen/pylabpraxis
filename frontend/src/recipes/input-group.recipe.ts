import { defineRecipe } from '@chakra-ui/react'

export const inputGroupRecipe = defineRecipe({
  className: 'input-group',
  base: {
    width: '100%',
    display: 'flex',
    position: 'relative',
  },
  variants: {
    size: {
      sm: { fontSize: 'sm' },
      md: { fontSize: 'md' },
      lg: { fontSize: 'lg' },
    },
  },
  defaultVariants: {
    size: 'md',
  },
})
