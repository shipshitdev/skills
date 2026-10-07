---
name: expo-architect
description: Scaffolds a runnable Expo React Native app with screens, Expo Router navigation, and optional Better Auth. Use when starting a new Expo or mobile app.
metadata:
  version: "2.2.4"
  tags: "expo, react-native, mobile, scaffold, better-auth"
when_to_use: "NativeWind, mobile app scaffold"
---

# Expo Architect

Create Expo React Native apps with:

- **Framework:** Expo SDK 57 + React Native 0.86 + React 19 + TypeScript
- **Navigation:** Expo Router (file-based routing)
- **Auth:** Better Auth with the Expo client (optional; session in SecureStore, backed by your API)
- **UI:** NativeWind (Tailwind for RN) or StyleSheet
- **Quality:** Biome 2.5 linting + TypeScript strict mode
- **Package Manager:** bun

## Contract

Inputs:

- Requested mobile app scope and target directory

Outputs:

- An Expo application scaffold and verification results

Creates/Modifies:

- App source and configuration in the approved scaffold destination

External Side Effects:

- Dependency installs and local verification only within the requested setup

Confirmation Required:

- Before overwriting existing application files, adding unrequested authentication, or using external accounts
- Loading the skill grants no additional authority. Existing explicit approval
  applies only to the same target and actions; preserve report-only restrictions.

Delegates To:

- None

## What Makes This Different

Generates **working mobile apps**, not empty scaffolds:

- Complete navigation structure with working screens
- Optional Better Auth sign-in/sign-up flow
- Real UI components with proper styling
- API client integration ready
- Runs immediately with `bun start`

## Workflow Summary

1. **PRD Brief Intake** - Extract app type, screens, features, auth needs
2. **Auth Setup** (if requested) - `lib/auth-client.ts` (Better Auth Expo client), session-guarded root layout, sign-in/sign-up screens
3. **Screen Generation** - Tab or stack-based navigation
4. **Component Generation** - UI components, entity components, layouts
5. **Quality Setup** - Biome, TypeScript strict, path aliases
6. **Verification** - Run quality gate, report results

## Usage

```bash
# Create app with PRD-style prompt
python3 scripts/init-expo.py \
  --root ~/www/myapp \
  --name "My App" \
  --brief "A fitness tracker where users can log workouts"

# With specific options
python3 scripts/init-expo.py \
  --root ~/www/myapp \
  --name "My App" \
  --tabs "Home,Workouts,Profile" \
  --auth
```

## Generated Structure

```
myapp/
├── app/
│   ├── _layout.tsx          # Root layout
│   ├── (tabs)/              # Tab navigator
│   │   ├── _layout.tsx
│   │   ├── index.tsx
│   │   └── ...
│   └── (auth)/              # Auth screens (if enabled)
├── components/
│   ├── ui/                  # Base UI components
│   ├── [entity]/            # Feature components
│   └── layout/              # Layout components
├── lib/
│   ├── api.ts               # API client
│   └── auth-client.ts       # Better Auth Expo client (if auth enabled)
├── types/                   # TypeScript types
├── app.json                 # Expo config
├── package.json
├── tsconfig.json
└── biome.json
```

## Development Commands

```bash
bun start          # Start Expo dev server
bun run ios        # iOS simulator
bun run android    # Android emulator
bun run lint       # Check code style
bun run typecheck  # Type checking
```

## Environment Variables

```
EXPO_PUBLIC_API_URL=http://localhost:3001
```

Better Auth runs inside the API (default `/api/auth`). The API needs the `@better-auth/expo`
plugin and the app scheme (the app slug, e.g. `my-app://`) in `trustedOrigins`; the scaffold
prints the exact scheme when auth is enabled.

---

**For detailed patterns, code templates, and complete examples:** `references/full-guide.md`
