#!/usr/bin/env python3
"""
Scaffold a production-ready Expo React Native app.

This script creates a complete Expo mobile app with:
- Expo Router for file-based navigation
- Optional Better Auth authentication (Expo client, tokens in SecureStore)
- TypeScript with strict mode
- Biome linting
- Working screens and components

Usage:
  python3 init-expo.py --root ~/www/myapp --name "My App"
  python3 init-expo.py --root ~/www/myapp --name "Fitness" --tabs "Home,Workouts,Profile" --auth
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass


# Pins follow Expo SDK 57 (bundledNativeModules.json of expo 57.0.26) so `expo install --check`
# stays clean. Looked up with `npm view <pkg> version` on 2026-10-06.
SDK_PINS = {
    "expo": "57.0.26",
    "expo-router": "57.0.24",
    "expo-status-bar": "57.0.1",
    "expo-constants": "57.0.20",
    "expo-linking": "57.0.11",
    "expo-secure-store": "57.0.4",
    "expo-network": "57.0.2",
    "expo-web-browser": "57.0.3",
    "react": "19.2.3",
    "react-native": "0.86.3",
    "react-native-safe-area-context": "5.7.0",
    "react-native-screens": "4.26.2",
    "react-native-svg": "15.15.4",
}

# Not part of the Expo SDK bundle; newest stable releases.
EXTRA_PINS = {
    "lucide-react-native": "1.52.0",
    "better-auth": "1.7.7",
    "@better-auth/expo": "1.7.7",
    "@types/react": "19.2.18",
    "typescript": "6.0.3",
    "@biomejs/biome": "2.5.15",
}


@dataclass
class ScreenConfig:
    """Configuration for a screen to be generated."""
    name: str  # e.g., "Home"
    icon: str = "Home"  # Lucide icon name

    @property
    def pascal_case(self) -> str:
        return self.name[0].upper() + self.name[1:]

    @property
    def kebab_case(self) -> str:
        return self.name.lower().replace(" ", "-")

    @property
    def file_name(self) -> str:
        if self.name.lower() == "home":
            return "index"
        return self.kebab_case


# =============================================================================
# PACKAGE.JSON AND CONFIG TEMPLATES
# =============================================================================

def slugify(name: str) -> str:
    return name.lower().replace(" ", "-")


def create_package_json(name: str, with_auth: bool) -> str:
    slug = slugify(name)
    deps = {
        **{key: SDK_PINS[key] for key in (
            "expo",
            "expo-router",
            "expo-status-bar",
            "expo-constants",
            "expo-linking",
            "react",
            "react-native",
            "react-native-safe-area-context",
            "react-native-screens",
            "react-native-svg",
        )},
        "lucide-react-native": EXTRA_PINS["lucide-react-native"],
    }

    if with_auth:
        # expo-network and expo-web-browser are peers of @better-auth/expo
        for key in ("expo-secure-store", "expo-network", "expo-web-browser"):
            deps[key] = SDK_PINS[key]
        deps["better-auth"] = EXTRA_PINS["better-auth"]
        deps["@better-auth/expo"] = EXTRA_PINS["@better-auth/expo"]

    return json.dumps({
        "name": slug,
        "version": "1.0.0",
        "main": "expo-router/entry",
        "scripts": {
            "start": "expo start",
            "android": "expo start --android",
            "ios": "expo start --ios",
            "web": "expo start --web",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "typecheck": "tsc --noEmit"
        },
        "dependencies": deps,
        "devDependencies": {
            "@types/react": EXTRA_PINS["@types/react"],
            "typescript": EXTRA_PINS["typescript"],
            "@biomejs/biome": EXTRA_PINS["@biomejs/biome"]
        }
    }, indent=2)


def create_app_json(name: str) -> str:
    slug = name.lower().replace(" ", "-")
    return json.dumps({
        "expo": {
            "name": name,
            "slug": slug,
            "version": "1.0.0",
            "scheme": slug,
            "platforms": ["ios", "android"],
            "ios": {
                "supportsTablet": True,
                "bundleIdentifier": f"com.{slug.replace('-', '')}.app"
            },
            "android": {
                "package": f"com.{slug.replace('-', '')}.app"
            },
            "experiments": {
                "typedRoutes": True
            }
        }
    }, indent=2)


def create_tsconfig() -> str:
    return json.dumps({
        "extends": "expo/tsconfig.base",
        "compilerOptions": {
            "strict": True,
            "paths": {
                "@/*": ["./*"]
            }
        },
        "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"]
    }, indent=2)


def create_biome_config() -> str:
    return json.dumps({
        "$schema": f"https://biomejs.dev/schemas/{EXTRA_PINS['@biomejs/biome']}/schema.json",
        "assist": {
            "actions": {
                "source": {"organizeImports": "on"}
            }
        },
        "files": {
            "ignoreUnknown": True,
            "includes": ["**", "!**/node_modules", "!**/.expo", "!**/dist", "!**/expo-env.d.ts", "!**/bun.lock"]
        },
        "formatter": {
            "enabled": True,
            "indentStyle": "space",
            "indentWidth": 2,
            "lineWidth": 100
        },
        "linter": {
            "enabled": True,
            "rules": {
                "preset": "recommended"
            }
        },
        "javascript": {
            "formatter": {
                "quoteStyle": "double",
                "semicolons": "always",
                "trailingCommas": "es5"
            }
        }
    }, indent=2)


def create_env_example(with_auth: bool) -> str:
    content = "# API\nEXPO_PUBLIC_API_URL=http://localhost:3001\n"
    if with_auth:
        content += (
            "\n# Better Auth runs inside the API (default base path /api/auth).\n"
            "# The API needs the @better-auth/expo plugin and this app's scheme in trustedOrigins.\n"
        )
    return content


def create_gitignore() -> str:
    return dedent("""\
        # Dependencies
        node_modules/

        # Expo
        .expo/
        dist/
        web-build/

        # Native
        *.orig.*
        *.jks
        *.p8
        *.p12
        *.key
        *.mobileprovision

        # Environment
        .env
        .env.local
        .env.*.local

        # OS
        .DS_Store
        Thumbs.db

        # IDE
        .idea/
        .vscode/
    """)


# =============================================================================
# ROOT LAYOUT
# =============================================================================

def create_root_layout(with_auth: bool) -> str:
    if with_auth:
        return dedent("""\
            import { Stack } from "expo-router";
            import { StatusBar } from "expo-status-bar";
            import { authClient } from "@/lib/auth-client";

            export default function RootLayout() {
              const { data: session, isPending } = authClient.useSession();

              // Wait for the cached session so signed-in users do not flash the sign-in screen
              if (isPending) {
                return null;
              }

              return (
                <>
                  <Stack screenOptions={{ headerShown: false }}>
                    <Stack.Protected guard={!!session}>
                      <Stack.Screen name="(tabs)" />
                    </Stack.Protected>
                    <Stack.Protected guard={!session}>
                      <Stack.Screen name="(auth)" />
                    </Stack.Protected>
                  </Stack>
                  <StatusBar style="auto" />
                </>
              );
            }
        """)
    else:
        return dedent("""\
            import { Stack } from "expo-router";
            import { StatusBar } from "expo-status-bar";

            export default function RootLayout() {
              return (
                <>
                  <Stack>
                    <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                  </Stack>
                  <StatusBar style="auto" />
                </>
              );
            }
        """)


def create_auth_client(slug: str) -> str:
    return dedent(f"""\
        import {{ expoClient }} from "@better-auth/expo/client";
        import {{ createAuthClient }} from "better-auth/react";
        import * as SecureStore from "expo-secure-store";

        // Better Auth runs inside the API (default base path /api/auth). The session cookie is
        // kept in SecureStore by the Expo client plugin, so there is no provider to mount.
        export const authClient = createAuthClient({{
          baseURL: process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:3001",
          plugins: [
            expoClient({{
              scheme: "{slug}",
              storagePrefix: "{slug}",
              storage: SecureStore,
            }}),
          ],
        }});
    """)


# =============================================================================
# TAB NAVIGATOR
# =============================================================================

def create_tab_layout(screens: list[ScreenConfig]) -> str:
    imports = ["import { Tabs } from \"expo-router\";"]
    icon_imports = ", ".join(s.icon for s in screens)
    imports.append(f'import {{ {icon_imports} }} from "lucide-react-native";')

    tabs = []
    for screen in screens:
        tabs.append(f"""\
      <Tabs.Screen
        name="{screen.file_name}"
        options={{{{
          title: "{screen.pascal_case}",
          tabBarIcon: ({{ color, size }}) => <{screen.icon} size={{size}} color={{color}} />,
        }}}}
      />""")

    tabs_str = "\n".join(tabs)

    return dedent(f"""\
        {chr(10).join(imports)}

        export default function TabLayout() {{
          return (
            <Tabs
              screenOptions={{{{
                tabBarActiveTintColor: "#3b82f6",
                tabBarInactiveTintColor: "#9ca3af",
                tabBarStyle: {{ backgroundColor: "#0f172a" }},
                headerStyle: {{ backgroundColor: "#0f172a" }},
                headerTintColor: "#fff",
              }}}}
            >
        {tabs_str}
            </Tabs>
          );
        }}
    """)


def create_screen_component(screen: ScreenConfig) -> str:
    return dedent(f"""\
        import {{ View, Text, StyleSheet }} from "react-native";
        import {{ SafeContainer }} from "@/components/layout/SafeContainer";

        export default function {screen.pascal_case}Screen() {{
          return (
            <SafeContainer>
              <View style={{styles.container}}>
                <Text style={{styles.title}}>{screen.pascal_case}</Text>
                <Text style={{styles.subtitle}}>This is the {screen.name.lower()} screen.</Text>
              </View>
            </SafeContainer>
          );
        }}

        const styles = StyleSheet.create({{
          container: {{
            flex: 1,
            padding: 20,
          }},
          title: {{
            fontSize: 28,
            fontWeight: "bold",
            color: "#fff",
            marginBottom: 8,
          }},
          subtitle: {{
            fontSize: 16,
            color: "#9ca3af",
          }},
        }});
    """)


# =============================================================================
# AUTH SCREENS
# =============================================================================

def create_auth_layout() -> str:
    return dedent("""\
        import { Stack } from "expo-router";

        export default function AuthLayout() {
          return (
            <Stack
              screenOptions={{
                headerStyle: { backgroundColor: "#0f172a" },
                headerTintColor: "#fff",
              }}
            >
              <Stack.Screen name="sign-in" options={{ title: "Sign In" }} />
              <Stack.Screen name="sign-up" options={{ title: "Sign Up" }} />
            </Stack>
          );
        }
    """)


def create_sign_in_screen() -> str:
    return dedent("""\
        import { View, Text, TextInput, Pressable, StyleSheet } from "react-native";
        import { useState } from "react";
        import { useRouter } from "expo-router";
        import { SafeContainer } from "@/components/layout/SafeContainer";
        import { authClient } from "@/lib/auth-client";

        export default function SignInScreen() {
          const router = useRouter();
          const [email, setEmail] = useState("");
          const [password, setPassword] = useState("");
          const [error, setError] = useState("");

          // A successful sign-in updates the session, and the root layout swaps to the tabs.
          const handleSignIn = async () => {
            const { error: signInError } = await authClient.signIn.email({ email, password });
            setError(signInError?.message ?? "");
          };

          return (
            <SafeContainer>
              <View style={styles.container}>
                <Text style={styles.title}>Welcome Back</Text>

                {error ? <Text style={styles.error}>{error}</Text> : null}

                <TextInput
                  style={styles.input}
                  placeholder="Email"
                  placeholderTextColor="#9ca3af"
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                />

                <TextInput
                  style={styles.input}
                  placeholder="Password"
                  placeholderTextColor="#9ca3af"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                />

                <Pressable style={styles.button} onPress={handleSignIn}>
                  <Text style={styles.buttonText}>Sign In</Text>
                </Pressable>

                <Pressable onPress={() => router.push("/(auth)/sign-up")}>
                  <Text style={styles.link}>Don't have an account? Sign Up</Text>
                </Pressable>
              </View>
            </SafeContainer>
          );
        }

        const styles = StyleSheet.create({
          container: {
            flex: 1,
            padding: 20,
            justifyContent: "center",
          },
          title: {
            fontSize: 28,
            fontWeight: "bold",
            color: "#fff",
            marginBottom: 24,
            textAlign: "center",
          },
          input: {
            backgroundColor: "#1e293b",
            color: "#fff",
            padding: 16,
            borderRadius: 8,
            marginBottom: 12,
            fontSize: 16,
          },
          button: {
            backgroundColor: "#3b82f6",
            padding: 16,
            borderRadius: 8,
            alignItems: "center",
            marginTop: 8,
          },
          buttonText: {
            color: "#fff",
            fontSize: 16,
            fontWeight: "600",
          },
          link: {
            color: "#3b82f6",
            textAlign: "center",
            marginTop: 16,
          },
          error: {
            color: "#ef4444",
            marginBottom: 12,
            textAlign: "center",
          },
        });
    """)


def create_sign_up_screen() -> str:
    return dedent("""\
        import { View, Text, TextInput, Pressable, StyleSheet } from "react-native";
        import { useState } from "react";
        import { useRouter } from "expo-router";
        import { SafeContainer } from "@/components/layout/SafeContainer";
        import { authClient } from "@/lib/auth-client";

        export default function SignUpScreen() {
          const router = useRouter();
          const [name, setName] = useState("");
          const [email, setEmail] = useState("");
          const [password, setPassword] = useState("");
          const [error, setError] = useState("");

          // A successful sign-up opens a session, and the root layout swaps to the tabs.
          const handleSignUp = async () => {
            const { error: signUpError } = await authClient.signUp.email({ name, email, password });
            setError(signUpError?.message ?? "");
          };

          return (
            <SafeContainer>
              <View style={styles.container}>
                <Text style={styles.title}>Create Account</Text>

                {error ? <Text style={styles.error}>{error}</Text> : null}

                <TextInput
                  style={styles.input}
                  placeholder="Name"
                  placeholderTextColor="#9ca3af"
                  value={name}
                  onChangeText={setName}
                />

                <TextInput
                  style={styles.input}
                  placeholder="Email"
                  placeholderTextColor="#9ca3af"
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                />

                <TextInput
                  style={styles.input}
                  placeholder="Password"
                  placeholderTextColor="#9ca3af"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                />

                <Pressable style={styles.button} onPress={handleSignUp}>
                  <Text style={styles.buttonText}>Sign Up</Text>
                </Pressable>

                <Pressable onPress={() => router.push("/(auth)/sign-in")}>
                  <Text style={styles.link}>Already have an account? Sign In</Text>
                </Pressable>
              </View>
            </SafeContainer>
          );
        }

        const styles = StyleSheet.create({
          container: {
            flex: 1,
            padding: 20,
            justifyContent: "center",
          },
          title: {
            fontSize: 28,
            fontWeight: "bold",
            color: "#fff",
            marginBottom: 24,
            textAlign: "center",
          },
          input: {
            backgroundColor: "#1e293b",
            color: "#fff",
            padding: 16,
            borderRadius: 8,
            marginBottom: 12,
            fontSize: 16,
          },
          button: {
            backgroundColor: "#3b82f6",
            padding: 16,
            borderRadius: 8,
            alignItems: "center",
            marginTop: 8,
          },
          buttonText: {
            color: "#fff",
            fontSize: 16,
            fontWeight: "600",
          },
          link: {
            color: "#3b82f6",
            textAlign: "center",
            marginTop: 16,
          },
          error: {
            color: "#ef4444",
            marginBottom: 12,
            textAlign: "center",
          },
        });
    """)


# =============================================================================
# UI COMPONENTS
# =============================================================================

def create_safe_container() -> str:
    return dedent("""\
        import { SafeAreaView, StyleSheet, ViewStyle } from "react-native";
        import { ReactNode } from "react";

        interface Props {
          children: ReactNode;
          style?: ViewStyle;
        }

        export function SafeContainer({ children, style }: Props) {
          return (
            <SafeAreaView style={[styles.container, style]}>
              {children}
            </SafeAreaView>
          );
        }

        const styles = StyleSheet.create({
          container: {
            flex: 1,
            backgroundColor: "#0f172a",
          },
        });
    """)


def create_button_component() -> str:
    return dedent("""\
        import { Pressable, Text, StyleSheet, ViewStyle } from "react-native";
        import { ReactNode } from "react";

        interface Props {
          children: ReactNode;
          onPress: () => void;
          variant?: "primary" | "secondary" | "ghost";
          style?: ViewStyle;
        }

        export function Button({ children, onPress, variant = "primary", style }: Props) {
          return (
            <Pressable
              style={[styles.button, styles[variant], style]}
              onPress={onPress}
            >
              <Text style={[styles.text, variant === "ghost" && styles.ghostText]}>
                {children}
              </Text>
            </Pressable>
          );
        }

        const styles = StyleSheet.create({
          button: {
            padding: 16,
            borderRadius: 8,
            alignItems: "center",
          },
          primary: {
            backgroundColor: "#3b82f6",
          },
          secondary: {
            backgroundColor: "#1e293b",
          },
          ghost: {
            backgroundColor: "transparent",
          },
          text: {
            color: "#fff",
            fontSize: 16,
            fontWeight: "600",
          },
          ghostText: {
            color: "#3b82f6",
          },
        });
    """)


def create_input_component() -> str:
    return dedent("""\
        import { TextInput, StyleSheet, TextInputProps } from "react-native";

        interface Props extends TextInputProps {
          // Add custom props here
        }

        export function Input(props: Props) {
          return (
            <TextInput
              style={styles.input}
              placeholderTextColor="#9ca3af"
              {...props}
            />
          );
        }

        const styles = StyleSheet.create({
          input: {
            backgroundColor: "#1e293b",
            color: "#fff",
            padding: 16,
            borderRadius: 8,
            fontSize: 16,
          },
        });
    """)


def create_card_component() -> str:
    return dedent("""\
        import { View, StyleSheet, ViewStyle } from "react-native";
        import { ReactNode } from "react";

        interface Props {
          children: ReactNode;
          style?: ViewStyle;
        }

        export function Card({ children, style }: Props) {
          return (
            <View style={[styles.card, style]}>
              {children}
            </View>
          );
        }

        const styles = StyleSheet.create({
          card: {
            backgroundColor: "#1e293b",
            borderRadius: 12,
            padding: 16,
          },
        });
    """)


# =============================================================================
# LIB FILES
# =============================================================================

API_CLIENT_BODY = """\
export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  patch: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  delete: <T>(endpoint: string) => request<T>(endpoint, { method: "DELETE" }),
};
"""


def create_api_client(with_auth: bool) -> str:
    if with_auth:
        head = dedent("""\
            import { authClient } from "@/lib/auth-client";

            const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:3001";

            async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
              // Better Auth keeps the session cookie in SecureStore; send it explicitly on native
              const cookie = await authClient.getCookie();

              const response = await fetch(`${API_URL}${endpoint}`, {
                ...options,
                // "include" would override the Cookie header set below
                credentials: "omit",
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
        """)
    else:
        head = dedent("""\
            const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:3001";

            async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
              const response = await fetch(`${API_URL}${endpoint}`, {
                ...options,
                headers: {
                  "Content-Type": "application/json",
                  ...options.headers,
                },
              });

              if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
              }

              return response.json();
            }
        """)
    return f"{head}\n{API_CLIENT_BODY}"


def create_types_index() -> str:
    return dedent("""\
        // Add your TypeScript types here

        // Mirrors the Better Auth user returned by authClient.useSession()
        export interface User {
          id: string;
          email: string;
          name: string;
          createdAt: string;
          updatedAt: string;
        }

        // Example entity type
        export interface Entity {
          _id: string;
          title: string;
          description?: string;
          userId: string;
          createdAt: string;
          updatedAt: string;
        }
    """)


# =============================================================================
# MAIN SCAFFOLD FUNCTION
# =============================================================================

def scaffold_expo_app(
    root: Path,
    name: str,
    screens: list[ScreenConfig],
    with_auth: bool,
    allow_outside: bool,
) -> None:
    """Create the full Expo app structure."""

    cwd = Path.cwd()
    if not allow_outside and not root.is_relative_to(cwd):
        print(f"Error: Target path {root} is outside current directory.")
        print("Use --allow-outside to confirm this is intentional.")
        sys.exit(1)

    if root.exists():
        print(f"Error: {root} already exists.")
        sys.exit(1)

    print(f"Creating Expo app at {root}...")
    print(f"Screens: {', '.join(s.name for s in screens)}")
    print(f"Auth: {'Yes' if with_auth else 'No'}")

    # Create directories
    dirs = [
        root,
        root / ".agents",
        root / "app" / "(tabs)",
        root / "components" / "layout",
        root / "components" / "ui",
        root / "lib",
        root / "types",
    ]

    if with_auth:
        dirs.extend([
            root / "app" / "(auth)",
        ])

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Base files
    files = {
        root / "package.json": create_package_json(name, with_auth),
        root / "app.json": create_app_json(name),
        root / "tsconfig.json": create_tsconfig(),
        root / "biome.json": create_biome_config(),
        root / ".env.example": create_env_example(with_auth),
        root / ".gitignore": create_gitignore(),

        # Root layout
        root / "app" / "_layout.tsx": create_root_layout(with_auth),

        # Tab navigator
        root / "app" / "(tabs)" / "_layout.tsx": create_tab_layout(screens),

        # Components
        root / "components" / "layout" / "SafeContainer.tsx": create_safe_container(),
        root / "components" / "ui" / "Button.tsx": create_button_component(),
        root / "components" / "ui" / "Input.tsx": create_input_component(),
        root / "components" / "ui" / "Card.tsx": create_card_component(),

        # Lib
        root / "lib" / "api.ts": create_api_client(with_auth),

        # Types
        root / "types" / "index.ts": create_types_index(),
    }

    # Screen files
    for screen in screens:
        files[root / "app" / "(tabs)" / f"{screen.file_name}.tsx"] = create_screen_component(screen)

    # Auth files
    if with_auth:
        files[root / "lib" / "auth-client.ts"] = create_auth_client(slugify(name))
        files[root / "app" / "(auth)" / "_layout.tsx"] = create_auth_layout()
        files[root / "app" / "(auth)" / "sign-in.tsx"] = create_sign_in_screen()
        files[root / "app" / "(auth)" / "sign-up.tsx"] = create_sign_up_screen()

    # Write all files
    for filepath, content in files.items():
        filepath.write_text(content)
        print(f"Created: {filepath.relative_to(root)}")

    print(f"\n✅ Expo app created at: {root}")
    print(f"\nNext steps:")
    print(f"1. cd {root}")
    print(f"2. bun install")
    if with_auth:
        print(f"3. Copy .env.example to .env and point EXPO_PUBLIC_API_URL at your API")
        print(f"4. Add the @better-auth/expo plugin and the '{slugify(name)}://' scheme to the API's")
        print(f"   Better Auth config (plugins + trustedOrigins)")
        print(f"5. bun start")
    else:
        print(f"3. bun start")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a production-ready Expo React Native app."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Directory to create the app in",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="App name",
    )
    parser.add_argument(
        "--tabs",
        type=str,
        default="Home,Settings",
        help="Comma-separated list of tab names (default: 'Home,Settings')",
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Include Better Auth authentication (Expo client)",
    )
    parser.add_argument(
        "--allow-outside",
        action="store_true",
        help="Allow creating files outside current directory",
    )

    args = parser.parse_args()

    # Parse screens with default icons
    icon_map = {
        "home": "Home",
        "settings": "Settings",
        "profile": "User",
        "search": "Search",
        "workouts": "Dumbbell",
        "explore": "Compass",
        "favorites": "Heart",
        "notifications": "Bell",
        "messages": "MessageCircle",
        "calendar": "Calendar",
    }

    screens = []
    for tab_name in args.tabs.split(","):
        tab_name = tab_name.strip()
        icon = icon_map.get(tab_name.lower(), "Circle")
        screens.append(ScreenConfig(name=tab_name, icon=icon))

    scaffold_expo_app(
        root=args.root.resolve(),
        name=args.name,
        screens=screens,
        with_auth=args.auth,
        allow_outside=args.allow_outside,
    )


if __name__ == "__main__":
    main()
