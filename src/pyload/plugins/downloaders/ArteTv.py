"""
pyLoad Plugin: ArteTv.py
Unterstützte URLs:
  https://www.arte.tv/de/videos/106660-000-A/die-unsichtbare-patientin-sind-frauen-anders-krank/
  https://www.arte.tv/fr/videos/106660-000-A/la-sante-des-femmes-de-l-ignorance-a-la-reconnaissance/
  https://www.arte.tv/en/videos/106660-000-A/are-women-ill-differently/
  ... (alle Sprachvarianten: de, fr, en, es, pl, it)

Ablauf:
  1. Video-ID und Sprache aus der URL extrahieren
  2. ARTE Player API v2 abfragen (config + playlist Endpunkt)
  3. Beste verfügbare Stream-Qualität auswählen (bevorzugt MP4, sonst HLS)
  4. Download starten

Getestet mit pyLoad 0.4.x und pyLoad-ng (0.5.x).
"""

import re
import json
import json
import operator
import os
import re
import subprocess
import time
import urllib.parse
from datetime import timedelta

from pyload import PKGDIR
from pyload.core.utils.convert import to_str
from pyload.core.utils import fs

from ..base.simple_downloader import SimpleDownloader
from ..helpers import exists, is_executable, renice, replace_patterns, which
from pyload.core.utils.fs import safename
from urllib.parse import urljoin
import re
# import requests
from urllib.parse import urljoin


