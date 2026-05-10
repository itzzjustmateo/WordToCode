use clap::Parser;
use std::io::{self, Read};
use word_to_code::{convert_words, parse_input, Language};

#[cfg(feature = "gui")]
use eframe::egui;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Target programming language (lua, luau, python, java, kotlin, rust, js, ts, cpp, csharp, c)
    #[arg(short, long, default_value = "luau")]
    lang: String,

    /// Launch GUI mode
    #[arg(short, long)]
    gui: bool,

    /// Input file (reads from stdin if not provided)
    #[arg(short, long)]
    input: Option<std::path::PathBuf>,

    /// Copy output to clipboard
    #[arg(short, long)]
    copy: bool,
}

fn main() {
    let args = Args::parse();

    #[cfg(feature = "gui")]
    {
        if args.gui {
            let native_options = eframe::NativeOptions {
                viewport: egui::ViewportBuilder::default()
                    .with_inner_size([700.0, 500.0])
                    .with_resizable(true),
                ..Default::default()
            };
            eframe::run_native(
                "Words → Code Converter",
                native_options,
                Box::new(|cc| Ok(Box::new(App::new(cc)))),
            )
            .expect("Failed to run GUI");
            return;
        }
    }

    #[cfg(not(feature = "gui"))]
    {
        if args.gui {
            eprintln!("GUI feature not enabled. Recompile with --features gui");
            std::process::exit(1);
        }
    }

    let language = match Language::from_name(&args.lang) {
        Some(lang) => lang,
        None => {
            eprintln!("Unknown language: {}", args.lang);
            eprintln!("Available languages:");
            for lang in Language::all() {
                eprintln!("  - {} (or aliases)", lang.name().to_lowercase());
            }
            std::process::exit(1);
        }
    };

    let input = if let Some(path) = args.input {
        match std::fs::read_to_string(&path) {
            Ok(content) => content,
            Err(e) => {
                eprintln!("Failed to read file {}: {}", path.display(), e);
                std::process::exit(1);
            }
        }
    } else {
        let mut buffer = String::new();
        io::stdin()
            .read_to_string(&mut buffer)
            .expect("Failed to read from stdin");
        buffer
    };

    let words = parse_input(&input);
    let result = convert_words(&words, language);

    if args.copy {
        match arboard::Clipboard::new() {
            Ok(mut clipboard) => {
                if let Err(e) = clipboard.set_text(result.clone()) {
                    eprintln!("Failed to copy to clipboard: {}", e);
                } else {
                    eprintln!("Copied to clipboard!");
                }
            }
            Err(e) => eprintln!("Failed to access clipboard: {}", e),
        }
    }

    println!("{}", result);
}

#[cfg(feature = "gui")]
struct App {
    input_text: String,
    output_text: String,
    selected_lang: Language,
    copied_message: Option<String>,
}

#[cfg(feature = "gui")]
impl App {
    fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        Self {
            input_text: String::new(),
            output_text: String::new(),
            selected_lang: Language::Luau,
            copied_message: None,
        }
    }
}

#[cfg(feature = "gui")]
impl eframe::App for App {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Words → Code Converter");
            ui.add_space(10.0);

            ui.horizontal(|ui| {
                ui.label("Target Language:");
                egui::ComboBox::from_label("")
                    .selected_text(self.selected_lang.name())
                    .show_ui(ui, |ui| {
                        for lang in Language::all() {
                            ui.selectable_value(&mut self.selected_lang, *lang, lang.name());
                        }
                    });
            });

            ui.add_space(10.0);
            ui.label("Input words (one per line):");

            let input_response = ui.add(
                egui::TextEdit::multiline(&mut self.input_text)
                    .font(egui::TextStyle::Monospace)
                    .desired_rows(8)
                    .desired_width(f32::INFINITY),
            );

            ui.horizontal(|ui| {
                if ui.button("Convert").clicked() || input_response.lost_focus() {
                    let words = parse_input(&self.input_text);
                    self.output_text = convert_words(&words, self.selected_lang);
                    self.copied_message = None;
                }

                if ui.button("Copy to Clipboard").clicked() && !self.output_text.is_empty() {
                    match arboard::Clipboard::new() {
                        Ok(mut clipboard) => {
                            if clipboard.set_text(self.output_text.clone()).is_ok() {
                                self.copied_message = Some("Copied!".to_string());
                            } else {
                                self.copied_message = Some("Failed to copy".to_string());
                            }
                        }
                        Err(_) => {
                            self.copied_message = Some("Clipboard unavailable".to_string());
                        }
                    }
                }

                if ui.button("Clear All").clicked() {
                    self.input_text.clear();
                    self.output_text.clear();
                    self.copied_message = None;
                }

                if let Some(msg) = &self.copied_message {
                    ui.label(msg);
                }
            });

            ui.add_space(10.0);
            ui.label(format!("{} output:", self.selected_lang.name()));

            ui.add(
                egui::TextEdit::multiline(&mut self.output_text.as_str())
                    .font(egui::TextStyle::Monospace)
                    .desired_rows(10)
                    .desired_width(f32::INFINITY)
                    .interactive(false),
            );
        });
    }
}
