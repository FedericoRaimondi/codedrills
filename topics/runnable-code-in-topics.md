# Code Snippet Runnability Criteria — LLM Authoring Guide

This document defines what makes a code snippet **runnable** or **not runnable** for each language supported by the execution backend. Use these rules when generating the `code` field in lesson entries.

---

## 🏗️ Execution Architecture (context for all rules)

| Language | Runtime | Where executed |
| --- | --- | --- |
| `javascript` | Node.js, single `.js` file, `node main.js` | Runner container |
| `typescript` | Node.js + `tsx`, single `.ts` file | Runner container |
| `python` | `python3`, single `.py` file, sandboxed harness | Runner container |
| `rust` | `rustc --edition=2021`, single `main.rs` with `fn main()` | Runner container |
| `sql` | SQLite in-memory, single `SELECT` statement | Backend (no subprocess) |

**Hard limits applying to all languages:**

- **Wall-clock timeout:** 8 seconds (10 s outer kill)
- **Output cap:** 1 MB total stdout+stderr
- **No network access** — outbound connections are blocked
- **No filesystem persistence** — each execution gets an ephemeral `/tmp/exec_*` dir that is deleted immediately after
- **No environment variables** — `process.env` / `os.environ` are not forwarded; the child sees only a hardcoded minimal `PATH`

---

## 🟡 JavaScript

**Runtime:** `node --max-old-space-size=256 --max-semi-space-size=8 main.js`  
**Execution model:** single file, CommonJS context (not ESM), no bundler, no imports resolved from other files.

### ✅ Runnable

- Any self-contained code using `console.log`, `console.warn`, `console.error`, `console.table`
- All built-in globals: `Math`, `JSON`, `Date`, `Array`, `Object`, `Map`, `Set`, `RegExp`, `Promise`, `setTimeout`, `clearTimeout`, `setInterval`, `clearInterval`
- Arrow functions, closures, classes, destructuring, spread, generators, `async`/`await`
- `setTimeout` and `setInterval` if the script exits naturally (Node drains the event loop before exit)

### ❌ Not Runnable — will error or hang

| Category | Examples | Reason |
| --- | --- | --- |
| **DOM / Browser APIs** | `document`, `window`, `navigator`, `location`, `localStorage`, `HTMLElement`, `Event`, `addEventListener` on global/DOM | Node has no DOM — `ReferenceError` |
| **ES Module syntax** | `import x from './file.js'`, `export const x`, `export default` | Runner executes a single `.js` file as CommonJS script; `import`/`export` cause a `SyntaxError` or cannot resolve relative paths |
| **`fetch` / network calls** | `fetch('https://...')`, `XMLHttpRequest`, `WebSocket` | No network access; `fetch` is available in Node ≥18 but all outbound connections are blocked — will hang until timeout |
| **Relative file imports** | `require('./utils')`, `import { x } from './math.js'` | No other files exist in the execution directory |
| **Infinite timers** | `setInterval(fn, 1000)` without `clearInterval` | Hangs the process; killed after 8 s |
| **Long `setTimeout` delays** | `setTimeout(fn, 5000)` or more | Killed before firing |
| **Shell / process access** | `child_process`, `process.exit`, `process.env` | `process` object is available but `process.env` is empty; `child_process.exec` will fail silently or be blocked |
| **`console.dir` with circular refs** | Deeply nested circular objects | Can trigger output cap or crash |
| **Comment-only or terminal snippets** | `// node main.js`, `// node --version` | Produces no output; not executable code |
| **Bare expressions with no output** | `2 + 2`, `Math.random()` (without `console.log`) | Runs silently — produces nothing visible |

---

## 🟢 Python

**Runtime:** `python3 -E harness.py` (sandboxed — the harness wraps user code in a restricted `exec()` environment)  
The harness blocks imports of a large set of modules at the language level.

### ✅ Runnable

- `print()`, all builtins (`len`, `range`, `enumerate`, `zip`, `map`, `filter`, `sorted`, etc.)
- Standard library modules **not on the blocklist**: `math`, `random`, `datetime`, `re`, `json`, `collections`, `itertools`, `functools`, `string`, `decimal`, `fractions`, `statistics`, `copy`, `heapq`, `bisect`, `struct`, `io`, `textwrap`, `unicodedata`, `pathlib` *(read-only; no writes succeed)*
- Classes, dataclasses, list/dict/set comprehensions, generators, `async`/`await`, decorators
- `open()` for reading files that the snippet itself wrote (extremely rare; the working dir is ephemeral)

### ❌ Not Runnable — blocked by harness or sandbox

| Category | Blocked identifiers | Reason |
| --- | --- | --- |
| **Introspection / meta** | `ctypes`, `gc`, `inspect`, `importlib`, `linecache`, `code`, `dis`, `ast`, `compileall` | Explicitly blocked by harness |
| **Subprocess / process** | `subprocess`, `os.system`, `os.popen`, `os.fork`, `os.exec*`, `os.spawn*` | Blocked both by harness and `ulimit`; raises `PermissionError` |
| **Networking** | `socket`, `ssl`, `http`, `urllib`, `ftplib`, `smtplib`, `telnetlib`, `xmlrpc` | Blocked by harness |
| **Concurrency** | `threading`, `multiprocessing` | Blocked by harness |
| **Serialisation helpers** | `pickle`, `pickletools` | Blocked by harness |
| **Object subclass escape** | `object.__subclasses__()` to find `_wrap_close` or `Popen` | Neutered by harness |
| **Shell access** | Any attempt to spawn a shell via any path | Blocked by ulimit `-u 64` + harness |
| **File I/O outside working dir** | Writing to `/etc`, `/app`, arbitrary `/tmp` paths | Sandbox user has no write permission outside the exec dir |
| **Infinite loops / sleep** | `while True: pass`, `time.sleep(10)` | Killed after 5 CPU seconds / 8 s wall clock |
| **`input()`** | `name = input("Enter name: ")` | No stdin is connected; blocks forever then times out |
| **Terminal / shell comments** | `# pip install requests`, `# python3 main.py` | Comment-only snippets produce no output |

