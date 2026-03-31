#!/usr/bin/env python3
"""
ADB App Manager - A TUI for managing Android apps via ADB
Usage: python adb_manager.py
"""

import subprocess
import re
from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, DataTable, Label, Button, Static, Input, LoadingIndicator
)
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual import work
from textual.worker import Worker, WorkerState
from rich.text import Text
from rich.console import Console
import asyncio

# ─── Friendly name lookup ──────────────────────────────────────────────────────
FRIENDLY_NAMES: dict[str, str] = {
    "org.ketto.sip": "Ketto (Fundraising)",
    "com.google.audio.hearing.visualization.accessibility.scribe": "Google Recorder",
    "com.delhiveryConsigneeApp": "Delhivery (Delivery tracking)",
    "com.ubercab.eats": "Uber Eats",
    "com.shazam.android": "Shazam",
    "org.digiyatra.org": "DigiYatra (Airport face check-in)",
    "in.swiggy.android.toing": "Swiggy Toing (Games)",
    "com.naver.linewebtoon": "Webtoon",
    "com.reddit.frontpage": "Reddit",
    "ak.alizandro.smartaudiobookplayer": "Smart Audiobook Player",
    "vpn.usa_tap2free": "Free VPN (sketchy, delete)",
    "com.udemy.android": "Udemy",
    "com.google.android.apps.paidtasks": "Google Tasks",
    "app.mihon": "Mihon (Manga reader)",
    "com.cdotindia.capsachet": "C-DOT India (Govt)",
    "com.github.android": "GitHub",
    "com.blockabc.cctip": "CCTip (Crypto tipping)",
    "com.suno.android": "Suno (AI music)",
    "com.linkedin.android": "LinkedIn",
    "eu.kanade.tachiyomi.extension.all.webtoons": "Tachiyomi — Webtoons source",
    "eu.kanade.tachiyomi.animeextension.all.jellyfin": "Tachiyomi — Jellyfin source",
    "org.zwanoo.android.speedtest": "Speedtest by Ookla",
    "com.rapido.passenger": "Rapido (Bike taxi)",
    "com.deepl.mobiletranslator": "DeepL Translator",
    "com.termux": "Termux (Linux terminal)",
    "com.twitter.android": "Twitter / X",
    "eu.kanade.tachiyomi.extension.all.mangaplus": "Tachiyomi — MangaPlus source",
    "com.google.android.play.games": "Google Play Games",
    "in.amazon.mShop.android.shopping": "Amazon Shopping",
    "com.neave.zoomearth": "Zoom Earth (Live maps)",
    "io.elevenlabs.coreapp": "ElevenLabs (AI voice)",
    "com.wispr.flowapp": "Flow (AI writing)",
    "com.shiksha.android": "Shiksha (College search)",
    "io.elevenlabs.readerapp": "ElevenLabs Reader",
    "com.ttee.leeplayer": "Lee Player (Video player)",
    "com.huami.watch.hmwatchmanager": "Amazfit / Zepp (Smartwatch)",
    "com.msf.angelmobile": "MSF Angel (Doctors Without Borders)",
    "com.google.android.ims": "Google RCS / IMS",
    "com.collegedunia": "CollegeDunia",
    "com.vitotechnology.StarWalk2Free": "Star Walk 2 (Stargazing)",
    "ai.mistral.chat": "Mistral AI",
    "com.renshuu.renshuu_org": "Renshuu (Japanese learning)",
    "finance.global.travel.niyo": "Niyo (Travel card)",
    "com.google.android.apps.customization.pixel": "Pixel Customizer",
    "com.bt.bms": "BT BMS (unknown/obscure)",
    "com.naturalsoft.personalweb": "Personal Web",
    "com.PYOPYO.StarTracker": "Star Tracker (Stargazing)",
    "com.google.android.apps.docs.editors.slides": "Google Slides",
    "com.nextbillion.groww": "Groww (Stocks & Mutual Funds)",
    "com.instagram.lite": "Instagram Lite",
    "xyz.penpencil.physicswala": "PhysicsWallah",
    "com.wallapers.sillysmiles.live.wallpaper": "Silly Smiles Live Wallpaper",
    "org.freecodecamp": "freeCodeCamp",
    "com.jio.media.ondemand": "JioCinema",
    "com.deepseek.chat": "DeepSeek",
    "com.google.android.apps.authenticator2": "Google Authenticator",
    "com.hp.printercontrol": "HP Smart (Printer)",
    "ginlemon.iconpackstudio": "Icon Pack Studio",
    "com.amazon.avod.thirdpartyclient": "Amazon Prime Video",
    "com.notasimplestudio.webnovelfull": "WebNovel Full (Novel reader)",
    "com.chess": "Chess.com",
    "com.tiktokmashup.dance": "TikTok Mashup (3rd party TikTok)",
    "com.canva.editor": "Canva",
    "com.quillbot.mobile": "QuillBot (AI writing)",
    "md.obsidian": "Obsidian (Notes)",
    "net.podslink": "PodsLink (AirPods clone control)",
    "com.bashsoftware.boycott": "Boycott (BDS app)",
    "com.junkfood.seal": "Seal (yt-dlp downloader)",
    "com.lulilanguages.j5a": "Japanese! (Language learning)",
    "co.brainly": "Brainly (Homework Q&A)",
    "com.lgeha.nuts": "LG ThinQ (Smart home)",
    "com.zhiliaoapp.musically": "TikTok",
    "com.alibaba.intl.android.apps.poseidon": "Alibaba (B2B shopping)",
    "com.qidian.Int.reader": "Webnovel (Qidian)",
    "io.capacities.mobile": "Capacities (Notes)",
    "com.locationchanger": "Location Changer (GPS spoof)",
    "in.org.npci.upiapp": "BHIM UPI",
    "com.wolfram.android.alphapro": "Wolfram Alpha",
    "com.diskwalaapp": "DiskWala (unknown)",
    "in.burgerking.android": "Burger King India",
    "com.microsoft.teams": "Microsoft Teams",
    "app.revanced.android.youtube": "ReVanced YouTube (ad-free YT)",
    "org.mozilla.focus": "Firefox Focus (Private browser)",
    "in.swiggy.android.instamart": "Swiggy Instamart (Groceries)",
    "com.zerodha.coin": "Zerodha Coin (Mutual Funds)",
    "com.grofers.customerapp": "Blinkit (Groceries)",
    "com.jonathanpuckey.radiogarden": "Radio Garden",
    "com.bigbasket.mobileapp": "BigBasket (Groceries)",
    "com.yousx.thetoolsapp": "The Tools App",
    "com.elevatelabs.geonosis": "Geonosis (unknown)",
    "com.sbi.lotusintouch": "SBI Anywhere (Banking)",
    "tv.standard.nebula": "Nebula (Creator streaming)",
    "com.photo.widget.zwh.picturewidget.app": "Picture Widget (Home screen widget)",
    "com.indymobileapp.document.scanner": "Document Scanner",
    "com.google.android.apps.docs.editors.sheets": "Google Sheets",
    "com.truecaller": "Truecaller (Caller ID)",
    "com.rezvorck.tiktokplugin": "TikTok Plugin (3rd party)",
    "com.pomodrone.app": "Pomodrone (Pomodoro timer)",
    "com.grammarly.android.keyboard": "Grammarly Keyboard",
    "com.aihomework": "AI Homework Helper",
    "com.olx.southasia": "OLX (Classifieds)",
    "com.happymod.apk": "HappyMod (APK installer — sketchy)",
    "com.blackiconpack.zwart": "Zwart Icon Pack",
    "com.anilab.android": "AniLab (Anime tracker)",
    "com.bigwinepot.nwdn.international": "NewsDog (News)",
    "com.netflix.mediaclient": "Netflix",
    "com.google.android.apps.translate": "Google Translate",
    "com.miko3.app": "Miko 3 (Kids robot app)",
    "com.desmos.calculator": "Desmos (Graphing calculator)",
    "com.ascent": "Ascent (unknown)",
    "org.chromium.webapk.a6d63f8b786815ac1_v2": "Chrome Web App (PWA shortcut)",
    "com.duolingo": "Duolingo",
    "eu.kanade.tachiyomi.animeextension.en.gogoanime": "Tachiyomi — GogoAnime source",
    "eu.kanade.tachiyomi.animeextension.all.torrentioanime": "Tachiyomi — Torrentio source",
    "com.busuu.android.enc": "Busuu (Language learning)",
    "eu.kanade.tachiyomi.extension.all.nhentai": "Tachiyomi — NHentai source",
    "com.olacabs.customer": "Ola Cabs",
    "com.hrd.vocabulary": "Vocabulary Builder",
    "in.startv.hotstar": "Disney+ Hotstar",
    "com.apple.android.music": "Apple Music",
    "com.ubisoft.uplay": "Ubisoft Connect",
    "app.revanced.manager.flutter": "ReVanced Manager",
    "com.athan": "Athan (Prayer times)",
    "jp.co.shueisha.mangaplus": "MangaPlus by Shueisha",
    "com.kovetstech.candlestickpatterns": "Candlestick Patterns (Trading)",
    "com.touchtype.swiftkey": "SwiftKey Keyboard (Microsoft)",
    "com.whereismytrain.android": "Where Is My Train",
    "com.wssc.simpleclock": "Simple Clock Widget",
    "com.google.earth": "Google Earth",
    "ai.sarvam.indus": "Sarvam AI (Indian LLM)",
    "com.ttxapps.drivesync": "DriveSync (Google Drive sync)",
    "com.skoolsmart": "SkoolSmart (School app)",
    "com.KhoGames.WarzoneCommander": "Warzone Commander (Game)",
    "com.deen": "Deen (Islamic app)",
    "xyz.jmir.tachiyomi.mi": "TachiyomiJ2K (Manga reader)",
    "com.moonshot.kimichat": "Kimi Chat (AI)",
    "com.dubox.drive": "Dubox / TeraBox (Cloud storage)",
    "com.airbnb.android": "Airbnb",
    "com.shiksha.studyabroad": "Shiksha Study Abroad",
    "com.encanto.gamersgift": "Gamers Gift (unknown)",
    "com.Slack": "Slack",
    "ai.perplexity.app.android": "Perplexity AI",
    "com.ubercab": "Uber",
    "in.indwealth": "INDmoney (Stocks & Finance)",
    "com.magi.closer": "Closer (Social app)",
    "com.pinterest": "Pinterest",
    "com.valvesoftware.steamlink": "Steam Link",
    "company.thebrowser.arc": "Arc Browser",
    "com.yum.kfc": "KFC India",
    "com.superbyte.studybunny": "Study Bunny (Study timer)",
    "nic.org.mygrievance": "MyGrievance (Govt portal)",
    "com.philips.ka.oneka.app": "Philips (Smart home)",
    "com.tplink.iot": "TP-Link Tapo (Smart home)",
    "com.tempmail": "Temp Mail (Disposable email)",
    "com.andatsoft.myapk.fwa": "MyAPK (unknown)",
    "com.tiktok.plugin": "TikTok Plugin",
    "co.thewordlab.luzia": "Luzia (AI assistant)",
    "com.radio.pocketfm": "Pocket FM (Audio stories)",
    "com.openai.chatgpt": "ChatGPT",
    "com.lagradost.quicknovel": "QuickNovel (Novel reader)",
    "com.flipkart.android": "Flipkart",
    "com.arrowsapp.nightscreen": "Night Screen (Blue light filter)",
    "free.programming.programming": "Programming Hub",
    "app.vinztech.trackit": "TrackIt",
    "in.gov.umang.negd.g2c": "UMANG (Govt services)",
    "com.hrd.iam": "IAM (HR/Identity app)",
    "com.redotpay": "RedotPay (Crypto card)",
    "com.google.android.apps.labs.language.tailwind": "Google Translate Labs",
    "droom.sleepIfUCan": "Sleep If U Can (Alarm)",
    "com.Dominos": "Domino's Pizza",
    "com.google.android.apps.nbu.paisa.user": "Google Pay",
    "com.lawofindia.indianlaw.ipc.crpc.cpc.nia.ida.hma.iea.mva.law4u": "Indian Law (IPC/CrPC reference)",
    "net.ctpool": "CTPool (unknown)",
    "mtstylesforklwp.kustom.pack": "KLWP Style Pack",
    "ai.x.grok": "Grok (xAI)",
    "org.chromium.webapk.a51fe383e76d9c7b8_v2": "Chrome Web App (PWA shortcut)",
    "com.cengage.Cengage": "Cengage (Education)",
    "com.brave.browser": "Brave Browser",
    "com.onihstudio.remakeraifaceswap": "Remake AI (Face swap — delete)",
    "com.sony.songpal.mdr": "Sony Headphones Connect",
    "com.whatsapp": "WhatsApp",
    "eu.kanade.tachiyomi.extension.en.kingofshojo": "Tachiyomi — King of Shojo source",
    "com.google.android.contactkeys": "Contact Key Verification",
    "com.anthropic.claude": "Claude (Anthropic)",
    "org.localsend.localsend_app": "LocalSend (LAN file transfer)",
    "io.mewtant.pixaiart": "PixAI (AI art generator)",
    "host.exp.exponent": "Expo Go (React Native dev)",
    "com.jio.myjio": "MyJio",
    "com.flightradar24free": "Flightradar24",
    "com.microblink.photomath": "Photomath",
    "com.measureprotocol.contributor.production": "Measure Protocol (Data rewards)",
    "com.quizlet.quizletandroid": "Quizlet",
    "com.typeless.mobile": "Typeless (AI notes)",
    "eu.kanade.tachiyomi.animeextension.all.googledrive": "Tachiyomi — Google Drive source",
    "com.getsomeheadspace.android": "Headspace (Meditation)",
    "com.mindtwisted.kanjistudy": "Kanji Study",
    "com.blackmagicdesign.android.blackmagiccam": "Blackmagic Camera",
    "org.telegram.messenger": "Telegram",
    "in.swiggy.android": "Swiggy (Food delivery)",
    "eu.kanade.tachiyomi.animeextension.en.zoro": "Tachiyomi — Zoro source",
    "com.findmybluetooth.headset.headphones.devices": "Find My Bluetooth Device",
    "com.fiverr.fiverr": "Fiverr",
    "com.apkpure.aegon": "APKPure (APK installer)",
    "com.instagram.android": "Instagram",
    "com.google.android.apps.subscriptions.red": "YouTube Premium",
    "com.tailscale.ipn": "Tailscale (VPN)",
    "com.jio.media.jiobeats": "JioSaavn (Music)",
    "android.autoinstalls.config.Nothing.Pong": "Nothing Phone 1 config (system — safe to remove)",
    "com.bytebox.find.devices.bluetooth": "Find Bluetooth Devices",
    "io.faceapp": "FaceApp",
    "tv.twitch.android.app": "Twitch",
    "com.digilocker.android": "DigiLocker (Govt ID wallet)",
    "ginlemon.iconpackstudio": "Icon Pack Studio",
    "ginlemon.iconpackstudio.exported": "Icon Pack Studio (exported)",
    "org.khanacademy.android": "Khan Academy",
    "com.jpl.jiomart": "JioMart (Groceries)",
    "com.storycraft.lightnovel.readerapp": "Light Novel Reader",
    "org.jellyfin.mobile": "Jellyfin (Media server)",
    "com.google.android.apps.docs.editors.docs": "Google Docs",
    "ai.qwenlm.chat.android": "Qwen Chat (Alibaba AI)",
    "com.candywriter.bitlife": "BitLife (Life simulator game)",
    "org.schabi.newpipe": "NewPipe (YouTube alternative)",
    "cc.forestapp": "Forest (Focus / Stay off phone)",
    "bunpro.jp.bunpro_srs": "Bunpro (Japanese grammar SRS)",
    "com.StaffanEkvall.CarpetBombing": "Carpet Bombing (Game)",
    "cbse.class12.solvedPapers": "CBSE Class 12 Solved Papers",
    "com.blackbox.blackboxapp": "Blackbox (Coding puzzles)",
    "com.imdb.mobile": "IMDb",
    "com.scee.psxandroid": "PlayStation App",
    "com.tibith.badboxing": "Bad Boxing (Game)",
    "com.dashlane": "Dashlane (Password manager)",
    "com.valvesoftware.android.steam.community": "Steam (Gaming)",
    "com.gpsmapcamera.geotagginglocationonphoto": "GPS Map Camera (Photo geotagging)",
    "com.sonyliv": "SonyLIV",
    "advanced.scientific.calculator.calc991.plus": "Calculator Plus (Scientific)",
    "com.microsoft.xboxone.smartglass": "Xbox (Microsoft)",
    "com.mgoogle.android.gms": "MicroG GMS (ReVanced companion)",
    "com.discord": "Discord",
    "org.readera": "ReadEra (PDF & ebook reader)",
    "com.paypal.android.p2pmobile": "PayPal",
    "com.application.zomato": "Zomato (Food delivery)",
    "eu.kanade.tachiyomi.extension.en.kunmanga": "Tachiyomi — KunManga source",
    "com.fampay.in": "FamPay (Teen payments)",
    "notion.id": "Notion",
    "com.bunpoapp": "Bunpo (Japanese grammar)",
    "com.you.browser": "YOU Browser",
    "com.edurev.iit": "EduRev (JEE/NEET prep)",
    "me.zhanghai.android.files": "Material Files (File manager)",
    "com.yangdai.opennote": "OpenNote (Notes)",
    "com.lemon.lvoverseas": "LV Overseas (Study abroad)",
    "ch.protonvpn.android": "ProtonVPN",
    "io.metamask": "MetaMask (Crypto wallet)",
    "app.revanced.android.gms": "ReVanced MicroG",
    "mobi.eup.jpnews": "Japanese News (JP learning)",
    "com.facebook.katana": "Facebook",
    "android.autoinstalls.config.Nothing.Spacewar": "Nothing Phone 1 config (system — safe to remove)",
    "eu.kanade.tachiyomi.extension.all.batoto": "Tachiyomi — Batoto source",
    "com.nordvpn.android": "NordVPN",
    "com.cloudflare.onedotonedotonedotone": "Cloudflare WARP (1.1.1.1 VPN)",
    "com.google.android.apps.adm": "Find My Device",
    "com.randonautica.app": "Randonautica",
    "eu.kanade.tachiyomi.extension.en.manhwaclan": "Tachiyomi — ManhwaClan source",
    "com.ai.sound.donna": "Donna (AI voice assistant)",
}

