"use client"

import { createSlotRecipeContext, type HTMLChakraProps } from "@chakra-ui/react"
import { tabsRecipe } from "@/recipes/tabs.recipe"
import * as React from "react"

const TabsContext = React.createContext<{
  value?: string;
  onChange?: (details: { value: string }) => void;
}>({})

const { withProvider, withContext } = createSlotRecipeContext({
  recipe: tabsRecipe,
})

interface TabsProps extends Omit<HTMLChakraProps<"div">, "onChange"> {
  defaultValue?: string;
  value?: string;
  onChange?: (details: { value: string }) => void;
}

interface TabContentProps extends HTMLChakraProps<"div"> {
  value: string;
}

export const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ value, defaultValue, onChange, children, ...rest }, ref) => {
    const [localValue, setLocalValue] = React.useState(defaultValue)
    const currentValue = value ?? localValue

    const ctx = React.useMemo(
      () => ({
        value: currentValue,
        onChange: (details: { value: string }) => {
          setLocalValue(details.value)
          onChange?.(details)
        },
      }),
      [currentValue, onChange]
    )

    const BaseTab = withProvider<HTMLDivElement, TabsProps>("div", "root")

    return (
      <TabsContext.Provider value={ctx}>
        <BaseTab ref={ref} {...rest}>
          {children}
        </BaseTab>
      </TabsContext.Provider>
    )
  }
)

export const TabList = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "list")

export const TabTrigger = React.forwardRef<HTMLButtonElement, HTMLChakraProps<"button"> & { value: string }>(
  ({ value, onClick, ...props }, ref) => {
    const ctx = React.useContext(TabsContext)
    const BaseTrigger = withContext<HTMLButtonElement, HTMLChakraProps<"button">>("button", "trigger")

    return (
      <BaseTrigger
        ref={ref}
        aria-selected={ctx.value === value}
        onClick={(e) => {
          onClick?.(e)
          ctx.onChange?.({ value })
        }}
        {...props}
      />
    )
  }
)

export const TabContent = React.forwardRef<HTMLDivElement, TabContentProps>(
  ({ value, ...props }, ref) => {
    const ctx = React.useContext(TabsContext)
    const BaseContent = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "content")
    const isSelected = ctx.value === value

    return (
      <BaseContent
        ref={ref}
        data-state={isSelected ? "open" : "closed"}
        hidden={!isSelected}
        {...props}
      />
    )
  }
)
