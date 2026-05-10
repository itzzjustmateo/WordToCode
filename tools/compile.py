#!/usr/bin/env python3
"""
Compile WordToCode with GUI + CLI support.
Outputs portable EXE and MSI installer to build/ directory.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
CARGO_TARGET = PROJECT_ROOT / "target"
RELEASE_DIR = CARGO_TARGET / "release"
WIX_DIR = CARGO_TARGET / "wix"

def run(cmd, cwd=None):
    """Run a command, show output, raise on error."""
    print(f"\n>>> {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            check=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        sys.exit(1)

def check_rust():
    """Verify Rust is installed."""
    try:
        subprocess.run(["cargo", "--version"], check=True, capture_output=True, text=True)
        subprocess.run(["rustc", "--version"], check=True, capture_output=True, text=True)
        print("✓ Rust toolchain found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Rust not found. Install from https://rustup.rs/")
        sys.exit(1)

def check_cargo_wix():
    """Check if cargo-wix is available (Windows only)."""
    if platform.system() != "Windows":
        return False
    try:
        result = subprocess.run(
            ["cargo", "wix", "--version"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ cargo-wix found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARNING: cargo-wix not found. MSI installer will be skipped.")
        print("         To create MSI installers:")
        print("         1. Install WiX v3: dotnet tool install --global wix --version 3.14.1")
        print("         2. Install cargo-wix: cargo install cargo-wix")
        return False

def clean_build():
    """Remove old build directory."""
    if BUILD_DIR.exists():
        print(f"\n>>> Cleaning build/ directory")
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

def build_release():
    """Build CLI + GUI in release mode with optimizations."""
    print("\n>>> Building release (CLI + GUI enabled)")
    run([
        "cargo", "build",
        "--release",
        "--features", "gui",
        "--package", "word-to-code"
    ])

def copy_portable():
    """Copy portable executable to build/."""
    exe_name = "word-to-code.exe" if platform.system() == "Windows" else "word-to-code"
    src = RELEASE_DIR / exe_name
    dst = BUILD_DIR / f"word-to-code-portable{'.exe' if platform.system() == 'Windows' else ''}"

    if src.exists():
        print(f"\n>>> Copying portable: {src} -> {dst}")
        shutil.copy2(src, dst)
        print(f"✓ Portable binary: {dst}")
    else:
        print(f"WARNING: Portable binary not found at {src}")

def build_msi(has_wix):
    """Build MSI installer (Windows + cargo-wix only)."""
    if platform.system() != "Windows":
        print(f"\n>>> Skipping MSI (not Windows: {platform.system()})")
        return

    if not has_wix:
        print("\n>>> Skipping MSI (cargo-wix not installed)")
        return

    print("\n>>> Building MSI installer")
    run([
        "cargo", "wix",
        "--package", "word-to-code",
        "--features", "gui",
        "--nocapture"
    ])

    if WIX_DIR.exists():
        for msi in WIX_DIR.glob("*.msi"):
            dst = BUILD_DIR / msi.name
            print(f">>> Copying MSI: {msi} -> {dst}")
            shutil.copy2(msi, dst)
            print(f"✓ MSI installer: {dst}")

def show_summary():
    """Show build outputs."""
    print("\n" + "=" * 60)
    print("BUILD COMPLETED")
    print("=" * 60)
    print(f"Output directory: {BUILD_DIR}")
    print("\nFiles in build/:")

    if BUILD_DIR.exists():
        for item in sorted(BUILD_DIR.iterdir()):
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                print(f"  - {item.name} ({size_mb:.2f} MB)")
    else:
        print("  (empty)")

    print("\nTo run:")
    exe_suffix = ".exe" if platform.system() == "Windows" else ""
    print(f"  Portable: .\\build\\word-to-code-portable{exe_suffix}")
    print(f"  CLI:      .\\build\\word-to-code-portable{exe_suffix} --help")
    print(f"  GUI:      .\\build\\word-to-code-portable{exe_suffix} --gui")

def main():
    print("=" * 60)
    print("WordToCode - Compile Script")
    print("=" * 60)
    print(f"Platform: {platform.system()}")
    print(f"Project:  {PROJECT_ROOT}")

    check_rust()
    has_wix = check_cargo_wix()
    clean_build()
    build_release()
    copy_portable()
    build_msi(has_wix)
    show_summary()

if __name__ == "__main__":
    main()
