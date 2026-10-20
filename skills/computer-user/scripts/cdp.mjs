#!/usr/bin/env bun
// Minimal Chrome DevTools Protocol client for the computer-user Brave session.
// Usage: bun cdp.mjs --port <port> [--target <id>] <command> [args]
// Commands: tabs | new <url> | open <url> | url | text | eval <js> | click <css>
//           type <css> <text> | key <Enter|Tab|Escape|Backspace> | screenshot <file>
//           console [seconds]

import { writeFileSync } from 'node:fs';

const argv = process.argv.slice(2);
const flag = (name) => {
  const i = argv.indexOf(name);
  if (i === -1) return undefined;
  const [, value] = argv.splice(i, 2);
  return value;
};
const port = flag('--port') ?? process.env.COMPUTER_USER_PORT;
const targetId = flag('--target');
const [command, ...rest] = argv;
if (!port || !command) {
  console.error('usage: cdp.mjs --port <port> [--target <id>] <command> [args]');
  process.exit(2);
}
const base = `http://127.0.0.1:${port}`;

const pages = async () =>
  (await (await fetch(`${base}/json/list`)).json()).filter(
    (t) => t.type === 'page' && !t.url.startsWith('devtools://')
  );

async function connect() {
  const list = await pages();
  const target = targetId ? list.find((t) => t.id === targetId) : list[0];
  if (!target) throw new Error(targetId ? `no page target ${targetId}` : 'no page target open');
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });
  let id = 0;
  const pending = new Map();
  const listeners = [];
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
    } else if (msg.method) {
      for (const fn of listeners) fn(msg);
    }
  };
  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      pending.set(++id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  return { send, on: (fn) => listeners.push(fn), close: () => ws.close(), target };
}

async function evaluate(cdp, expression) {
  const { result, exceptionDetails } = await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (exceptionDetails)
    throw new Error(exceptionDetails.exception?.description ?? exceptionDetails.text);
  return result.value;
}

async function waitForLoad(cdp) {
  for (let i = 0; i < 100; i++) {
    if ((await evaluate(cdp, 'document.readyState')) === 'complete') return;
    await Bun.sleep(100);
  }
}

async function center(cdp, selector) {
  const box = await evaluate(
    cdp,
    `(() => { const el = document.querySelector(${JSON.stringify(selector)});
      if (!el) return null; el.scrollIntoView({ block: 'center' });
      const r = el.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`
  );
  if (!box) throw new Error(`no element matches ${selector}`);
  return box;
}

const KEYS = {
  Enter: { key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, text: '\r' },
  Tab: { key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 },
  Escape: { key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 },
  Backspace: { key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8 },
};

if (command === 'tabs') {
  for (const t of await pages()) console.log(`${t.id}\t${t.url}\t${t.title}`);
  process.exit(0);
}
if (command === 'new') {
  const res = await fetch(`${base}/json/new?${encodeURIComponent(rest[0] ?? 'about:blank')}`, {
    method: 'PUT',
  });
  const t = await res.json();
  console.log(`${t.id}\t${t.url}`);
  process.exit(0);
}

const cdp = await connect();
try {
  switch (command) {
    case 'open': {
      await cdp.send('Page.navigate', { url: rest[0] });
      await Bun.sleep(200);
      await waitForLoad(cdp);
      console.log(await evaluate(cdp, 'location.href'));
      break;
    }
    case 'url':
      console.log(await evaluate(cdp, 'location.href'));
      break;
    case 'text':
      console.log(await evaluate(cdp, 'document.body.innerText'));
      break;
    case 'eval': {
      const value = await evaluate(cdp, rest.join(' '));
      console.log(typeof value === 'string' ? value : JSON.stringify(value, null, 2));
      break;
    }
    case 'click': {
      const { x, y } = await center(cdp, rest[0]);
      for (const type of ['mousePressed', 'mouseReleased']) {
        await cdp.send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
      }
      console.log(`clicked ${rest[0]}`);
      break;
    }
    case 'type': {
      const [selector, ...words] = rest;
      await evaluate(cdp, `document.querySelector(${JSON.stringify(selector)})?.focus()`);
      await cdp.send('Input.insertText', { text: words.join(' ') });
      console.log(`typed into ${selector}`);
      break;
    }
    case 'key': {
      const k = KEYS[rest[0]];
      if (!k) throw new Error(`unsupported key ${rest[0]}`);
      await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', ...k });
      await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', ...k });
      console.log(`pressed ${rest[0]}`);
      break;
    }
    case 'screenshot': {
      const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(rest[0], Buffer.from(data, 'base64'));
      console.log(rest[0]);
      break;
    }
    case 'console': {
      const seconds = Number(rest[0] ?? 5);
      cdp.on((msg) => {
        if (msg.method === 'Runtime.consoleAPICalled') {
          const text = msg.params.args.map((a) => a.value ?? a.description ?? a.type).join(' ');
          console.log(`[${msg.params.type}] ${text}`);
        } else if (msg.method === 'Runtime.exceptionThrown') {
          console.log(
            `[exception] ${msg.params.exceptionDetails.exception?.description ?? msg.params.exceptionDetails.text}`
          );
        } else if (msg.method === 'Log.entryAdded') {
          console.log(
            `[${msg.params.entry.level}] ${msg.params.entry.text} ${msg.params.entry.url ?? ''}`
          );
        }
      });
      await cdp.send('Runtime.enable');
      await cdp.send('Log.enable');
      await Bun.sleep(seconds * 1000);
      break;
    }
    default:
      throw new Error(`unknown command ${command}`);
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  cdp.close();
}
