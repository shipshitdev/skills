# React/Next.js Component Library Standards Guide

## Project Component Architecture Discovery

Before creating or modifying components, understand the existing architecture:

```bash
# Discover component locations
find . -type d -name "components" -not -path "./node_modules/*"

# Find existing patterns
grep -r "export.*function.*Props" --include="*.tsx" | head -20

# Check for component libraries in use
grep -E "(shadcn|radix|headless)" package.json
```

### Architecture Analysis Checklist

1. **Identify component directories**: `src/components/`, `app/components/`, `packages/ui/`
2. **Check for design system**: Look for `ui/`, `primitives/`, `atoms/` folders
3. **Find barrel exports**: `index.ts` files that re-export components
4. **Detect styling approach**: Tailwind config, CSS modules, styled-components
5. **Review existing patterns**: Study 3+ similar components before writing new ones

```typescript
// Example: Analyzing existing component structure
// src/components/ui/button/index.ts
export { Button } from './button';
export type { ButtonProps } from './button.types';

// src/components/ui/button/button.tsx
// src/components/ui/button/button.types.ts
// src/components/ui/button/button.test.tsx
// src/components/ui/button/button.stories.tsx
```

---

## Component Location Rules

### Directory Structure

```
src/
├── components/
│   ├── ui/                    # Primitive/atomic components
│   │   ├── button/
│   │   ├── input/
│   │   └── modal/
│   ├── patterns/              # Composed patterns
│   │   ├── data-table/
│   │   ├── form-field/
│   │   └── card-list/
│   └── features/              # Feature-specific components
│       ├── auth/
│       ├── dashboard/
│       └── checkout/
├── app/                       # Next.js App Router
│   └── (routes)/
│       └── _components/       # Route-specific components
└── packages/                  # Monorepo shared packages
    └── ui/
        └── src/
```

### Placement Decision Tree

```typescript
/*
 * Component Placement Rules:
 *
 * 1. Used across multiple features? → src/components/ui/
 * 2. Used by one feature, multiple routes? → src/components/features/{feature}/
 * 3. Used by one route only? → app/{route}/_components/
 * 4. Shared across packages? → packages/ui/src/
 */

// Example: Feature component
// src/components/features/checkout/checkout-summary.tsx
export function CheckoutSummary({ items, total }: CheckoutSummaryProps) {
  return (
    <Card>
      <CardHeader>Order Summary</CardHeader>
      <CardContent>
        {items.map((item) => (
          <CheckoutItem key={item.id} {...item} />
        ))}
      </CardContent>
      <CardFooter>
        <Price value={total} />
      </CardFooter>
    </Card>
  );
}
```

---

## Component Naming Conventions

### File Naming

```
kebab-case for files:
├── data-table.tsx
├── data-table.types.ts
├── data-table.test.tsx
├── data-table.stories.tsx
└── index.ts
```

### Component Naming

```typescript
// PascalCase for components
export function DataTable<T>({ data, columns }: DataTableProps<T>) {}

// PascalCase for types with Props/State suffix
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
}

// camelCase for hooks
export function useDataTable<T>(options: UseDataTableOptions<T>) {}

// camelCase for utilities
export function formatTableData<T>(data: T[]): FormattedData<T> {}

// SCREAMING_SNAKE_CASE for constants
export const DEFAULT_PAGE_SIZE = 10;
export const TABLE_VARIANTS = ['default', 'compact', 'comfortable'] as const;
```

### Compound Component Naming

```typescript
// Parent component as namespace
export const Accordion = {
  Root: AccordionRoot,
  Item: AccordionItem,
  Trigger: AccordionTrigger,
  Content: AccordionContent,
};

// Or with dot notation export
export const Accordion = AccordionRoot as typeof AccordionRoot & {
  Item: typeof AccordionItem;
  Trigger: typeof AccordionTrigger;
  Content: typeof AccordionContent;
};

Accordion.Item = AccordionItem;
Accordion.Trigger = AccordionTrigger;
Accordion.Content = AccordionContent;
```

---

## Component Structure Template

### Standard Component File

```typescript
// src/components/ui/button/button.tsx

import { forwardRef, type ComponentPropsWithoutRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

import type { ButtonProps } from './button.types';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';

    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      >
        {children}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

export { buttonVariants };
```

### Types File

