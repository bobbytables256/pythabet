#!/usr/bin/env python

import sys, os, glob, random
import subprocess
import string

from PIL import Image
from PIL import ImageFilter
import pyocr

#number of letter copies to paste into a file to OCR
OCR_REPEAT = 20
#number of samples to start each generation with
GEN_SIZE = 12 
#number of fenerations to run
GEN_NUM = 12

#set up pyOCR
#keep this global so we only have to load it once
OCR = pyocr.get_available_tools()[0]

def main():
    inp = loadInputs()

    print "Using OCR tool: ", OCR.get_name()

    #for letter in inp["Courier"]:
    #for letter in "cgGZ":
    for letter in string.ascii_lowercase + string.digits:
        print "Starting letter:", letter
        #first generation, pick some random fonts
        samples = []
        fonts = random.sample(inp, GEN_SIZE)
        for f in fonts:
            temp = Image.new("L", (48,48))
            temp.putdata(inp[f][letter])
            samples.append(temp)

        scores = scoreSamples(samples, letter)

        for gen in range(GEN_NUM): #number of generations to run
            print "Running {} gen {}".format(letter, gen)
            samples =  makeNewGen(scores, letter, float(gen)/GEN_NUM, inp)
            scores = scoreSamples(samples, letter)
            #save out all of the scores
            for i in range(len(scores)):
                scores[i][0].save('{}_{:03d}_{:05d}_{:03d}.png'.format(letter, gen, scores[i][1], i))
            #save out the best score in each generation
            scores[0][0].save('best/best_{}_{:03d}_{:05d}.png'.format(letter, gen, scores[0][1]))

        #save out the final best score
        scores[0][0].save('!final{}_{:05d}.png'.format(letter, scores[0][1]))


    return

#return a list of new samples
#"heat" progresses from 0.0 to 1.0 as the generations pass
#and is used to give more conservative modifications in later generations
def makeNewGen(scores, letter, heat, inp):
    samples = []
    if heat > 0.7:
        #very conservative move: copy over the best two from the previous gen directly
        samples.append(scores[0][0])
        samples.append(scores[1][0])
    #if heat > 0.9:
        #conservative move: copy smoothed and sharpened versions of the best two
        #a = scores[0][0].filter(ImageFilter.GaussianBlur(0.5))
        #b = scores[1][0].filter(ImageFilter.GaussianBlur(0.5))
        #samples.append(a.filter(ImageFilter.SHARPEN))
        #samples.append(b.filter(ImageFilter.SHARPEN))
    if heat > 0.7:
        #take one of the top 3 and copy a square onto itself to move things around a bit
        i = random.choice([0, 1, 2])
        a = scores[i][0]
        copyRandomSquare(a, a)
        copyRandomSquare(a, a)
        copyRandomSquare(a, a)

    if heat < 0.5:
        #introduce a lot of new randomness into the pool
        #cross the best two with two new random fonts each
        a1 = scores[0][0].copy()
        a2 = a1.copy()
        b1 = scores[1][0].copy()
        b2 = b1.copy()
        #easiest way to make an image to fill is just to copy one
        rand = a1.copy()
        fonts = random.sample(inp, 8)
        #fill rand with a random font
        rand.putdata(inp[fonts[0]][letter])
        crossRandomSquare(a1, rand)
        rand.putdata(inp[fonts[1]][letter])
        crossRandomSquare(a1, rand)
        samples.append(a1)

        rand.putdata(inp[fonts[2]][letter])
        crossRandomSquare(a2, rand)
        rand.putdata(inp[fonts[3]][letter])
        crossRandomSquare(a2, rand)
        samples.append(a2)

        rand.putdata(inp[fonts[4]][letter])
        crossRandomSquare(b1, rand)
        rand.putdata(inp[fonts[5]][letter])
        crossRandomSquare(b1, rand)
        samples.append(b1)

        rand.putdata(inp[fonts[6]][letter])
        crossRandomSquare(b2, rand)
        rand.putdata(inp[fonts[7]][letter])
        crossRandomSquare(b2, rand)
        samples.append(b2)

    #cross the best three with eachother
    a = scores[0][0].copy()
    b = scores[1][0].copy()
    c = scores[2][0].copy()
    crossRandomSquare(a, b)
    crossRandomSquare(a, c)
    crossRandomSquare(b, c)
    samples.append(a)
    samples.append(b)
    samples.append(c)
    #copy parts from two best into the third
    c = scores[2][0].copy()
    copyRandomSquare(c, scores[0][0])
    copyRandomSquare(c, scores[0][0])
    copyRandomSquare(c, scores[1][0])
    copyRandomSquare(c, scores[1][0])
    #maybe add a bit of blur or sharpen
    #if random.choice([True] + [False]*19):
    #    c = c.filter(ImageFilter.GaussianBlur(random.random()*0.5))
    #    c = c.filter(ImageFilter.SHARPEN)
    samples.append(c)
    #now fill the rest randomly
    for i in range(len(samples), GEN_SIZE):
        l = random.sample(scores, 4)
        n = l[0][0].copy()
        crossRandomSquare(n, l[1][0].copy())
        crossRandomSquare(n, l[2][0].copy())
        copyRandomSquare(n, n)
        copyRandomSquare(n, n)
        copyRandomSquare(n, l[3][0])
        copyRandomSquare(n, l[3][0])
        #if random.choice([True] + [False]*19):
        #    n = (n.filter(ImageFilter.GaussianBlur(random.random()*0.2)))
        #    n = n.filter(ImageFilter.SHARPEN)
        samples.append(n)
    return samples

