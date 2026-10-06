---
title: Pass Refs Through to the Underlying Element
impact: CRITICAL
impactDescription: enables integration with form libraries and focus management
tags: arch, ref, react-19, refs, composition, forms
---

## Pass Refs Through to the Underlying Element

Custom components wrapping shadcn/ui primitives must pass `ref` to the underlying element so form libraries, focus management, and imperative handles keep working. In React 19 (the version current shadcn components target) `ref` is an ordinary prop, so you spread it with the rest of the props. `forwardRef` is no longer needed, and shadcn removed it from its own components.

**Incorrect (ref dropped by an explicit props list):**

```tsx
interface SearchInputProps {
  onSearch: (query: string) => void
}

function SearchInput({ onSearch }: SearchInputProps) {
  const [query, setQuery] = useState("")

  return (
    <Input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      onKeyDown={(e) => e.key === "Enter" && onSearch(query)}
    />
  )
}

// Parent cannot focus the input
function SearchForm() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus() // null - ref never reaches the input
  }, [])

  return <SearchInput ref={inputRef} onSearch={handleSearch} />
}
```

**Correct (React 19: type the props with ComponentProps and spread them):**

```tsx
type SearchInputProps = React.ComponentProps<typeof Input> & {
  onSearch: (query: string) => void
}

function SearchInput({ onSearch, ...props }: SearchInputProps) {
  const [query, setQuery] = useState("")

  return (
    <Input
      {...props} // includes ref
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      onKeyDown={(e) => e.key === "Enter" && onSearch(query)}
    />
  )
}

// Parent can now focus the input
function SearchForm() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus() // Works - ref passed through to Input
  }, [])

  return <SearchInput ref={inputRef} onSearch={handleSearch} />
}
```

**Always pass the ref through when:**

- Wrapping form inputs (Input, Select, Textarea)
- Creating trigger components for modals/popovers
- Building components used with React Hook Form

**React 18 projects:** wrap with `React.forwardRef` and set `displayName`. Migrate with the `remove-forward-ref` codemod when upgrading to React 19.

Reference: [React: ref as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop) and [shadcn/ui Tailwind v4 and React 19](https://ui.shadcn.com/docs/tailwind-v4)
