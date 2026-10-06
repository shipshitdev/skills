# React Native Components Guide

> Complete reference for building production-ready React Native components with TypeScript.

## Table of Contents

1. [Core Components](#core-components)
2. [StyleSheet Patterns](#stylesheet-patterns)
3. [Real-World Component Patterns](#real-world-component-patterns)
4. [Performance Optimization](#performance-optimization)
5. [Custom Hooks](#custom-hooks)
6. [Accessibility](#accessibility)
7. [Layout Patterns](#layout-patterns)
8. [Advanced Patterns](#advanced-patterns)
9. [Best Practices](#best-practices)

---

## Core Components

### View

The fundamental container component for layout.

```typescript
import { View, ViewStyle } from 'react-native';

interface ContainerProps {
  children: React.ReactNode;
  style?: ViewStyle;
  testID?: string;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  style,
  testID
}) => {
  return (
    <View
      style={[styles.container, style]}
      testID={testID}
    >
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
});
```

### Text

For displaying text content with proper styling.

```typescript
import { Text, TextStyle, TextProps as RNTextProps } from 'react-native';

type TextVariant = 'h1' | 'h2' | 'h3' | 'body' | 'caption' | 'label';
type TextWeight = 'regular' | 'medium' | 'semibold' | 'bold';

interface TextProps extends RNTextProps {
  variant?: TextVariant;
  weight?: TextWeight;
  color?: string;
  align?: TextStyle['textAlign'];
  children: React.ReactNode;
}

const variantStyles: Record<TextVariant, TextStyle> = {
  h1: { fontSize: 32, lineHeight: 40 },
  h2: { fontSize: 24, lineHeight: 32 },
  h3: { fontSize: 20, lineHeight: 28 },
  body: { fontSize: 16, lineHeight: 24 },
  caption: { fontSize: 14, lineHeight: 20 },
  label: { fontSize: 12, lineHeight: 16 },
};

const weightStyles: Record<TextWeight, TextStyle> = {
  regular: { fontWeight: '400' },
  medium: { fontWeight: '500' },
  semibold: { fontWeight: '600' },
  bold: { fontWeight: '700' },
};

export const Typography: React.FC<TextProps> = ({
  variant = 'body',
  weight = 'regular',
  color = '#1A1A1A',
  align = 'left',
  style,
  children,
  ...props
}) => {
  return (
    <Text
      style={[
        variantStyles[variant],
        weightStyles[weight],
        { color, textAlign: align },
        style,
      ]}
      {...props}
    >
      {children}
    </Text>
  );
};
```

### Image

Handling images with loading states and error fallbacks.

```typescript
import {
  Image,
  ImageProps,
  ImageStyle,
  View,
  ActivityIndicator,
  ImageSourcePropType
} from 'react-native';
import { useState } from 'react';

interface OptimizedImageProps extends Omit<ImageProps, 'source'> {
  source: ImageSourcePropType;
  fallback?: ImageSourcePropType;
  showLoader?: boolean;
  containerStyle?: ImageStyle;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  source,
  fallback,
  showLoader = true,
  style,
  containerStyle,
  ...props
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const imageSource = hasError && fallback ? fallback : source;

  return (
    <View style={[styles.imageContainer, containerStyle]}>
      <Image
        source={imageSource}
        style={[styles.image, style]}
        onLoadStart={() => setIsLoading(true)}
        onLoadEnd={() => setIsLoading(false)}
        onError={() => {
          setHasError(true);
          setIsLoading(false);
        }}
        {...props}
      />
      {isLoading && showLoader && (
        <View style={styles.loaderContainer}>
          <ActivityIndicator size="small" color="#6366F1" />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  imageContainer: {
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  loaderContainer: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
  },
});
```

### ScrollView

Scrollable container with pull-to-refresh and keyboard handling.

```typescript
import {
  ScrollView,
  ScrollViewProps,
  RefreshControl,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useState, useCallback } from 'react';

interface EnhancedScrollViewProps extends ScrollViewProps {
  onRefresh?: () => Promise<void>;
  keyboardAvoiding?: boolean;
  children: React.ReactNode;
}

export const EnhancedScrollView: React.FC<EnhancedScrollViewProps> = ({
  onRefresh,
  keyboardAvoiding = false,
  children,
  contentContainerStyle,
  ...props
}) => {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = useCallback(async () => {
    if (!onRefresh) return;
    setRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setRefreshing(false);
    }
  }, [onRefresh]);

  const scrollContent = (
    <ScrollView
      contentContainerStyle={[styles.content, contentContainerStyle]}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor="#6366F1"
            colors={['#6366F1']}
          />
        ) : undefined
      }
      {...props}
    >
      {children}
    </ScrollView>
  );

  if (keyboardAvoiding) {
    return (
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
      >
        {scrollContent}
      </KeyboardAvoidingView>
    );
  }

  return scrollContent;
};

const styles = StyleSheet.create({
  flex: {
    flex: 1,
  },
  content: {
    flexGrow: 1,
    paddingHorizontal: 16,
    paddingVertical: 24,
  },
});
```

---

## StyleSheet Patterns

### StyleSheet.create

The recommended way to define styles for performance optimization.

```typescript
import { StyleSheet, ViewStyle, TextStyle, ImageStyle } from 'react-native';

// Type-safe style definitions
interface Styles {
  container: ViewStyle;
  title: TextStyle;
  avatar: ImageStyle;
  row: ViewStyle;
}

const styles = StyleSheet.create<Styles>({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 16,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
});
```

### Dynamic Styles

Creating styles based on props or state.

```typescript
import { StyleSheet, View, ViewStyle } from 'react-native';

type StatusType = 'success' | 'warning' | 'error' | 'info';

interface StatusBadgeProps {
  status: StatusType;
  size?: 'small' | 'medium' | 'large';
}

const statusColors: Record<StatusType, string> = {
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
};

const sizeValues: Record<string, number> = {
  small: 8,
  medium: 12,
  large: 16,
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'medium'
}) => {
  const dynamicStyle: ViewStyle = {
    backgroundColor: statusColors[status],
    width: sizeValues[size],
    height: sizeValues[size],
    borderRadius: sizeValues[size] / 2,
  };

  return <View style={[styles.badge, dynamicStyle]} />;
};

const styles = StyleSheet.create({
  badge: {
    // Base styles that don't change
  },
});
```

### Responsive Styles

Adapting to different screen sizes.

```typescript
import {
  StyleSheet,
  Dimensions,
  PixelRatio,
  Platform,
  useWindowDimensions
} from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// Base dimensions (design reference)
const BASE_WIDTH = 375;
const BASE_HEIGHT = 812;

// Scaling functions
export const scale = (size: number): number => {
  return (SCREEN_WIDTH / BASE_WIDTH) * size;
};

export const verticalScale = (size: number): number => {
  return (SCREEN_HEIGHT / BASE_HEIGHT) * size;
};

export const moderateScale = (size: number, factor: number = 0.5): number => {
  return size + (scale(size) - size) * factor;
};

// Normalize font size across devices
export const normalize = (size: number): number => {
  const newSize = scale(size);
  if (Platform.OS === 'ios') {
    return Math.round(PixelRatio.roundToNearestPixel(newSize));
  }
  return Math.round(PixelRatio.roundToNearestPixel(newSize)) - 2;
};

// Hook for responsive values
export const useResponsive = () => {
  const { width, height } = useWindowDimensions();

  const isSmallDevice = width < 375;
  const isMediumDevice = width >= 375 && width < 414;
  const isLargeDevice = width >= 414;
  const isTablet = width >= 768;

  return {
    width,
    height,
    isSmallDevice,
    isMediumDevice,
    isLargeDevice,
    isTablet,
    scale: (size: number) => (width / BASE_WIDTH) * size,
  };
};

// Usage in component
export const ResponsiveCard: React.FC = () => {
  const { isTablet, scale } = useResponsive();

  return (
    <View style={[
      styles.card,
      {
        padding: scale(16),
        width: isTablet ? '48%' : '100%',
      }
    ]}>
      {/* Content */}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
});
```

### Platform-Specific Styles

Handling iOS and Android differences.

```typescript
import { StyleSheet, Platform, PlatformColor } from 'react-native';

const styles = StyleSheet.create({
  // Using Platform.select for complex differences
  container: {
    flex: 1,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
      },
      android: {
        elevation: 4,
      },
    }),
  },

  // Simple OS check
  header: {
    paddingTop: Platform.OS === 'ios' ? 44 : 24,
    backgroundColor: '#FFFFFF',
  },

  // Font family per platform
  text: {
    fontFamily: Platform.select({
      ios: 'SF Pro Display',
      android: 'Roboto',
      default: 'System',
    }),
    fontSize: 16,
  },

  // Using platform version
  input: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: Platform.OS === 'android' && Platform.Version < 21 ? 0 : 8,
  },
});

// Platform-specific component files
// Button.ios.tsx - iOS specific implementation
// Button.android.tsx - Android specific implementation
// Button.tsx - Default/shared implementation
```

---

## Real-World Component Patterns

### Card Component

```typescript
import {
  View,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  Pressable
} from 'react-native';
import { ReactNode } from 'react';

type CardVariant = 'elevated' | 'outlined' | 'filled';

interface CardProps {
  children: ReactNode;
  variant?: CardVariant;
  onPress?: () => void;
  disabled?: boolean;
  style?: ViewStyle;
  testID?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'elevated',
  onPress,
  disabled = false,
  style,
  testID,
}) => {
  const cardStyles = [
    styles.base,
    styles[variant],
    disabled && styles.disabled,
    style,
  ];

  if (onPress) {
    return (
      <Pressable
        style={({ pressed }) => [
          cardStyles,
          pressed && styles.pressed,
        ]}
        onPress={onPress}
        disabled={disabled}
        testID={testID}
        accessibilityRole="button"
      >
        {children}
      </Pressable>
    );
  }

  return (
    <View style={cardStyles} testID={testID}>
      {children}
    </View>
  );
};

// Sub-components for composition
Card.Header = ({ children, style }: { children: ReactNode; style?: ViewStyle }) => (
  <View style={[styles.header, style]}>{children}</View>
);

Card.Body = ({ children, style }: { children: ReactNode; style?: ViewStyle }) => (
  <View style={[styles.body, style]}>{children}</View>
);

Card.Footer = ({ children, style }: { children: ReactNode; style?: ViewStyle }) => (
  <View style={[styles.footer, style]}>{children}</View>
);

const styles = StyleSheet.create({
  base: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  elevated: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 3,
  },
  outlined: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  filled: {
    backgroundColor: '#F3F4F6',
  },
  disabled: {
    opacity: 0.5,
  },
  pressed: {
    opacity: 0.9,
    transform: [{ scale: 0.98 }],
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  body: {
    padding: 16,
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
});
```

### Input Component

```typescript
import {
  View,
  TextInput,
  TextInputProps,
  Text,
  StyleSheet,
  Animated,
  TouchableOpacity,
} from 'react-native';
import { useState, useRef, useEffect } from 'react';

interface InputProps extends TextInputProps {
  label: string;
  error?: string;
  hint?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  onRightIconPress?: () => void;
  required?: boolean;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  hint,
  leftIcon,
  rightIcon,
  onRightIconPress,
  required = false,
  value,
  onFocus,
  onBlur,
  style,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const labelAnimation = useRef(new Animated.Value(value ? 1 : 0)).current;

  const hasValue = Boolean(value && value.length > 0);
  const isActive = isFocused || hasValue;

  useEffect(() => {
    Animated.timing(labelAnimation, {
      toValue: isActive ? 1 : 0,
      duration: 150,
      useNativeDriver: false,
    }).start();
  }, [isActive, labelAnimation]);

  const handleFocus = (e: any) => {
    setIsFocused(true);
    onFocus?.(e);
  };

  const handleBlur = (e: any) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const labelStyle = {
    top: labelAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: [16, -8],
    }),
    fontSize: labelAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: [16, 12],
    }),
    color: labelAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: ['#9CA3AF', error ? '#EF4444' : '#6366F1'],
    }),
  };

  return (
    <View style={styles.container}>
      <View
        style={[
          styles.inputContainer,
          isFocused && styles.focused,
          error && styles.error,
        ]}
      >
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}

        <View style={styles.inputWrapper}>
          <Animated.Text style={[styles.label, labelStyle]}>
            {label}
            {required && <Text style={styles.required}> *</Text>}
          </Animated.Text>

          <TextInput
            style={[
              styles.input,
              leftIcon && styles.inputWithLeftIcon,
              rightIcon && styles.inputWithRightIcon,
              style,
            ]}
            value={value}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholderTextColor="#9CA3AF"
            accessibilityLabel={label}
            accessibilityHint={hint}
            {...props}
          />
        </View>

        {rightIcon && (
          <TouchableOpacity
            style={styles.rightIcon}
            onPress={onRightIconPress}
            disabled={!onRightIconPress}
          >
            {rightIcon}
          </TouchableOpacity>
        )}
      </View>

      {(error || hint) && (
        <Text style={[styles.helperText, error && styles.errorText]}>
          {error || hint}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
    minHeight: 56,
  },
  focused: {
    borderColor: '#6366F1',
    borderWidth: 2,
  },
  error: {
    borderColor: '#EF4444',
  },
  inputWrapper: {
    flex: 1,
    position: 'relative',
    justifyContent: 'center',
  },
  label: {
    position: 'absolute',
    left: 12,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 4,
  },
  required: {
    color: '#EF4444',
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#1A1A1A',
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  inputWithLeftIcon: {
    paddingLeft: 8,
  },
  inputWithRightIcon: {
    paddingRight: 8,
  },
  leftIcon: {
    paddingLeft: 12,
  },
  rightIcon: {
    paddingRight: 12,
  },
  helperText: {
    marginTop: 4,
    marginLeft: 12,
    fontSize: 12,
    color: '#6B7280',
  },
  errorText: {
    color: '#EF4444',
  },
});
```

### Button Component

```typescript
import {
  TouchableOpacity,
  Text,
  ActivityIndicator,
  StyleSheet,
  ViewStyle,
  TextStyle,
  Pressable,
  View,
} from 'react-native';
import { ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  testID?: string;
}

const variantStyles: Record<ButtonVariant, { container: ViewStyle; text: TextStyle }> = {
  primary: {
    container: { backgroundColor: '#6366F1' },
    text: { color: '#FFFFFF' },
  },
  secondary: {
    container: { backgroundColor: '#F3F4F6' },
    text: { color: '#1A1A1A' },
  },
  outline: {
    container: { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#6366F1' },
    text: { color: '#6366F1' },
  },
  ghost: {
    container: { backgroundColor: 'transparent' },
    text: { color: '#6366F1' },
  },
  danger: {
    container: { backgroundColor: '#EF4444' },
    text: { color: '#FFFFFF' },
  },
};

const sizeStyles: Record<ButtonSize, { container: ViewStyle; text: TextStyle }> = {
  small: {
    container: { paddingVertical: 8, paddingHorizontal: 12, borderRadius: 6 },
    text: { fontSize: 14 },
  },
  medium: {
    container: { paddingVertical: 12, paddingHorizontal: 16, borderRadius: 8 },
    text: { fontSize: 16 },
  },
  large: {
    container: { paddingVertical: 16, paddingHorizontal: 24, borderRadius: 10 },
    text: { fontSize: 18 },
  },
};

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  style,
  textStyle,
  testID,
}) => {
  const isDisabled = disabled || loading;
  const variantStyle = variantStyles[variant];
  const sizeStyle = sizeStyles[size];

  return (
    <Pressable
      style={({ pressed }) => [
        styles.base,
        variantStyle.container,
        sizeStyle.container,
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        pressed && !isDisabled && styles.pressed,
        style,
      ]}
      onPress={onPress}
      disabled={isDisabled}
      testID={testID}
      accessibilityRole="button"
      accessibilityState={{ disabled: isDisabled }}
      accessibilityLabel={title}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variantStyle.text.color}
        />
      ) : (
        <View style={styles.content}>
          {leftIcon && <View style={styles.iconLeft}>{leftIcon}</View>}
          <Text
            style={[
              styles.text,
              variantStyle.text,
              sizeStyle.text,
              textStyle,
            ]}
          >
            {title}
          </Text>
          {rightIcon && <View style={styles.iconRight}>{rightIcon}</View>}
        </View>
      )}
    </Pressable>
  );
};

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  fullWidth: {
    width: '100%',
  },
  disabled: {
    opacity: 0.5,
  },
  pressed: {
    opacity: 0.8,
    transform: [{ scale: 0.98 }],
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
});
```

### Section Header Component

```typescript
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ReactNode } from 'react';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: {
    label: string;
    onPress: () => void;
  };
  rightElement?: ReactNode;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  action,
  rightElement,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.textContainer}>
        <Text style={styles.title}>{title}</Text>
        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      </View>

      {action && (
        <TouchableOpacity
          onPress={action.onPress}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          accessibilityRole="button"
          accessibilityLabel={action.label}
        >
          <Text style={styles.actionText}>{action.label}</Text>
        </TouchableOpacity>
      )}

      {rightElement}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  textContainer: {
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6366F1',
  },
});
```

---

## Performance Optimization

### FlatList Optimization

```typescript
import {
  FlatList,
  View,
  Text,
  StyleSheet,
  ListRenderItem,
  ViewToken,
} from 'react-native';
import { useCallback, useMemo, memo } from 'react';

interface Item {
  id: string;
  title: string;
  description: string;
}

interface OptimizedListProps {
  data: Item[];
  onItemPress: (item: Item) => void;
  onEndReached?: () => void;
  refreshing?: boolean;
  onRefresh?: () => void;
}

// Memoized item component
const ListItem = memo<{ item: Item; onPress: (item: Item) => void }>(
  ({ item, onPress }) => {
    const handlePress = useCallback(() => {
      onPress(item);
    }, [item, onPress]);

    return (
      <TouchableOpacity style={styles.item} onPress={handlePress}>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.description}>{item.description}</Text>
      </TouchableOpacity>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison for optimal re-renders
    return (
      prevProps.item.id === nextProps.item.id &&
      prevProps.item.title === nextProps.item.title
    );
  }
);

export const OptimizedList: React.FC<OptimizedListProps> = ({
  data,
  onItemPress,
  onEndReached,
  refreshing = false,
  onRefresh,
}) => {
  // Stable key extractor
  const keyExtractor = useCallback((item: Item) => item.id, []);

  // Memoized render function
  const renderItem: ListRenderItem<Item> = useCallback(
    ({ item }) => <ListItem item={item} onPress={onItemPress} />,
    [onItemPress]
  );

  // Memoized item layout for fixed-height items
  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: ITEM_HEIGHT,
      offset: ITEM_HEIGHT * index,
      index,
    }),
    []
  );

  // Viewability configuration
  const viewabilityConfig = useMemo(
    () => ({
      itemVisiblePercentThreshold: 50,
      minimumViewTime: 200,
    }),
    []
  );

  const onViewableItemsChanged = useCallback(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      // Track visible items for analytics
      console.log('Visible items:', viewableItems.length);
    },
    []
  );

  // Memoized separator
  const ItemSeparator = useCallback(
    () => <View style={styles.separator} />,
    []
  );

  // Memoized empty component
  const ListEmpty = useMemo(
    () => (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No items found</Text>
      </View>
    ),
    []
  );

  // Memoized footer
  const ListFooter = useMemo(
    () => <View style={styles.footer} />,
    []
  );

  return (
    <FlatList
      data={data}
      keyExtractor={keyExtractor}
      renderItem={renderItem}
      getItemLayout={getItemLayout}
      ItemSeparatorComponent={ItemSeparator}
      ListEmptyComponent={ListEmpty}
      ListFooterComponent={ListFooter}

      // Performance props
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={5}
      initialNumToRender={10}
      updateCellsBatchingPeriod={50}

      // Scroll behavior
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}

      // Refresh
      refreshing={refreshing}
      onRefresh={onRefresh}

      // Viewability
      viewabilityConfig={viewabilityConfig}
      onViewableItemsChanged={onViewableItemsChanged}

      // Style
      contentContainerStyle={styles.list}
      showsVerticalScrollIndicator={false}
    />
  );
};

const ITEM_HEIGHT = 80;

const styles = StyleSheet.create({
  list: {
    flexGrow: 1,
    paddingHorizontal: 16,
  },
  item: {
    height: ITEM_HEIGHT,
    justifyContent: 'center',
    paddingVertical: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  description: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  separator: {
    height: 1,
    backgroundColor: '#E5E7EB',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
  },
  footer: {
    height: 24,
  },
});
```

### Memoization Patterns

```typescript
import { memo, useMemo, useCallback, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface UserCardProps {
  user: User;
  onPress: (user: User) => void;
  isSelected: boolean;
}

// React.memo with custom comparison
export const UserCard = memo<UserCardProps>(
  ({ user, onPress, isSelected }) => {
    // useCallback for stable function references
    const handlePress = useCallback(() => {
      onPress(user);
    }, [onPress, user]);

    // useMemo for expensive computations
    const roleLabel = useMemo(() => {
      return user.role === 'admin' ? 'Administrator' : 'Standard User';
    }, [user.role]);

    // useMemo for derived styles
    const cardStyle = useMemo(
      () => [styles.card, isSelected && styles.selected],
      [isSelected]
    );

    return (
      <TouchableOpacity style={cardStyle} onPress={handlePress}>
        <Text style={styles.name}>{user.name}</Text>
        <Text style={styles.email}>{user.email}</Text>
        <Text style={styles.role}>{roleLabel}</Text>
      </TouchableOpacity>
    );
  },
  // Custom comparison function
  (prevProps, nextProps) => {
    return (
      prevProps.user.id === nextProps.user.id &&
      prevProps.user.name === nextProps.user.name &&
      prevProps.isSelected === nextProps.isSelected
    );
  }
);

// Parent component with proper memoization
export const UserList: React.FC<{ users: User[] }> = ({ users }) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Memoize handler to prevent child re-renders
  const handleUserPress = useCallback((user: User) => {
    setSelectedId(user.id);
  }, []);

  // Memoize filtered data
  const sortedUsers = useMemo(
    () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
    [users]
  );

  return (
    <View style={styles.container}>
      {sortedUsers.map((user) => (
        <UserCard
          key={user.id}
          user={user}
          onPress={handleUserPress}
          isSelected={selectedId === user.id}
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  card: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selected: {
    borderColor: '#6366F1',
    backgroundColor: '#EEF2FF',
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  email: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  role: {
    fontSize: 12,
    color: '#6366F1',
    marginTop: 8,
    fontWeight: '500',
  },
});
```

---

## Custom Hooks

### useDebounce

```typescript
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Usage
const SearchScreen: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 300);

  useEffect(() => {
    if (debouncedSearch) {
      // Perform search API call
      searchApi(debouncedSearch);
    }
  }, [debouncedSearch]);

  return (
    <TextInput
      value={searchTerm}
      onChangeText={setSearchTerm}
      placeholder="Search..."
    />
  );
};
```

### useKeyboard

```typescript
import { useEffect, useState } from 'react';
import { Keyboard, KeyboardEvent, Platform } from 'react-native';

interface KeyboardState {
  isVisible: boolean;
  height: number;
}

export function useKeyboard(): KeyboardState {
  const [keyboardState, setKeyboardState] = useState<KeyboardState>({
    isVisible: false,
    height: 0,
  });

  useEffect(() => {
    const showEvent = Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow';
    const hideEvent = Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide';

    const handleKeyboardShow = (event: KeyboardEvent) => {
      setKeyboardState({
        isVisible: true,
        height: event.endCoordinates.height,
      });
    };

    const handleKeyboardHide = () => {
      setKeyboardState({
        isVisible: false,
        height: 0,
      });
    };

    const showSubscription = Keyboard.addListener(showEvent, handleKeyboardShow);
    const hideSubscription = Keyboard.addListener(hideEvent, handleKeyboardHide);

    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  return keyboardState;
}
```

### useAsync

```typescript
import { useState, useCallback, useEffect, useRef } from 'react';

interface AsyncState<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
}

interface UseAsyncReturn<T> extends AsyncState<T> {
  execute: () => Promise<void>;
  reset: () => void;
}

export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate: boolean = false
): UseAsyncReturn<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    isLoading: immediate,
  });

  const isMounted = useRef(true);

  const execute = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const result = await asyncFunction();
      if (isMounted.current) {
        setState({ data: result, error: null, isLoading: false });
      }
    } catch (error) {
      if (isMounted.current) {
        setState({ data: null, error: error as Error, isLoading: false });
      }
    }
  }, [asyncFunction]);

  const reset = useCallback(() => {
    setState({ data: null, error: null, isLoading: false });
  }, []);

  useEffect(() => {
    isMounted.current = true;
    if (immediate) {
      execute();
    }
    return () => {
      isMounted.current = false;
    };
  }, [execute, immediate]);

  return { ...state, execute, reset };
}

// Usage
const ProfileScreen: React.FC = () => {
  const { data: user, isLoading, error, execute } = useAsync(
    () => fetchUserProfile(),
    true // Execute immediately
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorView error={error} onRetry={execute} />;
  if (!user) return null;

  return <UserProfile user={user} />;
};
```

### useForm

```typescript
import { useState, useCallback, useMemo } from 'react';

type ValidationRule<T> = (value: T) => string | undefined;

interface FieldConfig<T> {
  initialValue: T;
  validate?: ValidationRule<T>[];
}

interface FormConfig {
  [key: string]: FieldConfig<any>;
}

type FormValues<T extends FormConfig> = {
  [K in keyof T]: T[K]['initialValue'];
};

type FormErrors<T extends FormConfig> = {
  [K in keyof T]?: string;
};

interface UseFormReturn<T extends FormConfig> {
  values: FormValues<T>;
  errors: FormErrors<T>;
  touched: { [K in keyof T]?: boolean };
  isValid: boolean;
  isDirty: boolean;
  setValue: <K extends keyof T>(field: K, value: T[K]['initialValue']) => void;
  setTouched: (field: keyof T) => void;
  validateField: (field: keyof T) => boolean;
  validateAll: () => boolean;
  reset: () => void;
  handleSubmit: (onSubmit: (values: FormValues<T>) => void) => () => void;
}

export function useForm<T extends FormConfig>(config: T): UseFormReturn<T> {
  const initialValues = useMemo(() => {
    const values: any = {};
    for (const key in config) {
      values[key] = config[key].initialValue;
    }
    return values as FormValues<T>;
  }, []);

  const [values, setValues] = useState<FormValues<T>>(initialValues);
  const [errors, setErrors] = useState<FormErrors<T>>({});
  const [touched, setTouchedFields] = useState<{ [K in keyof T]?: boolean }>({});

  const setValue = useCallback(<K extends keyof T>(
    field: K,
    value: T[K]['initialValue']
  ) => {
    setValues((prev) => ({ ...prev, [field]: value }));
  }, []);

  const setTouched = useCallback((field: keyof T) => {
    setTouchedFields((prev) => ({ ...prev, [field]: true }));
  }, []);

  const validateField = useCallback(
    (field: keyof T): boolean => {
      const fieldConfig = config[field];
      const value = values[field];

      if (!fieldConfig.validate) return true;

      for (const rule of fieldConfig.validate) {
        const error = rule(value);
        if (error) {
          setErrors((prev) => ({ ...prev, [field]: error }));
          return false;
        }
      }

      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
      return true;
    },
    [config, values]
  );

  const validateAll = useCallback((): boolean => {
    let isValid = true;
    const newErrors: FormErrors<T> = {};

    for (const field in config) {
      const fieldConfig = config[field];
      const value = values[field];

      if (fieldConfig.validate) {
        for (const rule of fieldConfig.validate) {
          const error = rule(value);
          if (error) {
            newErrors[field] = error;
            isValid = false;
            break;
          }
        }
      }
    }

    setErrors(newErrors);
    return isValid;
  }, [config, values]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouchedFields({});
  }, [initialValues]);

  const handleSubmit = useCallback(
    (onSubmit: (values: FormValues<T>) => void) => {
      return () => {
        if (validateAll()) {
          onSubmit(values);
        }
      };
    },
    [validateAll, values]
  );

  const isValid = Object.keys(errors).length === 0;
  const isDirty = JSON.stringify(values) !== JSON.stringify(initialValues);

  return {
    values,
    errors,
    touched,
    isValid,
    isDirty,
    setValue,
    setTouched,
    validateField,
    validateAll,
    reset,
    handleSubmit,
  };
}

// Validation helpers
export const required = (message = 'This field is required') =>
  (value: any) => (!value || (typeof value === 'string' && !value.trim()) ? message : undefined);

export const email = (message = 'Invalid email address') =>
  (value: string) => (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? message : undefined);

export const minLength = (length: number, message?: string) =>
  (value: string) => (value.length < length ? message || `Must be at least ${length} characters` : undefined);

// Usage
const SignupForm: React.FC = () => {
  const form = useForm({
    email: {
      initialValue: '',
      validate: [required(), email()],
    },
    password: {
      initialValue: '',
      validate: [required(), minLength(8)],
    },
    name: {
      initialValue: '',
      validate: [required()],
    },
  });

  return (
    <View>
      <Input
        label="Name"
        value={form.values.name}
        onChangeText={(value) => form.setValue('name', value)}
        onBlur={() => {
          form.setTouched('name');
          form.validateField('name');
        }}
        error={form.touched.name ? form.errors.name : undefined}
      />
      <Input
        label="Email"
        value={form.values.email}
        onChangeText={(value) => form.setValue('email', value)}
        onBlur={() => {
          form.setTouched('email');
          form.validateField('email');
        }}
        error={form.touched.email ? form.errors.email : undefined}
        keyboardType="email-address"
      />
      <Input
        label="Password"
        value={form.values.password}
        onChangeText={(value) => form.setValue('password', value)}
        onBlur={() => {
          form.setTouched('password');
          form.validateField('password');
        }}
        error={form.touched.password ? form.errors.password : undefined}
        secureTextEntry
      />
      <Button
        title="Sign Up"
        onPress={form.handleSubmit((values) => {
          console.log('Form submitted:', values);
        })}
        disabled={!form.isDirty}
      />
    </View>
  );
};
```

---

## Accessibility

### Screen Reader Support

```typescript
import {
  View,
  Text,
  TouchableOpacity,
  AccessibilityInfo,
  StyleSheet,
} from 'react-native';
import { useEffect, useState } from 'react';

// Check if screen reader is enabled
export function useScreenReader() {
  const [isEnabled, setIsEnabled] = useState(false);

  useEffect(() => {
    const checkScreenReader = async () => {
      const enabled = await AccessibilityInfo.isScreenReaderEnabled();
      setIsEnabled(enabled);
    };

    checkScreenReader();

    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      setIsEnabled
    );

    return () => {
      subscription.remove();
    };
  }, []);

  return isEnabled;
}

// Accessible Button Component
interface AccessibleButtonProps {
  title: string;
  onPress: () => void;
  hint?: string;
  disabled?: boolean;
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  title,
  onPress,
  hint,
  disabled = false,
}) => {
  return (
    <TouchableOpacity
      style={[styles.button, disabled && styles.disabled]}
      onPress={onPress}
      disabled={disabled}
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityHint={hint}
      accessibilityState={{
        disabled,
      }}
    >
      <Text style={styles.buttonText}>{title}</Text>
    </TouchableOpacity>
  );
};

// Accessible Image with description
interface AccessibleImageProps {
  source: ImageSourcePropType;
  description: string;
  isDecorative?: boolean;
}

export const AccessibleImage: React.FC<AccessibleImageProps> = ({
  source,
  description,
  isDecorative = false,
}) => {
  return (
    <Image
      source={source}
      style={styles.image}
      accessible={!isDecorative}
      accessibilityLabel={isDecorative ? undefined : description}
      accessibilityRole={isDecorative ? undefined : 'image'}
      accessibilityElementsHidden={isDecorative}
      importantForAccessibility={isDecorative ? 'no-hide-descendants' : 'yes'}
    />
  );
};

// Accessible Form Field
interface AccessibleFieldProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  required?: boolean;
}

export const AccessibleField: React.FC<AccessibleFieldProps> = ({
  label,
  value,
  onChangeText,
  error,
  required = false,
}) => {
  const accessibilityLabel = required ? `${label}, required` : label;
  const accessibilityHint = error
    ? `Error: ${error}`
    : `Enter your ${label.toLowerCase()}`;

  return (
    <View style={styles.field}>
      <Text
        style={styles.label}
        accessibilityRole="text"
      >
        {label}
        {required && <Text style={styles.required}> *</Text>}
      </Text>
      <TextInput
        style={[styles.input, error && styles.inputError]}
        value={value}
        onChangeText={onChangeText}
        accessible={true}
        accessibilityLabel={accessibilityLabel}
        accessibilityHint={accessibilityHint}
        accessibilityRole="none"
        accessibilityState={{
          disabled: false,
        }}
        accessibilityValue={{
          text: value || 'empty',
        }}
      />
      {error && (
        <Text
          style={styles.error}
          accessibilityRole="alert"
          accessibilityLiveRegion="polite"
        >
          {error}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#6366F1',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    minHeight: 48, // Minimum touch target
    justifyContent: 'center',
    alignItems: 'center',
  },
  disabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  image: {
    width: 100,
    height: 100,
  },
  field: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 4,
  },
  required: {
    color: '#EF4444',
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    minHeight: 48,
  },
  inputError: {
    borderColor: '#EF4444',
  },
  error: {
    color: '#EF4444',
    fontSize: 12,
    marginTop: 4,
  },
});
```

### Accessibility Roles

```typescript
import { View, Text, AccessibilityRole } from 'react-native';

// Common accessibility roles and their usage
const accessibilityRoles: Record<AccessibilityRole, string> = {
  // Interactive elements
  button: 'For clickable elements that perform an action',
  link: 'For navigation to another screen or URL',
  search: 'For search input fields',
  checkbox: 'For toggleable options (checked/unchecked)',
  radio: 'For single selection from multiple options',
  switch: 'For on/off toggles',
  slider: 'For adjustable values',
  spinbutton: 'For numeric input with increment/decrement',

  // Content elements
  header: 'For section headers',
  text: 'For static text content',
  image: 'For images with descriptions',
  imagebutton: 'For clickable images',

  // Feedback elements
  alert: 'For important messages requiring attention',
  progressbar: 'For loading or progress indicators',

  // Structural elements
  menu: 'For menu containers',
  menuitem: 'For items within a menu',
  menubar: 'For menu bar navigation',
  tab: 'For tab navigation items',
  tablist: 'For tab container',
  toolbar: 'For toolbar containers',
  list: 'For list containers',
  listitem: 'For items within a list',
  grid: 'For grid layouts',

  // Other
  adjustable: 'For elements with adjustable values',
  combobox: 'For dropdown selection',
  summary: 'For expandable summary sections',
  timer: 'For countdown or timer elements',
  none: 'For decorative elements to ignore',
};

// Example: Accessible List Component
interface ListItemProps {
  title: string;
  subtitle?: string;
  index: number;
  total: number;
  onPress: () => void;
}

export const AccessibleListItem: React.FC<ListItemProps> = ({
  title,
  subtitle,
  index,
  total,
  onPress,
}) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={`${title}${subtitle ? `, ${subtitle}` : ''}`}
      accessibilityHint={`Item ${index + 1} of ${total}. Double tap to open.`}
    >
      <View style={styles.listItem}>
        <Text style={styles.title}>{title}</Text>
        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      </View>
    </TouchableOpacity>
  );
};
```

### Focus Management

```typescript
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  AccessibilityInfo,
  findNodeHandle,
  StyleSheet,
} from 'react-native';
import { useRef, useCallback, useEffect } from 'react';

interface FocusableFormProps {
  onSubmit: (data: { email: string; password: string }) => void;
}

export const FocusableForm: React.FC<FocusableFormProps> = ({ onSubmit }) => {
  const emailRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);
  const submitRef = useRef<TouchableOpacity>(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Focus first input on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      emailRef.current?.focus();
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Announce error to screen readers
  useEffect(() => {
    if (error) {
      AccessibilityInfo.announceForAccessibility(error);
    }
  }, [error]);

  // Move focus to next field
  const focusPassword = useCallback(() => {
    passwordRef.current?.focus();
  }, []);

  // Move focus to submit button
  const focusSubmit = useCallback(() => {
    if (submitRef.current) {
      const reactTag = findNodeHandle(submitRef.current);
      if (reactTag) {
        AccessibilityInfo.setAccessibilityFocus(reactTag);
      }
    }
  }, []);

  const handleSubmit = useCallback(() => {
    if (!email || !password) {
      setError('Please fill in all fields');
      // Return focus to first empty field
      if (!email) {
        emailRef.current?.focus();
      } else {
        passwordRef.current?.focus();
      }
      return;
    }

    setError(null);
    onSubmit({ email, password });

    // Announce success
    AccessibilityInfo.announceForAccessibility('Form submitted successfully');
  }, [email, password, onSubmit]);

  return (
    <View style={styles.container}>
      {error && (
        <View
          style={styles.errorContainer}
          accessibilityRole="alert"
          accessibilityLiveRegion="assertive"
        >
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <TextInput
        ref={emailRef}
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        keyboardType="email-address"
        autoCapitalize="none"
        returnKeyType="next"
        onSubmitEditing={focusPassword}
        blurOnSubmit={false}
        accessible={true}
        accessibilityLabel="Email address"
        accessibilityHint="Enter your email address"
      />

      <TextInput
        ref={passwordRef}
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
        returnKeyType="done"
        onSubmitEditing={handleSubmit}
        accessible={true}
        accessibilityLabel="Password"
        accessibilityHint="Enter your password"
      />

      <TouchableOpacity
        ref={submitRef}
        style={styles.button}
        onPress={handleSubmit}
        accessible={true}
        accessibilityRole="button"
        accessibilityLabel="Submit form"
        accessibilityHint="Double tap to submit the login form"
      >
        <Text style={styles.buttonText}>Submit</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 14,
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 12,
    minHeight: 48,
  },
  button: {
    backgroundColor: '#6366F1',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 48,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

---

## Layout Patterns

### Flexbox Layouts

```typescript
import { View, Text, StyleSheet } from 'react-native';

// Row Layout
export const Row: React.FC<{
  children: React.ReactNode;
  gap?: number;
  align?: 'flex-start' | 'center' | 'flex-end' | 'stretch';
  justify?: 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around' | 'space-evenly';
  wrap?: boolean;
}> = ({
  children,
  gap = 0,
  align = 'center',
  justify = 'flex-start',
  wrap = false,
}) => (
  <View
    style={[
      styles.row,
      {
        gap,
        alignItems: align,
        justifyContent: justify,
        flexWrap: wrap ? 'wrap' : 'nowrap',
      },
    ]}
  >
    {children}
  </View>
);

// Column Layout
export const Column: React.FC<{
  children: React.ReactNode;
  gap?: number;
  align?: 'flex-start' | 'center' | 'flex-end' | 'stretch';
  justify?: 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around';
}> = ({
  children,
  gap = 0,
  align = 'stretch',
  justify = 'flex-start',
}) => (
  <View
    style={[
      styles.column,
      {
        gap,
        alignItems: align,
        justifyContent: justify,
      },
    ]}
  >
    {children}
  </View>
);

// Center Layout
export const Center: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <View style={styles.center}>{children}</View>
);

// Spacer Component
export const Spacer: React.FC<{
  size?: number;
  flex?: number;
  horizontal?: boolean;
}> = ({ size, flex, horizontal = false }) => {
  if (flex) {
    return <View style={{ flex }} />;
  }
  return (
    <View
      style={{
        [horizontal ? 'width' : 'height']: size || 16,
      }}
    />
  );
};

// Grid Layout
export const Grid: React.FC<{
  children: React.ReactNode;
  columns: number;
  gap?: number;
}> = ({ children, columns, gap = 12 }) => {
  const childArray = React.Children.toArray(children);

  return (
    <View style={[styles.grid, { gap }]}>
      {childArray.map((child, index) => (
        <View
          key={index}
          style={{
            width: `${(100 - (gap * (columns - 1)) / columns) / columns}%`,
          }}
        >
          {child}
        </View>
      ))}
    </View>
  );
};

// Usage Examples
const LayoutExamples: React.FC = () => {
  return (
    <View style={styles.container}>
      {/* Horizontal Row */}
      <Row gap={12} justify="space-between">
        <Text>Left</Text>
        <Text>Center</Text>
        <Text>Right</Text>
      </Row>

      <Spacer size={24} />

      {/* Vertical Column */}
      <Column gap={8}>
        <Text>Item 1</Text>
        <Text>Item 2</Text>
        <Text>Item 3</Text>
      </Column>

      <Spacer size={24} />

      {/* Centered Content */}
      <Center>
        <Text>Perfectly Centered</Text>
      </Center>

      <Spacer flex={1} />

      {/* Grid Layout */}
      <Grid columns={2} gap={16}>
        <Card>Item 1</Card>
        <Card>Item 2</Card>
        <Card>Item 3</Card>
        <Card>Item 4</Card>
      </Grid>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  row: {
    flexDirection: 'row',
  },
  column: {
    flexDirection: 'column',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
});
```

### Absolute Positioning

```typescript
import { View, Text, Image, StyleSheet, Dimensions } from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// Overlay Pattern
interface OverlayProps {
  children: React.ReactNode;
  visible: boolean;
  backgroundColor?: string;
  opacity?: number;
}

export const Overlay: React.FC<OverlayProps> = ({
  children,
  visible,
  backgroundColor = '#000000',
  opacity = 0.5,
}) => {
  if (!visible) return null;

  return (
    <View style={styles.overlayContainer}>
      <View
        style={[
          styles.overlayBackground,
          { backgroundColor, opacity },
        ]}
      />
      <View style={styles.overlayContent}>{children}</View>
    </View>
  );
};

// Badge on Avatar
interface AvatarWithBadgeProps {
  imageUri: string;
  badgeCount?: number;
  online?: boolean;
  size?: number;
}

export const AvatarWithBadge: React.FC<AvatarWithBadgeProps> = ({
  imageUri,
  badgeCount,
  online,
  size = 48,
}) => {
  return (
    <View style={[styles.avatarContainer, { width: size, height: size }]}>
      <Image
        source={{ uri: imageUri }}
        style={[styles.avatar, { width: size, height: size, borderRadius: size / 2 }]}
      />

      {/* Notification Badge */}
      {badgeCount !== undefined && badgeCount > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>
            {badgeCount > 99 ? '99+' : badgeCount}
          </Text>
        </View>
      )}

      {/* Online Indicator */}
      {online !== undefined && (
        <View
          style={[
            styles.onlineIndicator,
            { backgroundColor: online ? '#10B981' : '#9CA3AF' },
          ]}
        />
      )}
    </View>
  );
};

// Floating Action Button
interface FABProps {
  icon: React.ReactNode;
  onPress: () => void;
  position?: 'bottom-right' | 'bottom-left' | 'bottom-center';
}

export const FloatingActionButton: React.FC<FABProps> = ({
  icon,
  onPress,
  position = 'bottom-right',
}) => {
  const positionStyles = {
    'bottom-right': { right: 16, bottom: 16 },
    'bottom-left': { left: 16, bottom: 16 },
    'bottom-center': { left: SCREEN_WIDTH / 2 - 28, bottom: 16 },
  };

  return (
    <TouchableOpacity
      style={[styles.fab, positionStyles[position]]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      {icon}
    </TouchableOpacity>
  );
};

// Card with Ribbon
interface RibbonCardProps {
  children: React.ReactNode;
  ribbonText: string;
  ribbonColor?: string;
}

export const RibbonCard: React.FC<RibbonCardProps> = ({
  children,
  ribbonText,
  ribbonColor = '#EF4444',
}) => {
  return (
    <View style={styles.ribbonCard}>
      {children}
      <View style={[styles.ribbon, { backgroundColor: ribbonColor }]}>
        <Text style={styles.ribbonText}>{ribbonText}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  // Overlay
  overlayContainer: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  overlayBackground: {
    ...StyleSheet.absoluteFillObject,
  },
  overlayContent: {
    zIndex: 1,
  },

  // Avatar with Badge
  avatarContainer: {
    position: 'relative',
  },
  avatar: {
    backgroundColor: '#E5E7EB',
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#EF4444',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 14,
    height: 14,
    borderRadius: 7,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },

  // FAB
  fab: {
    position: 'absolute',
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#6366F1',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },

  // Ribbon Card
  ribbonCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    overflow: 'hidden',
    position: 'relative',
  },
  ribbon: {
    position: 'absolute',
    top: 12,
    right: -30,
    paddingVertical: 4,
    paddingHorizontal: 32,
    transform: [{ rotate: '45deg' }],
  },
  ribbonText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
});
```

---

## Advanced Patterns

### Compound Components

```typescript
import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  LayoutAnimation,
  Platform,
  UIManager,
} from 'react-native';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// Accordion Context
interface AccordionContextType {
  expandedId: string | null;
  setExpandedId: (id: string | null) => void;
  allowMultiple: boolean;
  expandedIds: Set<string>;
  toggleExpanded: (id: string) => void;
}

const AccordionContext = createContext<AccordionContextType | null>(null);

// Item Context
interface AccordionItemContextType {
  id: string;
  isExpanded: boolean;
}

const AccordionItemContext = createContext<AccordionItemContextType | null>(null);

// Main Accordion Component
interface AccordionProps {
  children: ReactNode;
  allowMultiple?: boolean;
  defaultExpandedId?: string;
}

const Accordion = ({ children, allowMultiple = false, defaultExpandedId }: AccordionProps) => {
  const [expandedId, setExpandedId] = useState<string | null>(defaultExpandedId || null);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(
    defaultExpandedId ? new Set([defaultExpandedId]) : new Set()
  );

  const toggleExpanded = (id: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);

    if (allowMultiple) {
      setExpandedIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
        } else {
          next.add(id);
        }
        return next;
      });
    } else {
      setExpandedId((prev) => (prev === id ? null : id));
    }
  };

  return (
    <AccordionContext.Provider
      value={{
        expandedId,
        setExpandedId,
        allowMultiple,
        expandedIds,
        toggleExpanded,
      }}
    >
      <View style={styles.accordion}>{children}</View>
    </AccordionContext.Provider>
  );
};

// Accordion Item
interface AccordionItemProps {
  children: ReactNode;
  id: string;
}

const AccordionItem = ({ children, id }: AccordionItemProps) => {
  const context = useContext(AccordionContext);
  if (!context) throw new Error('AccordionItem must be used within Accordion');

  const isExpanded = context.allowMultiple
    ? context.expandedIds.has(id)
    : context.expandedId === id;

  return (
    <AccordionItemContext.Provider value={{ id, isExpanded }}>
      <View style={styles.accordionItem}>{children}</View>
    </AccordionItemContext.Provider>
  );
};

// Accordion Header
interface AccordionHeaderProps {
  children: ReactNode;
}

const AccordionHeader = ({ children }: AccordionHeaderProps) => {
  const accordionContext = useContext(AccordionContext);
  const itemContext = useContext(AccordionItemContext);

  if (!accordionContext || !itemContext) {
    throw new Error('AccordionHeader must be used within AccordionItem');
  }

  const handlePress = () => {
    accordionContext.toggleExpanded(itemContext.id);
  };

  return (
    <TouchableOpacity
      style={styles.accordionHeader}
      onPress={handlePress}
      activeOpacity={0.7}
      accessibilityRole="button"
      accessibilityState={{ expanded: itemContext.isExpanded }}
    >
      <View style={styles.accordionHeaderContent}>{children}</View>
      <Text style={styles.accordionChevron}>
        {itemContext.isExpanded ? '▲' : '▼'}
      </Text>
    </TouchableOpacity>
  );
};

// Accordion Content
interface AccordionContentProps {
  children: ReactNode;
}

const AccordionContent = ({ children }: AccordionContentProps) => {
  const itemContext = useContext(AccordionItemContext);

  if (!itemContext) {
    throw new Error('AccordionContent must be used within AccordionItem');
  }

  if (!itemContext.isExpanded) return null;

  return <View style={styles.accordionContent}>{children}</View>;
};

// Attach sub-components
Accordion.Item = AccordionItem;
Accordion.Header = AccordionHeader;
Accordion.Content = AccordionContent;

export { Accordion };

// Usage
const AccordionExample: React.FC = () => {
  return (
    <Accordion allowMultiple={false} defaultExpandedId="1">
      <Accordion.Item id="1">
        <Accordion.Header>
          <Text style={styles.headerText}>Section 1</Text>
        </Accordion.Header>
        <Accordion.Content>
          <Text style={styles.contentText}>
            Content for section 1 goes here.
          </Text>
        </Accordion.Content>
      </Accordion.Item>

      <Accordion.Item id="2">
        <Accordion.Header>
          <Text style={styles.headerText}>Section 2</Text>
        </Accordion.Header>
        <Accordion.Content>
          <Text style={styles.contentText}>
            Content for section 2 goes here.
          </Text>
        </Accordion.Content>
      </Accordion.Item>

      <Accordion.Item id="3">
        <Accordion.Header>
          <Text style={styles.headerText}>Section 3</Text>
        </Accordion.Header>
        <Accordion.Content>
          <Text style={styles.contentText}>
            Content for section 3 goes here.
          </Text>
        </Accordion.Content>
      </Accordion.Item>
    </Accordion>
  );
};

const styles = StyleSheet.create({
  accordion: {
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  accordionItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  accordionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#F9FAFB',
  },
  accordionHeaderContent: {
    flex: 1,
  },
  accordionChevron: {
    fontSize: 12,
    color: '#6B7280',
  },
  accordionContent: {
    padding: 16,
    backgroundColor: '#FFFFFF',
  },
  headerText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  contentText: {
    fontSize: 14,
    color: '#4B5563',
    lineHeight: 22,
  },
});
```

### Render Props Pattern

```typescript
import React, { useState, useCallback, ReactNode } from 'react';
import {
  View,
  FlatList,
  TextInput,
  ActivityIndicator,
  Text,
  StyleSheet,
} from 'react-native';

// Generic data type
interface DataItem {
  id: string;
  [key: string]: any;
}

// Render props for list
interface ListRenderProps<T> {
  data: T[];
  isLoading: boolean;
  error: Error | null;
  searchQuery: string;
  filteredData: T[];
  setSearchQuery: (query: string) => void;
  refresh: () => Promise<void>;
  isRefreshing: boolean;
}

// Props for the component
interface SearchableListProps<T extends DataItem> {
  data: T[];
  isLoading?: boolean;
  error?: Error | null;
  searchKeys: (keyof T)[];
  onRefresh?: () => Promise<void>;
  children: (props: ListRenderProps<T>) => ReactNode;
}

export function SearchableList<T extends DataItem>({
  data,
  isLoading = false,
  error = null,
  searchKeys,
  onRefresh,
  children,
}: SearchableListProps<T>) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Filter data based on search query
  const filteredData = React.useMemo(() => {
    if (!searchQuery.trim()) return data;

    const query = searchQuery.toLowerCase();
    return data.filter((item) =>
      searchKeys.some((key) => {
        const value = item[key];
        if (typeof value === 'string') {
          return value.toLowerCase().includes(query);
        }
        if (typeof value === 'number') {
          return value.toString().includes(query);
        }
        return false;
      })
    );
  }, [data, searchQuery, searchKeys]);

  // Handle refresh
  const refresh = useCallback(async () => {
    if (!onRefresh) return;
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  }, [onRefresh]);

  // Render props
  return (
    <>
      {children({
        data,
        isLoading,
        error,
        searchQuery,
        filteredData,
        setSearchQuery,
        refresh,
        isRefreshing,
      })}
    </>
  );
}

// Usage Example
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

const UserListScreen: React.FC = () => {
  const [users] = useState<User[]>([
    { id: '1', name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
    { id: '3', name: 'Bob Johnson', email: 'bob@example.com', role: 'User' },
  ]);

  return (
    <View style={styles.container}>
      <SearchableList
        data={users}
        searchKeys={['name', 'email', 'role']}
        onRefresh={async () => {
          // Fetch fresh data
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }}
      >
        {({
          filteredData,
          isLoading,
          error,
          searchQuery,
          setSearchQuery,
          refresh,
          isRefreshing,
        }) => (
          <>
            {/* Search Input */}
            <View style={styles.searchContainer}>
              <TextInput
                style={styles.searchInput}
                value={searchQuery}
                onChangeText={setSearchQuery}
                placeholder="Search users..."
                placeholderTextColor="#9CA3AF"
              />
            </View>

            {/* Loading State */}
            {isLoading && (
              <View style={styles.centered}>
                <ActivityIndicator size="large" color="#6366F1" />
              </View>
            )}

            {/* Error State */}
            {error && (
              <View style={styles.centered}>
                <Text style={styles.errorText}>{error.message}</Text>
              </View>
            )}

            {/* Empty State */}
            {!isLoading && !error && filteredData.length === 0 && (
              <View style={styles.centered}>
                <Text style={styles.emptyText}>
                  {searchQuery ? 'No results found' : 'No users'}
                </Text>
              </View>
            )}

            {/* List */}
            {!isLoading && !error && (
              <FlatList
                data={filteredData}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                  <View style={styles.userItem}>
                    <Text style={styles.userName}>{item.name}</Text>
                    <Text style={styles.userEmail}>{item.email}</Text>
                    <Text style={styles.userRole}>{item.role}</Text>
                  </View>
                )}
                refreshing={isRefreshing}
                onRefresh={refresh}
                contentContainerStyle={styles.listContent}
              />
            )}
          </>
        )}
      </SearchableList>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  searchContainer: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  searchInput: {
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: '#EF4444',
    fontSize: 16,
  },
  emptyText: {
    color: '#6B7280',
    fontSize: 16,
  },
  listContent: {
    padding: 16,
  },
  userItem: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  userEmail: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  userRole: {
    fontSize: 12,
    color: '#6366F1',
    marginTop: 8,
    fontWeight: '500',
  },
});
```

---

## Best Practices

### Component Structure

```typescript
// 1. Keep components focused and single-purpose
// Bad: Component doing too many things
const BadUserProfile = () => {
  // Fetches data, manages form, handles navigation, etc.
};

// Good: Separated concerns
const UserProfile = () => <ProfileView user={user} />;
const UserProfileForm = () => <ProfileForm onSubmit={handleSubmit} />;

// 2. Use composition over inheritance
interface CardProps {
  children: ReactNode;
  variant?: 'default' | 'highlighted';
}

const Card: React.FC<CardProps> = ({ children, variant = 'default' }) => (
  <View style={[styles.card, variant === 'highlighted' && styles.highlighted]}>
    {children}
  </View>
);

// Compose specialized cards
const UserCard: React.FC<{ user: User }> = ({ user }) => (
  <Card variant="highlighted">
    <Avatar source={user.avatar} />
    <Text>{user.name}</Text>
  </Card>
);

// 3. Prop interface naming convention
interface ButtonProps {} // For component props
interface ButtonState {} // For component state (if using class components)
type ButtonVariant = 'primary' | 'secondary'; // For union types

// 4. Default prop values
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  ...props
}) => {
  // Implementation
};

