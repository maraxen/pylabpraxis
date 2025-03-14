import { defineSlotRecipe } from "@chakra-ui/react"

export const cardRecipe = defineSlotRecipe({
  className: "card",
  slots: ["root", "body"],
  base: {
    root: {
      borderWidth: "1px",
      borderRadius: "md",
      borderColor: { base: "brand.100", _dark: "brand.700" },
      bg: { base: "white", _dark: "gray.800" },
      overflow: "hidden",
    },
    body: {
      p: 6,
    },
  },
});
