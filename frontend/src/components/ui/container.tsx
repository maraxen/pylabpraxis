"use client"

import { chakra } from "@chakra-ui/react"
import { containerRecipe } from "@/recipes/container.recipe"
import * as React from "react"

const ChakraContainer = chakra("div", containerRecipe)

interface ContainerProps extends React.ComponentProps<typeof ChakraContainer> {
  centerContent?: boolean
  fluid?: boolean
}

export const Container = React.forwardRef<HTMLDivElement, ContainerProps>(
  ({ children, centerContent, fluid, ...props }, ref) => {
    return (
      <ChakraContainer
        ref={ref}
        centerContent={centerContent}
        fluid={fluid}
        {...props}
      >
        {children}
      </ChakraContainer>
    )
  }
)

Container.displayName = "Container"
