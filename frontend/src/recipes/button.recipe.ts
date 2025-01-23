import { defineRecipe } from "@chakra-ui/react";

export const buttonRecipe = defineRecipe({
  base: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
  },
  variants: {
    visual: {
      solid: {
        bg: "button.background",
        color: "button.color",
        _hover: { bg: "button.hover" },
      },
      ghost: {
        color: { base: "brand.300", _dark: "brand.100" },
        _hover: {
          color: { base: "white", _dark: "brand.50" },
          bg: { base: "brand.300", _dark: "brand.800" },
        },
      },
      outline: {
        color: { base: "brand.300", _dark: "brand.100" },
        borderColor: { base: "brand.300", _dark: "brand.100" },
        borderWidth: "1px",
        _hover: {
          color: { base: "white", _dark: "brand.50" },
          bg: { base: "brand.300", _dark: "brand.800" },
        },
      },
    },
    size: {
      sm: { px: 3, py: 1, fontSize: "sm" },
      md: { px: 4, py: 2, fontSize: "md" },
      lg: { px: 6, py: 3, fontSize: "lg" },
    },
  },
  defaultVariants: {
    visual: "solid",
    size: "md",
  },
});
