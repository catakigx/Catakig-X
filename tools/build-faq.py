#!/usr/bin/env python3
"""Regenerates the FAQ and Keyboard Shortcuts sections of docs/index.html
from the app's Help pages (Troubleshooting.html, Keyboard-Shortcuts.html).
Usage: build-faq.py HELP_DIR INDEX_HTML"""
import re, sys
help_dir, index = sys.argv[1], sys.argv[2]
LINKS = {'ImportROMs': '<b>Import ROMs…</b>', 'ShowROMFolder': '<b>Show ROM Folder</b>',
         'ShowRecoveredDisks': '<b>Show Recovered Disks</b>',
         'ShowUserGuide': '<a href="Catakig-X-User-Guide.pdf">Catakig X User Guide</a>',
         'ShowTroubleshooting': '<a href="#faq">Troubleshooting &amp; FAQ</a>',
         'ShowKeyboardShortcuts': '<a href="#shortcuts">Keyboard Shortcuts</a>'}
def links(t):
    def f(m):
        name, text = m.group(1), m.group(2)
        if name == 'ShowKeyboardShortcuts': return f'<a href="#shortcuts">{text}</a>'
        if name == 'ShowUserGuide': return f'<a href="Catakig-X-User-Guide.pdf">{text}</a>'
        if name == 'ShowQuickStart': return f'<a href="Catakig-X-Quick-Start.pdf">{text}</a>'
        if name == 'ShowTroubleshooting': return f'<a href="#faq">{text}</a>'
        return f'<b>{text}</b>'
    return re.sub(r'<a href="catakig:(\w+)">(.*?)</a>', f, t, flags=re.S)
def body(path):
    s = open(path, encoding='utf-8').read()
    s = s[s.index('<body>')+6:s.index('</body>')]
    return re.sub(r'<!--.*?-->', '', s, flags=re.S)
def slug(t):
    t = t.replace('&amp;', 'and')
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

# FAQ
t = links(body(f'{help_dir}/Troubleshooting.html'))
out, group_open, item_open = [], False, False
for m in re.finditer(r'<(h2|h3)>(.*?)</\1>|(<p[ >].*?</p>)', t, flags=re.S):
    if m.group(1) == 'h2':
        if item_open: out.append('</div>\n</details>'); item_open = False
        if group_open: out.append('</div>')
        out.append(f'<h3 class="faq-group" id="faq-{slug(m.group(2))}">{m.group(2)}</h3>\n<div class="faq">')
        group_open = True
    elif m.group(1) == 'h3':
        if item_open: out.append('</div>\n</details>')
        out.append(f'<details>\n<summary>{m.group(2)}</summary>\n<div class="answer">')
        item_open = True
    elif item_open:
        out.append(m.group(3))
if item_open: out.append('</div>\n</details>')
if group_open: out.append('</div>')
faq = '\n'.join(out)

# Shortcuts
k = links(body(f'{help_dir}/Keyboard-Shortcuts.html'))
k = re.sub(r'<h1>.*?</h1>\s*<p class="intro">.*?</p>', '', k, flags=re.S)
k = k.replace('<h2>', '<h3 class="faq-group">').replace('</h2>', '</h3>').replace('<table>', '<table class="keys">')
shortcuts = k.strip()

s = open(index, encoding='utf-8').read()
s = re.sub(r'(<!-- FAQ:BEGIN -->\n).*?(\n<!-- FAQ:END -->)', lambda m: m.group(1)+faq+m.group(2), s, flags=re.S)
s = re.sub(r'(<!-- SHORTCUTS:BEGIN -->\n).*?(\n<!-- SHORTCUTS:END -->)', lambda m: m.group(1)+shortcuts+m.group(2), s, flags=re.S)
open(index, 'w', encoding='utf-8').write(s)
