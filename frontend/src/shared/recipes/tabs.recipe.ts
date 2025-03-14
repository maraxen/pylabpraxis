import { defineSlotRecipe } from "@chakra-ui/react"

export const tabsRecipe = defineSlotRecipe({
  className: "tabs",
  slots: ["root", "list", "trigger", "content"],
  base: {
    root: {
      width: "full",
      position: "relative",
    },
    list: {
      display: "flex",
      gap: 2,
      px: 6,
      height: "12",
      borderBottom: "1px solid",
      borderColor: { base: "brand.100", _dark: "brand.700" },
    },
    trigger: {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",  // Changed from flex-start to center
      gap: "2",
      px: 3,
      py: 1,
      fontSize: "sm",
      minWidth: "100px",
      borderRadius: "md",
      color: { base: "brand.300", _dark: "brand.100" },
      _selected: {
        color: { base: "white", _dark: "brand.50" },
        bg: { base: "brand.300", _dark: "brand.800" },
      },
      _hover: {
        color: { base: "white", _dark: "brand.50" },
        bg: { base: "brand.300", _dark: "brand.800" },
      },
    },
    content: {
      p: 6,
      position: "absolute",
      width: "full",
      visibility: "hidden", // Hide by default
      _open: {
        animationName: "fade-in, scale-in",
        animationDuration: "300ms",
        opacity: 1,
        transform: "scale(1)",
        visibility: "visible", // Show when open
      },
      _closed: {
        animationName: "fade-out, scale-out",
        animationDuration: "120ms",
        opacity: 0,
        transform: "scale(0.95)",
        visibility: "hidden", // Hide when closed
      },
    },
  },
});
