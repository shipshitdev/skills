---
name: react-native-components
description: Guides React Native component building — StyleSheet, dynamic styling, FlatList performance, accessible mobile UI. Use when building React Native UI components.
metadata:
  version: "2.2.5"
  tags: "[react-native, components, styling, performance, ui, accessibility, hooks]"
  category: mobile
  difficulty: advanced
when_to_use: "expo, View Text Image, mobile UI"
---

# React Native Component Patterns Expert

## When to Use

Use when you're:

- Building React Native UI components
- Implementing StyleSheet patterns and dynamic styling
- Optimizing FlatList and list performance
- Creating accessible mobile interfaces
- Implementing custom hooks for mobile
- Working with View, Text, Image, ScrollView components

## Quick Reference

### Core Components

- **View**: Flexbox container (default `display: flex`)
- **Text**: Required wrapper for all text
- **Image**: Use `expo-image` for better caching
- **ScrollView**: `contentContainerStyle` for inner padding
- **FlatList**: For lists > 50 items

### StyleSheet Patterns

- `StyleSheet.create`: Performance-optimized styles
- Array syntax: `[baseStyle, condition && activeStyle]`
- Dynamic: `useWindowDimensions` for responsive
- Platform: `Platform.select({ ios: {}, android: {} })`

### Performance

- `FlatList` with `initialNumToRender`, `windowSize`
- `React.memo` for pure components
- `useMemo` for expensive calculations
- `useCallback` for event handlers

## References

- [Full guide: Components, patterns, accessibility, performance](references/full-guide.md)
