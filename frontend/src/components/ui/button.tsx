import type { ButtonProps as ChakraButtonProps } from "@chakra-ui/react"
import { chakra, AbsoluteCenter, Span, Spinner, useRecipe } from "@chakra-ui/react"
import * as React from "react"
import { buttonRecipe } from "@/recipes/button.recipe"
import type { RecipeVariantProps } from "@chakra-ui/react"

type ButtonVariantProps = RecipeVariantProps<typeof buttonRecipe>

interface ButtonLoadingProps {
  loading?: boolean
  loadingText?: React.ReactNode
}

export interface ButtonProps extends ButtonVariantProps, ButtonLoadingProps, Omit<ChakraButtonProps, keyof ButtonVariantProps> { }

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(props, ref) {
    const { loading, disabled, loadingText, children, ...rest } = props
    const recipe = useRecipe({ key: "button" })
    const [recipeProps, otherProps] = recipe.splitVariantProps(rest)
    const styles = recipe(recipeProps)

    return (
      <chakra.button
        ref={ref}
        disabled={loading || disabled}
        css={styles}
        {...otherProps}
      >
        {loading && !loadingText ? (
          <>
            <AbsoluteCenter display="inline-flex">
              <Spinner size="inherit" color="inherit" />
            </AbsoluteCenter>
            <Span opacity={0}>{children}</Span>
          </>
        ) : loading && loadingText ? (
          <>
            <Spinner size="inherit" color="inherit" />
            {loadingText}
          </>
        ) : (
          children
        )}
      </chakra.button>
    )
  },
)
