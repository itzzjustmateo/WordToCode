use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Language {
    Lua,
    Luau,
    Python,
    Java,
    Kotlin,
    Rust,
    JavaScript,
    TypeScript,
    CPlusPlus,
    CSharp,
    C,
}

impl Language {
    pub fn all() -> &'static [Language] {
        &[
            Language::Lua,
            Language::Luau,
            Language::Python,
            Language::Java,
            Language::Kotlin,
            Language::Rust,
            Language::JavaScript,
            Language::TypeScript,
            Language::CPlusPlus,
            Language::CSharp,
            Language::C,
        ]
    }

    pub fn name(&self) -> &'static str {
        match self {
            Language::Lua => "Lua",
            Language::Luau => "Luau",
            Language::Python => "Python",
            Language::Java => "Java",
            Language::Kotlin => "Kotlin",
            Language::Rust => "Rust",
            Language::JavaScript => "JavaScript",
            Language::TypeScript => "TypeScript",
            Language::CPlusPlus => "C++",
            Language::CSharp => "C#",
            Language::C => "C",
        }
    }

    pub fn from_name(name: &str) -> Option<Language> {
        let name_lower = name.to_lowercase();
        match name_lower.as_str() {
            "lua" => Some(Language::Lua),
            "luau" => Some(Language::Luau),
            "python" | "py" => Some(Language::Python),
            "java" => Some(Language::Java),
            "kotlin" | "kt" => Some(Language::Kotlin),
            "rust" | "rs" => Some(Language::Rust),
            "javascript" | "js" => Some(Language::JavaScript),
            "typescript" | "ts" => Some(Language::TypeScript),
            "c++" | "cpp" | "cxx" => Some(Language::CPlusPlus),
            "c#" | "csharp" | "cs" => Some(Language::CSharp),
            "c" => Some(Language::C),
            _ => None,
        }
    }
}

impl fmt::Display for Language {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.name())
    }
}

fn escape_string(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
}

pub fn convert_words(words: &[String], language: Language) -> String {
    let trimmed_words: Vec<String> = words
        .iter()
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
        .collect();

    match language {
        Language::Lua => convert_lua(&trimmed_words),
        Language::Luau => convert_luau(&trimmed_words),
        Language::Python => convert_python(&trimmed_words),
        Language::Java => convert_java(&trimmed_words),
        Language::Kotlin => convert_kotlin(&trimmed_words),
        Language::Rust => convert_rust(&trimmed_words),
        Language::JavaScript => convert_javascript(&trimmed_words),
        Language::TypeScript => convert_typescript(&trimmed_words),
        Language::CPlusPlus => convert_cpp(&trimmed_words),
        Language::CSharp => convert_csharp(&trimmed_words),
        Language::C => convert_c(&trimmed_words),
    }
}

pub fn parse_input(input: &str) -> Vec<String> {
    input.lines().map(|s| s.to_string()).collect()
}

