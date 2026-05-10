# WordToCode

Convert lists of words to array literals in **11 programming languages**. Rust rewrite with CLI + optional GUI.

**Short command:** `wtc`  
**One-click compile:** `python tools/compile.py`

---

## Quick Start

```bash
# Build all binaries
python tools/compile.py

# Use the built binary (Linux/WSL example)
./build/wtc-linux-gui                    # Opens GUI
echo "hello" | ./build/wtc-linux-gui -l python   # CLI mode
```

---

## `wtc` Usage (Short Command)

| Command | What it does |
|---------|--------------|
| `wtc` (no args, no pipe) | **Opens GUI** |
| `wtc -l python ...` | CLI mode |
| `echo "x" \| wtc` | CLI mode (detects pipe) |
| `wtc --gui` | Opens GUI (explicit) |
| `wtc --help` | Show help |
| `wtc --version` | Show version |

---

## Supported Languages

| Language   | CLI Alias          | Output Example                                   |
| ---------- | ------------------ | ------------------------------------------------ |
| Lua        | `lua`              | `local words = { "a", "b" }`                     |
| Luau       | `luau`             | `{ "a", "b" }`                                   |
| Python     | `python`, `py`     | `words = ["a", "b"]`                             |
| Java       | `java`             | `String[] words = { "a", "b" };`                 |
| Kotlin     | `kotlin`, `kt`     | `val words = listOf("a", "b")`                   |
| Rust       | `rust`, `rs`       | `let words = vec!["a", "b"];`                    |
| JavaScript | `javascript`, `js` | `const words = ["a", "b"];`                      |
| TypeScript | `typescript`, `ts` | `const words: string[] = ["a", "b"];`            |
| C++        | `cpp`, `c++`       | `std::vector<std::string> words = { "a", "b" };` |
| C#         | `cs`, `csharp`     | `string[] words = { "a", "b" };`                 |
| C          | `c`                | `const char* words[] = { "a", "b", NULL };`      |

---

## Build

### Prerequisites

- **Rust toolchain** (MSRV: 1.72+)
  ```bash
  # Linux/macOS/WSL
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

  # Windows: https://rustup.rs/
  ```

### One-click Compile

```bash
python tools/compile.py
```

---

## What Gets Built

**Portable ZIP** is always created (no extra dependencies needed).

| Output | Format | Dependencies |
|--------|--------|--------------|
| Portable ZIP | `.zip` | None (always created) |
| NSIS Installer | `.exe` | NSIS (`makensis` in PATH) - optional |
| WiX MSI | `.msi` | WiX v3.14 + cargo-wix - legacy/optional |

**Build Outputs (`build/`):**

| Windows | Linux/WSL |
|---------|-----------|
| `wtc-windows-gui.exe` | `wtc-linux-gui` |
| `wtc-windows-cli.exe` | `wtc-linux-cli` |
| `word-to-code-windows-gui.exe` | `word-to-code-linux-gui` |
| `WordToCode-portable-windows.zip` | `WordToCode-portable-linux.zip` |
| `WordToCode-Setup.exe` (if NSIS) | |

---

## Distribution Options

### 1. Portable ZIP (Recommended, Default)

**Always created** - no extra dependencies needed.

Just distribute the `.zip` file. Users extract and run.

```
WordToCode-portable-windows.zip
├── wtc-windows-gui.exe    (main: CLI + GUI)
├── wtc-windows-cli.exe    (smaller: CLI only)
└── README.txt
```

### 2. NSIS Installer (Optional)

NSIS is lightweight and doesn't have the WiX v3/v4 confusion.

**Install NSIS:**
- Download from: https://nsis.sourceforge.io/Download
- Or with winget: `winget install NSIS.NSIS`
- Make sure `makensis` is in your PATH

**The compile script will auto-detect and use it.**

Output: `build/WordToCode-Setup.exe`

### 3. WiX MSI (Legacy, Not Recommended)

WiX has v3 vs v4 compatibility issues. Only use if you specifically need MSI.

**Must install IN THIS ORDER:**

1. **WiX Toolset v3.14** (NOT v4)
   - Download: https://github.com/wixtoolset/wix3/releases
   - Look for `wix314.exe`
   - Run installer, **restart terminal**

2. **cargo-wix**
   ```powershell
   cargo install cargo-wix
   ```

The compile script will attempt MSI if both are found.

---

## CLI Usage

```
wtc [OPTIONS]

Options:
  -l, --lang <LANG>    Target language [default: luau]
  -i, --input <FILE>   Read from file (default: stdin)
  -c, --copy           Copy output to clipboard
  -g, --gui            Launch GUI mode
  -h, --help           Print help
  -V, --version        Print version
```

### CLI Examples

```bash
# Pipe input
echo -e "hello\nworld\nfoo" | wtc

# Specific language
echo -e "hello\nworld" | wtc -l python

# From file + copy to clipboard
wtc -l rust -i words.txt -c
```

---

## Install (System-wide)

### Linux

```bash
# Copy to a location in your PATH
sudo cp ./build/wtc-linux-gui /usr/local/bin/wtc

# Now just run:
wtc                    # opens GUI
wtc -l python ...      # CLI mode
```

### Windows

```powershell
# Option 1: Use the portable EXE
# Copy to a directory in your PATH

# Option 2: Use NSIS installer (if built)
# Double-click: .\build\WordToCode-Setup.exe

# Option 3: Extract portable ZIP anywhere
```

---

## Project Structure

```
WordToCode/
├── Cargo.toml              # Rust project config
├── README.md               # This file
├── .gitignore
├── src/
│   ├── main.rs             # CLI + GUI entry point
│   └── lib.rs              # Core conversion logic (11 languages)
├── tools/
│   └── compile.py          # One-click build script
├── wix/                    # Created by `cargo wix init` (optional)
│   └── main.wxs            # WiX MSI template
├── build/                  # Output (created by compile.py)
│   ├── wtc-linux-gui       # Shortcut binary
│   ├── word-to-code-linux-gui
│   ├── WordToCode-portable-linux.zip
│   └── ...
└── target/                 # Rust build artifacts
```

---

## Original Project

Originally a Python tkinter app (`main.py`) that only converted to Luau arrays. Rewritten in Rust with:
- 11 programming languages
- Smart `wtc` command (no args = GUI)
- Optional egui GUI
- Portable self-contained binaries
- Multiple installer options (portable ZIP, NSIS, WiX)
