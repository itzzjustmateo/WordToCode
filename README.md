# WordToCode

Convert lists of words to array literals in **11 programming languages**. A Rust rewrite with CLI and optional GUI.

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

## Prerequisites

- **Rust toolchain** (MSRV: 1.70+)
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```

---

## Portable Builds (Single .exe / Binary)

Rust produces statically-linked, self-contained executables.

### Build

```bash
# CLI-only (smaller)
cargo build --release

# CLI + GUI (egui)
cargo build --release --features gui
```

### Output

| Platform | Portable Binary Location          |
| -------- | --------------------------------- |
| Windows  | `target\release\word-to-code.exe` |
| Linux    | `target/release/word-to-code`     |
| macOS    | `target/release/word-to-code`     |

**Portable = just copy the binary anywhere and run it.**

---

## Installers

### Windows (MSI Installer via WiX)

**First-time setup:**

```powershell
# Install WiX v3
dotnet tool install --global wix --version 3.14.1

# Install cargo-wix
cargo install cargo-wix
```

**Build MSI installer:**

```powershell
# CLI-only
cargo wix --package word-to-code --output target/wix/

# CLI + GUI
cargo wix --package word-to-code --features gui --output target/wix/
```

**Output:** `target/wix/word-to-code-<version>-x86_64.msi`

---

### Linux (.deb Package)

**First-time setup:**

```bash
cargo install cargo-deb
```

**Build .deb package:**

```bash
# CLI-only
cargo deb

# CLI + GUI
cargo deb --features gui
```

**Output:** `target/debian/word-to-code_<version>_amd64.deb`

**Install:**

```bash
sudo dpkg -i target/debian/word-to-code_*.deb
```

---

### Linux (Generic tarball / Archive)

```bash
# Build first
cargo build --release --features gui

# Create portable archive
cd target/release
tar czvf word-to-code-portable.tar.gz word-to-code
# or for Windows: zip word-to-code-portable.zip word-to-code.exe
```

---

### macOS (.dmg)

**Build:**

```bash
cargo build --release --features gui
```

**Manual .dmg creation:**

1. Create a folder `WordToCode`
2. Copy `target/release/word-to-code` into it
3. Open Disk Utility → File → New Image → Image from Folder

Or use `cargo-bundle`:

```bash
cargo install cargo-bundle
cargo bundle --release --features gui
```

**Output:** `target/release/bundle/osx/WordToCode.app`

---

## CLI Usage

```
word-to-code [OPTIONS]

Options:
  -l, --lang <LANG>    Target language [default: luau]
  -i, --input <FILE>   Read from file (default: stdin)
  -c, --copy           Copy output to clipboard
  -g, --gui            Launch GUI
  -h, --help           Print help
```

### Examples

```bash
# Pipe input
echo -e "hello\nworld\nfoo" | word-to-code

# Specific language
echo -e "hello\nworld" | word-to-code -l python

# From file
word-to-code -l rust -i words.txt

# To clipboard
echo -e "apple\nbanana" | word-to-code -l js -c
```

---

## GUI Usage

```bash
word-to-code --gui
```

Requires build with `--features gui`. Features:

- Dropdown to select target language
- Multi-line text input
- Convert & Copy to Clipboard buttons
- Live preview

---

## Cross-Compile (Portable for Other Platforms)

### Windows → Linux

```bash
rustup target add x86_64-unknown-linux-gnu
cargo build --release --target x86_64-unknown-linux-gnu
```

### Linux → Windows

```bash
rustup target add x86_64-pc-windows-gnu
cargo build --release --target x86_64-pc-windows-gnu
```

---

## Original Project

Originally a Python tkinter app (`main.py`) that only converted to Luau arrays.
