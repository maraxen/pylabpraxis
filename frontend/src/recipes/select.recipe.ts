import { defineSlotRecipe } from "@chakra-ui/react"

export const selectRecipe = defineSlotRecipe({
  className: "select",
  slots: ["root", "trigger", "content", "item", "valueText", "indicator", "clearTrigger"],
  base: {
    root: {
      width: "full",
      position: "relative",
    },
    trigger: {
      width: "full",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "2",
      px: 3,
      py: 2,
      borderWidth: "1px",
      borderStyle: "solid",
      borderRadius: "md",
      borderColor: { base: "brand.100", _dark: "brand.700" },
      color: { base: "brand.300", _dark: "brand.100" },
      bg: { base: "white", _dark: "gray.800" },
      _hover: {
        borderColor: { base: "brand.300", _dark: "brand.500" },
      },
      _focus: {
        borderColor: { base: "brand.300", _dark: "brand.500" },
        boxShadow: "0 0 0 1px var(--chakra-colors-brand-300)",
      },
    },
    content: {
      bg: { base: "white", _dark: "gray.800" },
      borderWidth: "1px",
      borderStyle: "solid",
      borderColor: { base: "brand.100", _dark: "brand.700" },
      borderRadius: "md",
      boxShadow: "lg",
      minWidth: "200px",
      maxHeight: "300px",
      overflowY: "auto",
      zIndex: 1000,
      opacity: 0,
      transform: "translateY(-8px)",
      transition: "opacity 0.2s, transform 0.2s",
      _open: {
        opacity: 1,
        transform: "translateY(0)",
      },
    },
    item: {
      px: 3,
      py: 2,
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: 2,
      _hover: {
        bg: { base: "brand.50", _dark: "brand.900" },
      },
      _selected: {
        bg: { base: "brand.300", _dark: "brand.800" },
        color: "white",
      },
      _disabled: {
        opacity: 0.5,
        cursor: "not-allowed",
      },
    },
    valueText: {
      fontSize: "sm",
      color: { base: "brand.300", _dark: "brand.100" },
    },
    indicator: {
      color: { base: "brand.300", _dark: "brand.100" },
      transition: "transform 0.2s",
      _open: {
        transform: "rotate(180deg)",
      },
    },
    clearTrigger: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: "24px",
      height: "24px",
      borderRadius: "full",
      bg: { base: "brand.100", _dark: "brand.700" },
      color: { base: "brand.300", _dark: "brand.100" },
      cursor: "pointer",
      _hover: {
        bg: { base: "brand.300", _dark: "brand.500" },
        color: "white",
      },
    },
  },
})
