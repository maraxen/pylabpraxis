"use client"

import { createSlotRecipeContext, type HTMLChakraProps } from "@chakra-ui/react"
import { fieldsetRecipe } from "@/recipes/fieldset.recipe"
import { LuChevronDown } from "react-icons/lu"
import * as React from "react"

const FieldsetContext = React.createContext<{
  isOpen: boolean;
  onToggle: () => void;
}>({
  isOpen: true,
  onToggle: () => { },
})

const { withProvider, withContext } = createSlotRecipeContext({
  recipe: fieldsetRecipe,
})

interface FieldsetRootProps extends HTMLChakraProps<"fieldset"> {
  defaultOpen?: boolean;
}

// Move all base components outside module scope
const BaseLegend = withContext<HTMLLegendElement, HTMLChakraProps<"legend">>("legend", "legend")
const BaseTrigger = withContext<HTMLSpanElement, HTMLChakraProps<"span">>("span", "trigger")
const BaseContent = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "content")
const BaseFieldset = withProvider<HTMLFieldSetElement, FieldsetRootProps>("fieldset", "root")

// Create a stable animation key
const ANIMATION_KEY = 'fieldset-animation'

export const Fieldset = React.memo(React.forwardRef<HTMLFieldSetElement, FieldsetRootProps>(
  ({ defaultOpen = true, children, ...props }, ref) => {
    // Use lazy initial state to prevent re-renders
    const [isOpen, setIsOpen] = React.useState(() => defaultOpen)
    const onToggle = React.useCallback(() => setIsOpen(prev => !prev), [])
    const contextValue = React.useMemo(() => ({ isOpen, onToggle }), [isOpen])

    return (
      <FieldsetContext.Provider value={contextValue}>
        <BaseFieldset ref={ref} data-state={isOpen ? "open" : "closed"} {...props}>
          {children}
        </BaseFieldset>
      </FieldsetContext.Provider>
    )
  }
))

export const FieldsetLegend = React.memo(React.forwardRef<HTMLLegendElement, HTMLChakraProps<"legend">>(
  ({ children, onClick, ...props }, ref) => {
    const { isOpen, onToggle } = React.useContext(FieldsetContext)

    const handleClick = React.useCallback((e: React.MouseEvent<HTMLLegendElement>) => {
      onClick?.(e)
      onToggle()
    }, [onClick, onToggle])

    return (
      <BaseLegend ref={ref} onClick={handleClick} {...props}>
        {children}
        <BaseTrigger data-state={isOpen ? "open" : "closed"}>
          <LuChevronDown size={20} />
        </BaseTrigger>
      </BaseLegend>
    )
  }
))

export const FieldsetContent = React.memo(React.forwardRef<HTMLDivElement, HTMLChakraProps<"div">>(
  ({ children, ...props }, ref) => {
    const { isOpen } = React.useContext(FieldsetContext)

    // Use a stable key for animations
    return (
      <BaseContent
        ref={ref}
        key={ANIMATION_KEY}
        data-state={isOpen ? "open" : "closed"}
        hidden={!isOpen}
        {...props}
      >
        {children}
      </BaseContent>
    )
  }
))

FieldsetLegend.displayName = 'FieldsetLegend'
FieldsetContent.displayName = 'FieldsetContent'
Fieldset.displayName = 'Fieldset'
