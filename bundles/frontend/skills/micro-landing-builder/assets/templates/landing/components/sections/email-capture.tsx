"use client"

import { useId, useState, type FormEvent } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface EmailCaptureProps {
  placeholder?: string
  buttonText?: string
}

type Status = "idle" | "loading" | "done" | "error"

export function EmailCapture({
  placeholder = "Enter your email",
  buttonText = "Join Waitlist",
}: EmailCaptureProps) {
  const inputId = useId()
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const email = String(new FormData(event.currentTarget).get("email") ?? "")
    setStatus("loading")
    try {
      const response = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      })
      const body = (await response.json()) as { message?: string }
      setMessage(body.message ?? "")
      setStatus(response.ok ? "done" : "error")
    } catch {
      setMessage("Network error. Please try again.")
      setStatus("error")
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex w-full max-w-md flex-col gap-2">
      <div className="flex gap-2">
        <label htmlFor={inputId} className="sr-only">
          Email address
        </label>
        <Input
          id={inputId}
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder={placeholder}
          className="h-9"
        />
        <Button type="submit" size="lg" disabled={status === "loading" || status === "done"}>
          {buttonText}
        </Button>
      </div>
      <p
        role="status"
        className={status === "error" ? "text-sm text-destructive" : "text-sm text-muted-foreground"}
      >
        {message}
      </p>
    </form>
  )
}
