"use client"

import { createSlotRecipeContext, type HTMLChakraProps, Portal, mergeRefs } from "@chakra-ui/react"
import { selectRecipe } from "@/recipes/select.recipe"
import { LuChevronDown } from "react-icons/lu"
import * as React from "react"

interface SelectContextValue {
  value?: string[];
  onChange?: (event: { value: string[] }) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const SelectContext = React.createContext<SelectContextValue>({
  isOpen: false,
  onToggle: () => { },
})

const { withProvider, withContext } = createSlotRecipeContext({
  recipe: selectRecipe,
})

interface SelectRootProps extends Omit<HTMLChakraProps<"div">, "onChange"> {
  value?: string[];
  onChange?: (event: { value: string[] }) => void;
  collection: { items: Array<{ value: string; label: string }> };
}

const BaseSelect = withProvider<HTMLDivElement, SelectRootProps>("div", "root")

export const SelectRoot = React.forwardRef<HTMLDivElement, SelectRootProps>(
  ({ value, onChange, children, ...props }, ref) => {
    const [isOpen, setIsOpen] = React.useState(false)
    const ctx = React.useMemo(
      () => ({
        value,
        onChange,
        isOpen,
        onToggle: () => setIsOpen(prev => !prev)
      }),
      [value, onChange, isOpen]
    )

    return (
      <SelectContext.Provider value={ctx}>
        <BaseSelect ref={ref} {...props}>
          {children}
        </BaseSelect>
      </SelectContext.Provider>
    )
  }
)

export const SelectTrigger = React.forwardRef<HTMLButtonElement, HTMLChakraProps<"button">>(
  (props, ref) => {
    const { onToggle, isOpen } = React.useContext(SelectContext)
    const triggerRef = React.useRef<HTMLButtonElement>(null)
    const BaseTrigger = withContext<HTMLButtonElement, HTMLChakraProps<"button">>("button", "trigger")

    React.useEffect(() => {
      if (isOpen && triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect()
        document.documentElement.style.setProperty('--select-trigger-width', `${rect.width}px`)
        document.documentElement.style.setProperty('--select-trigger-left', `${rect.left}px`)
        document.documentElement.style.setProperty('--select-trigger-bottom', `${rect.bottom + 4}px`)
      }
    }, [isOpen])

    return (
      <BaseTrigger
        ref={mergeRefs(ref, triggerRef)}
        onClick={onToggle}
        aria-expanded={isOpen}
        {...props}
      >
        {props.children}
        <LuChevronDown
          size={16}
          style={{
            transform: isOpen ? 'rotate(180deg)' : undefined,
            transition: 'transform 0.2s'
          }}
        />
      </BaseTrigger>
    )
  }
)

export const SelectContent = React.forwardRef<HTMLDivElement, HTMLChakraProps<"div">>(
  (props, ref) => {
    const { isOpen } = React.useContext(SelectContext)
    const BaseContent = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "content")

    if (!isOpen) return null

    return (
      <Portal>
        <BaseContent
          ref={ref}
          data-state={isOpen ? "open" : "closed"}
          style={{
            position: 'fixed',
            width: 'var(--select-trigger-width)',
            left: 'var(--select-trigger-left)',
            top: 'var(--select-trigger-bottom)',
          }}
          {...props}
        />
      </Portal>
    )
  }
)

interface SelectItemProps extends HTMLChakraProps<"div"> {
  item: { value: string; label: string };
}

export const SelectItem = React.forwardRef<HTMLDivElement, SelectItemProps>(
  ({ item, children, ...props }, ref) => {
    const { value = [], onChange } = React.useContext(SelectContext)
    const BaseItem = withContext<HTMLDivElement, HTMLChakraProps<"div">>("div", "item")
    const isSelected = value.includes(item.value)

    return (
      <BaseItem
        ref={ref}
        role="option"
        aria-selected={isSelected}
        data-selected={isSelected}
        onClick={() => onChange?.({ value: [item.value] })}
        {...props}
      >
        {children || item.label}
      </BaseItem>
    )
  }
)

interface SelectValueTextProps extends HTMLChakraProps<"span"> {
  placeholder?: string;
}

export const SelectValueText = React.forwardRef<HTMLSpanElement, SelectValueTextProps>(
  ({ placeholder, ...props }, ref) => {
    const { value = [] } = React.useContext(SelectContext)
    const BaseValueText = withContext<HTMLSpanElement, HTMLChakraProps<"span">>("span", "valueText")

    return (
      <BaseValueText ref={ref} {...props}>
        {value.length > 0 ? value.join(", ") : placeholder}
      </BaseValueText>
    )
  }
)

SelectRoot.displayName = 'SelectRoot'
SelectTrigger.displayName = 'SelectTrigger'
SelectContent.displayName = 'SelectContent'
SelectItem.displayName = 'SelectItem'
SelectValueText.displayName = 'SelectValueText'
