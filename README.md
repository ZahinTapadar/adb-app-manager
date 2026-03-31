<p align="center">
  <img src="https://img.icons8.com/color/120/000000/android-os.png" alt="Android Logo" width="100"/>
</p>
<h1 align="center">ADB App Manager & Cleaner</h1>

<p align="center">
  <strong>A lightning-fast, visually appealing Terminal UI (TUI) to manage and clean up Android applications via ADB.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

---

## 🚀 Overview

**ADB App Manager** provides an interactive, beautiful Terminal UI for managing apps installed on your Android device. It intelligently identifies third-party applications, pulls real-time usage statistics (identifying apps you haven't used in months), and dynamically fetches friendly, human-readable app names covering thousands of popular apps on the Play Store.

Alternatively, use the **CLI Cleaner** (`DeviceCleanerAndroid.py`) to quickly detect and uninstall unused apps automatically.

### ✨ Features
- 📊 **Smart Usage Tracking:** Instantly flags apps that haven't been opened for months (or never used!).
- 🏷️ **Dynamic Friendly Names:** Resolves cryptic package names (e.g., `com.zhiliaoapp.musically`) into human-readable app names (`TikTok`) via a vast internal dictionary and dynamic Play Store lookup.
- 🎨 **Beautiful TUI:** Built with `textual` to provide a fast, mouse-friendly, responsive interface in your terminal.
- 🛡️ **Safe by Default:** Explicitly ignores system/core Android packages to prevent accidental damage.
- 📦 **Batch Operations:** Select multiple apps and uninstall them safely with a single keystroke.

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- `adb` (Android Debug Bridge) installed and added to your system PATH
- An Android device with **USB Debugging** enabled

### Via Homebrew (macOS / Linux)
```bash
brew tap ZahinTapadar/tap
brew install adb-app-manager
```
*Note: Homebrew automatically manages ADB (`android-platform-tools`) and seamlessly configures the Python environment for you.*

### Manual Installation
```bash
git clone https://github.com/ZahinTapadar/adb-app-manager.git
cd adb-app-manager
pip install -r requirements.txt
```

## 🎮 Usage

Make sure your Android device is connected and authorized (`adb devices`).

### 1. The Interactive TUI (Recommended)
Launch the beautifully designed interactive textual interface via the Homebrew command:
```bash
adb-app-manager
```

**Keybindings:**
- <kbd>Space</kbd>: Toggle selection of the highlighted app
- <kbd>A</kbd>: Select all apps that have **NEVER** been used
- <kbd>Ctrl+A</kbd>: Deselect all apps
- <kbd>U</kbd>: Uninstall selected apps
- <kbd>R</kbd>: Reload the app list
- <kbd>Q</kbd>: Quit

### 2. The CLI Cleaner
If you prefer a fast, automated approach that detects apps unused for over 90 days:
```bash
python DeviceCleanerAndroid.py
```
> **Note:** For safety, the script will output a confirmation prompt before performing any uninstallation.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page]() if you want to contribute.

## 📄 License
This project is [MIT](LICENSE) licensed.