```typescript
// src/components/ui/button/button.types.ts

import type { ComponentPropsWithoutRef } from 'react';
import type { VariantProps } from 'class-variance-authority';

import type { buttonVariants } from './button';

export interface ButtonProps
  extends ComponentPropsWithoutRef<'button'>,
    VariantProps<typeof buttonVariants> {
  /** Render as child element (for composition with links) */
  asChild?: boolean;
  /** Loading state */
  isLoading?: boolean;
  /** Left icon */
  leftIcon?: React.ReactNode;
  /** Right icon */
  rightIcon?: React.ReactNode;
}
```

### Index File (Barrel Export)

```typescript
// src/components/ui/button/index.ts

export { Button, buttonVariants } from './button';
export type { ButtonProps } from './button.types';
```

---

## Component Design Patterns

### 1. Composition Pattern

```typescript
// Favor composition over configuration
// BAD: Prop-heavy component
<Card
  title="Welcome"
  subtitle="Get started"
  icon={<UserIcon />}
  footer={<Button>Continue</Button>}
  hasCloseButton
  onClose={handleClose}
/>

// GOOD: Composable component
<Card>
  <Card.Header>
    <Card.Icon><UserIcon /></Card.Icon>
    <Card.Title>Welcome</Card.Title>
    <Card.Subtitle>Get started</Card.Subtitle>
    <Card.CloseButton onClick={handleClose} />
  </Card.Header>
  <Card.Footer>
    <Button>Continue</Button>
  </Card.Footer>
</Card>
```

### 2. Controlled & Uncontrolled Pattern

```typescript
// src/components/ui/input/input.tsx

interface InputProps extends Omit<ComponentPropsWithoutRef<'input'>, 'value' | 'onChange'> {
  /** Controlled value */
  value?: string;
  /** Controlled change handler */
  onChange?: (value: string) => void;
  /** Default value for uncontrolled mode */
  defaultValue?: string;
}

export function Input({ value, onChange, defaultValue, ...props }: InputProps) {
  // Internal state for uncontrolled mode
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');

  // Determine if controlled
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;

    if (!isControlled) {
      setInternalValue(newValue);
    }

    onChange?.(newValue);
  };

  return (
    <input
      value={currentValue}
      onChange={handleChange}
      {...props}
    />
  );
}
```

### 3. Render Props Pattern

```typescript
// src/components/patterns/data-fetcher/data-fetcher.tsx

interface DataFetcherProps<T> {
  url: string;
  children: (state: {
    data: T | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
  }) => React.ReactNode;
}

export function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Fetch failed');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  useEffect(() => {
    const controller = new AbortController();
    fetchData();
    return () => controller.abort();
  }, [fetchData]);

  return <>{children({ data, isLoading, error, refetch: fetchData })}</>;
}

// Usage
<DataFetcher<User[]> url="/api/users">
  {({ data, isLoading, error }) => {
    if (isLoading) return <Skeleton />;
    if (error) return <ErrorMessage error={error} />;
    return <UserList users={data!} />;
  }}
</DataFetcher>
```

### 4. Compound Components Pattern

```typescript
// src/components/ui/tabs/tabs.tsx

import { createContext, useContext, useState, useId } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
  baseId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within Tabs.Root');
  }
  return context;
}

// Root
interface TabsRootProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
}

function TabsRoot({ defaultValue, value, onValueChange, children }: TabsRootProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const baseId = useId();

  const activeTab = value ?? internalValue;
  const setActiveTab = (newValue: string) => {
    setInternalValue(newValue);
    onValueChange?.(newValue);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab, baseId }}>
      <div className="tabs-root">{children}</div>
    </TabsContext.Provider>
  );
}

// List
function TabsList({ children }: { children: React.ReactNode }) {
  return (
    <div role="tablist" className="tabs-list">
      {children}
    </div>
  );
}

// Trigger
interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  disabled?: boolean;
}

function TabsTrigger({ value, children, disabled }: TabsTriggerProps) {
  const { activeTab, setActiveTab, baseId } = useTabsContext();
  const isActive = activeTab === value;

  return (
    <button
      role="tab"
      id={`${baseId}-trigger-${value}`}
      aria-controls={`${baseId}-content-${value}`}
      aria-selected={isActive}
      disabled={disabled}
      onClick={() => setActiveTab(value)}
      className={cn('tabs-trigger', isActive && 'tabs-trigger--active')}
    >
      {children}
    </button>
  );
}

// Content
interface TabsContentProps {
  value: string;
  children: React.ReactNode;
}

function TabsContent({ value, children }: TabsContentProps) {
  const { activeTab, baseId } = useTabsContext();
  const isActive = activeTab === value;

  if (!isActive) return null;

  return (
    <div
      role="tabpanel"
      id={`${baseId}-content-${value}`}
      aria-labelledby={`${baseId}-trigger-${value}`}
      className="tabs-content"
    >
      {children}
    </div>
  );
}

// Export compound component
export const Tabs = {
  Root: TabsRoot,
  List: TabsList,
  Trigger: TabsTrigger,
  Content: TabsContent,
};

// Usage
<Tabs.Root defaultValue="account">
  <Tabs.List>
    <Tabs.Trigger value="account">Account</Tabs.Trigger>
    <Tabs.Trigger value="settings">Settings</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="account">Account settings here</Tabs.Content>
  <Tabs.Content value="settings">App settings here</Tabs.Content>
</Tabs.Root>
```

