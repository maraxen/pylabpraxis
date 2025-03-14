import { defineRecipe } from "@chakra-ui/react";

export const buttonRecipe = defineRecipe({
  base: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",  // Changed from flex-start to center
    gap: "2",
    position: "relative",
    borderRadius: "md",
    minWidth: "100px",
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
      xs: { px: 2, py: 1, fontSize: "xs", minWidth: "40px" },
      sm: { px: 3, py: 1, fontSize: "sm", minWidth: "100px" },
      md: { px: 4, py: 2, fontSize: "md", minWidth: "120px" },
      lg: { px: 6, py: 3, fontSize: "lg", minWidth: "140px" },
    },
    loading: {
      true: {
        cursor: "not-allowed",
        "& .button-content": {
          opacity: 0,
        },
        "& .button-spinner": {
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
        },
      },
    },
  },
  compoundVariants: [
    {
      visual: "solid",
      loading: true,
      css: {
        _hover: { bg: "button.background" },
      },
    },
    {
      visual: "ghost",
      loading: true,
      css: {
        _hover: { bg: "transparent" },
      },
    },
    {
      visual: "outline",
      loading: true,
      css: {
        _hover: { bg: "transparent" },
      },
    },
  ],
  defaultVariants: {
    visual: "solid",
    size: "md",
    loading: false,
  },
});
