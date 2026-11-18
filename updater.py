"""User-initiated updates from this project's public GitHub releases."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from tkinter import messagebox
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from localization import tr

REPOSITORY = 'cyberfirepulse/AssemblyEditor'
API_URL = 'https://api.github.com/repos/' + REPOSITORY + '/releases/latest'
MAX_INSTALLER_BYTES = 200 * 1024 * 1024

def version_tuple(value):
    match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', value)
    if not match:
        raise ValueError(tr('Ongeldige releaseversie.'))
    return tuple(map(int, match.groups()))

def open_url(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in ('api.github.com', 'github.com'):
        raise ValueError(tr('Ongeldige downloadbron.'))
    return urlopen(Request(url, headers={'User-Agent': 'CyberFirePulse-AssemblyEditor',
                                        'Accept': 'application/vnd.github+json'}), timeout=30)

def bounded_read(url, limit):
    with open_url(url) as response:
        result = response.read(limit + 1)
    if len(result) > limit:
        raise ValueError(tr('Download is groter dan toegestaan.'))
    return result

def latest_release(current):
    try:
        release = json.loads(bounded_read(API_URL, 1024 * 1024))
    except Exception as exc:
        # GitHub returns 404 when there is no published regular release yet.
        if getattr(exc, 'code', None) == 404:
            return None
        raise
    if release.get('draft') or release.get('prerelease'):
        return None
    version = release['tag_name'].removeprefix('v')
    if version_tuple(version) <= version_tuple(current):
        return None
    expected = ('AssemblyEditor_' + version + '_Setup.exe', 'AssemblyEditor_' + version + '_SHA256.txt')
    assets = {asset['name']: asset['browser_download_url'] for asset in release.get('assets', [])}
    urls = []
    for name in expected:
        if name not in assets:
            raise ValueError(tr('De release mist een installer of controlesommenbestand.'))
        url = assets[name]
        prefix = 'https://github.com/' + REPOSITORY + '/releases/download/' + release['tag_name'] + '/'
        if url != prefix + name:
            raise ValueError(tr('Ongeldige downloadbron.'))
        urls.append(url)
    return version, expected[0], urls

def download_verified(release):
    version, filename, (installer_url, checksum_url) = release
    checksums = bounded_read(checksum_url, 65536).decode('utf-8-sig')
    digest = None
    for line in checksums.splitlines():
        match = re.fullmatch(r'([a-fA-F0-9]{64})\s+\*?(.+)', line.strip())
        if match and match[2] == filename:
            digest = match[1].lower()
    if digest is None:
        raise ValueError(tr('Geen geldige SHA-256 voor de installer gevonden.'))
    folder = Path(tempfile.mkdtemp(prefix='AssemblyEditor-update-'))
    target = folder / filename
    partial = folder / (filename + '.partial')
    try:
        hasher = hashlib.sha256()
        total = 0
        with open_url(installer_url) as response, partial.open('xb') as stream:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_INSTALLER_BYTES:
                    raise ValueError(tr('Download is groter dan toegestaan.'))
                hasher.update(chunk)
                stream.write(chunk)
        if hasher.hexdigest() != digest:
            raise ValueError(tr('SHA-256 komt niet overeen. De installer wordt niet gestart.'))
        os.replace(partial, target)
        return target
    except Exception:
        partial.unlink(missing_ok=True)
        folder.rmdir()
        raise

def check_for_updates(app):
    def checked(release):
        if not release:
            messagebox.showinfo(tr('Controleren op updates'), tr('Je gebruikt de nieuwste beschikbare versie.'), parent=app)
            return
        version, filename, urls = release
        prompt = tr('Nieuwe versie beschikbaar: ') + version + '\n\n' + tr('Installer downloaden en met SHA-256 controleren?')
        if not messagebox.askyesno(tr('Controleren op updates'), prompt, parent=app):
            return
        app.log(tr('Update downloaden en controleren...'))
        def downloaded(path):
            prompt = tr('Download gecontroleerd. Installer starten? Sla je werk op en sluit de editor voordat je de installatie afrondt.')
            if messagebox.askyesno(tr('Update installeren'), prompt, parent=app):
                if not app.confirm_replace():
                    return
                try:
                    if os.name != 'nt':
                        raise OSError(tr('Deze installer is alleen voor Windows.'))
                    subprocess.Popen([str(path)])
                except OSError as exc:
                    messagebox.showerror(tr('Update installeren'), str(exc), parent=app)
        app.start_task(lambda: download_verified(release), downloaded)
    app.log(tr('Controleren op updates...'))
    app.start_task(lambda: latest_release(app.version), checked)