### 5. Polymorphic Component Pattern

```typescript
// src/components/ui/box/box.tsx

import type { ElementType, ComponentPropsWithoutRef } from 'react';

type BoxProps<E extends ElementType = 'div'> = {
  as?: E;
  children?: React.ReactNode;
} & Omit<ComponentPropsWithoutRef<E>, 'as'>;

export function Box<E extends ElementType = 'div'>({
  as,
  children,
  ...props
}: BoxProps<E>) {
  const Component = as || 'div';
  return <Component {...props}>{children}</Component>;
}

// Usage
<Box>Default div</Box>
<Box as="section">Section element</Box>
<Box as="a" href="/home">Link element</Box>
<Box as={Link} to="/about">React Router Link</Box>
```

---

## Styling Standards

### Tailwind CSS

```typescript
// src/lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Component usage
import { cn } from '@/lib/utils';

interface CardProps {
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
}

export function Card({ className, variant = 'default' }: CardProps) {
  return (
    <div
      className={cn(
        // Base styles
        'rounded-lg p-6',
        // Variant styles
        {
          'bg-card text-card-foreground shadow': variant === 'default',
          'border border-border bg-transparent': variant === 'outline',
          'bg-transparent': variant === 'ghost',
        },
        // Allow override
        className
      )}
    />
  );
}
```

### Class Variance Authority (CVA)

```typescript
// src/components/ui/badge/badge.tsx

import { cva, type VariantProps } from 'class-variance-authority';

const badgeVariants = cva(
  // Base styles
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground',
        secondary: 'bg-secondary text-secondary-foreground',
        success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100',
        error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
        outline: 'border border-current bg-transparent',
      },
      size: {
        sm: 'text-xs px-2 py-0.5',
        md: 'text-sm px-2.5 py-0.5',
        lg: 'text-base px-3 py-1',
      },
    },
    compoundVariants: [
      {
        variant: 'outline',
        size: 'lg',
        className: 'border-2',
      },
    ],
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, size, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant, size }), className)} {...props} />;
}
```

### CSS Modules (When Needed)

```typescript
// src/components/ui/spinner/spinner.module.css
.spinner {
  animation: spin 1s linear infinite;
}

.spinner--sm { width: 1rem; height: 1rem; }
.spinner--md { width: 1.5rem; height: 1.5rem; }
.spinner--lg { width: 2rem; height: 2rem; }

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// src/components/ui/spinner/spinner.tsx
import styles from './spinner.module.css';
import { cn } from '@/lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <svg
      className={cn(styles.spinner, styles[`spinner--${size}`], className)}
      viewBox="0 0 24 24"
    >
      <circle cx="12" cy="12" r="10" fill="none" strokeWidth="2" />
    </svg>
  );
}
```

---

## TypeScript Best Practices

### Props Types

```typescript
// Extend native element props
interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  variant?: 'primary' | 'secondary';
}

// Omit conflicting props
interface InputProps extends Omit<ComponentPropsWithoutRef<'input'>, 'size'> {
  size?: 'sm' | 'md' | 'lg';
}

// Required children
interface CardProps {
  children: React.ReactNode; // Required
}

// Optional children
interface IconProps {
  children?: React.ReactNode; // Optional
}

// Specific children type
interface ListProps {
  children: React.ReactElement<ListItemProps> | React.ReactElement<ListItemProps>[];
}

// Discriminated unions
type AlertProps =
  | { variant: 'success'; onDismiss?: () => void }
  | { variant: 'error'; error: Error; retry?: () => void }
  | { variant: 'loading'; progress?: number };
```

### Generics