class ArteTv(SimpleDownloader):
    __name__    = "ArteTv"
    __type__    = "downloader"
    __version__ = "0.01"
    __status__  = "testing"

    # Alle unterstützten Sprachkürzel lt. arte.tv
    __SUPPORTED_LANGS__ = ("de", "fr", "en", "es", "pl", "it")

    __pattern__ = r"https?://(?:www\.)?arte\.tv/(?P<lang>de|fr|en|es|pl|it)/videos/(?P<video_id>\d{5,}-\d{3}-[A-Z])/.*"

    __description__ = "arte.tv video downloader"
    __license__     = "GPLv3"
    __authors__     = [("pyLoad Community", "")]

    # Qualitätsrangfolge (absteigend) – wir wählen das beste verfügbare Format
    QUALITY_ORDER = ["SQ_3", "HQ", "MQ", "EQ", "SQ", "XQ", "XQ"]

    # API-Endpunkte (Player API v2)
    API_CONFIG_URL   = "https://api.arte.tv/api/player/v2/config/{lang}/{video_id}"
    API_PLAYLIST_URL = "https://api.arte.tv/api/player/v2/playlist/{lang}/{video_id}"

    def process(self, pyfile):
        m = re.match(self.__pattern__, pyfile.url)
        if not m:
            self.error("URL passt nicht zum Muster")

        lang     = m.group("lang")
        video_id = m.group("video_id")

        self.log_debug(f"Starte Download: lang={lang}, video_id={video_id}")

        # ---------- 1. Playlist-API abfragen (liefert direkte Stream-Links) ----------
        playlist_url = self.API_PLAYLIST_URL.format(lang=lang, video_id=video_id)
        try:
            playlist_data = self.load(playlist_url, decode=True)
        except Exception as e:
            self.log_warning(f"Playlist-API nicht erreichbar: {e}")
            playlist_data = None

        stream_url = None
        filename   = None

        if playlist_data:

            try:
                data = json.loads(playlist_data)
                stream_url, filename = self._parse_playlist(data, lang)
            except (ValueError, KeyError) as e:
                self.log_warning(f"Playlist-Parsing fehlgeschlagen: {e}")

        # ---------- 2. Fallback: Config-API ----------
        if not stream_url:
            config_url = self.API_CONFIG_URL.format(lang=lang, video_id=video_id)
            try:
                config_data = self.load(config_url, decode=True)
            except Exception as e:
                self.fail(f"Beide API-Endpunkte nicht erreichbar: {e}")

            try:
                data = json.loads(config_data)
                stream_url, filename = self._parse_config(data, lang)
            except (ValueError, KeyError) as e:
                self.fail(f"Config-Parsing fehlgeschlagen: {e}")

        if not stream_url:
            self.fail("Kein Stream-Link gefunden – Video möglicherweise nicht verfügbar oder geoblockt")

        if filename:
            pyfile.name = safename(filename)

        self.log_info(f"Lade herunter: {pyfile.name}")
        self.log_debug(f"Stream-URL: {stream_url}")

        # pyfile.url = stream_url
        m3u8_data = self.load(stream_url)
        streams = {}
        for m in re.finditer(r"#EXT-X-STREAM-INF:(.+\s.+)", m3u8_data):
            stream = dict(
                [
                    (x.group(1) or x.group(5), x.group(2) or x.group(3) or x.group(4))
                    for x in re.finditer(r'([\w-]+)=(?:(?=")"([^"]+)|(?!")([^,]+))|((http)s?://\S+)', m.group(1))
                ]
            )
            quality = int(stream["RESOLUTION"].split("x")[1])
            audio = stream["AUDIO"]
            subtitles = stream["SUBTITLES"]
            dl_url = stream["http"]
            streams[quality] = streams.get(quality, []) + [dl_url, audio, subtitles]
        audio_streams = {}
        for m in re.finditer(r"#EXT-X-MEDIA:(.+\S.+)", m3u8_data):
            stream = dict(
                [
                    (x.group(1), x.group(2) or x.group(3))
                    for x in re.finditer(r'([\w-]+)=(?:(?=")"([^"]+)|(?!")([^,]+))', m.group(1))
                ]
            )
            type =  stream["GROUP-ID"]
            language = stream["LANGUAGE"]
            title = stream["NAME"]
            dl_url = stream["URI"]
            if not type in audio_streams:
                audio_streams[type] = []
            audio_streams.get(type, []).append([dl_url, language, title])

        self.pyfile.set_custom_status("downloading")
        self.pyfile.set_progress(0)

        self.ffmpeg = Ffmpeg(self.config.get("priority"), self)

        if self.ffmpeg.found:
            self.ffmpeg.set_video(streams[720])
            self.ffmpeg.set_audio_streams(audio_streams)
            # Untertitel müssen auch noch dazu

            dl_root_folder = self.pyload.config.get("general", "storage_folder")
            dl_package_folder = fs.safejoin(dl_root_folder, self.pyfile.package().folder)
            if not os.path.exists(dl_package_folder):
                os.makedirs(dl_package_folder)
            self.ffmpeg.set_output_filename(dl_package_folder, pyfile.name)
            self.pyfile.size = 1000000000

            if not self.ffmpeg.run():
                self.log_warning(self._("ffmpeg error"), self.ffmpeg.error_message)

        self.pyfile.set_progress(100)
        self.last_download = pyfile.name

    # -----------------------------------------------------------------------
    # Interne Hilfsmethoden
    # -----------------------------------------------------------------------

    def _parse_playlist(self, data, lang):
        """
        Parst die Antwort des /playlist/ Endpunkts.
        Struktur (vereinfacht):
        {
          "data": {
            "attributes": {
              "streams": [
                {
                  "url": "https://.../<quality>.mp4",
                  "versions": [{"label": "VOF-DE", ...}],
                  "mainQuality": {"code": "SQ_3", ...}
                }
              ],
              "metadata": {"title": "...", "subtitle": "..."}
            }
          }
        }
        """
        attrs    = data["data"]["attributes"]
        streams  = attrs.get("streams", [])
        metadata = attrs.get("metadata", {})

        title    = metadata.get("title", "")
        subtitle = metadata.get("subtitle", "")
        filename = self._build_filename(title, subtitle)

        best_url, best_q = self._select_best_stream(streams, prefer_mp4=True)
        if best_url:
            self.log_info(f"Gewählte Qualität: {best_q}")
        return best_url, filename

    def _parse_config(self, data, lang):
        """
        Parst die Antwort des /config/ Endpunkts.
        Struktur (vereinfacht):
        {
          "data": {
            "attributes": {
              "streams": [...],
              "metadata": {"title": "...", "subtitle": "..."}
            }
          }
        }
        """
        # Config-API hat dieselbe Struktur wie Playlist-API
        return self._parse_playlist(data, lang)

    def _select_best_stream(self, streams, prefer_mp4=True):
        """
        Wählt den besten Stream nach Qualitätscode und Format.
        Bevorzugt MP4 gegenüber HLS (.m3u8), sofern verfügbar.
        Gibt (url, quality_code) zurück.
        """
        # Gruppiere nach Qualitätscode
        by_quality = {}
        for stream in streams:
            url = stream.get("url", "")
            if not url:
                continue
            q = stream.get("mainQuality", {}).get("code", "UNKNOWN")
            # Bevorzuge MP4
            if q not in by_quality:
                by_quality[q] = url
            elif prefer_mp4 and not url.endswith(".m3u8") and by_quality[q].endswith(".m3u8"):
                by_quality[q] = url

        # Wähle beste verfügbare Qualität aus der Rangfolge
        for q in self.QUALITY_ORDER:
            if q in by_quality:
                return by_quality[q], q

        # Fallback: irgendeinen nehmen
        if by_quality:
            q, url = next(iter(by_quality.items()))
            return url, q

        return None, None

    def _build_filename(self, title, subtitle):
        """Baut einen sinnvollen Dateinamen aus Titel und Untertitel."""
        parts = [p.strip() for p in [title, subtitle] if p and p.strip()]
        name  = " - ".join(parts) if parts else "arte_video"
        return safename(name) + ".mkv"