// 5. Forward refs properly
const Input = React.forwardRef<TextInput, InputProps>(
  ({ label, error, ...props }, ref) => {
    return (
      <View>
        <Text>{label}</Text>
        <TextInput ref={ref} {...props} />
        {error && <Text style={styles.error}>{error}</Text>}
      </View>
    );
  }
);

Input.displayName = 'Input';
```

### Performance Guidelines

```typescript
// 1. Avoid inline functions in render
// Bad
<TouchableOpacity onPress={() => handlePress(item.id)}>

// Good
const handleItemPress = useCallback(() => {
  handlePress(item.id);
}, [item.id]);

<TouchableOpacity onPress={handleItemPress}>

// 2. Avoid inline styles for repeated elements
// Bad
{items.map(item => (
  <View style={{ padding: 16, margin: 8, backgroundColor: '#FFF' }}>
    {/* ... */}
  </View>
))}

// Good
const styles = StyleSheet.create({
  itemContainer: {
    padding: 16,
    margin: 8,
    backgroundColor: '#FFF',
  },
});

{items.map(item => (
  <View style={styles.itemContainer}>
    {/* ... */}
  </View>
))}

// 3. Use appropriate list component
// For small, static lists (< 50 items)
<ScrollView>
  {items.map(item => <Item key={item.id} {...item} />)}