```typescript
// Generic list component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
}

export function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}

// Generic table component
interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T extends { id: string | number }> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
}

export function DataTable<T extends { id: string | number }>({
  data,
  columns,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key as string}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={item.id} onClick={() => onRowClick?.(item)}>
            {columns.map((col) => (
              <td key={col.key as string}>
                {col.render ? col.render(item) : String(item[col.key as keyof T])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### Event Handlers

```typescript
// Proper event typing
interface FormProps {
  onSubmit: (data: FormData) => void | Promise<void>;
}

export function Form({ onSubmit }: FormProps) {
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    await onSubmit(Object.fromEntries(formData) as FormData);
  };

  return <form onSubmit={handleSubmit}>{/* ... */}</form>;
}

// Custom event handlers
interface SelectProps {
  onChange: (value: string, option: Option) => void;
}

// Keyboard event handlers
interface SearchInputProps {
  onSearch: (query: string) => void;
}

function SearchInput({ onSearch }: SearchInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch(e.currentTarget.value);
    }
  };

  return <input type="search" onKeyDown={handleKeyDown} />;
}
```

---

## Performance Optimization

### Memoization

```typescript
// React.memo for expensive renders
interface ExpensiveListProps {
  items: Item[];
  onSelect: (item: Item) => void;
}

export const ExpensiveList = memo(function ExpensiveList({
  items,
  onSelect,
}: ExpensiveListProps) {
  return (
    <ul>
      {items.map((item) => (
        <ExpensiveListItem key={item.id} item={item} onSelect={onSelect} />
      ))}
    </ul>
  );
});

