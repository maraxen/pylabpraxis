"use client"

import { createSlotRecipeContext, type HTMLChakraProps } from "@chakra-ui/react"
import { cardRecipe } from "@recipes/card.recipe"

const { withProvider, withContext } = createSlotRecipeContext({
  recipe: cardRecipe,
})

export const Card = withProvider<HTMLDivElement, HTMLChakraProps<"div">>("div", "root")
export const CardBody = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "body")