---

## 🦀 Rust

**Runtime:** `rustc main.rs --edition=2021 -o main` then `./main`  
Compilation timeout: **30 s**. Execution timeout: **8 s**.

### ✅ Runnable

- Any self-contained program with a valid `fn main()`
- `println!`, `eprintln!`, `dbg!`, `print!`
- All of `std`: `Vec`, `HashMap`, `HashSet`, `String`, `Option`, `Result`, `Iterator`, closures, traits, generics, enums, pattern matching, `Box`, `Rc`, `Arc`, `Mutex`, `Cell`, `RefCell`
- `std::thread::spawn` (allowed by ulimit — but keep thread counts low)
- Async with `std` only (no external async runtime — `tokio`, `async-std` etc. are **not** available)

### ❌ Not Runnable

| Category | Examples | Reason |
| --- | --- | --- |
| **External crates** | `use serde::Serialize`, `use tokio::main`, `use reqwest` | No `Cargo.toml`; only `rustc` is used, so only `std` is available |
| **Network I/O** | `std::net::TcpStream::connect(...)`, `UdpSocket` | Network is blocked |
| **`std::process::Command`** | `Command::new("ls").output()` | Blocked by ulimit `-u 64`; will fail |
| **File writes outside working dir** | Writing to arbitrary paths | Sandbox permissions deny access |
| **Missing `fn main()`** | Snippet is only a struct/trait/function definition | Will not compile — `rustc` requires an entry point |
| **Infinite loops without output** | `loop {}` | Killed after 8 s with no output |
| **Long compilations** | Very large generated code, many macro expansions | May exceed the 30 s compile timeout |

---

## 🗄️ SQL

**Runtime:** SQLite in-memory, single `SELECT` statement only. Schema is pre-loaded with the following tables: `employees`, `departments`, `locations`, `customers`, `orders`, `products`, `books`, `students`, `sales`, `order_items`, `scores`, `stock_prices`, `contractors`, `transactions`, `events`, `metrics`, `contacts`, `reviews`, `users`, `sizes`, `colors`, `tags`, `annual_sales`, `logs`, `logins`, `daily_sales` and more.

Dialect normalisation is applied automatically: `ILIKE→LIKE`, `NOW()→datetime('now')`, `EXTRACT(x FROM y)→strftime(...)`, `STRING_AGG→GROUP_CONCAT`, `LEN→LENGTH`, `NVL→IFNULL`, `FETCH FIRST n ROWS ONLY→LIMIT n`, PostgreSQL `::cast` operator, `SELECT TOP n`.

### ✅ Runnable

- Any single `SELECT` query against the pre-loaded tables
- `JOIN`, `LEFT JOIN`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`
- Subqueries, CTEs (`WITH`), window functions (`ROW_NUMBER()`, `RANK()`, `LAG()`, `LEAD()`, etc.)
- Aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP_CONCAT`
- String functions: `LENGTH`, `UPPER`, `LOWER`, `SUBSTR`, `TRIM`, `REPLACE`, `INSTR`, `LIKE`, `GLOB`
- Date functions: `datetime('now')`, `strftime`, `date`, `julianday`
- `CASE WHEN`, `COALESCE`, `NULLIF`, `IFNULL`, `IIF`
- `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`

### ❌ Not Runnable

| Category | Examples | Reason |
| --- | --- | --- |
| **Write statements** | `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER` | Only `SELECT` readers are permitted; the backend checks `statement.reader` and rejects all others |
| **Multiple statements** | Two queries separated by `;` | Detected by the backend and rejected with an error message |
| **References to non-existent tables** | `SELECT * FROM invoices` | Table doesn't exist in the schema; SQLite returns an error |
| **Stored procedures / functions** | `CREATE FUNCTION`, `EXEC`, `CALL` | Not supported by SQLite |
| **`PRAGMA` statements** | `PRAGMA table_info(employees)` | Not a `SELECT`; rejected as non-reader |
| **External data access** | `ATTACH DATABASE`, `.import` | Not supported in the in-memory context |
| **Comment-only snippets** | `-- SELECT * FROM employees` | Stripped to empty string; returns "No SQL query provided" |

---

## ✅ Universal "Safe to Run" Checklist

Before setting a `code` field, verify all of the following:

1. **Self-contained** — the snippet does not reference any external file, module, or URL that isn't part of the language's standard library (or the pre-loaded SQL schema).
2. **Produces visible output** — there is at least one `console.log` / `print` / `println!` / `SELECT` that will produce something on stdout. Snippets that are purely definitional (no output) should set `runnable: false` or include a `console.log` call to demonstrate the result.
3. **Terminates within 8 seconds** — no infinite loops, no timers longer than ~4 s, no blocking reads.
4. **No network calls** — no `fetch`, `http`, `socket`, `TcpStream`, `requests`, or any URL reference that would be used at runtime.
5. **Single entry point** — for Rust, there is exactly one `fn main()`. For JS/TS/Python, the code runs top-to-bottom as a script.
6. **No multi-file imports** — for JS/TS, no `import`/`require` of relative paths. For Python, no imports of blocked modules.
7. **For SQL** — exactly one `SELECT` statement, targeting only the pre-loaded tables listed above.