import urllib.request
import json
import os

class AppNameManager:
    def __init__(self):
        self.names = FRIENDLY_NAMES.copy()
        self.cache_file = os.path.expanduser("~/.cache/adb_manager_names.json")
        self._load_cache()

    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.names.update(json.load(f))
        except Exception:
            pass

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.names, f)
        except Exception:
            pass

    def get(self, pkg: str, fallback: str) -> str:
        return self.names.get(pkg, fallback)

    def has(self, pkg: str) -> bool:
        return pkg in self.names

    def add(self, pkg: str, name: str) -> None:
        self.names[pkg] = name
        self._save_cache()

app_names = AppNameManager()


# ─── ADB helpers ──────────────────────────────────────────────────────────────

def adb(cmd: str) -> str:
    try:
        result = subprocess.run(
            ["adb", "shell"] + cmd.split(),
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return ""


def adb_raw(args: list) -> str:
    try:
        result = subprocess.run(
            ["adb", "shell"] + args,
            capture_output=True, text=True, timeout=60
        )
        return result.stdout.strip()
    except Exception:
        return ""


def check_device() -> bool:
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().splitlines()
        return any("device" in l and "List" not in l for l in lines)
    except Exception:
        return False


def get_packages() -> list[str]:
    # Third-party packages
    out3 = adb("pm list packages -3")
    third_party = set(
        line.replace("package:", "").strip()
        for line in out3.splitlines()
        if line.startswith("package:")
    )

    # System packages — explicitly exclude these
    outs = adb("pm list packages -s")
    system = set(
        line.replace("package:", "").strip()
        for line in outs.splitlines()
        if line.startswith("package:")
    )

    # Extra safety: known system-level prefixes that Nothing OS leaks as "third-party"
    SYSTEM_PREFIXES = (
        "android.",
        "com.android.",
        "com.google.android.gms",
        "com.google.android.gsf",
        "com.qualcomm.",
        "com.nothing.",
        "android.autoinstalls.",
    )

    safe = set()
    for pkg in third_party:
        if pkg in system:
            continue  # explicitly listed as system
        if any(pkg.startswith(p) for p in SYSTEM_PREFIXES):
            continue  # prefix-matched system package
        safe.add(pkg)

    return sorted(safe)


def get_usage_stats() -> dict[str, datetime | None]:
    """
    Returns {package: last_used_datetime or None}.
    Parses dumpsys usagestats line-by-line (fast, no DOTALL regex).
    Falls back to package-level query if full dump is too slow.
    """
    stats: dict[str, datetime] = {}

    try:
        # Stream output line by line with a hard 20s timeout
        proc = subprocess.Popen(
            ["adb", "shell", "dumpsys", "usagestats"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True
        )

        pkg_re = re.compile(r'package=(\S+)')
        ts_re  = re.compile(r'lastTimeUsed=(\d{10,})')   # epoch ms, at least 10 digits

        current_pkg = None
        import signal, threading

        # Kill process after 15 seconds to avoid hanging forever
        def _kill():
            try:
                proc.kill()
            except Exception:
                pass
        timer = threading.Timer(15.0, _kill)
        timer.start()

        for line in proc.stdout:
            pm = pkg_re.search(line)
            if pm:
                current_pkg = pm.group(1)
            if current_pkg:
                tm = ts_re.search(line)
                if tm:
                    ts_ms = int(tm.group(1))
                    # Sanity check: must be after year 2015
                    if ts_ms > 1_420_000_000_000:
                        dt = datetime.fromtimestamp(ts_ms / 1000)
                        if current_pkg not in stats or dt > stats[current_pkg]:
                            stats[current_pkg] = dt

        timer.cancel()
        proc.wait(timeout=2)

    except Exception:
        pass

    return stats


def get_app_label(package: str) -> str:
    """Try to get a human-readable app name."""
    out = adb(f"pm dump {package}")
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("label="):
            label = line[6:].strip()
            if label and label != "null" and not label.startswith("0x"):
                return label
    return package  # fallback to package name


def uninstall_packages(packages: list[str]) -> dict[str, bool]:
    results = {}
    for pkg in packages:
        result = subprocess.run(
            ["adb", "shell", "pm", "uninstall", "-k", "--user", "0", pkg],
            capture_output=True, text=True, timeout=30
        )
        results[pkg] = "Success" in result.stdout or "success" in result.stdout
    return results


# ─── Screens ──────────────────────────────────────────────────────────────────

class ConfirmScreen(ModalScreen):
    """Confirmation dialog before uninstalling."""

    CSS = """
    ConfirmScreen {
        align: center middle;
    }
    #confirm-box {
        background: $surface;
        border: heavy $warning;
        padding: 2 4;
        width: 60;
        height: auto;
    }
    #confirm-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    #confirm-msg {
        text-align: center;
        margin-bottom: 2;
    }
    #confirm-buttons {
        align: center middle;
        height: auto;
    }
    Button {
        margin: 0 2;
    }
    """

    def __init__(self, count: int, packages: list[str]):
        super().__init__()
        self.count = count
        self.packages = packages

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-box"):
            yield Label("⚠  CONFIRM UNINSTALL", id="confirm-title")
            yield Label(
                f"You are about to uninstall [bold]{self.count}[/bold] apps.\n"
                f"This is reversible — apps can be reinstalled from Play Store.\n"
                f"[dim](Uses -k --user 0, keeps data)[/dim]",
                id="confirm-msg",
                markup=True
            )
            with Horizontal(id="confirm-buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button(f"Uninstall {self.count} apps", variant="error", id="confirm")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)


class ResultScreen(ModalScreen):
    """Shows uninstall results."""

    CSS = """
    ResultScreen {
        align: center middle;
    }
    #result-box {
        background: $surface;
        border: heavy $success;
        padding: 2 4;
        width: 70;
        height: auto;
        max-height: 40;
    }
    #result-title {
        text-align: center;
        text-style: bold;
        color: $success;
        margin-bottom: 1;
    }
    #result-scroll {
        height: 20;
        border: solid $panel;
        padding: 0 1;
        margin-bottom: 1;
    }
    #ok-btn {
        align-horizontal: center;
    }
    """

    def __init__(self, results: dict[str, bool]):
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        ok = sum(1 for v in self.results.values() if v)
        fail = len(self.results) - ok
        with Vertical(id="result-box"):
            yield Label(f"✓ Done — {ok} uninstalled, {fail} failed", id="result-title")
            with ScrollableContainer(id="result-scroll"):
                for pkg, success in self.results.items():
                    icon = "✓" if success else "✗"
                    color = "green" if success else "red"
                    yield Label(f"[{color}]{icon}[/{color}] {pkg}", markup=True)
            yield Button("Close", variant="primary", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


# ─── Main App ─────────────────────────────────────────────────────────────────

class ADBManager(App):
    """ADB App Manager TUI"""

    TITLE = "ADB App Manager"
    SUB_TITLE = "Select apps to uninstall"

    CSS = """
    Screen {
        background: $background;
    }

    #loading-container {
        align: center middle;
        height: 1fr;
    }

    #loading-label {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }

    #no-device {
        align: center middle;
        height: 1fr;
        color: $error;
        text-align: center;
    }

    /* ── top bar ── */
    #top-bar {
        height: 3;
        background: $panel;
        padding: 0 2;
        align: left middle;
    }

    #search-input {
        width: 40;
        margin-right: 3;
    }

    #stats-label {
        color: $text-muted;
        width: 1fr;
    }

    #select-btns {
        height: 3;
        align: right middle;
    }

    /* ── table ── */
    #app-table {
        height: 1fr;
    }

    DataTable {
        height: 1fr;
    }

    /* ── bottom bar ── */
    #bottom-bar {
        height: 3;
        background: $panel;
        padding: 0 2;
        align: right middle;
    }

    #selected-label {
        width: 1fr;
        color: $warning;
        text-style: bold;
    }

    #uninstall-btn {
        margin-left: 2;
    }

    /* legend */
    #legend {
        height: 1;
        background: $panel-darken-1;
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("space", "toggle_selected", "Select/Deselect", show=True),
        Binding("a", "select_all_never", "Select all NEVER", show=True),
        Binding("ctrl+a", "deselect_all", "Deselect all", show=True),
        Binding("u", "uninstall", "Uninstall selected", show=True),
        Binding("r", "reload", "Reload", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.all_rows: list[dict] = []        # full dataset
        self.filtered_rows: list[dict] = []   # after search filter
        self.selected: set[str] = set()       # selected package names
        self.loading = True

    def compose(self) -> ComposeResult:
        yield Header()
        # Loading state
        with Vertical(id="loading-container"):
            yield Label("Connecting to device & loading apps...", id="loading-label", markup=True)
            yield LoadingIndicator()
        yield Footer()

    def on_mount(self) -> None:
        self.load_apps()

    @work(thread=True)
    def fetch_missing_names(self, packages: list[str]) -> None:
        """Dynamically fetch friendly names from Google Play for missing packages."""
        import ssl
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        except Exception:
            ctx = None

        updated = False
        for pkg in packages:
            if app_names.has(pkg):
                continue
            
            try:
                url = f"https://play.google.com/store/apps/details?id={pkg}&hl=en"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req, timeout=3, context=ctx).read().decode('utf-8')
                match = re.search(r'<title[^>]*>(.*?)</title>', html)
                if match:
                    name = match.group(1).replace(' - Apps on Google Play', '').strip()
                    if name:
                        app_names.add(pkg, name)
                        updated = True
                        self.call_from_thread(self._update_table_cell, pkg, name)
            except Exception:
                # Mark as failed to prevent endless retries
                app_names.add(pkg, pkg.split(".")[-1])

        if updated:
            self.call_from_thread(self.rebuild_table)

    def _update_table_cell(self, pkg: str, name: str) -> None:
        try:
            table = self.query_one(DataTable)
            # Try to update the specific cell if possible (requires column key)
            for row_key in range(len(table.rows)):
                if table.get_row_at(row_key)[1].plain == pkg:
                    # Found it, but updating via rebuild_table is safer for sorting
                    pass
        except Exception:
            pass

    def _set_loading_msg(self, msg: str) -> None:
        try:
            self.query_one("#loading-label").update(msg)
        except Exception:
            pass

    @work(thread=True)
    def load_apps(self) -> None:
        """Background worker to fetch all app data."""
        self.call_from_thread(self._set_loading_msg, "Checking ADB device connection...")
        if not check_device():
            self.call_from_thread(self.show_no_device)
            return

        self.call_from_thread(self._set_loading_msg, "Fetching installed packages...")
        packages = get_packages()

        self.call_from_thread(
            self._set_loading_msg,
            f"Found [bold]{len(packages)}[/bold] apps. Reading usage stats (may take ~10s)..."
        )
        usage = get_usage_stats()

        self.call_from_thread(self._set_loading_msg, "Building table...")
        now = datetime.now()

        rows = []
        for pkg in packages:
            last = usage.get(pkg)
            if last is None:
                age_days = None
                age_label = "NEVER"
                sort_key = -1  # sort first
            else:
                age_days = (now - last).days
                age_label = last.strftime("%Y-%m-%d")
                sort_key = age_days

            rows.append({
                "package": pkg,
                "label": pkg.split(".")[-1],   # short name fallback
                "last_used": last,
                "age_days": age_days,
                "age_label": age_label,
                "sort_key": sort_key if sort_key != -1 else 999999,
            })

        # Sort: never used first, then by most days unused
        rows.sort(key=lambda r: -r["sort_key"])

        self.call_from_thread(self.show_table, rows)
        
        # Trigger background fetch for missing names to cover thousands of popular apps dynamically
        self.fetch_missing_names(packages)

    def show_no_device(self) -> None:
        self.query_one("#loading-container").remove()
        self.mount(
            Label(
                "❌ No Android device found via ADB.\n\n"
                "1. Connect phone via USB\n"
                "2. Enable USB Debugging (Settings → Developer Options)\n"
                "3. Accept the RSA key prompt on your phone\n"
                "4. Press [R] to reload",
                id="no-device"
            )
        )

    def show_table(self, rows: list[dict]) -> None:
        self.all_rows = rows
        self.filtered_rows = rows[:]
        self.loading = False

        # Remove loading UI
        self.query_one("#loading-container").remove()

        # Build the UI
        top_bar = Horizontal(id="top-bar")
        search = Input(placeholder="🔍 Filter packages...", id="search-input")
        stats = Label("", id="stats-label")
        select_btns = Horizontal(
            Button("Select NEVER", variant="warning", id="sel-never"),
            Button("Deselect All", variant="default", id="desel-all"),
            id="select-btns"
        )

        legend = Static(
            "  [dim]SPACE[/dim] toggle  [dim]A[/dim] select-never  [dim]Ctrl+A[/dim] deselect-all  "
            "[dim]U[/dim] uninstall  [dim]R[/dim] reload  [dim]Q[/dim] quit",
            id="legend", markup=True
        )

        table = DataTable(id="app-table", cursor_type="row", zebra_stripes=True)
        table.add_columns("  ", "Package", "Short Name", "Last Used", "Days Ago")

        bottom_bar = Horizontal(
            Label("0 apps selected", id="selected-label"),
            Button("Uninstall Selected ⚠", variant="error", id="uninstall-btn", disabled=True),
            id="bottom-bar"
        )

        self.mount(top_bar)
        self.mount(legend)
        self.mount(table)
        self.mount(bottom_bar)

        self.query_one("#top-bar").mount(search)
        self.query_one("#top-bar").mount(stats)
        self.query_one("#top-bar").mount(select_btns)

        self.rebuild_table()

    def rebuild_table(self) -> None:
        try:
            table = self.query_one(DataTable)
        except Exception:
            return

        # Save cursor position (by package name) before clearing
        saved_pkg = None
        try:
            cell = table.get_row_at(table.cursor_row)[1]
            saved_pkg = cell.plain if hasattr(cell, "plain") else str(cell)
        except Exception:
            pass

        table.clear()

        never_count = sum(1 for r in self.filtered_rows if r["age_days"] is None)
        total = len(self.filtered_rows)

        for row in self.filtered_rows:
            pkg = row["package"]
            selected = pkg in self.selected
            checkbox = "◉" if selected else "○"

            # Color last-used
            if row["age_days"] is None:
                last_text = Text("NEVER", style="bold red")
                days_text = Text("—", style="dim")
            elif row["age_days"] > 180:
                last_text = Text(row["age_label"], style="yellow")
                days_text = Text(f"{row['age_days']}d", style="yellow")
            elif row["age_days"] > 60:
                last_text = Text(row["age_label"], style="cyan")
                days_text = Text(f"{row['age_days']}d", style="cyan")
            else:
                last_text = Text(row["age_label"], style="green")
                days_text = Text(f"{row['age_days']}d", style="green")

            checkbox_text = Text(checkbox, style="bold yellow" if selected else "dim")
            pkg_text = Text(pkg, style="bold" if selected else "")
            friendly = app_names.get(pkg, row["label"])
            friendly_text = Text(friendly, style="bold green" if app_names.has(pkg) else "dim")

            table.add_row(
                checkbox_text,
                pkg_text,
                friendly_text,
                last_text,
                days_text,
                key=pkg
            )

        # Restore cursor to same row
        if saved_pkg:
            try:
                table.move_cursor(row=table.get_row_index(saved_pkg))
            except Exception:
                pass

        # Update stats
        try:
            self.query_one("#stats-label").update(
                f"[dim]{total} apps  ·  [red]{never_count} never used[/red]  ·  "
                f"[yellow]{len(self.selected)} selected[/yellow][/dim]"
            )
        except Exception:
            pass

        self.update_bottom_bar()

    def update_bottom_bar(self) -> None:
        count = len(self.selected)
        try:
            self.query_one("#selected-label").update(
                f"[yellow]{count}[/yellow] app{'s' if count != 1 else ''} selected"
                if count > 0 else "No apps selected"
            )
            btn = self.query_one("#uninstall-btn")
            btn.disabled = count == 0
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower().strip()
        if query:
            self.filtered_rows = [
                r for r in self.all_rows
                if query in r["package"].lower() or query in r["label"].lower()
            ]
        else:
            self.filtered_rows = self.all_rows[:]
        self.rebuild_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        pkg = event.row_key.value
        if pkg in self.selected:
            self.selected.discard(pkg)
        else:
            self.selected.add(pkg)
        self.rebuild_table()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "sel-never":
            self.action_select_all_never()
        elif event.button.id == "desel-all":
            self.action_deselect_all()
        elif event.button.id == "uninstall-btn":
            self.action_uninstall()

    def action_toggle_selected(self) -> None:
        try:
            table = self.query_one(DataTable)
            row_key = table.cursor_row
            pkg = table.get_row_at(row_key)[1]
            # Extract plain text if Rich Text
            if hasattr(pkg, 'plain'):
                pkg = pkg.plain
            if pkg in self.selected:
                self.selected.discard(pkg)
            else:
                self.selected.add(pkg)
            self.rebuild_table()
        except Exception:
            pass

    def action_select_all_never(self) -> None:
        for r in self.filtered_rows:
            if r["age_days"] is None:
                self.selected.add(r["package"])
        self.rebuild_table()

    def action_deselect_all(self) -> None:
        self.selected.clear()
        self.rebuild_table()

    def action_uninstall(self) -> None:
        if not self.selected:
            return
        pkgs = list(self.selected)

        def do_uninstall(confirmed: bool | None) -> None:
            if not confirmed:
                return
            results = uninstall_packages(pkgs)
            # Remove successfully uninstalled from data
            removed = {p for p, ok in results.items() if ok}
            self.selected -= removed
            self.all_rows = [r for r in self.all_rows if r["package"] not in removed]
            self.filtered_rows = [r for r in self.filtered_rows if r["package"] not in removed]
            self.push_screen(ResultScreen(results))
            self.rebuild_table()

        self.push_screen(ConfirmScreen(len(pkgs), pkgs), do_uninstall)

    def action_reload(self) -> None:
        self.selected.clear()
        self.all_rows = []
        self.filtered_rows = []
        try:
            self.query_one(DataTable).remove()
            self.query_one("#top-bar").remove()
            self.query_one("#bottom-bar").remove()
            self.query_one("#legend").remove()
        except Exception:
            pass
        try:
            self.query_one("#no-device").remove()
        except Exception:
            pass
        loading = Vertical(
            Label("Reloading...", id="loading-label", markup=True),
            LoadingIndicator(),
            id="loading-container"
        )
        self.mount(loading)
        self.load_apps()


if __name__ == "__main__":
    app = ADBManager()
    app.run()