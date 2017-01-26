#!/usr/bin/env python
# coding=utf-8
"""
command line for mdtree
=============================================================================
"""
import argparse
import mdtree


def parse_args(args=None, values=None):
    """
    Define and parse `optparse` options for command-line usage.
    """
    usage = """mdtree [options] [source file]"""
    desc = "convert markdown to html with TOC(Table of contents) tree"
    ver = "0.0.1"

    parser = argparse.ArgumentParser(usage=usage, description=desc, version=ver)
    parser.add_argument("source", default="", help="souce file, markdown")
    parser.add_argument("-t", "--target", dest="target",
                        help="Write output to TARGET. Defaults to STDOUT.")
    parser.add_argument("--css", dest="css", default="", help="more css, http/s links")
    parser.add_argument("--js", dest="js", default="", help="more js, http/s links")

    return parser.parse_args()


def main():  # pragma: no cover
    """Run Markdown from the command line."""

    args = parse_args()

    if not args.source:
        return

    params = {
        "source": args.source,
        "target": args.target,
        "js": args.js,
        "css": args.css
    }
    html = mdtree.convert_file(**params)


if __name__ == '__main__':
    main()
