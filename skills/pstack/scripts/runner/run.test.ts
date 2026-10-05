import { afterEach, beforeEach, describe, expect, it, spyOn } from "bun:test";
import * as fs from "node:fs";
import {
  chmodSync,
  cpSync,
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";
import { childEnvironment, runLane } from "./run.ts";
import { main } from "./cli.ts";
import type { Provider, RunnerOptions, RunnerReceipt } from "./types.ts";

let scratch = "";
let bin = "";
let previousPath: string | undefined;

function streamPath(path: string | null): string {
  if (path === null) throw new Error("expected a reserved stream artifact path");
  return path;
}

const fake = `#!/usr/bin/env bun
import { appendFileSync, existsSync, unlinkSync, writeFileSync } from "node:fs";
const args = process.argv.slice(2);
const name = process.argv[1].split("/").at(-1);
const isPreflight =
  (name === "claude" && args[0] === "auth") ||
  (name === "codex" && args[0] === "login") ||
  (name === "grok" && args[0] === "models");
const stage = isPreflight ? "preflight" : "model";
const startedPath = isPreflight
  ? process.env.FAKE_PREFLIGHT_STARTED_PATH
  : process.env.FAKE_MODEL_STARTED_PATH;
if (startedPath) writeFileSync(startedPath, String(process.pid));
const cancelStage = process.env.FAKE_CANCEL_STAGE ??
  (process.env.FAKE_CANCEL === "1" ? "model" : "");
if (cancelStage === stage) {
  const stop = (signal) => {
    writeFileSync(process.env.FAKE_TERMINATED_PATH, signal);
    if (process.env.FAKE_IGNORE_SIGNAL !== "1") process.exit(0);
  };
  process.on("SIGINT", () => stop("SIGINT"));
  process.on("SIGTERM", () => stop("SIGTERM"));
  writeFileSync(process.env.FAKE_STARTED_PATH, String(process.pid));
  await Bun.sleep(5_000);
}
const delay = Number(
  stage === "preflight"
    ? process.env.FAKE_PREFLIGHT_DELAY_MS ?? 0
    : process.env.FAKE_MODEL_DELAY_MS ?? 0
);
if (delay > 0) await Bun.sleep(delay);
if (process.env.FAKE_TIMEOUT === "1" && !args.includes("status") && !args.includes("models")) {
  await Bun.sleep(5_000);
}
if (name === "claude" && args[0] === "auth") {
  if (process.env.FAKE_REMOVE_EXECUTABLE_AFTER_PREFLIGHT === "1") {
    unlinkSync(process.argv[1]);
  }
  console.log(JSON.stringify({loggedIn:true}));
  process.exit(0);
}
if (name === "codex" && args[0] === "login") {
  console.log("Logged in using ChatGPT");
  process.exit(0);
}
if (name === "grok" && args[0] === "models") {
  if (process.env.FAKE_GROK_PREFLIGHT_LOG_PATH) {
    appendFileSync(process.env.FAKE_GROK_PREFLIGHT_LOG_PATH, "attempt\\n");
  }
  if (process.env.FAKE_GROK_PREFLIGHT_OUTPUT !== undefined) {
    console.log(process.env.FAKE_GROK_PREFLIGHT_OUTPUT);
    if (process.env.FAKE_GROK_PREFLIGHT_ERROR) console.error(process.env.FAKE_GROK_PREFLIGHT_ERROR);
    process.exit(0);
  }
  const transientMarker = process.env.FAKE_GROK_TRANSIENT_UNAUTH_PATH;
  if (transientMarker && !existsSync(transientMarker)) {
    writeFileSync(transientMarker, String(process.pid));
    console.log("Available models:\\n  * grok-4.6 (default)");
    console.error("You are not authenticated.");
    process.exit(0);
  }
  if (process.env.FAKE_GROK_MISSING_MODEL === "1") {
    console.log("You are logged in with grok.com.\\nAvailable models:\\n  * grok-4.5 (default)");
    process.exit(0);
  }
  if (process.env.FAKE_GROK_UNAUTH === "1") {
    console.error("Not logged in. Run grok auth login.");
    process.exit(1);
  }
  console.log("You are logged in with grok.com.\\nAvailable models:\\n  * grok-4.6 (default)");
  process.exit(0);
}
const modelIndex = args.findIndex((value) => value === "--model");
const model = modelIndex >= 0 ? args[modelIndex + 1] : "unknown";
const reportedModel = model === "fable"
  ? "claude-fable-9-9"
  : model === "opus"
    ? "claude-opus-9"
    : model;
if (process.env.FAKE_INVALID_MODEL === "1") {
  console.error("The requested model is not supported with this account.");
  process.exit(1);
}
if (stage === "model" && process.env.FAKE_DESCENDANT_HOLDS_PIPES_MS) {
  const seconds = Number(process.env.FAKE_DESCENDANT_HOLDS_PIPES_MS) / 1000;
  const descendant = Bun.spawn(["/bin/sh", "-c", "sleep " + seconds], {
    stdin: "ignore",
    stdout: "inherit",
    stderr: "inherit",
  });
  if (process.env.FAKE_DESCENDANT_PID_PATH) {
    writeFileSync(process.env.FAKE_DESCENDANT_PID_PATH, String(descendant.pid));
  }
  descendant.unref();
}
if (stage === "model" && process.env.FAKE_SELF_SIGNAL) {
  process.kill(process.pid, process.env.FAKE_SELF_SIGNAL);
  await Bun.sleep(5_000);
}
if (name === "claude") {
  console.log(JSON.stringify({result:"CLAUDE_OK",session_id:"c1",usage:{input_tokens:10,output_tokens:2},total_cost_usd:0.01,modelUsage:{[reportedModel]:{}}}));
} else if (name === "codex") {
  console.log(JSON.stringify({type:"thread.started",thread_id:"o1"}));
  console.log(JSON.stringify({type:"item.completed",item:{type:"agent_message",text:"CODEX_OK"}}));
  console.log(JSON.stringify({type:"turn.completed",usage:{input_tokens:20,cached_input_tokens:5,output_tokens:3,reasoning_output_tokens:1}}));
} else if (process.env.FAKE_GROK_ERROR_RESULT === "1") {
  console.log(JSON.stringify({type:"system",subtype:"init",skills:Array(500).fill("skill-name")}));
  console.log(JSON.stringify({type:"result",subtype:"error_during_execution",is_error:true,stop_reason:"cancelled",errors:["cancelled"]}));
} else {
  console.log(JSON.stringify({type:"assistant",message:{content:[{type:"text",text:"progress"}]}}));
  console.log(JSON.stringify({type:"result",subtype:"success",is_error:false,result:"GROK_OK",session_id:"g1",usage:{input_tokens:30,output_tokens:4,total_tokens:34},total_cost_usd:0.02,modelUsage:{[model + "-build"]:{}}}));
}
if (process.env.FAKE_MODEL_EXITING_PATH) {
  writeFileSync(process.env.FAKE_MODEL_EXITING_PATH, String(process.pid));
}
`;

function makeExecutable(name: string): void {
  const path = join(bin, name);
  writeFileSync(path, fake);
  chmodSync(path, 0o755);
}

function options(provider: Provider, suffix: string = provider): RunnerOptions {
  const parent = provider === "codex" ? "claude" : "codex";
  const model =
    provider === "claude"
      ? "fable"
      : provider === "codex"
        ? "gpt-5.6-sol"
        : "grok-4.6";
  return {
    parent,
    provider,
    model,
    effort: provider === "grok" ? "xhigh" : "max",
    mode: "read-only",
    promptPath: join(scratch, "prompt.md"),
    cwd: scratch,
    outputPath: join(scratch, `${suffix}.out`),
    receiptPath: join(scratch, `${suffix}.receipt.json`),
    timeoutMs: null,
  };
}

function receipt(path: string): RunnerReceipt {
  return JSON.parse(readFileSync(path, "utf8")) as RunnerReceipt;
}

function runnerArgs(input: RunnerOptions): string[] {
  const args = [
    join(import.meta.dir, "pstack-runner"),
    "--parent", input.parent,
    "--provider", input.provider,
    "--model", input.model,
    "--effort", input.effort,
    "--mode", input.mode,
    "--prompt", input.promptPath,
    "--cwd", input.cwd,
    "--output", input.outputPath,
    "--receipt", input.receiptPath,
  ];
  if (input.timeoutMs !== null) {
    args.push("--timeout", String(input.timeoutMs / 1_000));
  }
  return args;
}

async function waitFor(path: string): Promise<void> {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (existsSync(path)) return;
    await Bun.sleep(10);
  }
  throw new Error(`timed out waiting for ${path}`);
}

