#!/usr/bin/python
import os
import sys
import subprocess
import curses

import socket
import fcntl
import struct

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from epd import epd
from curses import wrapper

WHITE = 1
BLACK = 0

FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
FONT_SIZE  = 12

def sysInfo(epd):
    # initially set all white background
    image = Image.new('1', edp.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    startX = 4
    startY = 4

    # clear the display buffer
    draw.rectangle((2, 2, width - 2, height - 2), fill=WHITE, outline=BLACK)
    draw.text((startX, startY),"PaPiRus System Info", fill=BLACK, font=font)
    draw.text((startX, FONT_SIZE + startY),
      'eth0 IP:{p:s}'.format(p=getIPAddress("eth0")), fill=BLACK, font=font)
    draw.text((startX, 2 * FONT_SIZE + startY),
      'wlan0 IP:{p:s}'.format(p=getIPAddress("wlan0")), fill=BLACK, font=font)
    epd.display(image)
    epd.update()

def getIPAddress(ifname):
    # Return the IP address of interface
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  struct.pack('256s', ifname[:15]))[20:24])
    except:
        ip = "0.0.0.0"
    return ip

def getMAC(interface):
    # Return the MAC address of interface
    try:
      mac = open('/sys/class/net/' + interface + '/address').read()
    except:
      mac = "00:00:00:00:00:00"
    return mac[0:17]

#
# Main display using curses
#
def main(stdscr):
    # Clear screen and hide cursor
    stdscr.clear()
    curses.curs_set(0)

    # Add title and footer
    exittxt = 'Press "q" to exit'
    title = '**** PaPiRus System Info ****'
    stdscr.addstr(0, (curses.COLS - len(title)) / 2, title)
    stdscr.addstr(22, (curses.COLS - len(exittxt)) / 2, exittxt)
    stdscr.refresh()

    papirus = Papirus()
    # Issue a command to the screen to populate the screen status which otherwise would show as undefined
    papirus.clear()

    # Check for HAT
    if os.path.exists(PRODUCT):
        isHAT = True
        vendor = str(subprocess.check_output(["cat", VENDOR])).rstrip(' \n\r\0')
        product = str(subprocess.check_output(["cat", PRODUCT])).rstrip(' \n\r\0')
        serial = str(subprocess.check_output(["cat", UUID])).rstrip(' \n\r\0')

        panelwin = curses.newwin(10, curses.COLS - 6, 2, 3)
    else:
        isHAT = False
        panelwin = curses.newwin(9, curses.COLS - 6, 2, 3)

    display_status = str(subprocess.check_output(["cat", STATUS])).rstrip(' \n\r\0')

    netwin = curses.newwin(4, curses.COLS - 6, 12, 3)

    # Fill firmware info window.
    panelwin.erase()
    panelwin.border()
    if isHAT:
        panelwin.addstr(1, 2, 'Vendor: {v:s}'.format(v=vendor))
        panelwin.addstr(2, 2, 'Product: {p:s}'.format(p=product))
        panelwin.addstr(3, 2, 'PANEL: {p:s}" ({w:d} x {h:d})'.format(p=papirus.panel, w=papirus.width, h=papirus.height))
        panelwin.addstr(4, 2, 'FILM: {v:s}'.format(v=papirus.version))
        panelwin.addstr(5, 2, 'COG: {g:d}'.format(g=papirus.cog))
        panelwin.addstr(6, 2, 'VERSION: {f:d}'.format(f=papirus.film))
        panelwin.addstr(7, 2, 'UUID: {s:s}'.format(s=serial))
        panelwin.addstr(8, 2, 'Screen status: {b:s}'.format(b=display_status))
    else:
        panelwin.addstr(1, 2, 'Vendor: Pi Supply')
        panelwin.addstr(2, 2, 'Product: PaPiRus Zero')
        panelwin.addstr(3, 2, 'PANEL: {p:s}" ({w:d} x {h:d})'.format(p=papirus.panel, w=papirus.width, h=papirus.height))
        panelwin.addstr(4, 2, 'FILM: {v:s}'.format(v=papirus.version))
        panelwin.addstr(5, 2, 'COG: {g:d}'.format(g=papirus.cog))
        panelwin.addstr(6, 2, 'VERSION: {f:d}'.format(f=papirus.film))
        panelwin.addstr(7, 2, 'Screen status: {b:s}'.format(b=display_status))
    panelwin.refresh()

    netwin.erase()
    netwin.border()
    netwin.addstr(1, 2, 'eth0 IP: {i:s} - MAC: {m:s}'.format(i=getIPAddress("eth0"), m=getMAC("eth0")))
    netwin.addstr(2, 2, 'wlan0 IP: {i:s} - MAC: {m:s}'.format(i=getIPAddress("wlan0"), m=getMAC("wlan0")))
    netwin.refresh()

    papirus.clear()
    sysInfo(papirus)

    c = stdscr.getch()
    if c == ord('q'):
        exit();


wrapper(main)

# main
if "__main__" == __name__:
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
