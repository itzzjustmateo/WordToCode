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

## Compile

### Prerequisites

- **Rust toolchain** (MSRV: 1.70+)
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```

### CLI Only (Fast Build)

```bash
cargo build --release
```

Binary: `target/release/word-to-code`

### CLI + GUI (egui)

```bash
cargo build --release --features gui
```

Binary: `target/release/word-to-code`

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

## GUI Usage

```bash
word-to-code --gui
```

Requires build with `--features gui`. Features:

- Dropdown to select target language
- Multi-line text input
- Convert & Copy to Clipboard buttons
- Live preview

## Original Project

Originally a Python tkinter app (`main.py`) that only converted to Luau arrays.