async function exitWithin(child: Bun.Subprocess, milliseconds: number): Promise<number> {
  const result = await Promise.race([
    child.exited,
    Bun.sleep(milliseconds).then(() => null),
  ]);
  if (result !== null) return result;
  child.kill("SIGKILL");
  await child.exited;
  throw new Error(`runner did not exit within ${milliseconds}ms`);
}

function processIsAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

async function waitForExit(pid: number): Promise<void> {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (!processIsAlive(pid)) return;
    await Bun.sleep(10);
  }
  throw new Error(`timed out waiting for process ${pid} to exit`);
}

beforeEach(() => {
  scratch = mkdtempSync(join(tmpdir(), "pstack-runner-test-"));
  bin = join(scratch, "bin");
  mkdirSync(bin);
  writeFileSync(join(scratch, "prompt.md"), "Return the marker.");
  for (const name of ["claude", "codex", "grok"]) makeExecutable(name);
  previousPath = process.env.PATH;
  process.env.PATH = `${bin}:${dirname(process.execPath)}:${previousPath ?? ""}`;
  delete process.env.FAKE_TIMEOUT;
  delete process.env.FAKE_INVALID_MODEL;
  delete process.env.FAKE_CANCEL;
  delete process.env.FAKE_CANCEL_STAGE;
  delete process.env.FAKE_IGNORE_SIGNAL;
  delete process.env.FAKE_PREFLIGHT_DELAY_MS;
  delete process.env.FAKE_MODEL_DELAY_MS;
  delete process.env.FAKE_STARTED_PATH;
  delete process.env.FAKE_TERMINATED_PATH;
  delete process.env.FAKE_PREFLIGHT_STARTED_PATH;
  delete process.env.FAKE_MODEL_STARTED_PATH;
  delete process.env.FAKE_MODEL_EXITING_PATH;
  delete process.env.FAKE_REMOVE_EXECUTABLE_AFTER_PREFLIGHT;
  delete process.env.FAKE_GROK_UNAUTH;
  delete process.env.FAKE_GROK_PREFLIGHT_OUTPUT;
  delete process.env.FAKE_GROK_PREFLIGHT_ERROR;
  delete process.env.FAKE_GROK_TRANSIENT_UNAUTH_PATH;
  delete process.env.FAKE_GROK_PREFLIGHT_LOG_PATH;
  delete process.env.FAKE_GROK_MISSING_MODEL;
  delete process.env.FAKE_DESCENDANT_HOLDS_PIPES_MS;
  delete process.env.FAKE_DESCENDANT_PID_PATH;
  delete process.env.FAKE_SELF_SIGNAL;
  delete process.env.FAKE_GROK_ERROR_RESULT;
});

afterEach(() => {
  process.env.PATH = previousPath;
  delete process.env.FAKE_TIMEOUT;
  delete process.env.FAKE_INVALID_MODEL;
  delete process.env.FAKE_CANCEL;
  delete process.env.FAKE_CANCEL_STAGE;
  delete process.env.FAKE_IGNORE_SIGNAL;
  delete process.env.FAKE_PREFLIGHT_DELAY_MS;
  delete process.env.FAKE_MODEL_DELAY_MS;
  delete process.env.FAKE_STARTED_PATH;
  delete process.env.FAKE_TERMINATED_PATH;
  delete process.env.FAKE_PREFLIGHT_STARTED_PATH;
  delete process.env.FAKE_MODEL_STARTED_PATH;
  delete process.env.FAKE_MODEL_EXITING_PATH;
  delete process.env.FAKE_REMOVE_EXECUTABLE_AFTER_PREFLIGHT;
  delete process.env.FAKE_GROK_UNAUTH;
  delete process.env.FAKE_GROK_PREFLIGHT_OUTPUT;
  delete process.env.FAKE_GROK_PREFLIGHT_ERROR;
  delete process.env.FAKE_GROK_TRANSIENT_UNAUTH_PATH;
  delete process.env.FAKE_GROK_PREFLIGHT_LOG_PATH;
  delete process.env.FAKE_GROK_MISSING_MODEL;
  delete process.env.FAKE_DESCENDANT_HOLDS_PIPES_MS;
  delete process.env.FAKE_DESCENDANT_PID_PATH;
  delete process.env.FAKE_SELF_SIGNAL;
  delete process.env.FAKE_GROK_ERROR_RESULT;
  rmSync(scratch, { recursive: true, force: true });
});