// useMemo for expensive calculations
function DataVisualization({ data }: { data: DataPoint[] }) {
  const processedData = useMemo(() => {
    return data
      .filter((d) => d.value > 0)
      .map((d) => ({ ...d, normalized: d.value / 100 }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  return <Chart data={processedData} />;
}

// useCallback for stable references
function ParentComponent() {
  const [items, setItems] = useState<Item[]>([]);

  const handleItemSelect = useCallback((item: Item) => {
    setItems((prev) => prev.map((i) =>
      i.id === item.id ? { ...i, selected: true } : i
    ));
  }, []);

  return <ItemList items={items} onSelect={handleItemSelect} />;
}
```

### Code Splitting

```typescript
// Dynamic imports for routes
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('@/components/features/dashboard'));
const Settings = lazy(() => import('@/components/features/settings'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}

// Dynamic imports for heavy components
const HeavyChart = lazy(() =>
  import('@/components/patterns/heavy-chart').then((mod) => ({
    default: mod.HeavyChart,
  }))
);

function AnalyticsPage() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <Button onClick={() => setShowChart(true)}>Show Analytics</Button>
      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
```

### Virtualization

```typescript
// Using @tanstack/react-virtual
import { useVirtualizer } from '@tanstack/react-virtual';

interface VirtualListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  estimateSize?: number;
}

export function VirtualList<T>({
  items,
  renderItem,
  estimateSize = 50,
}: VirtualListProps<T>) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan: 5,
  });

  return (
    <div ref={parentRef} className="h-[400px] overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {renderItem(items[virtualItem.index], virtualItem.index)}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Accessibility Requirements

### Semantic HTML

```typescript
// Use semantic elements
function Article({ title, content, author, date }: ArticleProps) {
  return (
    <article>
      <header>
        <h1>{title}</h1>
        <p>
          By <address>{author}</address> on <time dateTime={date}>{formatDate(date)}</time>
        </p>
      </header>
      <main>{content}</main>
    </article>
  );
}

// Navigation with landmarks
function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <header role="banner">
        <nav aria-label="Main navigation">{/* ... */}</nav>
      </header>
      <main role="main" id="main-content">
        {children}
      </main>
      <aside aria-label="Sidebar">{/* ... */}</aside>
      <footer role="contentinfo">{/* ... */}</footer>
    </>
  );
}
```

### ARIA Attributes

```typescript
// Dialog/Modal
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const titleId = useId();
  const descriptionId = useId();

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <h2 id={titleId}>{title}</h2>
      <div id={descriptionId}>{children}</div>
      <button onClick={onClose} aria-label="Close modal">
        <XIcon aria-hidden="true" />
      </button>
    </div>
  );
}

// Loading states
interface ButtonProps {
  isLoading?: boolean;
  children: React.ReactNode;
}

function Button({ isLoading, children, ...props }: ButtonProps) {
  return (
    <button
      disabled={isLoading}
      aria-busy={isLoading}
      aria-disabled={isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <Spinner aria-hidden="true" />
          <span className="sr-only">Loading...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}

// Live regions
function Notifications() {
  const [message, setMessage] = useState('');

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
}
```

### Keyboard Navigation

```typescript
// Focus management
function Dialog({ isOpen, onClose, children }: DialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      dialogRef.current?.focus();
    } else {
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      ref={dialogRef}
      tabIndex={-1}
      onKeyDown={handleKeyDown}
      role="dialog"
    >
      <FocusTrap>{children}</FocusTrap>
    </div>
  );
}

// Roving tabindex for lists
function MenuList({ items }: { items: MenuItem[] }) {
  const [focusedIndex, setFocusedIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex((prev) => Math.min(prev + 1, items.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex((prev) => Math.max(prev - 1, 0));
        break;
      case 'Home':
        e.preventDefault();
        setFocusedIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setFocusedIndex(items.length - 1);
        break;
    }
  };

  return (
    <ul role="menu" onKeyDown={handleKeyDown}>
      {items.map((item, index) => (
        <li
          key={item.id}
          role="menuitem"
          tabIndex={index === focusedIndex ? 0 : -1}
        >
          {item.label}
        </li>
      ))}
    </ul>
  );
}
```

---

## Error Handling & Loading States

### Error Boundaries

```typescript
// src/components/patterns/error-boundary/error-boundary.tsx

import { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error, reset: () => void) => ReactNode);
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

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.props.onError?.(error, errorInfo);
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(this.state.error, this.reset);
      }
      return this.props.fallback ?? <DefaultErrorFallback error={this.state.error} reset={this.reset} />;
    }

    return this.props.children;
  }
}

// Default fallback component
function DefaultErrorFallback({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div role="alert" className="error-fallback">
      <h2>Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Loading States Pattern

```typescript
// src/components/patterns/async-boundary/async-boundary.tsx

interface AsyncBoundaryProps<T> {
  data: T | undefined;
  isLoading: boolean;
  error: Error | null;
  loadingFallback?: ReactNode;
  errorFallback?: ReactNode | ((error: Error) => ReactNode);
  children: (data: T) => ReactNode;
}

export function AsyncBoundary<T>({
  data,
  isLoading,
  error,
  loadingFallback = <DefaultSkeleton />,
  errorFallback,
  children,
}: AsyncBoundaryProps<T>) {
  if (isLoading) {
    return <>{loadingFallback}</>;
  }

  if (error) {
    if (typeof errorFallback === 'function') {
      return <>{errorFallback(error)}</>;
    }
    return <>{errorFallback ?? <DefaultError error={error} />}</>;
  }

  if (data === undefined) {
    return null;
  }

  return <>{children(data)}</>;
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error } = useUser(userId);

  return (
    <AsyncBoundary
      data={data}
      isLoading={isLoading}
      error={error}
      loadingFallback={<UserProfileSkeleton />}
    >
      {(user) => (
        <div>
          <Avatar src={user.avatar} />
          <h1>{user.name}</h1>
        </div>
      )}
    </AsyncBoundary>
  );
}
```

### Skeleton Components

```typescript
// src/components/ui/skeleton/skeleton.tsx

import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
}: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse bg-muted',
        {
          'h-4 rounded': variant === 'text',
          'rounded-full': variant === 'circular',
          'rounded-md': variant === 'rectangular',
        },
        className
      )}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

// Composed skeleton
export function CardSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton variant="rectangular" height={200} />
      <Skeleton variant="text" width="60%" />
      <Skeleton variant="text" width="40%" />
    </div>
  );
}
```

---

## Testing Standards

### Component Testing with Vitest & Testing Library

```typescript
// src/components/ui/button/button.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { Button } from './button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('applies variant classes', () => {
    render(<Button variant="destructive">Delete</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-destructive');
  });

  it('handles click events', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Click</Button>);
    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('shows loading state', () => {
    render(<Button isLoading>Submit</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('forwards ref correctly', () => {
    const ref = vi.fn();
    render(<Button ref={ref}>Ref Button</Button>);
    expect(ref).toHaveBeenCalledWith(expect.any(HTMLButtonElement));
  });
});
```

### Testing Hooks

```typescript
// src/hooks/use-toggle.test.ts

import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

import { useToggle } from './use-toggle';

describe('useToggle', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useToggle());
    expect(result.current.isOpen).toBe(false);
  });

  it('initializes with custom value', () => {
    const { result } = renderHook(() => useToggle(true));
    expect(result.current.isOpen).toBe(true);
  });

  it('toggles value', () => {
    const { result } = renderHook(() => useToggle());

    act(() => {
      result.current.toggle();
    });

    expect(result.current.isOpen).toBe(true);
  });

  it('sets specific values', () => {
    const { result } = renderHook(() => useToggle());

    act(() => {
      result.current.setOpen(true);
    });
    expect(result.current.isOpen).toBe(true);

    act(() => {
      result.current.setOpen(false);
    });
    expect(result.current.isOpen).toBe(false);
  });
});
```

### Testing Async Components

```typescript
// src/components/features/user-list/user-list.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import { UserList } from './user-list';

