# -*- coding: utf-8 -*-
"""يحقن بنك الأسئلة من zad-alhuroof-questions.json داخل index.html،
ويحدّث بصمة sw.js ليصل التحديث إلى من ثبّت الموقع كتطبيق.

الملف zad-alhuroof-questions.json هو المرجع الوحيد للأسئلة.
عدّل فيه، ثم شغّل هذا الأمر ليحدّث الموقع:

    python build.py
"""
import hashlib
import io
import json
import re
import sys

LETTERS = ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش',
           'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه',
           'و', 'ي']

JSON_PATH = 'zad-alhuroof-questions.json'
HTML_PATH = 'index.html'
SW_PATH = 'sw.js'

BEGIN = '/* ══ بنك الأسئلة ══ مولَّد من zad-alhuroof-questions.json — لا تعدّله هنا */'
END = '/* ══ نهاية بنك الأسئلة ══ */'
SW_LINE = re.compile(r"^const VERSION = '[^']*';(\s*/\* ══ بصمة البناء ══ \*/)$", re.M)


def load_bank():
    data = json.load(io.open(JSON_PATH, encoding='utf-8'))

    seen = [g['letter'] for g in data]
    unknown = [x for x in seen if x not in LETTERS]
    if unknown:
        sys.exit('حروف غير معروفة في البنك: ' + ' '.join(unknown))
    repeated = sorted({x for x in seen if seen.count(x) > 1})
    if repeated:
        sys.exit('حروف مكرّرة في البنك: ' + ' '.join(repeated))

    for g in data:
        for i, it in enumerate(g['items']):
            if not it.get('q') or not it.get('a'):
                sys.exit('سؤال أو إجابة فارغة عند %s رقم %d' % (g['letter'], i))

    for x in LETTERS:
        if x not in seen:
            print('تنبيه: الحرف %s ليس له مدخل في البنك' % x)
    for g in data:
        if not g['items']:
            print('تنبيه: الحرف %s بلا أسئلة' % g['letter'])

    return data


def stamp_sw(html):
    """يضع بصمة index.html في sw.js ليُبطل مخزن النسخة السابقة."""
    version = hashlib.sha256(html.encode('utf-8')).hexdigest()[:12]
    sw = io.open(SW_PATH, encoding='utf-8', newline='').read()
    new, n = SW_LINE.subn(lambda m: "const VERSION = '%s';%s" % (version, m.group(1)), sw)
    if n != 1:
        sys.exit('لم أجد سطر البصمة في %s.' % SW_PATH)
    if new != sw:
        io.open(SW_PATH, 'w', encoding='utf-8', newline='').write(new)
        return version
    return None


def main():
    data = load_bank()
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    block = BEGIN + '\nconst RAW = ' + raw + ';\n' + END

    html = io.open(HTML_PATH, encoding='utf-8', newline='').read()
    pattern = re.escape(BEGIN) + '.*?' + re.escape(END)
    new, n = re.subn(pattern, lambda m: block, html, flags=re.S)
    if n != 1:
        sys.exit('لم أجد علامتي البنك في %s — أعدهما حول سطر const RAW.' % HTML_PATH)

    total = sum(len(g['items']) for g in data)
    if new == html:
        print('البنك في index.html مطابق للملف أصلاً · %d سؤالاً' % total)
    else:
        io.open(HTML_PATH, 'w', encoding='utf-8', newline='').write(new)
        print('حُدّث index.html · %d سؤالاً · %d حرفاً' % (total, len(data)))

    version = stamp_sw(new)
    if version:
        print('بصمة sw.js ← %s' % version)


if __name__ == '__main__':
    main()
