#!/usr/bin/env python

import subprocess
import string


#made with
#convert -list font  | grep 'Font:' | cut -f 2 -d : | grep -vi 'bold' | grep -vi 'italic' | grep -vi 'oblique' > fontlist.txt
fonts = []
fontfile = open("fontlist.txt", "r")
for line in fontfile:
    if not line.startswith("#"):
        fonts.append(line)
fontfile.close()


#convert -size 48x48 xc:white -fill white -fill black -font Courier -pointsize 40 -gravity center -draw "text 0,0  P" P.png
for f in fonts:
    print "||font: ", f.strip()
    for c in string.ascii_letters + string.digits:
    #for c in ["W"]:
        cmd = "/usr/bin/convert -size 48x48 xc:white -fill white -fill black -font {0} -pointsize 40 -gravity center".format(f.strip())
        cmdDraw = "-draw \"text 0,0  '{0}'\"".format(c)
        outFile = "letters/{0}_{1}.png".format(f.strip(), c)

        subprocess.call(" ".join([cmd, cmdDraw, outFile]), shell=True)
