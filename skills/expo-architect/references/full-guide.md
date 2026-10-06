# Expo Architect - Full Guide

Complete guide to scaffolding production-ready Expo React Native apps.

## Phase 1: PRD Brief Intake

**Ask the user for a brief product description**, then extract and confirm:

```
I'll help you build [App Name]. Based on your description, I understand:

**App Type:** [Tab-based / Stack-based / Drawer]

**Screens:**
- Home - [description]
- [Screen2] - [description]
- [Screen3] - [description]

**Features:**
- [Feature 1]
- [Feature 2]

**Auth Required:** Yes/No

**Backend API:** [URL or "none"]

Is this correct? Any adjustments?
```

## Phase 2: Auth Setup (If Requested)

Generate Better Auth authentication for mobile (Expo client plugin, email + password):

**Files:**

- `lib/auth-client.ts` - `createAuthClient` with `expoClient` (scheme, SecureStore storage)
- `app/(auth)/sign-in.tsx` - Sign in screen (`authClient.signIn.email`)
- `app/(auth)/sign-up.tsx` - Sign up screen (`authClient.signUp.email`)

**Packages:** `better-auth`, `@better-auth/expo`, `expo-secure-store`, `expo-network`,
`expo-web-browser` (`expo-linking` and `expo-constants` are already part of the base app).

**Environment:**

- `.env` with `EXPO_PUBLIC_API_URL` (Better Auth runs inside the API at `/api/auth`)

**API side:** add the `expo()` plugin from `@better-auth/expo` and the app scheme (for example
`my-app://`) to `trustedOrigins` in the API's Better Auth config. In development, Expo Go uses
the `exp://` scheme, which can be trusted only when `NODE_ENV` is `development`.

## Phase 3: Screen Generation

### Tab-based App Structure

```
app/
├── _layout.tsx              # Root layout with providers
├── (tabs)/
│   ├── _layout.tsx          # Tab navigator
│   ├── index.tsx            # Home tab
│   ├── [screen].tsx         # Other tabs
│   └── ...
├── (auth)/                  # Auth screens (if enabled)
│   ├── sign-in.tsx
│   └── sign-up.tsx
└── [entity]/
    └── [id].tsx             # Detail screens
```

### Stack-based App Structure

```
app/
├── _layout.tsx              # Root layout with providers
├── index.tsx                # Home screen
├── [screen].tsx             # Other screens
└── (auth)/                  # Auth screens (if enabled)
```

## Phase 4: Component Generation

```
components/
├── ui/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   └── Text.tsx
├── [entity]/
│   ├── [Entity]List.tsx
│   ├── [Entity]Item.tsx
│   └── [Entity]Form.tsx
└── layout/
    ├── Header.tsx
    └── SafeContainer.tsx
```

## Key Patterns

### Root Layout Pattern

```typescript
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { QueryProvider } from "@/providers/query-provider";
import { authClient } from "@/lib/auth-client";

export default function RootLayout() {
  // Better Auth needs no provider; the Expo client plugin caches the session in SecureStore
  const { data: session, isPending } = authClient.useSession();

  if (isPending) {
    return null;
  }

  return (
    <QueryProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Protected guard={!!session}>
          <Stack.Screen name="(tabs)" />
        </Stack.Protected>
        <Stack.Protected guard={!session}>
          <Stack.Screen name="(auth)" />
        </Stack.Protected>
      </Stack>
      <StatusBar style="auto" />
    </QueryProvider>
  );
}
```

### Tab Navigator Pattern

```typescript
import { Tabs } from "expo-router";
import { Home, Dumbbell, User } from "lucide-react-native";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#3b82f6",
        tabBarInactiveTintColor: "#9ca3af",
        tabBarStyle: { backgroundColor: "#0f172a" },
        headerStyle: { backgroundColor: "#0f172a" },
        headerTintColor: "#fff",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color, size }) => <Home size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="workouts"
        options={{
          title: "Workouts",
          tabBarIcon: ({ color, size }) => <Dumbbell size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => <User size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
```

### Screen Component Pattern

```typescript
import { View, Text, FlatList, StyleSheet } from "react-native";
import { useEffect, useState } from "react";
import { SafeContainer } from "@/components/layout/SafeContainer";
import { WorkoutItem } from "@/components/workout/WorkoutItem";
import { api } from "@/lib/api";
import type { Workout } from "@/types";

export default function WorkoutsScreen() {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.workouts.getAll()
      .then(setWorkouts)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <SafeContainer style={styles.center}>
        <Text>Loading...</Text>
      </SafeContainer>
    );
  }

  return (
    <SafeContainer>
      <FlatList
        data={workouts}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => <WorkoutItem workout={item} />}
        contentContainerStyle={styles.list}
      />
    </SafeContainer>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  list: { padding: 16, gap: 12 },
});
```

### API Client Pattern

```typescript
import { authClient } from "@/lib/auth-client";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:3001";

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Better Auth keeps the session cookie in SecureStore; send it explicitly on native
  const cookie = await authClient.getCookie();

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    credentials: "omit", // "include" would override the Cookie header
    headers: {
      "Content-Type": "application/json",
      ...(cookie ? { Cookie: cookie } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  workouts: {
    getAll: () => request<Workout[]>("/workouts"),
    getById: (id: string) => request<Workout>(`/workouts/${id}`),
    create: (data: Partial<Workout>) =>
      request<Workout>("/workouts", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Workout>) =>
      request<Workout>(`/workouts/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/workouts/${id}`, { method: "DELETE" }),
  },
};
```

## EAS Build Configuration

For production builds, create `eas.json`:

```json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  },
  "submit": {
    "production": {}
  }
}
```

## Quality Verification

Run quality gate and report results:

```
✅ Generation complete!

Quality Report:
- bun install: ✓ succeeded
- bun run lint: ✓ 0 errors
- TypeScript: ✓ no errors

Ready to run:
  cd [project]
  bun start
```
