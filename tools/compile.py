#!/usr/bin/env python3
"""
Compile WordToCode for multiple platforms.

AUTOMATIC DEPENDENCY SETUP (Windows + Linux/WSL):
  - Checks for Rust toolchain (cargo, rustc)
  - Installs Rust automatically if not found
  - On Windows: Checks for Scoop, installs if missing
  - Installs NSIS via Scoop for Windows installer creation

All outputs go to build/ directory.

Flags:
  --install   Copy the wtc binary to ~/.local/bin (Linux/WSL)
              or %USERPROFILE%\bin (Windows) after building.
  --no-setup  Skip automatic Rust/Scoop/NSIS setup.
              Use this if you want to install dependencies manually.
"""

import os
import sys
import shutil
import subprocess
import platform
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
BUILD_DIR = PROJECT_ROOT / "build"
CARGO_TARGET = PROJECT_ROOT / "target"

IS_WINDOWS = platform.system() == "Windows"
IS_WSL = "microsoft" in platform.system().lower() or (
    os.path.exists("/proc/version") and
    "microsoft" in open("/proc/version").read().lower()
) if os.path.exists("/proc/version") else False

DO_INSTALL = "--install" in sys.argv
SKIP_SETUP = "--no-setup" in sys.argv

def run(cmd, cwd=None, check=True, shell=False, capture_output=False):
    """Run a command, show output."""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    if not capture_output:
        print(f"\n>>> {cmd_str}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(PROJECT_ROOT),
            check=check,
            text=True,
            capture_output=capture_output
        )
        return result
    except subprocess.CalledProcessError as e:
        if not capture_output:
            print(f"ERROR: Command failed with exit code {e.returncode}")
        if check:
            raise
        return e

def run_powershell(ps_command, check=True):
    """Run a PowerShell command on Windows."""
    if not IS_WINDOWS:
        return None
    full_cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command]
    print(f"\n>>> [PowerShell] {ps_command[:80]}{'...' if len(ps_command) > 80 else ''}")
    try:
        result = subprocess.run(
            full_cmd,
            check=check,
            text=True,
            capture_output=False
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"WARNING: PowerShell command failed (exit code {e.returncode})")
        return None

