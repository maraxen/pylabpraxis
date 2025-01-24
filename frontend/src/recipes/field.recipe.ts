
import { defineSlotRecipe } from "@chakra-ui/react"

export const fieldRecipe = defineSlotRecipe({
  className: "field",
  slots: ["root", "label", "input", "helper"],
  base: {
    root: {
      fontSize: "lg",
      width: "full",
      position: "relative",
    },
    label: {
      display: "block",
      fontSize: "sm",
      fontWeight: "medium",
      color: { base: "brand.300", _dark: "brand.100" },
      mb: 2,
    },
    input: {
      width: "full",
      borderWidth: "1px",
      borderStyle: "solid",
      borderColor: { base: "brand.100", _dark: "brand.700" },
      borderRadius: "md",
      _hover: {
        borderColor: { base: "brand.300", _dark: "brand.500" },
      },
      _focus: {
        borderColor: { base: "brand.300", _dark: "brand.500" },
        boxShadow: "0 0 0 1px var(--chakra-colors-brand-300)",
      },
    },
    helper: {
      fontSize: "sm",
      color: { base: "gray.600", _dark: "gray.400" },
      mt: 1,
    },
  },
});