describe("Codex parent sandbox diagnostics", () => {
  let previousNetworkDisabled: string | undefined;

  beforeEach(() => {
    previousNetworkDisabled = process.env.CODEX_SANDBOX_NETWORK_DISABLED;
    delete process.env.CODEX_SANDBOX_NETWORK_DISABLED;
  });

  afterEach(() => {
    if (previousNetworkDisabled === undefined) {
      delete process.env.CODEX_SANDBOX_NETWORK_DISABLED;
    } else {
      process.env.CODEX_SANDBOX_NETWORK_DISABLED = previousNetworkDisabled;
    }
  });

  it("names likely Codex sandbox cause after child failure", async () => {
    process.env.CODEX_SANDBOX_NETWORK_DISABLED = "1";
    const invoked = join(scratch, "model-invoked.json");
    writeFileSync(join(bin, "claude"), `#!/usr/bin/env bun
import { writeFileSync } from "node:fs";
if (process.argv[2] === "auth") {
  console.log(JSON.stringify({ loggedIn: true }));
  process.exit(0);
}
writeFileSync(${JSON.stringify(invoked)}, JSON.stringify({
  argv: process.argv.slice(2),
  networkDisabled: process.env.CODEX_SANDBOX_NETWORK_DISABLED ?? null,
}));
console.error("ENOTFOUND api.anthropic.com");
process.exit(1);
`);
    const input = options("claude");
    const result = await runLane(input);
    const saved = receipt(input.receiptPath);
    expect(JSON.parse(readFileSync(invoked, "utf8"))).toMatchObject({
      argv: expect.arrayContaining(["--model", "fable"]),
      networkDisabled: null,
    });
    expect(result.exitCode).toBe(70);
    expect(saved.status).toBe("child-failed");
    expect(saved.exitCode).toBe(1);
    expect(saved.preflight.status).toBe("passed");
    expect(saved.error?.message).toContain("child exited with status 1");
    expect(saved.error?.message).toContain("likely cause: Codex parent sandbox has network disabled");
    expect(saved.error?.evidence).toStartWith("likely cause: Codex parent sandbox has network disabled");
    expect(saved.error?.evidence).toContain("ENOTFOUND api.anthropic.com");
    expect(saved.error?.message).toContain("provider-dispatch.md#host-and-parent-prerequisites");
    expect(saved.schemaVersion).toBe(1);
    expect(saved.model).toBe(input.model);
    expect(saved.effort).toBe(input.effort);
    expect(readFileSync(streamPath(saved.stderrPath), "utf8")).toBe("ENOTFOUND api.anthropic.com\n");
    expect(existsSync(input.outputPath)).toBe(false);
  });

  for (const marker of [undefined, "0", "true"]) {
    it(`does not infer blocked network from marker ${marker}`, async () => {
      if (marker !== undefined) process.env.CODEX_SANDBOX_NETWORK_DISABLED = marker;
      writeFileSync(join(bin, "claude"), `#!/usr/bin/env bun
if (process.argv[2] === "auth") {
  console.log(JSON.stringify({ loggedIn: true }));
  process.exit(0);
}
console.error("ENOTFOUND api.anthropic.com; EACCES local-state");
process.exit(1);
`);
      const result = await runLane(options("claude"));
      expect(result.exitCode).toBe(70);
      expect(result.receipt.error).toEqual({
        message: "child exited with status 1",
        evidence: "ENOTFOUND api.anthropic.com; EACCES local-state",
      });
    });
  }

  it("does not blame a Claude parent even with the network marker", async () => {
    process.env.CODEX_SANDBOX_NETWORK_DISABLED = "1";
    writeFileSync(join(bin, "grok"), `#!/usr/bin/env bun
if (process.argv[2] === "models") {
  console.log("You are logged in with grok.com.\\nAvailable models:\\n  * grok-4.6 (default)");
  process.exit(0);
}
console.error("ENOTFOUND grok.com");
process.exit(1);
`);
    const result = await runLane({ ...options("grok"), parent: "claude" });
    expect(result.exitCode).toBe(70);
    expect(result.receipt.error).toEqual({
      message: "child exited with status 1",
      evidence: "ENOTFOUND grok.com",
    });
  });

  it("puts the hint ahead of bounded evidence without changing raw sidecars", async () => {
    process.env.CODEX_SANDBOX_NETWORK_DISABLED = "1";
    const stderr = "startup warning\n".repeat(400) + "EACCES ~/.grok/managed_config.toml\n";
    writeFileSync(join(bin, "grok"), `#!/usr/bin/env bun
if (process.argv[2] === "models") {
  console.log("You are logged in with grok.com.\\nAvailable models:\\n  * grok-4.6 (default)");
  process.exit(0);
}
process.stderr.write(${JSON.stringify(stderr)});
process.exit(1);
`);
    const input = { ...options("grok"), parent: "codex" as const };
    const result = await runLane(input);
    expect(result.exitCode).toBe(70);
    expect(result.receipt.status).toBe("child-failed");
    expect(result.receipt.error?.evidence).toStartWith("likely cause: Codex parent sandbox has network disabled");
    expect(result.receipt.error?.evidence?.length).toBe(4_000);
    expect(readFileSync(streamPath(result.receipt.stderrPath), "utf8")).toBe(stderr);
  });

  for (const scenario of ["api-error", "cancelled"]) {
    it(`preserves provider-reported ${scenario} ahead of any sandbox hint`, async () => {
      process.env.CODEX_SANDBOX_NETWORK_DISABLED = "1";
      const reason = scenario === "api-error" ? "API unavailable" : "User cancelled the execution";
      const terminal = JSON.stringify({
        type: "result",
        subtype: scenario === "api-error" ? "api_error" : "error_during_execution",
        is_error: true,
        stop_reason: scenario === "api-error" ? "end_turn" : "cancelled",
        errors: [reason],
      });
      writeFileSync(join(bin, "grok"), `#!/usr/bin/env bun
if (process.argv[2] === "models") {
  console.log("You are logged in with grok.com.\\nAvailable models:\\n  * grok-4.6 (default)");
  process.exit(0);
}
console.log(${JSON.stringify(terminal)});
console.error("startup warning".repeat(500));
process.exit(1);
`);
      const result = await runLane({ ...options("grok"), parent: "codex" });
      expect(result.exitCode).toBe(scenario === "api-error" ? 70 : 130);
      expect(result.receipt.status).toBe(scenario === "api-error" ? "child-failed" : "cancelled");
      expect(result.receipt.error?.message).toBe(reason);
      expect(result.receipt.error?.evidence).toStartWith(reason);
      expect(result.receipt.error?.evidence).not.toContain("Codex parent sandbox");
    });
  }

  for (const provider of ["claude", "grok"] as const) {
    it(`leaves successful ${provider} lanes unchanged with the marker`, async () => {
      process.env.CODEX_SANDBOX_NETWORK_DISABLED = "1";
      const result = await runLane({ ...options(provider), parent: "codex" });
      expect(result.exitCode).toBe(0);
      expect(result.receipt.status).toBe("complete");
      expect(result.receipt.error).toBeNull();
    });
  }

  for (const status of ["unavailable-model", "unauthenticated", "timed-out"] as const) {
    it(`does not enrich ${status} with a sandbox hint`, async () => {
      process.env.CODEX_SANDBOX_NETWORK_DISABLED = "1";
      const input = { ...options("grok"), parent: "codex" as const,
        timeoutMs: status === "timed-out" ? 150 : null };
      if (status === "unavailable-model") process.env.FAKE_INVALID_MODEL = "1";
      if (status === "unauthenticated") {
        writeFileSync(join(bin, "grok"), `#!/usr/bin/env bun
if (process.argv[2] === "models") {
  console.log("You are logged in with grok.com.\\nAvailable models:\\n  * grok-4.6 (default)");
  process.exit(0);
}
console.error("Not logged in. Run grok auth login.");
process.exit(1);
`);
      }
      if (status === "timed-out") process.env.FAKE_TIMEOUT = "1";
      const result = await runLane(input);
      expect(result.receipt.status).toBe(status);
      expect(result.receipt.error?.message).not.toContain("Codex parent sandbox");
      expect(result.receipt.error?.evidence).not.toContain("Codex parent sandbox");
    });
  }
});

