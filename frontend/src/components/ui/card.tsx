"use client"

import { createSlotRecipeContext, type HTMLChakraProps } from "@chakra-ui/react"
import { cardRecipe } from "@/recipes/card.recipe"
import * as React from "react"

const { withProvider, withContext } = createSlotRecipeContext({
  recipe: cardRecipe,
})

export const Card = withProvider<HTMLDivElement, HTMLChakraProps<"div">>("div", "root")
export const CardBody = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "body")
