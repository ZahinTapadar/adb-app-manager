#!/usr/bin/env python3
import subprocess
import re
from datetime import datetime, timedelta

def run_adb(cmd):
    result = subprocess.run(
        ["adb", "shell"] + cmd.split(),
        capture_output=True, text=True
    )
    return result.stdout.strip()

def get_all_packages():
    """Get all user-installed packages (excludes system apps)."""
    output = run_adb("pm list packages -3")  # -3 = third-party only
    return [line.replace("package:", "").strip() for line in output.splitlines()]

def get_last_used(package):
    """Parse dumpsys usagestats for last time app was used."""
    output = subprocess.run(
        ["adb", "shell", "dumpsys", "usagestats"],
        capture_output=True, text=True
    ).stdout

    # Find the block for this package
    pattern = rf'package={re.escape(package)}.*?lastTimeUsed=(\d+)'
    match = re.search(pattern, output, re.DOTALL)
    if match:
        ts_ms = int(match.group(1))
        return datetime.fromtimestamp(ts_ms / 1000)
    return None

def main():
    print("🔍 Fetching installed packages...")
    packages = get_all_packages()
    print(f"Found {len(packages)} user-installed apps\n")

    results = []
    for pkg in packages:
        last_used = get_last_used(pkg)
        results.append((pkg, last_used))

    # Sort: never used first, then oldest used
    results.sort(key=lambda x: x[1] or datetime.min)

    threshold = datetime.now() - timedelta(days=90)  # 3 months inactive
    inactive = [(pkg, ts) for pkg, ts in results if ts is None or ts < threshold]

    print(f"{'Package':<50} {'Last Used'}")
    print("-" * 75)
    for pkg, ts in inactive:
        label = ts.strftime("%Y-%m-%d") if ts else "NEVER USED"
        print(f"{pkg:<50} {label}")

    print(f"\n⚠️  {len(inactive)} apps unused for 90+ days")
    confirm = input("\nDo you want to UNINSTALL all of these? (yes/no): ")

    if confirm.lower() == "yes":
        for pkg, _ in inactive:
            print(f"  Uninstalling {pkg}...")
            subprocess.run(["adb", "shell", "pm", "uninstall", "-k", "--user", "0", pkg])
        print("\n✅ Done!")
    else:
        # Export to file for manual review
        with open("inactive_apps.txt", "w") as f:
            for pkg, ts in inactive:
                label = ts.strftime("%Y-%m-%d") if ts else "NEVER"
                f.write(f"{pkg}\t{label}\n")
        print("📄 Saved to inactive_apps.txt for review")

if __name__ == "__main__":
    main()