def check_scoop():
    """Check if Scoop is installed and in PATH."""
    if not IS_WINDOWS:
        return False
    try:
        result = subprocess.run(
            ["scoop", "--version"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Scoop found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_scoop():
    """Attempt to install Scoop package manager on Windows."""
    if not IS_WINDOWS:
        return False
    
    print("\n" + "=" * 60)
    print("Scoop not found. Attempting automatic installation...")
    print("=" * 60)
    print("\nScoop is a Windows package manager that will help us install NSIS.")
    print("If automatic install fails, you can run these commands manually in PowerShell:")
    print("")
    print('  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser')
    print('  Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression')
    print('  scoop bucket add extras')
    print('  scoop install nsis')
    print("")

    print("\n>>> Step 1: Setting execution policy...")
    run_powershell("Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force", check=False)
    
    print("\n>>> Step 2: Installing Scoop...")
    install_cmd = (
        "Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression"
    )
    result = run_powershell(install_cmd, check=False)
    
    if result is None or result.returncode != 0:
        print("\n" + "!" * 60)
        print("WARNING: Automatic Scoop installation failed.")
        print("!" * 60)
        print("\nPlease run these commands MANUALLY in an ADMIN PowerShell:")
        print("")
        print('  1. Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser')
        print('  2. Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression')
        print('  3. Close and re-open your terminal')
        print('  4. scoop bucket add extras')
        print('  5. scoop install nsis')
        print("")
        print("Then re-run this script.")
        print("\nContinuing without NSIS... (portable ZIP will still be created)")
        print("!" * 60)
        return False
    
    print("✓ Scoop installed successfully!")
    return True

def install_nsis_via_scoop():
    """Install NSIS using Scoop."""
    if not IS_WINDOWS:
        return False
    
    print("\n>>> Installing NSIS via Scoop...")
    
    print("    -> Adding 'extras' bucket (needed for nsis)...")
    run(["scoop", "bucket", "add", "extras"], check=False)
    
    print("    -> Installing nsis package...")
    result = run(["scoop", "install", "nsis"], check=False)
    
    if result.returncode == 0:
        print("✓ NSIS installed via Scoop!")
        return True
    else:
        print("WARNING: Scoop NSIS install failed.")
        return False

def check_nsis():
    """Check if NSIS (makensis) is available, auto-install via Scoop if needed."""
    if not IS_WINDOWS:
        return False
    
    print("\n" + "-" * 60)
    print("Checking for NSIS (makensis)...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ["makensis", "-VERSION"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ NSIS found: makensis v{result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if SKIP_SETUP:
        print("- NSIS not found and --no-setup flag used. Skipping installer.")
        print("  Portable ZIP will still be created.")
        return False
    
    print("- NSIS (makensis) not found in PATH.")
    print("\nChecking for Scoop package manager...")
    
    has_scoop = check_scoop()
    
    if not has_scoop:
        print("- Scoop not found.")
        success = install_scoop()
        if not success:
            print("\nSkipping NSIS installer creation.")
            print("Portable ZIP will still work fine.")
            return False
        
        has_scoop = check_scoop()
        if not has_scoop:
            print("Scoop still not detected. Please restart your terminal.")
            return False
    
    print("\nScoop is available. Installing NSIS...")
    success = install_nsis_via_scoop()
    
    if success:
        try:
            result = subprocess.run(
                ["makensis", "-VERSION"],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✓ NSIS is now available: makensis v{result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("NOTE: You may need to restart your terminal for PATH changes to take effect.")
            return False
    
    return False

def run_wsl(cmd):
    """Run a command via WSL from Windows."""
    wsl_path = str(PROJECT_ROOT).replace("\\", "/").replace("C:", "/mnt/c")
    wsl_cmd = f"cd '{wsl_path}' && {cmd}"
    return run(["wsl", "-e", "bash", "-c", wsl_cmd], check=True)

def install_rust_linux():
    """Install Rust on Linux/WSL using rustup."""
    if IS_WINDOWS:
        return False
    
    print("\n" + "=" * 60)
    print("Rust not found. Attempting automatic installation...")
    print("=" * 60)
    print("\nRust is required to compile this project.")
    print("The official rustup installer will be used.")
    print("")
    print("Manual alternative:")
    print("  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
    print("")

    try:
        print("\n>>> Downloading and running rustup installer...")
        print("    NOTE: The installer may ask for input. Defaults are usually fine.")
        print("")
        
        result = run([
            "bash", "-c",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
        ], check=False)
        
        if result.returncode == 0:
            print("✓ Rust installed successfully!")
            print("")
            print("IMPORTANT: You need to restart your terminal or run:")
            print("  source ~/.cargo/env")
            print("")
            print("Then re-run this script.")
            
            cargo_env = Path.home() / ".cargo" / "env"
            if cargo_env.exists():
                print(f"\nTo use Rust immediately in this shell:")
                print(f"  source {cargo_env}")
            
            return True
        else:
            print("\n" + "!" * 60)
            print("Automatic Rust installation failed.")
            print("!" * 60)
            print("\nPlease install Rust manually:")
            print("")
            print("  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
            print("")
            print("Or visit: https://rustup.rs/")
            print("")
            return False
            
    except Exception as e:
        print(f"ERROR: Rust installation failed: {e}")
        return False

def install_rust_windows():
    """Install Rust on Windows using winget or rustup."""
    if not IS_WINDOWS:
        return False
    
    print("\n" + "=" * 60)
    print("Rust not found. Attempting automatic installation...")
    print("=" * 60)
    print("\nRust is required to compile this project.")
    print("")
    print("Manual options:")
    print("  1. winget install Rustlang.Rustup")
    print("  2. Download from https://rustup.rs/")
    print("")

    try:
        print(">>> Trying winget first...")
        result = run(["winget", "install", "--id", "Rustlang.Rustup", "--silent", "--accept-package-agreements", "--accept-source-agreements"], check=False)
        
        if result.returncode == 0:
            print("✓ Rust installed via winget!")
            print("\nIMPORTANT: You need to restart your terminal for PATH changes.")
            print("Then re-run this script.")
            return True
    except Exception as e:
        print(f"winget failed: {e}")
    
    print("\n>>> Trying PowerShell download method...")
    print("    Downloading rustup-init.exe...")
    
    try:
        download_cmd = (
            "$ProgressPreference = 'SilentlyContinue'; "
            "Invoke-WebRequest -Uri 'https://win.rustup.rs/x86_64' -OutFile '$env:TEMP\\rustup-init.exe'"
        )
        run_powershell(download_cmd, check=False)
        
        temp_dir = os.environ.get("TEMP", "C:\\Windows\\Temp")
        rustup_exe = Path(temp_dir) / "rustup-init.exe"
        
        if rustup_exe.exists():
            print("    Running rustup-init.exe in silent mode...")
            result = run([str(rustup_exe), "-y"], check=False)
            
            if result.returncode == 0:
                print("✓ Rust installed!")
                print("\nIMPORTANT: You need to restart your terminal.")
                print("Then re-run this script.")
                return True
    except Exception as e:
        print(f"Rustup download/run failed: {e}")
    
    print("\n" + "!" * 60)
    print("Automatic Rust installation failed.")
    print("!" * 60)
    print("\nPlease install Rust manually using ONE of these methods:")
    print("")
    print("Method 1 (winget - easiest):")
    print("  winget install Rustlang.Rustup")
    print("")
    print("Method 2 (download):")
    print("  Visit https://rustup.rs/ and download the installer")
    print("")
    print("Method 3 (scoop - if you have it):")
    print("  scoop install rust")
    print("")
    print("After installation, restart your terminal and re-run this script.")
    print("!" * 60)
    
    return False

def check_rust():
    """Verify Rust is installed, attempt auto-install if not found."""
    try:
        subprocess.run(["cargo", "--version"], check=True, capture_output=True, text=True)
        subprocess.run(["rustc", "--version"], check=True, capture_output=True, text=True)
        print("✓ Rust toolchain found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if SKIP_SETUP:
        print("- Rust not found and --no-setup flag used.")
        print("  Please install Rust from https://rustup.rs/")
        return False
    
    print("- Rust toolchain (cargo, rustc) not found in PATH.")
    
    if IS_WINDOWS and not IS_WSL:
        return install_rust_windows()
    else:
        return install_rust_linux()

def create_nsis_installer():
    """Create a simple NSIS installer."""
    print("\n>>> Creating NSIS installer")
    
    nsi_content = f'''
; WordToCode NSIS Installer
!define APP_NAME "WordToCode"
!define APP_VERSION "0.1.0"
!define APP_PUBLISHER "ItzzMateo"
!define APP_URL "https://github.com/ItzzMateo/WordToCode"
!define APP_EXE "wtc.exe"

; Modern UI
!include "MUI2.nsh"

; Installer name
Name "${{APP_NAME}} v${{APP_VERSION}}"

; Output file
OutFile "{BUILD_DIR / 'WordToCode-Setup.exe'}"

; Install directory
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""

; Request privileges
RequestExecutionLevel admin

;--------------------------------
; Pages

!insertmacro MUI_PAGE_LICENSE "{PROJECT_ROOT / 'LICENSE'}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer sections

Section "Install" SecInstall
  SetOutPath "$INSTDIR"
  
  ; Main executable
  File "{BUILD_DIR / 'wtc-windows-gui.exe'}"
  
  ; Rename for easier use
  Rename "$INSTDIR\\wtc-windows-gui.exe" "$INSTDIR\\wtc.exe"
  
  ; Write installation directory to registry
  WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
  
  ; Add to PATH (optional - write uninstaller info)
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
  
  ; Create start menu shortcut
  CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
  CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}} (GUI).lnk" "$INSTDIR\\wtc.exe" "--gui"
  CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
  
SectionEnd

;--------------------------------
; Uninstaller section

Section "Uninstall" SecUninstall
  ; Remove files
  Delete "$INSTDIR\\wtc.exe"
  Delete "$INSTDIR\\Uninstall.exe"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\\${{APP_NAME}}\\*.*"
  RMDir "$SMPROGRAMS\\${{APP_NAME}}"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\\${{APP_NAME}}"
  
  ; Remove install directory
  RMDir "$INSTDIR"
SectionEnd
'''
    
    nsi_file = BUILD_DIR / "installer.nsi"
    
    license_file = PROJECT_ROOT / "LICENSE"
    if not license_file.exists():
        license_file.write_text("MIT License")
    
    nsi_file.write_text(nsi_content)
    
    try:
        run(["makensis", str(nsi_file)])
        
        setup_exe = BUILD_DIR / "WordToCode-Setup.exe"
        if setup_exe.exists():
            size_mb = setup_exe.stat().st_size / (1024 * 1024)
            print(f"✓ NSIS installer: WordToCode-Setup.exe ({size_mb:.2f} MB)")
            return True
    except Exception as e:
        print(f"WARNING: NSIS installer creation failed: {e}")
    
    return False

def create_portable_zip():
    """Create a portable ZIP archive."""
    print("\n>>> Creating portable ZIP")
    
    if IS_WINDOWS:
        exe_gui = BUILD_DIR / "wtc-windows-gui.exe"
        exe_cli = BUILD_DIR / "wtc-windows-cli.exe"
        zip_path = BUILD_DIR / "WordToCode-portable-windows.zip"
    else:
        exe_gui = BUILD_DIR / "wtc-linux-gui"
        exe_cli = BUILD_DIR / "wtc-linux-cli"
        zip_path = BUILD_DIR / "WordToCode-portable-linux.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if exe_gui.exists():
            zf.write(exe_gui, exe_gui.name)
            print(f"  + Added: {exe_gui.name}")
        
        if exe_cli.exists():
            zf.write(exe_cli, exe_cli.name)
            print(f"  + Added: {exe_cli.name}")
        
        readme = PROJECT_ROOT / "README.md"
        if readme.exists():
            zf.write(readme, "README.txt")
            print(f"  + Added: README.txt")
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✓ Portable ZIP: {zip_path.name} ({size_mb:.2f} MB)")
    return zip_path

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
        print("- WSL not available. Skipping Linux cross-builds.")
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
    wtc_dst = BUILD_DIR / f"wtc-windows{suffix}.exe"

    if src.exists():
        shutil.copy2(src, dst)
        shutil.copy2(src, wtc_dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {dst.name} ({size_mb:.2f} MB)")
        print(f"✓ {wtc_dst.name} (shortcut)")
        return dst
    return None

def build_msi():
    """Build MSI installer (Windows only - legacy option)."""
    print("\n>>> Building MSI installer (WiX/cargo-wix)")

    try:
        run([
            "cargo", "wix",
            "--package", "word-to-code",
            "--features", "gui",
            "--nocapture"
        ], check=False)

        wix_dir = CARGO_TARGET / "wix"
        if wix_dir.exists():
            for msi in wix_dir.glob("*.msi"):
                dst = BUILD_DIR / msi.name
                shutil.copy2(msi, dst)
                size_mb = dst.stat().st_size / (1024 * 1024)
                print(f"✓ MSI installer: {dst.name} ({size_mb:.2f} MB)")
                return dst
    except Exception as e:
        print(f"MSI build skipped: {e}")
    
    print("MSI not created. Using portable ZIP and NSIS instead.")
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
        print("WARNING: Rust not installed in WSL. Skipping Linux builds.")
        return

    print("\n>>> Building Linux (CLI + GUI) via WSL...")
    run_wsl("cargo build --release --features gui --package word-to-code")

    linux_gui_src = PROJECT_ROOT / "target" / "release" / "word-to-code"
    linux_gui_dst = BUILD_DIR / "word-to-code-linux-gui"
    wtc_gui_dst = BUILD_DIR / "wtc-linux-gui"
    if linux_gui_src.exists():
        shutil.copy2(linux_gui_src, linux_gui_dst)
        shutil.copy2(linux_gui_src, wtc_gui_dst)
        size_mb = linux_gui_dst.stat().st_size / (1024 * 1024)
        print(f"✓ {linux_gui_dst.name} ({size_mb:.2f} MB)")
        print(f"✓ {wtc_gui_dst.name} (shortcut)")

    print("\n>>> Building Linux (CLI-only) via WSL...")
    run_wsl("cargo build --release --no-default-features --features cli --package word-to-code")

    linux_cli_src = PROJECT_ROOT / "target" / "release" / "word-to-code"
    linux_cli_dst = BUILD_DIR / "word-to-code-linux-cli"
    wtc_cli_dst = BUILD_DIR / "wtc-linux-cli"
    if linux_cli_src.exists():
        shutil.copy2(linux_cli_src, linux_cli_dst)
        shutil.copy2(linux_cli_src, wtc_cli_dst)
        size_mb = linux_cli_dst.stat().st_size / (1024 * 1024)
        print(f"✓ {linux_cli_dst.name} ({size_mb:.2f} MB)")
        print(f"✓ {wtc_cli_dst.name} (shortcut)")

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
    wtc_dst = BUILD_DIR / "wtc-linux-gui"
    if src.exists():
        shutil.copy2(src, dst)
        shutil.copy2(src, wtc_dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {dst.name} ({size_mb:.2f} MB)")
        print(f"✓ {wtc_dst.name} (shortcut)")

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
    wtc_dst = BUILD_DIR / "wtc-linux-cli"
    if src.exists():
        shutil.copy2(src, dst)
        shutil.copy2(src, wtc_dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {dst.name} ({size_mb:.2f} MB)")
        print(f"✓ {wtc_dst.name} (shortcut)")

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
                
                is_shortcut = item.name.startswith("wtc-") and not item.name.endswith(".zip") and not item.name.endswith(".exe")
                is_windows_exe_shortcut = item.name.startswith("wtc-windows")
                
                if is_shortcut or is_windows_exe_shortcut:
                    print(f"  - {item.name} (shortcut)")
                else:
                    print(f"  - {item.name} ({size_mb:.2f} MB)")

    if total_size == 0:
        print("  (none)")
    else:
        print(f"\nTotal: {total_size / (1024 * 1024):.2f} MB")

    print("\n" + "-" * 60)
    print("Usage:")
    print("-" * 60)
    print("\n  wtc (no args)      = Opens GUI")
    print("  wtc -l python ...   = CLI mode")
    print("  wtc --gui           = Opens GUI (explicit)")
    print("  wtc --help          = Show help")

    if IS_WINDOWS:
        print("\nWindows:")
        print("  .\\build\\wtc-windows-gui.exe")
        print("  .\\build\\wtc-windows-gui.exe -l rust")
        print("\n  Portable ZIP: .\\build\\WordToCode-portable-windows.zip")
        print("  NSIS Installer: .\\build\\WordToCode-Setup.exe (if NSIS installed)")
    else:
        print("\nLinux/WSL:")
        print("  ./build/wtc-linux-gui")
        print("  ./build/wtc-linux-gui -l python")
        print("  ./build/wtc-linux-cli  (smaller, no GUI)")
        print("\n  Portable ZIP: ./build/WordToCode-portable-linux.zip")

def install_binary():
    """Copy the wtc binary to user's local bin directory."""
    print("\n" + "=" * 60)
    print("Installing wtc to user bin directory")
    print("=" * 60)

    if IS_WINDOWS and not IS_WSL:
        install_dir = Path(os.environ.get("USERPROFILE", "C:\\Users\\Default")) / "bin"
        install_dir.mkdir(parents=True, exist_ok=True)
        src = BUILD_DIR / "wtc-windows-gui.exe"
        dst = install_dir / "wtc.exe"
        path_hint = f"%USERPROFILE%\\bin"
    else:
        install_dir = Path.home() / ".local" / "bin"
        install_dir.mkdir(parents=True, exist_ok=True)
        src = BUILD_DIR / "wtc-linux-gui"
        dst = install_dir / "wtc"
        path_hint = "$HOME/.local/bin"

    if src.exists():
        shutil.copy2(src, dst)
        dst.chmod(0o755)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ Installed: {dst} ({size_mb:.2f} MB)")
    else:
        print(f"WARNING: {src.name} not found. Run build first, or build + install together.")
        return

    if not IS_WINDOWS:
        bashrc = Path.home() / ".bashrc"
        export_line = f'\n# Add ~/.local/bin to PATH\nexport PATH="$HOME/.local/bin:$PATH"'
        if bashrc.exists():
            if f"export PATH=\"$HOME/.local/bin" not in bashrc.read_text():
                bashrc.open("a").write(export_line)
                print(f"✓ Added {path_hint} to PATH in {bashrc}")
        else:
            bashrc.write_text(export_line)
            print(f"✓ Created {bashrc} with {path_hint} in PATH")

    print(f"\n  To verify, open a NEW terminal and run:")
    if IS_WINDOWS and not IS_WSL:
        print(f"    wtc")
        print(f"\n  Note: You may need to add %USERPROFILE%\\bin to your Windows PATH.")
    else:
        print(f"    source ~/.bashrc")
        print(f"    wtc")

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

        has_nsis = check_nsis()
        has_wsl = check_wsl()

        build_windows("gui")
        
        print("\n" + "-" * 60)
        print("Portable ZIP (always created, no dependencies)")
        print("-" * 60)
        create_portable_zip()
        
        if has_nsis:
            create_nsis_installer()
        
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
        
        print("\n" + "-" * 60)
        print("Portable ZIP")
        print("-" * 60)
        create_portable_zip()

    show_summary()

    if DO_INSTALL:
        install_binary()

if __name__ == "__main__":
    main()
