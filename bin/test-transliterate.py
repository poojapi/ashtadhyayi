#!/usr/bin/python
import sys

from indic_transliteration import sanscript

word = sanscript.transliterate("idam adbhutam", sanscript.HK, sanscript.DEVANAGARI)
print word.encode('utf-8')

#word = input('Type a word in devanagari: ')
while 1:
    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        break

    if not line:
        break

    print line
    word = line.decode('utf-8')
    print sanscript.transliterate(word, sanscript.ITRANS, sanscript.SLP1)
    print sanscript.transliterate(word, sanscript.ITRANS, sanscript.WX)