fn convert_lua(words: &[String]) -> String {
    if words.is_empty() {
        return "local words = {}".to_string();
    }

    let mut lines = vec!["local words = {".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("}".to_string());

    lines.join("\n")
}

fn convert_luau(words: &[String]) -> String {
    if words.is_empty() {
        return "{\n}".to_string();
    }

    let mut lines = vec!["{".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("}".to_string());

    lines.join("\n")
}

fn convert_python(words: &[String]) -> String {
    if words.is_empty() {
        return "words = []".to_string();
    }

    let mut lines = vec!["words = [".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("]".to_string());

    lines.join("\n")
}

fn convert_java(words: &[String]) -> String {
    if words.is_empty() {
        return "String[] words = {};".to_string();
    }

    let mut lines = vec!["String[] words = {".to_string()];
    for (i, word) in words.iter().enumerate() {
        if i == words.len() - 1 {
            lines.push(format!("    \"{}\"", escape_string(word)));
        } else {
            lines.push(format!("    \"{}\",", escape_string(word)));
        }
    }
    lines.push("};".to_string());

    lines.join("\n")
}

fn convert_kotlin(words: &[String]) -> String {
    if words.is_empty() {
        return "val words = listOf<String>()".to_string();
    }

    let mut lines = vec!["val words = listOf(".to_string()];
    for (i, word) in words.iter().enumerate() {
        if i == words.len() - 1 {
            lines.push(format!("    \"{}\"", escape_string(word)));
        } else {
            lines.push(format!("    \"{}\",", escape_string(word)));
        }
    }
    lines.push(")".to_string());

    lines.join("\n")
}

fn convert_rust(words: &[String]) -> String {
    if words.is_empty() {
        return "let words: Vec<&str> = vec![];".to_string();
    }

    let mut lines = vec!["let words = vec![".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("];".to_string());

    lines.join("\n")
}

fn convert_javascript(words: &[String]) -> String {
    if words.is_empty() {
        return "const words = [];".to_string();
    }

    let mut lines = vec!["const words = [".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("];".to_string());

    lines.join("\n")
}

fn convert_typescript(words: &[String]) -> String {
    if words.is_empty() {
        return "const words: string[] = [];".to_string();
    }

    let mut lines = vec!["const words: string[] = [".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("];".to_string());

    lines.join("\n")
}

fn convert_cpp(words: &[String]) -> String {
    if words.is_empty() {
        return "std::vector<std::string> words = {};".to_string();
    }

    let mut lines = vec!["#include <vector>".to_string(), "#include <string>".to_string(), "".to_string()];
    lines.push("std::vector<std::string> words = {".to_string());
    for (i, word) in words.iter().enumerate() {
        if i == words.len() - 1 {
            lines.push(format!("    \"{}\"", escape_string(word)));
        } else {
            lines.push(format!("    \"{}\",", escape_string(word)));
        }
    }
    lines.push("};".to_string());

    lines.join("\n")
}

fn convert_csharp(words: &[String]) -> String {
    if words.is_empty() {
        return "string[] words = {};".to_string();
    }

    let mut lines = vec!["string[] words = {".to_string()];
    for (i, word) in words.iter().enumerate() {
        if i == words.len() - 1 {
            lines.push(format!("    \"{}\"", escape_string(word)));
        } else {
            lines.push(format!("    \"{}\",", escape_string(word)));
        }
    }
    lines.push("};".to_string());

    lines.join("\n")
}

fn convert_c(words: &[String]) -> String {
    if words.is_empty() {
        return "const char* words[] = { NULL };".to_string();
    }

    let mut lines = vec!["const char* words[] = {".to_string()];
    for word in words {
        lines.push(format!("    \"{}\",", escape_string(word)));
    }
    lines.push("    NULL".to_string());
    lines.push("};".to_string());

    lines.join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_luau_conversion() {
        let input = vec!["hello".to_string(), "world".to_string()];
        let result = convert_words(&input, Language::Luau);
        assert!(result.contains("\"hello\""));
        assert!(result.contains("\"world\""));
    }

    #[test]
    fn test_empty_input() {
        let input = vec![];
        let result = convert_words(&input, Language::Python);
        assert!(!result.contains('"'));
    }

    #[test]
    fn test_language_from_name() {
        assert_eq!(Language::from_name("python"), Some(Language::Python));
        assert_eq!(Language::from_name("py"), Some(Language::Python));
        assert_eq!(Language::from_name("rust"), Some(Language::Rust));
        assert_eq!(Language::from_name("js"), Some(Language::JavaScript));
        assert_eq!(Language::from_name("ts"), Some(Language::TypeScript));
        assert_eq!(Language::from_name("cpp"), Some(Language::CPlusPlus));
        assert_eq!(Language::from_name("cs"), Some(Language::CSharp));
        assert_eq!(Language::from_name("invalid"), None);
    }
}