#return a sorted list of (sample, score) tuples
def scoreSamples(samples, letter):
    scores = []
    for sample in samples:
        scores.append((sample, scoreOCR(letter, sample)))
    scores.sort(key=lambda x: -x[1])
    return scores


def noise(pixel):
    rand = random.random()
    if rand > 0.95:
        return 255 - pixel
    else:
        return pixel


def scoreOCR(letter, im):
    #print "OCR_R:", (OCR_REPEAT*48)
    comp = Image.new("L", (48*OCR_REPEAT, 48))
    for i in range(OCR_REPEAT):
        data = im.getdata()
        data = map(noise, data)
        temp = im.copy()
        temp.putdata(data)
        #temp.save(str(i) + ".png")
        comp.paste(temp, (48*i, 0))
    comp.save("temp.png")
    #get rid of whitespace and other weird characters 
    word = filter((lambda x: x in string.ascii_letters + string.digits), 
        OCR.image_to_string(comp, lang="eng", builder=pyocr.builders.TextBuilder()))
    #word = word.encode('ascii', 'replace')
    score = 2*word.count(letter) - len(word) 
    print score, "|", word
    #fix some range issues
    return score


def loadInputs():
    inputs = {}

    for infile in glob.glob("letters/*.png"):
        print "Loading:", infile
        root, ext = os.path.splitext(infile)
        font = os.path.basename(root)[:-2]
        char = root[-1:]
        #print font, "|", char
        if font not in inputs:
            inputs[font] = {}
        im = Image.open(infile)
        inputs[font][char] = list(im.getdata())
    return inputs

#We might want to put more constraints on a span, such as minimum width
def makeRandSpan():
    minWidth = 6
    z0 = z1 = 0
    while z0 == z1:
        z0 = random.randrange(48)
        z1 = random.randrange(48)
    if z0 <= z1:
        return (z0, z1)
    else:
        return (z1, z0)

#modifies a, b in-place
def crossRandomSquare(a, b):
    (x0, x1) = makeRandSpan()
    (y0, y1) = makeRandSpan()
    for x in range(x0, x1+1):
        for y in range(y0, y1+1):
            t = a.getpixel((x,y))
            a.putpixel((x,y), b.getpixel((x,y)))
            b.putpixel((x,y), t)

#copy a randomly-sized square from src to dest,
#adding a possible drift in the x and y dimensions
#modifies dest in-place
def copyRandomSquare(dest, src):
    (x0, x1) = makeRandSpan()
    (y0, y1) = makeRandSpan()
    xD = random.randint(-4,4)
    yD = random.randint(-4,4)
    for x in range(x0, x1+1):
        for y in range(y0, y1+1):
            #check to make sure the point is in bounds after applying the drift 
            if x0+xD >= 0 and x1+xD < 48 and y0+yD >= 0 and y1+yD < 48:
                dest.putpixel((x,y), src.getpixel((x,y)) )

def makeRandomMark(a):
    #center of the mark
    xC = random.randint(2, 44)
    yC = random.randint(2, 44)
    val = random.choice([0, 255])
    for x in range(xC-2, xC+3):
        for y in range(yC-2, yC+3):
            a[x*48+y] = val

#dump char arrays to the terminal for crude debugging
def dumpChar(pixelList):
    s = ""
    for x in range(48):
        for y in range(48):
            s += str( (pixelList[x*48+y]+1)/32 )
        s += "\n"
    return s

if __name__ == "__main__":
    main()