class Ffmpeg:
    _RE_DURATION = re.compile(rb"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2}),")
    _RE_TIME = re.compile(rb"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})")
    _RE_VERSION = re.compile(rb"ffmpeg version (.+?) ")

    CMD = None
    priority = 0
    output_filename = None
    error_message = ""

    def __init__(self, priority, plugin=None):
        self.plugin = plugin
        self.priority = priority

        self.video = None
        self.audio_streams = {}
        self.folder = None
        self.output_filename = None
        self.temp_filename = None
        self.error_message = ""

        self.find()

    @classmethod
    def find(cls):
        """
        Check for ffmpeg.
        """
        if cls.CMD is not None:
            return True

        try:
            if os.name == "nt":
                ffmpeg = (
                    os.path.join(PKGDIR, "lib", "ffmpeg.exe")
                    if is_executable(os.path.join(PKGDIR, "lib", "ffmpeg.exe"))
                    else "ffmpeg.exe"
                )
            else:
                ffmpeg = "ffmpeg"
            cmd = which(ffmpeg) or ffmpeg
            p = subprocess.Popen([cmd, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = (r.strip() if r else "" for r in p.communicate())
        except OSError:
            return False

        m = cls._RE_VERSION.search(out)
        if m is not None:
            cls.VERSION = m.group(1)

        cls.CMD = cmd

        return True

    @property
    def found(self):
        return self.CMD is not None

    def set_video(self, video):
        self.video = video

    def set_audio_streams(self, audio_streams):
        self.audio_streams = audio_streams

    def set_output_filename(self, folder, output_filename):
        self.folder = folder
        self.temp_filename = fs.safejoin(folder, "1_" + output_filename)
        self.output_filename = fs.safejoin(folder, output_filename)

    def download_vtt(self, m3u8_url):
        # text = self.plugin.data
        vtt_name = next(
            line.strip()
            for line in self.plugin.data.splitlines()
            if line.strip() and not line.startswith("#")
        )

        vtt_url = urljoin(m3u8_url, vtt_name)

        r = self.plugin.load(vtt_url)
        target = os.path.join(self.folder, vtt_name)
        with open(target, "w") as fp:
            fp.write(r)

        return target

    def classify_subtitle_source(self, url):
        if url.endswith(".vtt"):
            return "direct_vtt"
        if url.endswith(".m3u8"):
            self.plugin.data = self.plugin.load(url)
            vtt_count = len(re.findall(r"\.vtt", self.plugin.data))
            # CASE 1: single-file wrapper
            if vtt_count == 1:
                return "single_file_m3u8"
            # CASE 2: real HLS subtitle
            return "hls_m3u8"
        return "unknown"

    def resolve_subtitle(self, url):
        mode = self.classify_subtitle_source(url)
        if mode == "direct_vtt":
            return url
        if mode == "single_file_m3u8":
            # toDo: targefile_name definieren
            return self.download_vtt(url)
            # self.parse_m3u8_for_single_file(url)
        if mode == "hls_m3u8":
            return url
        return url

    def run(self):
        if self.CMD is None:
            return False

        if self.output_filename is None:
            return False

        if self.video is None:
            self.error_message = "No video stream defined"
            return False

        video_url = self.video[0]
        audio_group = self.video[1]
        subtitle_group = self.video[2]

        inputs = []
        maps = []
        metadata = []

        # Video
        inputs.extend(["-i", video_url,])
        maps.extend(["-map", "0:v:0",])
        input_index = 1
        # Audio
        audio_streams = self.audio_streams.get(audio_group, [])
        for idx, (audio_url, language, title) in enumerate(audio_streams, start=1):
            inputs.extend(["-i", audio_url])
            maps.extend(["-map", f"{input_index}:a:0"])
            metadata.extend([f"-metadata:s:a:{idx}", "language={}".format(language)])
            metadata.extend([f"-metadata:s:a:{idx}", "title={}".format(title)])
            input_index += 1

        call = ([self.CMD] + ["-loglevel", "level"] + inputs + maps + metadata
                + ["-c:v", "copy", "-c:a", "copy", "-y", self.temp_filename]
        )

        self.plugin.log_debug("EXECUTE " + " ".join(call))

        # encoding="utf-8"could be added for unicode instead of binary output
        p = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        renice(p.pid, self.priority)

        duration = self._find_duration(p) * 1.2

        if duration:
            last_line, stderr_log = self._progress(p, duration)
        else:
            last_line = ""
            stderr_log =[]

        out, err = (r.strip() if r else b"" for r in p.communicate())

        if p.returncode != 0:
            self.error_message = stderr_log
            return False

        self.error_message = ""

        # 2nd Call to merge subtitles
        inputs = []
        maps = []
        metadata = []
        inputs.extend(["-i", self.temp_filename])
        maps.extend(["-map", "0:v:0"])
        input_index = 1
        audio_streams = self.audio_streams.get(audio_group, [])
        for idx, __ in enumerate(audio_streams):
            # inputs.extend(["-i", audio_url])
            maps.extend(["-map", f"0:a:{idx}"])

        subtitle_streams = self.audio_streams.get(subtitle_group, [])
        for subtitle_index, (subtitle_url, language, title) in enumerate(subtitle_streams):
            real_url = self.resolve_subtitle(subtitle_url)
            inputs.extend(["-i", real_url])
            maps.extend(["-map", f"{input_index}:0"])
            metadata.extend([f"-metadata:s:s:{subtitle_index}", f"language={language}"])
            metadata.extend([f"-metadata:s:s:{subtitle_index}", f"language={title}"])
            input_index += 1

        call = ([self.CMD] + ["-loglevel", "level"] + inputs + maps + metadata
                + ["-c:v", "copy", "-c:a", "copy", "-c:s", "copy", "-y", self.output_filename]
        )

        self.plugin.log_debug("EXECUTE " + " ".join(call))

        # encoding="utf-8"could be added for unicode instead of binary output
        p = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        renice(p.pid, self.priority)

        duration = self._find_duration(p)

        if duration:
            last_line, stderr_log = self._progress(p, duration)
        else:
            last_line = ""
            stderr_log =[]

        out, err = (r.strip() if r else b"" for r in p.communicate())

        if p.returncode != 0:
            self.error_message = stderr_log
            return False

        self.error_message = ""

        return True

    def _find_duration(self, process):
        duration = 0
        while True:
            line = process.stderr.readline()  #: ffmpeg writes to stderr
            self.plugin.log_debug(f"ffmpg output:{line}")

            #: Quit loop on eof
            if not line:
                break

            m = self._RE_DURATION.search(line)
            if m is not None:
                duration = sum(
                    int(v) * [60 * 60 * 100, 60 * 100, 100, 1][i]
                    for i, v in enumerate(m.groups())
                )
                break

        return duration

    def _progress(self, process, duration):
        line = b""
        current_line = ""
        last_line = b""
        stderr_log = []
        while True:
            c = process.stderr.read(1)  #: ffmpeg writes to stderr

            #: Quit loop on eof
            if not c:
                stderr_log.append(line)
                # self.plugin.log_debug(f"ffmpg output:{line}")
                break

            elif c == b"\r":
                last_line = line.strip(b"\r\n")
                stderr_log.append(last_line)
                # self.plugin.log_debug(f"ffmpg output:{line}")
                line = b""
                m = self._RE_TIME.search(last_line)
                if m is not None:
                    current_time = sum(
                        int(v) * [60 * 60 * 100, 60 * 100, 100, 1][i]
                        for i, v in enumerate(m.groups())
                    )
                    if self.plugin:
                        progress = current_time * 100 // duration
                        self.plugin.pyfile.set_progress(progress)

            else:
                line += c
            continue
        return (to_str(last_line), "\n".join(to_str(x) for x in stderr_log))  #: Last line may contain error message