const mockUsers = [
  { id: '1', name: 'Alice', email: 'alice@example.com' },
  { id: '2', name: 'Bob', email: 'bob@example.com' },
];

const server = setupServer(
  http.get('/api/users', () => {
    return HttpResponse.json(mockUsers);
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserList', () => {
  it('shows loading state initially', () => {
    render(<UserList />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders users after loading', async () => {
    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });

  it('shows error state on failure', async () => {
    server.use(
      http.get('/api/users', () => {
        return HttpResponse.error();
      })
    );

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
});
```

### Accessibility Testing

```typescript
// src/components/ui/modal/modal.test.tsx

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { describe, it, expect } from 'vitest';

import { Modal } from './modal';

expect.extend(toHaveNoViolations);

describe('Modal accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(
      <Modal isOpen onClose={() => {}} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('traps focus within modal', async () => {
    const user = userEvent.setup();

    render(
      <Modal isOpen onClose={() => {}} title="Test">
        <input data-testid="first" />
        <button>Action</button>
        <input data-testid="last" />
      </Modal>
    );

    // Focus should cycle within modal
    await user.tab();
    expect(screen.getByTestId('first')).toHaveFocus();

    await user.tab();
    await user.tab();
    expect(screen.getByTestId('last')).toHaveFocus();

    await user.tab();
    expect(screen.getByTestId('first')).toHaveFocus();
  });

  it('closes on Escape key', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <Modal isOpen onClose={onClose} title="Test">
        Content
      </Modal>
    );

    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();
  });
});
```

---

## Documentation Standards

### JSDoc Comments

```typescript
/**
 * A customizable button component that supports multiple variants and sizes.
 *
 * @example
 * ```tsx
 * // Basic usage
 * <Button>Click me</Button>
 *
 * // With variant
 * <Button variant="destructive">Delete</Button>
 *
 * // As a link
 * <Button asChild>
 *   <a href="/home">Go Home</a>
 * </Button>
 * ```
 *
 * @see {@link https://ui.shadcn.com/docs/components/button} - Design reference
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    // ...
  }
);

/**
 * Props for the Button component.
 */
export interface ButtonProps
  extends ComponentPropsWithoutRef<'button'>,
    VariantProps<typeof buttonVariants> {
  /**
   * When true, the button will render its child as the root element.
   * Useful for composing with Link components.
   * @default false
   */
  asChild?: boolean;

  /**
   * Shows a loading spinner and disables the button.
   * @default false
   */
  isLoading?: boolean;

  /**
   * Icon to display before the button text.
   */
  leftIcon?: React.ReactNode;

  /**
   * Icon to display after the button text.
   */
  rightIcon?: React.ReactNode;
}
```

### Storybook Stories

```typescript
// src/components/ui/button/button.stories.tsx

import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import { Button } from './button';

const meta = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and sizes.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
      description: 'Visual style variant',
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
      description: 'Size of the button',
    },
    isLoading: {
      control: 'boolean',
      description: 'Shows loading state',
    },
    disabled: {
      control: 'boolean',
      description: 'Disables the button',
    },
  },
  args: {
    onClick: fn(),
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Button',
  },
};

export const Variants: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button variant="default">Default</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};

export const Loading: Story = {
  args: {
    children: 'Loading',
    isLoading: true,
  },
};

export const WithIcons: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button leftIcon={<PlusIcon />}>Add Item</Button>
      <Button rightIcon={<ArrowRightIcon />}>Continue</Button>
    </div>
  ),
};

