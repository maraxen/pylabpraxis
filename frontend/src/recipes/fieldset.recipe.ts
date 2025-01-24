import { defineSlotRecipe } from "@chakra-ui/react"

export const fieldsetRecipe = defineSlotRecipe({
  className: "fieldset",
  slots: ["root", "legend", "content", "trigger"],
  base: {
    root: {
      borderWidth: "1px",
      borderStyle: "solid",
      borderColor: { base: "brand.100", _dark: "brand.700" },
      borderRadius: "md",
      p: 4,
      fontSize: "lg",
    },
    legend: {
      px: 2,
      fontSize: "lg",
      fontWeight: "medium",
      color: { base: "brand.300", _dark: "brand.100" },
      display: "flex",
      alignItems: "center",
      gap: 2,
      cursor: "pointer",
      _hover: {
        color: { base: "brand.500", _dark: "brand.50" },
      },
    },
    content: {
      mt: 8,
      overflow: "hidden",
      transition: "all 0.2s ease-in-out",
      _closed: {
        mt: 0,
        opacity: 0,
        height: 0,
      },
      _open: {
        opacity: 1,
        height: "auto",
      },
    },
    trigger: {
      transition: "transform 0.2s ease-in-out",
      _open: {
        transform: "rotate(180deg)",
      },
    },
  },
});
