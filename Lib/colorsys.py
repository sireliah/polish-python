"""Conversion functions between RGB oraz other color systems.

This modules provides two functions dla each color system ABC:

  rgb_to_abc(r, g, b) --> a, b, c
  abc_to_rgb(a, b, c) --> r, g, b

All inputs oraz outputs are triples of floats w the range [0.0...1.0]
(przy the exception of I oraz Q, which covers a slightly larger range).
Inputs outside the valid range may cause exceptions albo invalid outputs.

Supported color systems:
RGB: Red, Green, Blue components
YIQ: Luminance, Chrominance (used by composite video signals)
HLS: Hue, Luminance, Saturation
HSV: Hue, Saturation, Value
"""

# References:
# http://en.wikipedia.org/wiki/YIQ
# http://en.wikipedia.org/wiki/HLS_color_space
# http://en.wikipedia.org/wiki/HSV_color_space

__all__ = ["rgb_to_yiq","yiq_to_rgb","rgb_to_hls","hls_to_rgb",
           "rgb_to_hsv","hsv_to_rgb"]

# Some floating point constants

ONE_THIRD = 1.0/3.0
ONE_SIXTH = 1.0/6.0
TWO_THIRD = 2.0/3.0

# YIQ: used by composite video signals (linear combinations of RGB)
# Y: perceived grey level (0.0 == black, 1.0 == white)
# I, Q: color components
#
# There are a great many versions of the constants used w these formulae.
# The ones w this library uses constants z the FCC version of NTSC.

def rgb_to_yiq(r, g, b):
    y = 0.30*r + 0.59*g + 0.11*b
    i = 0.74*(r-y) - 0.27*(b-y)
    q = 0.48*(r-y) + 0.41*(b-y)
    zwróć (y, i, q)

def yiq_to_rgb(y, i, q):
    # r = y + (0.27*q + 0.41*i) / (0.74*0.41 + 0.27*0.48)
    # b = y + (0.74*q - 0.48*i) / (0.74*0.41 + 0.27*0.48)
    # g = y - (0.30*(r-y) + 0.11*(b-y)) / 0.59

    r = y + 0.9468822170900693*i + 0.6235565819861433*q
    g = y - 0.27478764629897834*i - 0.6356910791873801*q
    b = y - 1.1085450346420322*i + 1.7090069284064666*q

    jeżeli r < 0.0:
        r = 0.0
    jeżeli g < 0.0:
        g = 0.0
    jeżeli b < 0.0:
        b = 0.0
    jeżeli r > 1.0:
        r = 1.0
    jeżeli g > 1.0:
        g = 1.0
    jeżeli b > 1.0:
        b = 1.0
    zwróć (r, g, b)


# HLS: Hue, Luminance, Saturation
# H: position w the spectrum
# L: color lightness
# S: color saturation

def rgb_to_hls(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    # XXX Can optimize (maxc+minc) oraz (maxc-minc)
    l = (minc+maxc)/2.0
    jeżeli minc == maxc:
        zwróć 0.0, l, 0.0
    jeżeli l <= 0.5:
        s = (maxc-minc) / (maxc+minc)
    inaczej:
        s = (maxc-minc) / (2.0-maxc-minc)
    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)
    jeżeli r == maxc:
        h = bc-gc
    albo_inaczej g == maxc:
        h = 2.0+rc-bc
    inaczej:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    zwróć h, l, s

def hls_to_rgb(h, l, s):
    jeżeli s == 0.0:
        zwróć l, l, l
    jeżeli l <= 0.5:
        m2 = l * (1.0+s)
    inaczej:
        m2 = l+s-(l*s)
    m1 = 2.0*l - m2
    zwróć (_v(m1, m2, h+ONE_THIRD), _v(m1, m2, h), _v(m1, m2, h-ONE_THIRD))

def _v(m1, m2, hue):
    hue = hue % 1.0
    jeżeli hue < ONE_SIXTH:
        zwróć m1 + (m2-m1)*hue*6.0
    jeżeli hue < 0.5:
        zwróć m2
    jeżeli hue < TWO_THIRD:
        zwróć m1 + (m2-m1)*(TWO_THIRD-hue)*6.0
    zwróć m1


# HSV: Hue, Saturation, Value
# H: position w the spectrum
# S: color saturation ("purity")
# V: color brightness

def rgb_to_hsv(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    jeżeli minc == maxc:
        zwróć 0.0, 0.0, v
    s = (maxc-minc) / maxc
    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)
    jeżeli r == maxc:
        h = bc-gc
    albo_inaczej g == maxc:
        h = 2.0+rc-bc
    inaczej:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    zwróć h, s, v

def hsv_to_rgb(h, s, v):
    jeżeli s == 0.0:
        zwróć v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    jeżeli i == 0:
        zwróć v, t, p
    jeżeli i == 1:
        zwróć q, v, p
    jeżeli i == 2:
        zwróć p, v, t
    jeżeli i == 3:
        zwróć p, q, v
    jeżeli i == 4:
        zwróć t, p, v
    jeżeli i == 5:
        zwróć v, p, q
    # Cannot get here
