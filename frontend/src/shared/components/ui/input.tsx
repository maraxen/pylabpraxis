"use client"

import { chakra, useRecipe, type RecipeVariantProps } from "@chakra-ui/react"
import { inputRecipe } from "@recipes/input.recipe"
import * as React from "react"

type InputVariantProps = RecipeVariantProps<typeof inputRecipe>

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
  InputVariantProps { }

const ChakraInput = chakra('input')

export const Input = React.memo(React.forwardRef<HTMLInputElement, InputProps>(
  function Input(props, ref) {
    const recipe = useRecipe({ recipe: inputRecipe })
    const [recipeProps, restProps] = recipe.splitVariantProps(props)
    const styles = React.useMemo(() => recipe(recipeProps), [recipe, recipeProps])

    return <ChakraInput ref={ref} css={styles} {...restProps} />
  }
))

Input.displayName = 'Input'