export const AsLink: Story = {
  render: () => (
    <Button asChild>
      <a href="https://example.com">External Link</a>
    </Button>
  ),
};
```

---

## Component Checklist

Before merging any component:

### Structure

- [ ] Component in correct location (ui/patterns/features)
- [ ] Follows file naming conventions (kebab-case)
- [ ] Has types file (`.types.ts`)
- [ ] Has barrel export (`index.ts`)
- [ ] Uses `forwardRef` where appropriate

### Code Quality

- [ ] No `any` types
- [ ] Props interface properly defined
- [ ] Default props documented
- [ ] Uses `cn()` for class merging
- [ ] Follows existing codebase patterns

### Accessibility

- [ ] Semantic HTML elements
- [ ] Proper ARIA attributes
- [ ] Keyboard navigation works
- [ ] Focus management implemented
- [ ] Screen reader tested

### Performance

- [ ] Memoization where needed
- [ ] No unnecessary re-renders
- [ ] Lazy loading for heavy components
- [ ] Bundle size checked

### Testing

- [ ] Unit tests written
- [ ] Edge cases covered
- [ ] Accessibility tests pass
- [ ] Visual regression tests (if applicable)

### Documentation

- [ ] JSDoc comments on exports
- [ ] Storybook stories created
- [ ] Usage examples provided
- [ ] Props documented

---

## Common Patterns Reference

### Button

```typescript
// Standard button with variants
interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'ghost' | 'link';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading,
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      className={cn(buttonVariants({ variant, size }))}
      {...props}
    >
      {isLoading ? (
        <Spinner className="mr-2" />
      ) : leftIcon ? (
        <span className="mr-2">{leftIcon}</span>
      ) : null}
      {children}
      {rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
}
```

### Card

```typescript
// Composable card component
interface CardProps extends ComponentPropsWithoutRef<'div'> {
  variant?: 'default' | 'outline' | 'elevated';
}

function CardRoot({ variant = 'default', className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg',
        {
          'bg-card text-card-foreground shadow-sm': variant === 'default',
          'border border-border': variant === 'outline',
          'bg-card shadow-lg': variant === 'elevated',
        },
        className
      )}
      {...props}
    />
  );
}

function CardHeader({ className, ...props }: ComponentPropsWithoutRef<'div'>) {
  return <div className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />;
}

function CardTitle({ className, ...props }: ComponentPropsWithoutRef<'h3'>) {
  return <h3 className={cn('text-2xl font-semibold leading-none tracking-tight', className)} {...props} />;
}

function CardContent({ className, ...props }: ComponentPropsWithoutRef<'div'>) {
  return <div className={cn('p-6 pt-0', className)} {...props} />;
}

function CardFooter({ className, ...props }: ComponentPropsWithoutRef<'div'>) {
  return <div className={cn('flex items-center p-6 pt-0', className)} {...props} />;
}

export const Card = Object.assign(CardRoot, {
  Header: CardHeader,
  Title: CardTitle,
  Content: CardContent,
  Footer: CardFooter,
});
```

### Modal/Dialog

```typescript
// Accessible modal with focus trap
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
}: ModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const modalRef = useRef<HTMLDivElement>(null);

  // Focus trap and restore
  useEffect(() => {
    if (!isOpen) return;

    const previousFocus = document.activeElement as HTMLElement;
    modalRef.current?.focus();

    return () => previousFocus?.focus();
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <Portal>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 animate-in fade-in"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        tabIndex={-1}
        className={cn(
          'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2',
          'bg-background rounded-lg shadow-lg p-6',
          'animate-in fade-in zoom-in-95',
          {
            'w-full max-w-sm': size === 'sm',
            'w-full max-w-md': size === 'md',
            'w-full max-w-lg': size === 'lg',
            'w-full max-w-xl': size === 'xl',
          }
        )}
      >
        <h2 id={titleId} className="text-lg font-semibold">
          {title}
        </h2>
        {description && (
          <p id={descriptionId} className="mt-2 text-sm text-muted-foreground">
            {description}
          </p>
        )}
        <div className="mt-4">{children}</div>
        <button
          onClick={onClose}
          className="absolute right-4 top-4"
          aria-label="Close"
        >
          <XIcon className="h-4 w-4" />
        </button>
      </div>
    </Portal>
  );
}
```

### Form Field

```typescript
// Accessible form field with validation
interface FormFieldProps {
  label: string;
  name: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: ReactElement<{ id: string; 'aria-describedby'?: string; 'aria-invalid'?: boolean }>;
}