describe("issue78 terminal results", () => {
  for (const { auth, scenario } of ["subscription", "api-key"].flatMap((auth) =>
    ["cancel-zero", "cancel-nonzero", "api-error", "api-error-nonzero", "success-streams"]
      .map((scenario) => ({ auth, scenario }))
  )) {
    it(`issue78 ${scenario} (${auth})`, async () => {
      const input = options("grok");
      const reason = scenario.startsWith("api-error")
        ? "API unavailable"
        : "User cancelled the execution for tool run_terminal_command";
      const terminal = {
        type: "result",
        subtype: scenario.startsWith("api-error") ? "api_error"
          : scenario === "success-streams" ? "success" : "error_during_execution",
        is_error: scenario !== "success-streams",
        stop_reason: scenario.startsWith("cancel") ? "cancelled" : "end_turn",
        errors: [reason],
        result: "GROK_OK",
        session_id: "terminal-session",
        usage: { input_tokens: 30, output_tokens: 4 },
        total_cost_usd: 0.02,
        modelUsage: { "grok-4.6-build": {} },
      };
      const stdout = JSON.stringify(terminal) + "\n";
      const stderr = "startup warning\n".repeat(400) + "\n";
      const authentication = auth === "api-key" ? "You are using XAI_API_KEY."
        : "You are logged in with grok.com.";
      writeFileSync(join(bin, "grok"), `#!/usr/bin/env bun
if (process.argv[2] === "models") {
  console.log(${JSON.stringify(`${authentication}\nAvailable models:\n  * grok-4.6 (default)`)});
  process.exit(0);
}
process.stdout.write(${JSON.stringify(stdout)});
process.stderr.write(${JSON.stringify(stderr)});
process.exit(${scenario.endsWith("nonzero") ? 1 : 0});
`);
      const result = await runLane(input);
      const saved = JSON.parse(readFileSync(input.receiptPath, "utf8"));
      expect(saved.status).toBe(scenario === "success-streams" ? "complete"
        : scenario.startsWith("api-error") ? "child-failed" : "cancelled");
      expect(result.exitCode).toBe(scenario === "success-streams" ? 0
        : scenario.startsWith("api-error") ? 70 : 130);
      expect(saved.exitCode).toBe(scenario.endsWith("nonzero") ? 1 : 0);
      expect(saved.reportedModel).toBe("grok-4.6-build");
      expect(saved.modelVerified).toBe(true);
      expect(saved.modelEvidence).toBe("provider-report");
      expect(saved.sessionId).toBe("terminal-session");
      expect(saved.usage).toEqual({ inputTokens: 30, outputTokens: 4 });
      expect(saved.costUsd).toBe(0.02);
      if (scenario !== "success-streams") {
        expect(saved.error.message).toBe(reason);
        expect(saved.error.evidence.startsWith(reason)).toBe(true);
        expect(saved.error.evidence.length).toBeLessThanOrEqual(4_000);
        expect(existsSync(input.outputPath)).toBe(false);
      }
      expect(saved.stdoutPath).toBe(`${input.receiptPath}.stdout`);
      expect(saved.stderrPath).toBe(`${input.receiptPath}.stderr`);
      expect(readFileSync(streamPath(saved.stdoutPath))).toEqual(Buffer.from(stdout));
      expect(readFileSync(streamPath(saved.stderrPath))).toEqual(Buffer.from(stderr));
      expect(statSync(streamPath(saved.stderrPath)).size).toBe(6_401);
      expect(saved.schemaVersion).toBe(1);
      for (const path of [saved.stdoutPath, saved.stderrPath, input.receiptPath]) {
        expect(statSync(streamPath(path)).mode & 0o777).toBe(0o600);
      }
    });
  }

  for (const stream of ["stdout", "stderr"]) {
    it(`rolls back reservations without overwriting an existing ${stream} sidecar`, async () => {
      const input = options("grok");
      const conflict = `${input.receiptPath}.${stream}`;
      writeFileSync(conflict, "operator evidence");
      await expect(runLane(input)).rejects.toThrow();
      expect(readFileSync(conflict, "utf8")).toBe("operator evidence");
      for (const path of [input.outputPath, input.receiptPath,
        `${input.receiptPath}.${stream === "stdout" ? "stderr" : "stdout"}`]) {
        expect(existsSync(path)).toBe(false);
      }
    });

    it(`rejects a ${stream} sidecar colliding with the prompt or output`, async () => {
      const input = options("grok");
      const conflict = `${input.receiptPath}.${stream}`;
      writeFileSync(conflict, "operator prompt");
      await expect(runLane({ ...input, promptPath: conflict })).rejects.toThrow("must be distinct");
      expect(readFileSync(conflict, "utf8")).toBe("operator prompt");
      rmSync(conflict);
      await expect(runLane({ ...input, outputPath: conflict })).rejects.toThrow("must be distinct");
      for (const path of [input.outputPath, input.receiptPath,
        `${input.receiptPath}.stdout`, `${input.receiptPath}.stderr`]) {
        expect(existsSync(path)).toBe(false);
      }
    });
  }

  it("retains complete streams when writes are partial", async () => {
    const input = options("grok");
    const stdout = JSON.stringify({ type: "result", subtype: "success", is_error: false,
      result: "GROK_OK", modelUsage: { "grok-4.6-build": {} } }) + "\n";
    const stderr = "complete stderr despite partial writes\n";
    writeFileSync(join(bin, "grok"), fake.replace("const modelIndex =",
      `process.stdout.write(${JSON.stringify(stdout)}); process.stderr.write(${JSON.stringify(stderr)}); process.exit(0);\nconst modelIndex =`));
    const originalWrite = fs.writeSync;
    let partialWrites = 0;
    const write = spyOn(fs, "writeSync").mockImplementation((descriptor, data, offset, length) => {
      if (typeof data === "string") return originalWrite(descriptor, data, offset);
      partialWrites++;
      return originalWrite(descriptor, data, offset,
        Math.min(typeof length === "number" ? length : data.byteLength, 7));
    });
    try {
      const result = await runLane(input);
      expect(result.exitCode).toBe(0);
      expect(partialWrites).toBeGreaterThan(1);
      expect(readFileSync(streamPath(result.receipt.stdoutPath))).toEqual(Buffer.from(stdout));
      expect(readFileSync(streamPath(result.receipt.stderrPath))).toEqual(Buffer.from(stderr));
    } finally {
      write.mockRestore();
    }
  });

  it("terminalizes a sidecar write failure without waiting for the child", async () => {
    const input = options("grok");
    writeFileSync(join(bin, "grok"), fake.replace("const modelIndex =",
      'process.stdout.write("stream data"); await Bun.sleep(10_000);\nconst modelIndex ='));
    const originalWrite = fs.writeSync;
    const write = spyOn(fs, "writeSync").mockImplementation((descriptor, data, offset, length) => {
      if (typeof data === "string") return originalWrite(descriptor, data, offset);
      throw new Error("sidecar storage unavailable");
    });
    try {
      const result = await runLane(input);
      expect(result.exitCode).toBe(70);
      expect(result.receipt.status).toBe("child-failed");
      expect(result.receipt.error?.evidence).toContain("sidecar storage unavailable");
      expect(existsSync(input.outputPath)).toBe(false);
      expect(existsSync(streamPath(result.receipt.stdoutPath))).toBe(true);
      expect(existsSync(streamPath(result.receipt.stderrPath))).toBe(true);
    } finally {
      write.mockRestore();
    }
  });

  it("retains undecodable stderr bytes rather than re-encoding captured text", async () => {
    const input = options("grok");
    const bytes = Buffer.from([0, 255, 195, 169, 13, 10]);
    writeFileSync(join(bin, "grok"), fake.replace("const modelIndex =",
      `process.stderr.write(Buffer.from(${JSON.stringify([...bytes])}));\nconst modelIndex =`));
    const result = await runLane(input);
    expect(result.exitCode).toBe(0);
    expect(readFileSync(streamPath(result.receipt.stderrPath))).toEqual(bytes);
  });

  for (const exitCode of [0, 1]) {
    it(`keeps malformed terminal data distinct after child exit ${exitCode}`, async () => {
      const input = options("grok");
      const stdout = '{"type":"result","is_error":true}\n';
      writeFileSync(join(bin, "grok"), fake.replace(
        'console.log(JSON.stringify({type:"result",subtype:"error_during_execution",is_error:true,stop_reason:"cancelled",errors:["cancelled"]}));',
        `process.stdout.write(${JSON.stringify(stdout)}); process.exit(${exitCode});`));
      process.env.FAKE_GROK_ERROR_RESULT = "1";
      const result = await runLane(input);
      expect(result.exitCode).toBe(exitCode === 0 ? 65 : 70);
      expect(result.receipt).toMatchObject({
        status: exitCode === 0 ? "malformed-output" : "child-failed",
        exitCode, reportedModel: null, modelVerified: false,
        sessionId: null, error: { message: exitCode === 0
          ? "grok result did not contain a valid terminal status" : "child exited with status 1" },
      });
      expect(readFileSync(streamPath(result.receipt.stdoutPath), "utf8")).toEndWith(stdout);
      expect(existsSync(input.outputPath)).toBe(false);
    });
  }

  for (const stdout of ['{"type":"system","subtype":"init"}\n', "startup failed\n"]) {
    for (const exitCode of [0, 1]) {
      it(`handles missing Grok terminal output ${JSON.stringify(stdout)} after exit ${exitCode}`, async () => {
        const input = options("grok");
        const stderr = "sandbox startup refused\n";
        writeFileSync(join(bin, "grok"), fake.replace("const modelIndex =",
          `process.stdout.write(${JSON.stringify(stdout)}); process.stderr.write(${JSON.stringify(stderr)}); process.exit(${exitCode});\nconst modelIndex =`));
        const result = await runLane(input);
        expect(result.exitCode).toBe(exitCode === 0 ? 65 : 70);
        expect(result.receipt).toMatchObject({
          status: exitCode === 0 ? "malformed-output" : "child-failed",
          exitCode, reportedModel: null, sessionId: null,
        });
        expect(readFileSync(streamPath(result.receipt.stdoutPath), "utf8")).toBe(stdout);
        expect(readFileSync(streamPath(result.receipt.stderrPath), "utf8")).toBe(stderr);
        expect(existsSync(input.outputPath)).toBe(false);
      });
    }
  }

  it("does not invent metadata for a valid provider failure", async () => {
    const input = options("grok");
    writeFileSync(join(bin, "grok"), fake.replace(
      'console.log(JSON.stringify({type:"result",subtype:"error_during_execution",is_error:true,stop_reason:"cancelled",errors:["cancelled"]}));',
      'console.log(JSON.stringify({type:"result",subtype:"api_error",is_error:true,errors:["API unavailable"]})); process.exit(1);'));
    process.env.FAKE_GROK_ERROR_RESULT = "1";
    const result = await runLane(input);
    expect(result.exitCode).toBe(70);
    expect(result.receipt).toMatchObject({
      status: "child-failed", exitCode: 1, reportedModel: null, modelVerified: false,
      modelEvidence: null, sessionId: null, usage: null, costUsd: null,
      error: { message: "API unavailable" },
    });
    expect(readFileSync(streamPath(result.receipt.stdoutPath), "utf8")).toContain("api_error");
    expect(existsSync(input.outputPath)).toBe(false);
  });

  it("retains strict model verification for successful Grok results", async () => {
    const input = options("grok");
    writeFileSync(join(bin, "grok"), fake.replace('[model + "-build"]', '["grok-unexpected"]'));
    const result = await runLane(input);
    expect(result.exitCode).toBe(65);
    expect(result.receipt).toMatchObject({ status: "malformed-output", modelVerified: false });
    expect(result.receipt.error?.message).toBe("requested model grok-4.6 was not reported by grok");
    expect(readFileSync(streamPath(result.receipt.stdoutPath), "utf8")).toContain("grok-unexpected");
    expect(existsSync(input.outputPath)).toBe(false);
  });
});

