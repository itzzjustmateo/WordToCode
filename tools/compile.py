#!/usr/bin/env python3
"""
Compile WordToCode for multiple platforms.

On Native Windows:
  1. Windows .exe (CLI + GUI)
  2. Windows .msi installer
  3. Via WSL: Linux binary (CLI + GUI)
  4. Via WSL: Linux binary (CLI-only)

On WSL/Linux/macOS:
  - Linux/macOS binary (CLI + GUI)
  - Linux/macOS binary (CLI-only)

All outputs go to build/ directory.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
BUILD_DIR = PROJECT_ROOT / "build"
CARGO_TARGET = PROJECT_ROOT / "target"

IS_WINDOWS = platform.system() == "Windows"
IS_WSL = "microsoft" in platform.system().lower() or os.path.exists("/proc/version") and "microsoft" in open("/proc/version").read().lower() if os.path.exists("/proc/version") else False

def run(cmd, cwd=None, check=True, shell=False):
    """Run a command, show output."""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    print(f"\n>>> {cmd_str}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(PROJECT_ROOT),
            check=check,
            text=True,
            shell=shell
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if check:
            sys.exit(1)
        return e

def run_wsl(cmd):
    """Run a command via WSL from Windows."""
    wsl_path = str(PROJECT_ROOT).replace("\\", "/").replace("C:", "/mnt/c")
    wsl_cmd = f"cd '{wsl_path}' && {cmd}"
    return run(["wsl", "-e", "bash", "-c", wsl_cmd], check=True)

def check_rust():
    """Verify Rust is installed."""
    try:
        subprocess.run(["cargo", "--version"], check=True, capture_output=True, text=True)
        subprocess.run(["rustc", "--version"], check=True, capture_output=True, text=True)
        print("✓ Rust toolchain found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_cargo_wix():
    """Check if cargo-wix is available."""
    if not IS_WINDOWS:
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
        print("         Install with:")
        print("         1. dotnet tool install --global wix --version 3.14.1")
        print("         2. cargo install cargo-wix")
        return False

def check_wsl():
    """Check if WSL is available from Windows."""
    if not IS_WINDOWS:
        return False
    try:
        result = subprocess.run(
            ["wsl", "--status"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ WSL available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARNING: WSL not available. Linux builds will be skipped.")
        return False

def clean_build():
    """Remove old build directory."""
    if BUILD_DIR.exists():
        print(f"\n>>> Cleaning build/ directory")
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

def build_windows(features="gui"):
    """Build Windows binary."""
    suffix = "-gui" if features == "gui" else "-cli"
    print(f"\n>>> Building Windows{suffix} (release mode)")

    run([
        "cargo", "build",
        "--release",
        "--features", features,
        "--package", "word-to-code"
    ])

    src = CARGO_TARGET / "release" / "word-to-code.exe"
    dst = BUILD_DIR / f"word-to-code-windows{suffix}.exe"

    if src.exists():
        shutil.copy2(src, dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {dst.name} ({size_mb:.2f} MB)")
        return dst
    return None

def build_msi():
    """Build MSI installer (Windows only)."""
    print("\n>>> Building MSI installer")

    run([
        "cargo", "wix",
        "--package", "word-to-code",
        "--features", "gui",
        "--nocapture"
    ])

    wix_dir = CARGO_TARGET / "wix"
    if wix_dir.exists():
        for msi in wix_dir.glob("*.msi"):
            dst = BUILD_DIR / msi.name
            shutil.copy2(msi, dst)
            size_mb = dst.stat().st_size / (1024 * 1024)
            print(f"✓ {dst.name} ({size_mb:.2f} MB)")
            return dst
    return None

def build_linux_via_wsl():
    """Build Linux binaries using WSL."""
    print("\n" + "=" * 60)
    print("Building Linux binaries via WSL...")
    print("=" * 60)

    print("\n>>> Checking Rust in WSL...")
    try:
        run_wsl("cargo --version")
    except SystemExit:
        print("WARNING: Rust not installed in WSL. Install with:")
        print("         wsl -e curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | wsl -e sh -s -- -y")
        return

    print("\n>>> Building Linux (CLI + GUI) via WSL...")
    run_wsl("cargo build --release --features gui --package word-to-code")

    linux_gui_src = PROJECT_ROOT / "target" / "release" / "word-to-code"
    linux_gui_dst = BUILD_DIR / "word-to-code-linux-gui"
    if linux_gui_src.exists():
        shutil.copy2(linux_gui_src, linux_gui_dst)
        size_mb = linux_gui_dst.stat().st_size / (1024 * 1024)
        print(f"✓ {linux_gui_dst.name} ({size_mb:.2f} MB)")

    print("\n>>> Building Linux (CLI-only) via WSL...")
    run_wsl("cargo build --release --no-default-features --features cli --package word-to-code")

    linux_cli_src = PROJECT_ROOT / "target" / "release" / "word-to-code"
    linux_cli_dst = BUILD_DIR / "word-to-code-linux-cli"
    if linux_cli_src.exists():
        shutil.copy2(linux_cli_src, linux_cli_dst)
        size_mb = linux_cli_dst.stat().st_size / (1024 * 1024)
        print(f"✓ {linux_cli_dst.name} ({size_mb:.2f} MB)")

def build_linux_native():
    """Build Linux binaries on native Linux/WSL."""
    print("\n>>> Building Linux (CLI + GUI)...")
    run([
        "cargo", "build",
        "--release",
        "--features", "gui",
        "--package", "word-to-code"
    ])

    src = CARGO_TARGET / "release" / "word-to-code"
    dst = BUILD_DIR / "word-to-code-linux-gui"
    if src.exists():
        shutil.copy2(src, dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {dst.name} ({size_mb:.2f} MB)")

    print("\n>>> Building Linux (CLI-only)...")
    run([
        "cargo", "build",
        "--release",
        "--no-default-features",
        "--features", "cli",
        "--package", "word-to-code"
    ])

    src = CARGO_TARGET / "release" / "word-to-code"
    dst = BUILD_DIR / "word-to-code-linux-cli"
    if src.exists():
        shutil.copy2(src, dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {dst.name} ({size_mb:.2f} MB)")

def show_summary():
    """Show build outputs."""
    print("\n" + "=" * 60)
    print("BUILD COMPLETED")
    print("=" * 60)
    print(f"Output directory: {BUILD_DIR}")
    print("\nBuilt artifacts:")

    total_size = 0
    if BUILD_DIR.exists():
        for item in sorted(BUILD_DIR.iterdir()):
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                total_size += item.stat().st_size
                print(f"  - {item.name} ({size_mb:.2f} MB)")

    if total_size == 0:
        print("  (none)")
    else:
        print(f"\nTotal: {total_size / (1024 * 1024):.2f} MB")

    print("\n" + "-" * 60)
    print("Usage:")
    print("-" * 60)
    if IS_WINDOWS:
        print("\nWindows:")
        print("  .\\build\\word-to-code-windows-gui.exe --help")
        print("  .\\build\\word-to-code-windows-gui.exe --gui")
        print("  .\\build\\word-to-code-windows-gui.exe (same as above, both CLI+GUI)")
    else:
        print("\nLinux:")
        print("  ./build/word-to-code-linux-gui --help")
        print("  ./build/word-to-code-linux-gui --gui")
        print("  ./build/word-to-code-linux-cli --help  (smaller, no GUI support)")

def main():
    print("=" * 60)
    print("WordToCode - Compile Script")
    print("=" * 60)
    print(f"Platform: {platform.system()}" + (" (WSL)" if IS_WSL else ""))
    print(f"Project:  {PROJECT_ROOT}")

    clean_build()

    if IS_WINDOWS and not IS_WSL:
        print("\n" + "=" * 60)
        print("Native Windows detected")
        print("=" * 60)

        if not check_rust():
            print("ERROR: Rust not found on Windows. Install from https://rustup.rs/")
            sys.exit(1)

        has_wix = check_cargo_wix()
        has_wsl = check_wsl()

        build_windows("gui")
        if has_wix:
            build_msi()
        if has_wsl:
            build_linux_via_wsl()

    else:
        print("\n" + "=" * 60)
        print("Linux/WSL/macOS detected")
        print("=" * 60)

        if not check_rust():
            print("ERROR: Rust not found. Install from https://rustup.rs/")
            sys.exit(1)

        build_linux_native()

    show_summary()

if __name__ == "__main__":
    main()