export function FormField({
  label,
  name,
  error,
  hint,
  required,
  children,
}: FormFieldProps) {
  const inputId = `field-${name}`;
  const errorId = `${inputId}-error`;
  const hintId = `${inputId}-hint`;

  const describedBy = [
    error ? errorId : null,
    hint ? hintId : null,
  ].filter(Boolean).join(' ') || undefined;

  return (
    <div className="space-y-2">
      <label htmlFor={inputId} className="text-sm font-medium">
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </label>

      {cloneElement(children, {
        id: inputId,
        'aria-describedby': describedBy,
        'aria-invalid': !!error,
      })}

      {hint && !error && (
        <p id={hintId} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}

      {error && (
        <p id={errorId} role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}

// Usage
<FormField
  label="Email"
  name="email"
  error={errors.email}
  hint="We'll never share your email"
  required
>
  <Input type="email" placeholder="you@example.com" />
</FormField>
```

### Data Table

```typescript
// Generic data table with sorting and selection
interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => ReactNode;
  sortable?: boolean;
  width?: string;
}

interface DataTableProps<T extends { id: string | number }> {
  data: T[];
  columns: Column<T>[];
  selectable?: boolean;
  selectedIds?: Set<string | number>;
  onSelectionChange?: (ids: Set<string | number>) => void;
  onRowClick?: (item: T) => void;
  emptyState?: ReactNode;
  isLoading?: boolean;
}

export function DataTable<T extends { id: string | number }>({
  data,
  columns,
  selectable,
  selectedIds = new Set(),
  onSelectionChange,
  onRowClick,
  emptyState,
  isLoading,
}: DataTableProps<T>) {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key as keyof T];
      const bVal = b[sortConfig.key as keyof T];

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);

  const toggleSort = (key: string) => {
    setSortConfig((current) => {
      if (current?.key !== key) return { key, direction: 'asc' };
      if (current.direction === 'asc') return { key, direction: 'desc' };
      return null;
    });
  };

  const toggleAll = () => {
    if (selectedIds.size === data.length) {
      onSelectionChange?.(new Set());
    } else {
      onSelectionChange?.(new Set(data.map((d) => d.id)));
    }
  };

  const toggleRow = (id: string | number) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    onSelectionChange?.(newSet);
  };

  if (isLoading) {
    return <TableSkeleton columns={columns.length} rows={5} />;
  }

  if (data.length === 0) {
    return emptyState ?? <EmptyState message="No data available" />;
  }

  return (
    <table className="w-full">
      <thead>
        <tr>
          {selectable && (
            <th className="w-12">
              <Checkbox
                checked={selectedIds.size === data.length}
                indeterminate={selectedIds.size > 0 && selectedIds.size < data.length}
                onChange={toggleAll}
                aria-label="Select all"
              />
            </th>
          )}
          {columns.map((col) => (
            <th
              key={col.key as string}
              style={{ width: col.width }}
              className={cn(col.sortable && 'cursor-pointer')}
              onClick={() => col.sortable && toggleSort(col.key as string)}
            >
              <div className="flex items-center gap-2">
                {col.header}
                {col.sortable && sortConfig?.key === col.key && (
                  <SortIcon direction={sortConfig.direction} />
                )}
              </div>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sortedData.map((item) => (
          <tr
            key={item.id}
            onClick={() => onRowClick?.(item)}
            className={cn(onRowClick && 'cursor-pointer hover:bg-muted')}
          >
            {selectable && (
              <td onClick={(e) => e.stopPropagation()}>
                <Checkbox
                  checked={selectedIds.has(item.id)}
                  onChange={() => toggleRow(item.id)}
                  aria-label={`Select row ${item.id}`}
                />
              </td>
            )}
            {columns.map((col) => (
              <td key={col.key as string}>
                {col.render
                  ? col.render(item)
                  : String(item[col.key as keyof T] ?? '')}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## Quick Reference

| Pattern | When to Use |
|---------|-------------|
| Composition | When props grow beyond 5-6 or flexibility needed |
| Controlled | When parent needs real-time value access |
| Uncontrolled | For simple forms, better performance |
| Compound | For multi-part components (tabs, accordions) |
| Polymorphic | When element type should be customizable |
| Render Props | For maximum flexibility in rendering |

| Performance Technique | When to Apply |
|-----------------------|---------------|
| `React.memo` | Components that re-render with same props |
| `useMemo` | Expensive calculations in render |
| `useCallback` | Callbacks passed to memoized children |
| Lazy loading | Routes, heavy components, modals |
| Virtualization | Lists with 100+ items |

| Accessibility | Required For |
|---------------|--------------|
| `role` | Non-semantic interactive elements |
| `aria-label` | Icon-only buttons, complex widgets |
| `aria-describedby` | Form fields with hints/errors |
| `aria-expanded` | Collapsible content triggers |
| `aria-live` | Dynamic content updates |