</ScrollView>

// For large or dynamic lists
<FlatList
  data={items}
  renderItem={({ item }) => <Item {...item} />}
  keyExtractor={item => item.id}
/>

// For sectioned data
<SectionList
  sections={sections}
  renderItem={({ item }) => <Item {...item} />}
  renderSectionHeader={({ section }) => <Header {...section} />}
/>

// 4. Optimize images
<Image
  source={{ uri: imageUrl }}
  style={styles.image}
  resizeMode="cover"
  // Use cache control
  cache="force-cache"
  // Specify dimensions to avoid layout thrashing
/>

// 5. Use InteractionManager for expensive operations
import { InteractionManager } from 'react-native';

useEffect(() => {
  const task = InteractionManager.runAfterInteractions(() => {
    // Expensive operation after animations complete
    loadHeavyData();
  });

  return () => task.cancel();
}, []);
```

### Error Handling

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

// Error Boundary Component
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    error: null,
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log to error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Something went wrong</Text>
          <Text style={styles.errorMessage}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </Text>
          <TouchableOpacity style={styles.retryButton} onPress={this.handleRetry}>
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

// Safe async handler
export function createSafeHandler<T extends (...args: any[]) => Promise<any>>(
  handler: T,
  onError?: (error: Error) => void
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await handler(...args);
    } catch (error) {
      console.error('Handler error:', error);
      onError?.(error as Error);
      throw error;
    }
  }) as T;
}

// Usage
const MyScreen: React.FC = () => {
  const handleSubmit = createSafeHandler(
    async (data: FormData) => {
      const response = await api.submit(data);
      return response;
    },
    (error) => {
      // Show error toast or alert
      Alert.alert('Error', error.message);
    }
  );

  return (
    <ErrorBoundary
      onError={(error) => {
        // Report to analytics
        analytics.logError(error);
      }}
    >
      <Form onSubmit={handleSubmit} />
    </ErrorBoundary>
  );
};

const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#FEF2F2',
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#DC2626',
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 14,
    color: '#7F1D1D',
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: '#DC2626',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### Testing Components

```typescript
// Component: Button.tsx
import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  testID?: string;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  loading = false,
  disabled = false,
  testID,
}) => {
  return (
    <TouchableOpacity
      style={[styles.button, disabled && styles.disabled]}
      onPress={onPress}
      disabled={disabled || loading}
      testID={testID}
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: disabled || loading }}
    >
      {loading ? (
        <ActivityIndicator testID={`${testID}-loader`} color="#FFFFFF" />
      ) : (
        <Text testID={`${testID}-text`} style={styles.text}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
};

// Test: Button.test.tsx
import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react-native';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders correctly with title', () => {
    render(<Button title="Click me" onPress={vi.fn()} testID="button" />);

    expect(screen.getByTestId('button')).toBeTruthy();
    expect(screen.getByTestId('button-text')).toHaveTextContent('Click me');
  });

  it('calls onPress when pressed', () => {
    const onPress = vi.fn();
    render(<Button title="Click me" onPress={onPress} testID="button" />);

    fireEvent.press(screen.getByTestId('button'));

    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it('shows loader when loading', () => {
    render(<Button title="Click me" onPress={vi.fn()} loading testID="button" />);

    expect(screen.getByTestId('button-loader')).toBeTruthy();
    expect(screen.queryByTestId('button-text')).toBeNull();
  });

  it('is disabled when disabled prop is true', () => {
    const onPress = vi.fn();
    render(<Button title="Click me" onPress={onPress} disabled testID="button" />);

    fireEvent.press(screen.getByTestId('button'));

    expect(onPress).not.toHaveBeenCalled();
  });

  it('has correct accessibility props', () => {
    render(<Button title="Submit form" onPress={vi.fn()} testID="button" />);

    const button = screen.getByTestId('button');

    expect(button).toHaveProp('accessibilityRole', 'button');
    expect(button).toHaveProp('accessibilityLabel', 'Submit form');
  });
});

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#6366F1',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

---

## Summary

This guide covers the essential patterns for building production-ready React Native applications:

1. **Core Components**: View, Text, Image, and ScrollView with proper typing and accessibility
2. **StyleSheet Patterns**: Static, dynamic, responsive, and platform-specific styling
3. **Real-World Components**: Card, Input, Button, and Section Header implementations
4. **Performance**: FlatList optimization, memoization with memo/useMemo/useCallback
5. **Custom Hooks**: Reusable logic for debouncing, keyboard handling, async operations, and forms
6. **Accessibility**: Screen reader support, proper roles, and focus management
7. **Layout**: Flexbox patterns and absolute positioning techniques
8. **Advanced Patterns**: Compound components and render props for flexible APIs
9. **Best Practices**: Component structure, performance guidelines, error handling, and testing

Follow these patterns consistently to build maintainable, performant, and accessible React Native applications.
