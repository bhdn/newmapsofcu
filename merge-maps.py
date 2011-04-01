#!/usr/bin/env python
import sys
import os
import Image

IMAGE_MODE = "RGB"
WIDTH = 501
HEIGHT = 401

def find_images(code, topdir):
    stepx = 0
    images = []
    maxy = 0
    while True:
        stepy = 0
        while True:
            path = "%s/%s-%02dx%02d.gif" % (topdir, code, stepx, stepy)
            if not os.path.exists(path):
                break
            maxy = stepy
            images.append((stepx, stepy, path))
            stepy += 1 
        if stepy == 0:
            break
        stepx += 1
    return stepx - 1, maxy, images

def merge(code, topdir):
    nx, ny, images = find_images(code, topdir)
    size = (WIDTH*nx/2, HEIGHT*ny/2)
    color = (0xff, 0xff, 0xff)
    big = Image.new(IMAGE_MODE, size, color)
    for x, y, path in images:
        img = Image.open(path)
        newimg = img.crop((0, HEIGHT/2, WIDTH/2, HEIGHT))
        xy = (x*HEIGHT/2, (ny-y-1)*(HEIGHT/2))
        big.paste(newimg, xy)
    big.save(os.path.join(topdir, code + "-big.png"))

merge(sys.argv[1], sys.argv[2])
