---
title: Use React Hook Form with shadcn/ui Forms
impact: HIGH
impactDescription: eliminates re-renders and provides validation
tags: form, react-hook-form, field, controller, validation, performance, integration
---

## Use React Hook Form with shadcn/ui Forms

shadcn/ui pairs React Hook Form with the `Field` components (`Field`, `FieldLabel`, `FieldError`, `FieldGroup`) and RHF's `Controller`. The older `Form`, `FormField`, `FormItem` wrapper is no longer in the registry. Using controlled state with useState causes re-renders on every keystroke.

**Incorrect (controlled state causes re-renders):**

```tsx
function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Manual validation logic...
    // Re-renders entire form on every keystroke
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      {errors.email && <p className="text-red-500">{errors.email}</p>}
      <Input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button type="submit">Login</Button>
    </form>
  )
}
```

**Correct (React Hook Form with the shadcn/ui Field components):**

```bash
bunx --bun shadcn@latest add field input button
bun add react-hook-form @hookform/resolvers zod
```

```tsx
import { Controller, useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"

const loginSchema = z.object({
  email: z.email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
})

type LoginFormValues = z.infer<typeof loginSchema>

function LoginForm() {
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  })

  const onSubmit = (data: LoginFormValues) => {
    // Validated data, no re-renders during typing
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FieldGroup>
        <Controller
          name="email"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="login-email">Email</FieldLabel>
              <Input
                {...field}
                id="login-email"
                aria-invalid={fieldState.invalid}
                placeholder="email@example.com"
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          name="password"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="login-password">Password</FieldLabel>
              <Input
                {...field}
                id="login-password"
                type="password"
                aria-invalid={fieldState.invalid}
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Button type="submit">Login</Button>
      </FieldGroup>
    </form>
  )
}
```

`Controller` owns each field's registration; `data-invalid` on `Field` and `aria-invalid` on the control drive the error styling and the accessibility state.

Reference: [shadcn/ui React Hook Form guide](https://ui.shadcn.com/docs/forms/react-hook-form)
