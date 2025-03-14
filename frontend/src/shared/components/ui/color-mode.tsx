"use client"

import * as React from 'react'
import { LuSun, LuMoon } from 'react-icons/lu'
import { Button } from './button'

type ColorMode = 'light' | 'dark' | 'system'

function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = React.useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      return initialValue
    }
  })

  React.useEffect(() => {
    window.localStorage.setItem(key, JSON.stringify(storedValue))
  }, [key, storedValue])

  return [storedValue, setStoredValue]
}

export function useColorMode() {
  const [colorMode, setColorMode] = useLocalStorage<ColorMode>(
    'chakra-ui-color-mode',
    'system'
  )

  React.useEffect(() => {
    const root = document.documentElement
    if (colorMode === 'system') {
      const systemMode = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      root.setAttribute('data-color-mode', systemMode)
    } else {
      root.setAttribute('data-color-mode', colorMode)
    }
  }, [colorMode])

  return {
    colorMode,
    setColorMode,
    toggleColorMode: () => setColorMode((prev: ColorMode) => prev === 'dark' ? 'light' : 'dark')
  }
}

export function useColorModeValue<T>(light: T, dark: T) {
  const { colorMode } = useColorMode()
  return colorMode === 'dark' ? dark : light
}

export const ColorModeButton = () => {
  const { colorMode, setColorMode } = useColorMode();

  const toggleColorMode = () => {
    const newMode = colorMode === 'light' ? 'dark' : 'light';
    setColorMode(newMode);
    localStorage.setItem('theme', newMode);
    document.documentElement.setAttribute('data-theme', newMode);
  };

  return (
    <Button onClick={toggleColorMode} visual="ghost" size="xs">
      {colorMode === 'light' ? <LuMoon size={14} /> : <LuSun size={14} />}
    </Button>
  );
};