describe("runLane", () => {
  for (const startup of ["dotenv", "bunfig", "bun-options", "node-options", "combined", "hostile-path", "bare-name"]) {
    it(`shipped launcher startup isolation: ${startup}`, async () => {
      const input = options("codex", startup);
      // Exceed pipe capacity so the fake provider must consume stdin before exiting.
      writeFileSync(input.promptPath, "Return the marker.\n".repeat(100_000));
      const captured = join(scratch, "provider-env.txt");
      const capturedPrompt = join(scratch, "provider-prompt.txt");
      const bunPreload = join(scratch, "bun-preload.ran");
      const nodePreload = join(scratch, "node-preload.ran");
      const env: Record<string, string> = {
        PATH: process.env.PATH!,
        PSTACK_ENV_CAPTURE: captured,
        PSTACK_PROMPT_CAPTURE: capturedPrompt,
        PSTACK_INHERITED_ENV_SENTINEL: "inherited-from-parent",
      };
      if (startup === "dotenv" || startup === "combined") {
        writeFileSync(join(scratch, ".env"), "PSTACK_PROJECT_ENV_SENTINEL=loaded-from-project-dotenv\n");
        writeFileSync(join(scratch, ".env.local"), "PSTACK_LOCAL_ENV_SENTINEL=loaded-from-project-local-dotenv\n");
      }
      if (startup === "bunfig" || startup === "combined") {
        writeFileSync(join(scratch, "bunfig.toml"), 'preload = ["./project-preload.ts"]\n');
        writeFileSync(join(scratch, "project-preload.ts"),
          `await Bun.write(${JSON.stringify(bunPreload)}, "project preload ran");\n`);
      }
      if (startup === "bun-options" || startup === "combined") {
        writeFileSync(join(scratch, "startup.env"), "PSTACK_PROJECT_ENV_SENTINEL=loaded-from-bun-options\n");
        env.BUN_OPTIONS = "--env-file=./startup.env";
      }
      if (startup === "node-options" || startup === "combined") {
        writeFileSync(join(scratch, "project-preload.cjs"),
          `require("node:fs").writeFileSync(${JSON.stringify(nodePreload)}, "node preload ran");\n`);
        env.NODE_OPTIONS = "--require=./project-preload.cjs";
      }
      writeFileSync(join(bin, "codex"), `#!/bin/sh
if [ "$1" = "login" ]; then
  printf '%s\\n' 'Logged in using ChatGPT'
  exit 0
fi
cat > "$PSTACK_PROMPT_CAPTURE"
printf '%s\\n' "\${PSTACK_PROJECT_ENV_SENTINEL-unset}" "\${PSTACK_LOCAL_ENV_SENTINEL-unset}" "\${PSTACK_INHERITED_ENV_SENTINEL-unset}" "\${BUN_OPTIONS-unset}" "\${NODE_OPTIONS-unset}" > "$PSTACK_ENV_CAPTURE"
printf '%s\\n' '{"type":"thread.started","thread_id":"isolated"}' '{"type":"item.completed","item":{"type":"agent_message","text":"CODEX_OK"}}' '{"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}'
`);
      chmodSync(join(bin, "codex"), 0o755);
      const helperSentinel = join(scratch, "helper.ran");
      if (startup === "hostile-path") {
        for (const name of ["env", "dirname", "readlink"]) {
          writeFileSync(join(bin, name), `#!/bin/sh\nprintf '%s\\n' '${name}' > "${helperSentinel}"\nexit 1\n`);
          chmodSync(join(bin, name), 0o755);
        }
      }
      const runner = Bun.spawn(startup === "bare-name"
        ? ["/bin/sh", "pstack-runner", ...runnerArgs(input).slice(1)]
        : runnerArgs(input), {
        cwd: startup === "bare-name" ? import.meta.dir : scratch,
        env,
        stdout: "pipe",
        stderr: "pipe",
      });
      const stdout = new Response(runner.stdout).text();
      const stderr = new Response(runner.stderr).text();
      const exitCode = await exitWithin(runner, 3_000);
      const [stdoutText, stderrText] = await Promise.all([stdout, stderr]);
      expect(exitCode, JSON.stringify({
        stdout: stdoutText,
        stderr: stderrText,
        receipt: existsSync(input.receiptPath) ? receipt(input.receiptPath) : null,
      })).toBe(0);
      expect(readFileSync(capturedPrompt, "utf8")).toBe(readFileSync(input.promptPath, "utf8"));
      expect(readFileSync(captured, "utf8")).toBe("unset\nunset\ninherited-from-parent\nunset\nunset\n");
      expect(existsSync(bunPreload)).toBe(false);
      expect(existsSync(nodePreload)).toBe(false);
      expect(existsSync(helperSentinel)).toBe(false);
      expect(readFileSync(input.outputPath, "utf8")).toContain("CODEX_OK");
      expect(receipt(input.receiptPath)).toMatchObject({ status: "complete" });
    });
  }

  for (const provider of ["claude", "codex", "grok"] as const) {
    it(`executes and receipts the ${provider} external lane`, async () => {
      const input = options(provider);
      const result = await runLane(input);
      expect(result.exitCode).toBe(0);
      expect(readFileSync(input.outputPath, "utf8")).toContain(
        provider.toUpperCase()
      );
      expect(receipt(input.receiptPath)).toMatchObject({
        status: "complete",
        provider,
        model: input.model,
        modelVerified: provider !== "codex",
        modelEvidence: provider === "codex" ? "pinned-argv" : "provider-report",
        preflight: { status: "passed" },
      });
      const saved = receipt(input.receiptPath);
      expect(readFileSync(streamPath(saved.stdoutPath), "utf8")).toContain(provider.toUpperCase());
      expect(readFileSync(streamPath(saved.stderrPath))).toEqual(Buffer.alloc(0));
      for (const path of [saved.stdoutPath, saved.stderrPath]) {
        expect(statSync(streamPath(path)).mode & 0o777).toBe(0o600);
      }
      if (provider === "claude") {
        expect(receipt(input.receiptPath).reportedModel).toBe("claude-fable-9-9");
      }
    });
  }

  it("records Codex's exact argv without fabricating a reported model", async () => {
    const input = options("codex");
    const result = await runLane(input);
    expect(result.exitCode).toBe(0);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "complete",
      model: "gpt-5.6-sol",
      reportedModel: null,
      modelVerified: false,
      modelEvidence: "pinned-argv",
    });
  });

  it("keeps Grok's terminal cancellation reason in bounded evidence", async () => {
    process.env.FAKE_GROK_ERROR_RESULT = "1";
    const input = options("grok", "grok-error-result");
    const result = await runLane(input);
    expect(result.exitCode).toBe(130);
    expect(existsSync(input.outputPath)).toBe(false);
    const recorded = receipt(input.receiptPath);
    expect(recorded).toMatchObject({
      status: "cancelled",
      exitCode: 0,
      error: { message: "cancelled" },
    });
    expect(recorded.error?.evidence).toStartWith("cancelled");
    expect(recorded.error?.evidence.length).toBeLessThanOrEqual(4_000);
  });

  it("classifies an unavailable model without falling back", async () => {
    process.env.FAKE_INVALID_MODEL = "1";
    const input = options("codex");
    const result = await runLane(input);
    expect(result.exitCode).toBe(69);
    expect(existsSync(input.outputPath)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "unavailable-model",
      model: "gpt-5.6-sol",
      reportedModel: null,
      modelVerified: false,
      modelEvidence: null,
    });
  });

  it("executes Grok after one API-key-authenticated exact-model preflight", async () => {
    process.env.FAKE_GROK_PREFLIGHT_OUTPUT = "You are using XAI_API_KEY.\nAvailable models: [grok-4.6] (default)";
    const preflightLog = join(scratch, "grok-api-key.log");
    const modelStarted = join(scratch, "grok-api-key.started");
    process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
    process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
    const input = options("grok", "grok-api-key");
    const result = await runLane(input);

    expect(result.exitCode).toBe(0);
    expect(readFileSync(preflightLog, "utf8")).toBe("attempt\n");
    expect(existsSync(modelStarted)).toBe(true);
    expect(readFileSync(input.outputPath, "utf8")).toBe("GROK_OK");
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "complete", model: "grok-4.6", reportedModel: "grok-4.6-build",
      modelVerified: true, modelEvidence: "provider-report",
      preflight: { status: "passed", evidence: "authenticated; model grok-4.6 available" },
    });
  }, 10_000);

  for (const auth of ["You are using XAI_API_KEY.", "You are logged in."]) {
    it(`rejects an explicitly unsupported Grok model despite ${auth}`, async () => {
      process.env.FAKE_GROK_PREFLIGHT_OUTPUT = `${auth}\nAvailable models: grok-4.6`;
      process.env.FAKE_GROK_PREFLIGHT_ERROR = "model grok-4.6 is not supported";
      const preflightLog = join(scratch, "grok-unsupported.log");
      const modelStarted = join(scratch, "grok-unsupported.started");
      process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
      process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
      const input = options("grok", "grok-unsupported");
      const result = await runLane(input);

      expect(result.exitCode).toBe(69);
      expect(readFileSync(preflightLog, "utf8")).toBe("attempt\n");
      expect(existsSync(modelStarted)).toBe(false);
      expect(existsSync(input.outputPath)).toBe(false);
      expect(receipt(input.receiptPath)).toMatchObject({
        status: "unavailable-model", model: "grok-4.6", preflight: { status: "failed" },
      });
      expect(receipt(input.receiptPath).preflight.evidence).toContain("not supported");
    });
  }

  for (const failure of ["unauthenticated", "You are not authenticated."]) {
    it(`fails closed on contradictory Grok API-key authentication: ${failure}`, async () => {
      process.env.FAKE_GROK_PREFLIGHT_OUTPUT = "You are using XAI_API_KEY.\nYou are logged in.\nAvailable models: grok-4.6";
      process.env.FAKE_GROK_PREFLIGHT_ERROR = failure;
      const preflightLog = join(scratch, "grok-api-key-unauth.log");
      const modelStarted = join(scratch, "grok-api-key-unauth.started");
      process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
      process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
      const input = options("grok", "grok-api-key-unauth");
      const result = await runLane(input);

      expect(result.exitCode).toBe(77);
      expect(readFileSync(preflightLog, "utf8")).toBe("attempt\nattempt\n");
      expect(existsSync(modelStarted)).toBe(false);
      expect(existsSync(input.outputPath)).toBe(false);
      expect(receipt(input.receiptPath)).toMatchObject({
        status: "unauthenticated", preflight: { status: "failed" },
      });
      expect(receipt(input.receiptPath).preflight.evidence).toContain("attempt 2 failed");
    }, 10_000);
  }

  for (const listed of ["grok-4.60", "xgrok-4.6", "grok-4.6-build", "grok-4x6"]) {
    it(`does not accept neighboring Grok model token ${listed}`, async () => {
      process.env.FAKE_GROK_PREFLIGHT_OUTPUT = `You are logged in.\nAvailable models: ${listed}`;
      const preflightLog = join(scratch, "grok-neighbor.log");
      const modelStarted = join(scratch, "grok-neighbor.started");
      process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
      process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
      const input = options("grok", "grok-neighbor");
      const result = await runLane(input);

      expect(result.exitCode).toBe(69);
      expect(readFileSync(preflightLog, "utf8")).toBe("attempt\n");
      expect(existsSync(modelStarted)).toBe(false);
      expect(existsSync(input.outputPath)).toBe(false);
      expect(receipt(input.receiptPath)).toMatchObject({
        status: "unavailable-model", preflight: { status: "failed" },
      });
    });
  }

  it("retries a contradictory Grok authentication preflight before running the model", async () => {
    const transientMarker = join(scratch, "grok-transient-unauth.seen");
    const preflightLog = join(scratch, "grok-transient-unauth.log");
    process.env.FAKE_GROK_TRANSIENT_UNAUTH_PATH = transientMarker;
    process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
    const modelStarted = join(scratch, "grok-transient-model.started");
    process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
    const input = options("grok", "grok-transient-unauth");
    const result = await runLane(input);

    expect(result.exitCode).toBe(0);
    expect(readFileSync(preflightLog, "utf8")).toBe("attempt\nattempt\n");
    expect(existsSync(modelStarted)).toBe(true);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "complete",
      preflight: { status: "passed" },
    });
    expect(receipt(input.receiptPath).preflight.evidence).toContain(
      "You are not authenticated."
    );
    expect(receipt(input.receiptPath).preflight.evidence).toContain(
      "attempt 2 passed"
    );
  }, 10_000);

  it("classifies Grok authentication failure after two consecutive preflights", async () => {
    process.env.FAKE_GROK_UNAUTH = "1";
    const preflightLog = join(scratch, "grok-unauthenticated.log");
    process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
    const modelStarted = join(scratch, "grok-model.started");
    process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
    const input = options("grok", "grok-unauthenticated");
    const result = await runLane(input);

    expect(result.exitCode).toBe(77);
    expect(readFileSync(preflightLog, "utf8")).toBe("attempt\nattempt\n");
    expect(existsSync(modelStarted)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "unauthenticated",
      preflight: { status: "failed" },
    });
    expect(receipt(input.receiptPath).preflight.evidence).toContain(
      "attempt 2 failed"
    );
  }, 10_000);

  it("counts the Grok retry delay against the wrapper deadline", async () => {
    const transientMarker = join(scratch, "grok-deadline-unauth.seen");
    const preflightLog = join(scratch, "grok-deadline-unauth.log");
    process.env.FAKE_GROK_TRANSIENT_UNAUTH_PATH = transientMarker;
    process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
    const modelStarted = join(scratch, "grok-deadline-model.started");
    process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
    const input = {
      ...options("grok", "grok-preflight-retry-deadline"),
      timeoutMs: 700,
    };
    const result = await runLane(input);
    const recorded = receipt(input.receiptPath);

    expect(result.exitCode).toBe(124);
    expect(readFileSync(preflightLog, "utf8")).toBe("attempt\n");
    expect(existsSync(modelStarted)).toBe(false);
    expect(recorded).toMatchObject({
      status: "timed-out",
      preflight: { status: "timed-out" },
    });
    expect(recorded.preflight.evidence).toContain("You are not authenticated.");
    expect(recorded.elapsedMs).toBeLessThan(1_200);
  });

  it("cancels during the Grok retry delay without starting another preflight", async () => {
    const transientMarker = join(scratch, "grok-cancel-unauth.pid");
    const preflightLog = join(scratch, "grok-cancel-unauth.log");
    const input = options("grok", "grok-preflight-retry-cancelled");
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_GROK_TRANSIENT_UNAUTH_PATH: transientMarker,
        FAKE_GROK_PREFLIGHT_LOG_PATH: preflightLog,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();
    await waitFor(transientMarker);
    await waitForExit(Number(readFileSync(transientMarker, "utf8")));
    await Bun.sleep(200);
    runner.kill("SIGTERM");

    expect(await exitWithin(runner, 2_000)).toBe(130);
    await Promise.all([stdout, stderr]);
    expect(readFileSync(preflightLog, "utf8")).toBe("attempt\n");
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "cancelled",
      preflight: { status: "cancelled" },
      error: {
        message: "launcher received SIGTERM during authentication preflight retry delay",
      },
    });
  });

  it("does not retry a Grok preflight with a missing model", async () => {
    process.env.FAKE_GROK_MISSING_MODEL = "1";
    const preflightLog = join(scratch, "grok-missing-model.log");
    process.env.FAKE_GROK_PREFLIGHT_LOG_PATH = preflightLog;
    const modelStarted = join(scratch, "grok-missing-model.started");
    process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
    const input = options("grok", "grok-missing-model");
    const result = await runLane(input);

    expect(result.exitCode).toBe(69);
    expect(readFileSync(preflightLog, "utf8")).toBe("attempt\n");
    expect(existsSync(modelStarted)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "unavailable-model",
      preflight: { status: "failed" },
    });
  });

  it("kills a timed-out child and preserves a failure receipt", async () => {
    process.env.FAKE_TIMEOUT = "1";
    const input = { ...options("claude"), timeoutMs: 30 };
    const result = await runLane(input);
    expect(result.exitCode).toBe(124);
    expect(existsSync(input.outputPath)).toBe(false);
    expect(receipt(input.receiptPath).status).toBe("timed-out");
  });

  it("does not spawn the model when preflight exhausts the wrapper deadline", async () => {
    const modelStarted = join(scratch, "deadline-model.started");
    const input = { ...options("claude", "preflight-deadline"), timeoutMs: 300 };
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_PREFLIGHT_DELAY_MS: "1000",
        FAKE_MODEL_STARTED_PATH: modelStarted,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();

    expect(await exitWithin(runner, 2_000)).toBe(124);
    await Promise.all([stdout, stderr]);
    expect(existsSync(modelStarted)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "timed-out",
      signal: "SIGTERM",
      preflight: { status: "timed-out" },
    });
  });

  it("lets a delayed wrapper lane finish when timeout is omitted", async () => {
    const input = options("claude", "unbounded-default");
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: { ...process.env, FAKE_MODEL_DELAY_MS: "400" },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();

    expect(await exitWithin(runner, 3_000)).toBe(0);
    await Promise.all([stdout, stderr]);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "complete",
      signal: null,
    });
    expect(receipt(input.receiptPath).elapsedMs).toBeGreaterThanOrEqual(400);
  });

  it("keeps a very long explicit deadline without timer overflow", async () => {
    const input = {
      ...options("claude", "long-runtime-deadline"),
      timeoutMs: 2_147_483_648,
    };
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: { ...process.env, FAKE_MODEL_DELAY_MS: "100" },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();

    expect(await exitWithin(runner, 2_000)).toBe(0);
    await Promise.all([stdout, stderr]);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "complete",
      signal: null,
      exitCode: 0,
    });
  });

  it("counts wrapper import and parsing time against an explicit deadline", async () => {
    const preflightStarted = join(scratch, "expired-preflight.started");
    const modelStarted = join(scratch, "expired-model.started");
    process.env.FAKE_PREFLIGHT_STARTED_PATH = preflightStarted;
    process.env.FAKE_MODEL_STARTED_PATH = modelStarted;
    const input = { ...options("claude", "expired-at-entry"), timeoutMs: 100 };
    const stdout: string[] = [];
    const stderr: string[] = [];

    const exitCode = await main(
      runnerArgs(input).slice(1),
      Date.now() - 1_000,
      {
        stdout: (value) => stdout.push(value),
        stderr: (value) => stderr.push(value),
      }
    );

    expect(exitCode).toBe(124);
    expect(stdout).toEqual([]);
    expect(stderr.join("")).toContain('"status":"timed-out"');
    expect(existsSync(preflightStarted)).toBe(false);
    expect(existsSync(modelStarted)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "timed-out",
      preflight: { status: "timed-out" },
    });
  });

  it("spends one explicit deadline across preflight and model execution", async () => {
    process.env.FAKE_PREFLIGHT_DELAY_MS = "1200";
    process.env.FAKE_MODEL_DELAY_MS = "1200";
    const input = { ...options("claude"), timeoutMs: 1_500 };
    const result = await runLane(input);
    const recorded = receipt(input.receiptPath);

    expect(result.exitCode).toBe(124);
    expect(recorded.status).toBe("timed-out");
    expect(recorded.preflight.status).toBe("passed");
    expect(recorded.elapsedMs).toBeLessThan(2_100);
  });

  it("bounds a descendant-held pipe by the explicit deadline without fabricating a signal", async () => {
    const descendantPidPath = join(scratch, "deadline-descendant.pid");
    const input = { ...options("claude", "deadline-drain"), timeoutMs: 700 };
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_DESCENDANT_HOLDS_PIPES_MS: "5000",
        FAKE_DESCENDANT_PID_PATH: descendantPidPath,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();

    expect(await exitWithin(runner, 2_000)).toBe(124);
    await Promise.all([stdout, stderr]);
    const recorded = receipt(input.receiptPath);
    expect(recorded).toMatchObject({
      status: "timed-out",
      exitCode: 0,
      signal: null,
      preflight: { status: "passed" },
    });
    expect(recorded.elapsedMs).toBeLessThan(1_500);

    const descendantPid = Number(readFileSync(descendantPidPath, "utf8"));
    if (processIsAlive(descendantPid)) process.kill(descendantPid, "SIGKILL");
  });

  it("does not claim a signal was sent to an already signal-reaped child", async () => {
    const descendantPidPath = join(scratch, "signalled-descendant.pid");
    const input = { ...options("claude", "signalled-drain"), timeoutMs: 700 };
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_DESCENDANT_HOLDS_PIPES_MS: "5000",
        FAKE_DESCENDANT_PID_PATH: descendantPidPath,
        FAKE_SELF_SIGNAL: "SIGTERM",
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();

    expect(await exitWithin(runner, 2_000)).toBe(124);
    await Promise.all([stdout, stderr]);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "timed-out",
      exitCode: 143,
      signal: null,
      preflight: { status: "passed" },
    });

    const descendantPid = Number(readFileSync(descendantPidPath, "utf8"));
    if (processIsAlive(descendantPid)) process.kill(descendantPid, "SIGKILL");
  });

  it("lets manual cancellation end a post-exit pipe drain without a default timeout", async () => {
    const descendantPidPath = join(scratch, "cancel-descendant.pid");
    const modelExiting = join(scratch, "cancel-model.exiting");
    const input = options("claude", "cancel-drain");
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_DESCENDANT_HOLDS_PIPES_MS: "5000",
        FAKE_DESCENDANT_PID_PATH: descendantPidPath,
        FAKE_MODEL_EXITING_PATH: modelExiting,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();
    await waitFor(modelExiting);
    await waitForExit(Number(readFileSync(modelExiting, "utf8")));
    runner.kill("SIGTERM");

    expect(await exitWithin(runner, 2_000)).toBe(130);
    await Promise.all([stdout, stderr]);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "cancelled",
      exitCode: 0,
      signal: null,
      preflight: { status: "passed" },
      error: { message: "launcher received SIGTERM after child exited" },
    });

    const descendantPid = Number(readFileSync(descendantPidPath, "utf8"));
    if (processIsAlive(descendantPid)) process.kill(descendantPid, "SIGKILL");
  });

  it("clears a losing long-deadline timer when the shipped wrapper succeeds", async () => {
    const input = { ...options("claude", "long-deadline"), timeoutMs: 60_000 };
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: { ...process.env },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();

    expect(await exitWithin(runner, 3_000)).toBe(0);
    await Promise.all([stdout, stderr]);
    expect(receipt(input.receiptPath).status).toBe("complete");
  });

  it("cancels a preflight with SIGINT and writes a terminal receipt", async () => {
    const input = options("claude", "preflight-cancelled");
    const started = join(scratch, "preflight-child.started");
    const terminated = join(scratch, "preflight-child.terminated");
    const isolatedRunner = join(scratch, "isolated-runner");
    cpSync(import.meta.dir, isolatedRunner, { recursive: true });
    const runner = Bun.spawn([
      join(isolatedRunner, "pstack-runner"),
      ...runnerArgs(input).slice(1),
    ], {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_CANCEL_STAGE: "preflight",
        FAKE_STARTED_PATH: started,
        FAKE_TERMINATED_PATH: terminated,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();
    await waitFor(started);
    runner.kill("SIGINT");

    expect(await exitWithin(runner, 3_000)).toBe(130);
    await Promise.all([stdout, stderr]);
    expect(readFileSync(terminated, "utf8")).toBe("SIGINT");
    expect(existsSync(input.outputPath)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "cancelled",
      signal: "SIGINT",
      preflight: { status: "cancelled" },
    });
  });

  it("reaps the child and exits after repeated cancellation with a long deadline", async () => {
    const input = { ...options("codex", "repeated-cancel"), timeoutMs: 60_000 };
    const started = join(scratch, "repeated-child.started");
    const terminated = join(scratch, "repeated-child.terminated");
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_CANCEL: "1",
        FAKE_IGNORE_SIGNAL: "1",
        FAKE_STARTED_PATH: started,
        FAKE_TERMINATED_PATH: terminated,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();
    await waitFor(started);
    const childPid = Number(readFileSync(started, "utf8"));
    runner.kill("SIGTERM");
    await Bun.sleep(100);
    runner.kill("SIGTERM");

    expect(await exitWithin(runner, 4_000)).toBe(130);
    await Promise.all([stdout, stderr]);
    expect(readFileSync(terminated, "utf8")).toBe("SIGTERM");
    expect(processIsAlive(childPid)).toBe(false);
    expect(existsSync(input.outputPath)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "cancelled",
      signal: "SIGTERM",
    });
  });

  it("forwards cancellation, preserves its receipt, and permits a new attempt", async () => {
    const input = options("codex", "cancelled");
    const started = join(scratch, "cancelled-child.started");
    const terminated = join(scratch, "cancelled-child.terminated");
    const env = {
      ...process.env,
      FAKE_CANCEL: "1",
      FAKE_STARTED_PATH: started,
      FAKE_TERMINATED_PATH: terminated,
    };
    const runner = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env,
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = new Response(runner.stdout).text();
    const stderr = new Response(runner.stderr).text();
    await waitFor(started);
    runner.kill("SIGTERM");

    expect(await runner.exited).toBe(130);
    await Promise.all([stdout, stderr]);
    expect(readFileSync(terminated, "utf8")).toBe("SIGTERM");
    expect(existsSync(input.outputPath)).toBe(false);
    expect(receipt(input.receiptPath)).toMatchObject({
      status: "cancelled",
      signal: "SIGTERM",
      exitCode: 0,
      error: { message: "launcher received SIGTERM; signal was sent to child" },
    });

    const samePaths = Bun.spawn(runnerArgs(input), {
      cwd: scratch,
      env: { ...process.env },
      stdout: "pipe",
      stderr: "pipe",
    });
    const sameStdout = new Response(samePaths.stdout).text();
    const sameStderr = new Response(samePaths.stderr).text();
    expect(await samePaths.exited).toBe(64);
    await Promise.all([sameStdout, sameStderr]);
    expect(receipt(input.receiptPath).status).toBe("cancelled");

    const retry = options("codex", "cancelled-retry");
    const result = await runLane(retry);
    expect(result.exitCode).toBe(0);
    expect(receipt(retry.receiptPath).status).toBe("complete");
  });

  it("reports a missing CLI without fabricating output", async () => {
    process.env.PATH = join(scratch, "empty-bin");
    mkdirSync(process.env.PATH);
    const input = options("grok");
    const result = await runLane(input);
    expect(result.exitCode).toBe(69);
    expect(existsSync(input.outputPath)).toBe(false);
    expect(receipt(input.receiptPath).status).toBe("unavailable-cli");
  });

  it("runs simultaneous same-provider lanes only into their unique paths", async () => {
    const first = options("grok", "first");
    const second = options("grok", "second");
    const results = await Promise.all([runLane(first), runLane(second)]);
    expect(results.map((result) => result.exitCode)).toEqual([0, 0]);
    expect(first.outputPath).not.toBe(second.outputPath);
    expect(receipt(first.receiptPath).sessionId).toBe("g1");
    expect(receipt(second.receiptPath).sessionId).toBe("g1");
  });

  it("refuses a second writer for an already-reserved path", async () => {
    const input = options("claude");
    writeFileSync(input.outputPath, "owned");
    await expect(runLane(input)).rejects.toThrow();
    expect(readFileSync(input.outputPath, "utf8")).toBe("owned");
    expect(existsSync(input.receiptPath)).toBe(false);
  });

  it("terminalizes catchable failures after reserving output paths", async () => {
    const unreadable = options("claude", "unreadable-prompt");
    chmodSync(unreadable.promptPath, 0o000);
    const unreadableRunner = Bun.spawn(runnerArgs(unreadable), {
      cwd: scratch,
      env: { ...process.env },
      stdout: "pipe",
      stderr: "pipe",
    });
    const unreadableStdout = new Response(unreadableRunner.stdout).text();
    const unreadableStderr = new Response(unreadableRunner.stderr).text();
    expect(await unreadableRunner.exited).toBe(70);
    await Promise.all([unreadableStdout, unreadableStderr]);
    chmodSync(unreadable.promptPath, 0o600);

    const preservedReceipt = readFileSync(unreadable.receiptPath, "utf8");
    expect(statSync(unreadable.receiptPath).size).toBeGreaterThan(0);
    expect(existsSync(unreadable.outputPath)).toBe(false);
    expect(receipt(unreadable.receiptPath)).toMatchObject({
      status: "child-failed",
      preflight: { status: "not-run" },
      error: { message: "launcher failed after reserving output paths" },
    });

    const samePaths = Bun.spawn(runnerArgs(unreadable), {
      cwd: scratch,
      env: { ...process.env },
      stdout: "pipe",
      stderr: "pipe",
    });
    const sameStdout = new Response(samePaths.stdout).text();
    const sameStderr = new Response(samePaths.stderr).text();
    expect(await samePaths.exited).toBe(64);
    await Promise.all([sameStdout, sameStderr]);
    expect(readFileSync(unreadable.receiptPath, "utf8")).toBe(preservedReceipt);

    const spawnFailure = options("claude", "spawn-failure");
    const modelStarted = join(scratch, "spawn-failure-model.started");
    const spawnRunner = Bun.spawn(runnerArgs(spawnFailure), {
      cwd: scratch,
      env: {
        ...process.env,
        FAKE_REMOVE_EXECUTABLE_AFTER_PREFLIGHT: "1",
        FAKE_MODEL_STARTED_PATH: modelStarted,
      },
      stdout: "pipe",
      stderr: "pipe",
    });
    const spawnStdout = new Response(spawnRunner.stdout).text();
    const spawnStderr = new Response(spawnRunner.stderr).text();
    expect(await spawnRunner.exited).toBe(70);
    await Promise.all([spawnStdout, spawnStderr]);
    expect(existsSync(modelStarted)).toBe(false);
    expect(existsSync(spawnFailure.outputPath)).toBe(false);
    expect(receipt(spawnFailure.receiptPath)).toMatchObject({
      status: "child-failed",
      preflight: { status: "passed" },
    });

    makeExecutable("claude");
    const retry = options("claude", "post-reservation-retry");
    expect((await runLane(retry)).exitCode).toBe(0);
    expect(receipt(retry.receiptPath).status).toBe("complete");
  });

  it("rejects same-provider recursion", async () => {
    const input = { ...options("claude"), parent: "claude" as const };
    await expect(runLane(input)).rejects.toThrow("native to parent");
  });

  it("rejects a versioned Claude family before it can stay pinned", async () => {
    const input = { ...options("claude"), model: "claude-fable-9-9" };
    await expect(runLane(input)).rejects.toThrow(
      "normalize it to fable before invoking the runner"
    );
    expect(existsSync(input.outputPath)).toBe(false);
    expect(existsSync(input.receiptPath)).toBe(false);
  });
});

describe("childEnvironment", () => {
  it("removes only inherited runtime identity needed to avoid nested detection", () => {
    const source = {
      PATH: "/bin",
      CODEX_THREAD_ID: "codex",
      CODEX_CI: "1",
      CLAUDECODE: "1",
      CLAUDE_CODE_CHILD_SESSION: "1",
      KEEP_ME: "yes",
    };
    expect(childEnvironment("claude", source)).toEqual({
      PATH: "/bin",
      CLAUDECODE: "1",
      CLAUDE_CODE_CHILD_SESSION: "1",
      KEEP_ME: "yes",
    });
    expect(childEnvironment("codex", source)).toEqual({
      PATH: "/bin",
      CODEX_THREAD_ID: "codex",
      CODEX_CI: "1",
      KEEP_ME: "yes",
    });
    expect(childEnvironment("grok", source)).toEqual({
      PATH: "/bin",
      KEEP_ME: "yes",
    });
  });
});
