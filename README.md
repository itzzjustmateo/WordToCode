# WordToCode

Convert lists of words to array literals in **11 programming languages**. A Rust rewrite with CLI and optional GUI.

**One-click compile script:** `python tools/compile.py`

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

## Quick Build (All Platforms)

### Prerequisites

- **Rust toolchain** (MSRV: 1.72+)
  ```bash
  # Linux/macOS/WSL
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

  # Windows
  # Download from https://rustup.rs/
  ```

### One-click Compile

```bash
python tools/compile.py
```

**What it builds:**

| Platform Running | Outputs to `build/` |
| ---------------- | -------------------- |
| **Native Windows** | `word-to-code-windows-gui.exe` (CLI + GUI), `.msi` (if cargo-wix installed), plus Linux builds via WSL |
| **WSL/Linux/macOS** | `word-to-code-linux-gui` (CLI + GUI), `word-to-code-linux-cli` (CLI-only, smaller) |

---

## Build Outputs

All binaries are **portable (self-contained)** - copy anywhere and run.

### Windows

| File | Description |
|------|-------------|
| `word-to-code-windows-gui.exe` | CLI + GUI (egui), ~15-20 MB |
| `word-to-code-<version>-x86_64.msi` | Windows installer (requires WiX + cargo-wix) |

### Linux

| File | Description |
|------|-------------|
| `word-to-code-linux-gui` | CLI + GUI (egui), ~15-20 MB |
| `word-to-code-linux-cli` | CLI-only, ~2-3 MB (much smaller) |

---

## Manual Build (Advanced)

### CLI-only (smallest)

```bash
cargo build --release --no-default-features --features cli
# Output: target/release/word-to-code
```

### CLI + GUI (egui)

```bash
cargo build --release --features gui
# Output: target/release/word-to-code
```

### Windows MSI Installer

**First-time setup:**
```powershell
# Install WiX v3 (required by cargo-wix)
dotnet tool install --global wix --version 3.14.1

# Install cargo-wix
cargo install cargo-wix
```

**Build:**
```powershell
cargo wix --package word-to-code --features gui
# Output: target/wix/word-to-code-<version>-x86_64.msi
```

### Linux .deb Package

```bash
cargo install cargo-deb
cargo deb --features gui
# Output: target/debian/word-to-code_<version>_amd64.deb

# Install
sudo dpkg -i target/debian/word-to-code_*.deb
```

---

## CLI Usage

```
word-to-code [OPTIONS]

Options:
  -l, --lang <LANG>    Target language [default: luau]
  -i, --input <FILE>   Read from file (default: stdin)
  -c, --copy           Copy output to clipboard
  -g, --gui            Launch GUI mode
  -h, --help           Print help
  -V, --version        Print version
```

### Examples

```bash
# Pipe input (default: Luau)
echo -e "hello\nworld\nfoo" | word-to-code

# Specific language
echo -e "hello\nworld" | word-to-code -l python

# From file + copy to clipboard
word-to-code -l rust -i words.txt -c

# List all supported languages
word-to-code --help
```

---

## GUI Usage

```bash
# Windows
.\build\word-to-code-windows-gui.exe --gui

# Linux
./build/word-to-code-linux-gui --gui
```

**GUI Features:**
- Dropdown to select target language (11 languages)
- Multi-line text input area
- "Convert" button
- "Copy to Clipboard" button
- "Clear All" button
- Read-only output preview with monospace font

---

## Project Structure

```
WordToCode/
├── Cargo.toml              # Rust project config
├── README.md               # This file
├── .gitignore
├── src/
│   ├── main.rs             # CLI + GUI entry point
│   └── lib.rs              # Core conversion logic (all languages)
├── tools/
│   └── compile.py          # One-click build script
├── build/                  # Output (created by compile.py)
└── target/                 # Rust build artifacts
```

---

## Original Project

Originally a Python tkinter app (`main.py`) that only converted to Luau arrays. Rewritten in Rust with:
- 11 programming languages supported
- CLI mode with piping support
- Optional GUI (egui)
- Portable self-contained binaries
- Installer generation
