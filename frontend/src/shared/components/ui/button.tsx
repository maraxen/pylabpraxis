"use client"

import { chakra, Spinner } from "@chakra-ui/react"
import { buttonRecipe } from "@recipes/button.recipe"
import * as React from "react"

const ChakraButton = chakra("button", buttonRecipe)

interface ButtonProps extends React.ComponentProps<typeof ChakraButton> {
  loading?: boolean
  loadingText?: string
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, loading, loadingText, ...props }, ref) => {
    return (
      <ChakraButton
        ref={ref}
        loading={loading}
        disabled={loading}
        {...props}
      >
        {loading && (
          <Spinner
            className="button-spinner"
            size={props.size === "sm" ? "xs" : "sm"}
          />
        )}
        <span className="button-content">
          {loading && loadingText ? loadingText : children}
        </span>
      </ChakraButton>
    )
  }
)
