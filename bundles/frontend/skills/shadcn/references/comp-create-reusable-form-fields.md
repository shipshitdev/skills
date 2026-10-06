---
title: Create Reusable Form Field Components
impact: MEDIUM
impactDescription: reduces boilerplate and ensures consistency
tags: comp, form, field, reusable, composition
---

## Create Reusable Form Field Components

Extract common form field patterns into reusable components to reduce boilerplate and maintain consistency across forms.

**Incorrect (repeated form field boilerplate):**

```tsx
function UserForm() {
  const form = useForm<UserFormValues>({
    resolver: zodResolver(userSchema),
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Controller
        control={form.control}
        name="firstName"
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor="firstName">First Name</FieldLabel>
            <Input id="firstName" placeholder="Enter first name" aria-invalid={fieldState.invalid} {...field} />
            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />
      <Controller
        control={form.control}
        name="lastName"
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor="lastName">Last Name</FieldLabel>
            <Input id="lastName" placeholder="Enter last name" aria-invalid={fieldState.invalid} {...field} />
            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />
      {/* 10 more fields with identical structure... */}
    </form>
  )
}
```

**Correct (reusable field components):**

```tsx
// components/form/text-field.tsx
interface TextFieldProps<T extends FieldValues> {
  control: Control<T>
  name: Path<T>
  label: string
  placeholder?: string
  description?: string
  type?: "text" | "email" | "password"
}

function TextField<T extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  description,
  type = "text",
}: TextFieldProps<T>) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>{label}</FieldLabel>
          <Input
            {...field}
            id={name}
            type={type}
            placeholder={placeholder}
            aria-invalid={fieldState.invalid}
          />
          {description && <FieldDescription>{description}</FieldDescription>}
          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  )
}

// components/form/select-field.tsx
interface SelectFieldProps<T extends FieldValues> {
  control: Control<T>
  name: Path<T>
  label: string
  placeholder?: string
  options: { value: string; label: string }[]
}

function SelectField<T extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  options,
}: SelectFieldProps<T>) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>{label}</FieldLabel>
          <Select name={field.name} value={field.value} onValueChange={field.onChange}>
            <SelectTrigger id={name} aria-invalid={fieldState.invalid}>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  )
}

// Usage - clean and consistent
function UserForm() {
  const form = useForm<UserFormValues>({ resolver: zodResolver(userSchema) })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FieldGroup>
        <TextField control={form.control} name="firstName" label="First Name" />
        <TextField control={form.control} name="lastName" label="Last Name" />
        <TextField control={form.control} name="email" label="Email" type="email" />
        <SelectField
          control={form.control}
          name="role"
          label="Role"
          options={roleOptions}
        />
      </FieldGroup>
    </form>
  )
}
```

Reference: [React Hook Form with TypeScript](https://react-hook-form.com/ts)
