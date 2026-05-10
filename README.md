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
| `wtc` (no args) | **Opens GUI** |
| `wtc -l python ...` | CLI mode |
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

**Build Outputs (`build/`):**

| Windows | Linux/WSL |
|---------|-----------|
| `wtc-windows-gui.exe` | `wtc-linux-gui` |
| `wtc-windows-cli.exe` | `wtc-linux-cli` |
| `word-to-code-windows-gui.exe` | `word-to-code-linux-gui` |
| `.msi` (if WiX installed) | `word-to-code-linux-cli` |

**On Native Windows:** Also builds Linux binaries via WSL (if available).

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
# Copy to a directory in your PATH, or install via MSI
# If using MSI: double-click the .msi installer
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
├── build/                  # Output (created by compile.py)
└── target/                 # Rust build artifacts
```

---

## Original Project

Originally a Python tkinter app (`main.py`) that only converted to Luau arrays. Rewritten in Rust with:
- 11 programming languages
- Smart `wtc` command (no args = GUI)
- Optional egui GUI
- Portable self-contained binaries
- MSI/.deb installer support
