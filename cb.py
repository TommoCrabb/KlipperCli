#!/usr/bin/env python3
'''
A command line tool for managing KDE's clipboard tool "klipper"
via the qdbus interface. 
TO-DO:
+ Make application work with both klipper and CopyQ
==============
+ Dump entire clipboard history to file or stdout
+ Dump selected entries to file or stdout
+ Delete entire clipboard history
+ Delete selected entries
+ Add an entry
PROBLEM:
When capturing stdout, there's no way of distinguishing between
items, since the items themselves can contain linebreaks.
There's also no way of determining how many items are in Klipper's
history. Klipper does not return an error if you ask for an item
it doesn't have; just a blank line, which is indistinguishable
from a blank line within an item. This makes iteration impractical.
QDBUS COMMANDS:
 USEFUL:
org.kde.klipper.klipper.clearClipboardHistory()
org.kde.klipper.klipper.getClipboardContents()
org.kde.klipper.klipper.getClipboardHistoryItem(int i)
org.kde.klipper.klipper.getClipboardHistoryMenu()
org.kde.klipper.klipper.setClipboardContents(QString s)
 QUESTIONABLE:
org.kde.klipper.klipper.showKlipperPopupMenu()
 NOT WORKING?:
org.kde.klipper.klipper.clearClipboardContents()
org.kde.klipper.klipper.showKlipperManuallyInvokeActionMenu()
org.kde.klipper.klipper.saveClipboardHistory()
'''

from subprocess import run, PIPE
from shutil import which
from time import strftime 
from sys import stdout
from re import compile as regex
import argparse

class empty:
    pass

class klipper:
    def __init__(self):
        # Klipper constants
        self.c = empty()
        self.c.clear = "clearClipboardHistory"
        self.c.get = "getClipboardContents"
        self.c.all = "getClipboardHistoryMenu"
        self.c.push = "setClipboardContents"
        self.c.item = "getClipboardHistoryItem"

    def clear(self):
        self.run(self.c.clear)
    def get(self):
        return self.run(self.c.get)
    def all(self):
        return self.run(self.c.all)
    def push(self, string):
        self.run(self.c.push, string)
    def item(self, integer):
        return self.run(self.c.item, integer)
    def run(self, *args):
        x = run( 
            ("qdbus","org.kde.klipper","/klipper") + args,
            stdout=PIPE, universal_newlines=True
        )
        return x.stdout

def sub_filename(n, c):
    n = n.replace( "%d", timestamp )
    n = n.replace( "%c", str(c) + "-lines")
    return n

def check_deps():
    for x in "qdbus", "klipper":
        w = which(x)
        if w == None:
            print("ERROR: Can't find", x)
            exit()

def parse_args():
    ap = argparse.ArgumentParser(
        description="""A fairly simple python script intended to
        make it easier to use the KDE clipboard manager (Klipper)
        from the command line, via the QDBUS interface.""",
        epilog="""Future versions might add compatibility for other
        clipboard managers. At this point, I'm looking at CopyQ,
        but it seems to have its own scripting language anyway.
        """
    )
    meg = ap.add_mutually_exclusive_group()
    meg.add_argument(
        "--get", "-g",
        action="store_true",
        help="Get the most recent item from clipboard."
    )
    meg.add_argument(
        "--clear", "-c", 
        action="store_true",
        help="Clear all items from clipboard history."
    )
    meg.add_argument(
        "--push", "-p",
        nargs="+",
        help="Push items to the clipboard."
    )
    meg.add_argument(
        "--search", "-s",
        help='''Takes a python-readable regular expression, and 
        uses it to search the clipboard history.'''
    )
    ap.add_argument(
        "--file", "-f",
        nargs="?",
        const='clipboard_%d_%c',
        default=stdout,
        help='''Specify a filename for writing output. If this 
        option is used without an argument, a default filename 
        will be generated. If this option is not used at all, 
        output will be writen to stdout (default).'''
    )
    ap.add_argument(
        "--template", "-t",
        action="store_true",
        help="""Activates filename substitutions.
        %%d (date) = timestamp.
        %%c (count) = number of matches.
        """
    )
    return ap.parse_args()

def search(a):
    x = []
    r = regex(args.search)
    for b in a:
        if r.search(b) != None:
            x.append(b)
    return x

def write(x):
    if type(args.file) == str:
        fn = sub_filename(n=args.file, c=len(x))
        args.file = open(fn, "a")
    for a in x:
        args.file.write(a + "\n")
    args.file.close()

def main():
    if args.clear:
        cb.clear()
    elif args.push:
        for a in args.push:
            cb.push(a)
    elif args.get:
        write( [cb.get()] )
    else:
        a = cb.all()
        a = a.splitlines()
        if args.search:
            a = search(a)
        write(a)

check_deps()
timestamp = strftime("%Y-%m%d-%H%M%S")
args = parse_args()
cb = klipper()
main()