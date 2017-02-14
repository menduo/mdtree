#!/usr/bin/env python
# coding=utf-8
"""
mdtree, convert markdown to html with TOC(table of contents) tree. https://github.com/menduo/mdtree
"""
import sys, os, re
import markdown
from .mdutils import PY3, _clean_list, to_unicode, utf8

_d_static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

__all__ = ["MdTree", "convert_file"]

_meta_data_fence_pattern = re.compile(r'^---[\ \t]*\n', re.MULTILINE)
_meta_data_pattern = re.compile(
    r'^(?:---[\ \t]*\n)?(.*:\s+>\n\s+[\S\s]+?)(?=\n\w+\s*:\s*\w+\n|\Z)|([\S\w]+\s*:(?! >)[ \t]*.*\n?)(?:---[\ \t]*\n)?',
    re.MULTILINE)


class MdTree(object):
    """
    Python markdown tree tool
    """

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        self._md_extensions = [
            "markdown.extensions.meta",
            "markdown.extensions.headerid",
            "markdown.extensions.tables",
            "markdown.extensions.toc",
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
        ]

        self._js_base = ""
        self._css_base = ""
        self._html = ""

        self._js_more = _clean_list(kwargs.get("js", []))
        self._css_more = _clean_list(kwargs.get("css", []))
        self._title = kwargs.get("title", "")

        exts = kwargs.get("exts", [])
        exts = _clean_list(exts)
        self._md_extensions = _clean_list(list(set(self._md_extensions + exts)))
        self._md_extensions = self._remove_exts(self._md_extensions, exts)

    def prepare_static_files(self):
        """
        prepare static files
        """
        __css_file = os.path.join(_d_static_path, "css/mdtree.min.css")
        __js_file = os.path.join(_d_static_path, "js/mdtree.min.js")
        with open(__css_file) as f:
            self._css_base = f.read()
        with open(__js_file) as f:
            self._js_base = f.read()
        return self._css_base, self._js_base

    def parse_static_files(self, meta):
        """
        Get more static files
        :param dict meta: markdown meta
        :return tuple: css, js
        """
        css_more = list(set(self._css_more + _clean_list(meta.get("css", []))))
        js_more = list(set(self._js_more + _clean_list(meta.get("js", []))))

        css = ["""<link href="%s" rel="stylesheet" type="text/css" />""" % c for c in
               css_more]

        js = ["""<script type="text/javascript" src="%s"></script>""" % j for j in
              js_more]

        return css, js

    def parse_title(self, mdstring):
        """
        get title
        """

        if mdstring.startswith("---"):
            fence_splits = re.split(_meta_data_fence_pattern, mdstring, maxsplit=2)
            metadata_content = fence_splits[1]
            match = re.findall(_meta_data_pattern, metadata_content)
            if match:
                mdstring = fence_splits[2]

        mdstring = mdstring.lstrip("\n").lstrip(" ")
        head_pattern1 = re.compile(r'^ *(#{1}) *([^\n\n]+?) *#* *(?:\n+|$)')
        m = re.match(head_pattern1, mdstring)
        if m:
            return m.group(2)

        head_pattern12 = re.compile(r'^ *(#{2}) *([^\n]+?) *#* *(?:\n+|$)')
        m = re.match(head_pattern12, mdstring)
        if m:
            return m.group(2)

        head_pattern2 = re.compile(r'^([^\n]+)\n *(=|-)+ *(?:\n+|$)')
        m = re.match(head_pattern2, mdstring)

        if m:
            return m.group(1)

        return "MdTree"

    def _remove_exts(self, l1, l2):
        """
        remove extensions from l1 which were defined in l2
        :param list l1: source list
        :param list l2: define list
        :return list:
        """
        _removed_ext_list = [i for i in l2 if i.startswith("-")]
        _removed_ext_list.extend([i.lstrip("-") for i in _removed_ext_list])
        return [i for i in l1 if i not in _removed_ext_list]

    def parse_md_config(self, source):
        """
        parse exts config from markdown file and update the markdown object

        exts source: https://pythonhosted.org/Markdown/extensions/
        :return:
        """
        md = markdown.Markdown(extensions=["markdown.extensions.meta"])
        md.convert(source)
        md_meta = md.Meta

        # remove exts
        exts = md_meta.get("exts", [])
        self._md_extensions = _clean_list(list(set(self._md_extensions + exts)))
        self._md_extensions = self._remove_exts(self._md_extensions, exts)

        # recreate an instance of Markdown object
        return markdown.Markdown(extensions=self._md_extensions)

    def gen_html(self, title, content, css_base, js_base, toc, css_more="", js_more=""):
        """
        Generate html
        :return str: html
        """
        with open(os.path.join(_d_static_path, "html/template.html")) as f:
            _tpl = f.read()
            _tpl = to_unicode(_tpl)

        title = to_unicode(title)
        css_more = to_unicode(css_more)
        js_more = to_unicode(js_more)
        css_base = to_unicode(css_base)
        js_base = to_unicode(js_base)

        html = _tpl.format(title=title, content=content, css_base=css_base, js_base=js_base,
                           toc_content=toc, css_more=css_more, js_more=js_more)

        self._html = utf8(html)
        return html

    def convert(self, source):
        """
        convert markdown to html with TOC
        :param str source: contents of markdown file
        :return:
        """
        source = to_unicode(source)

        # parse meta、exts config
        md = self.parse_md_config(source)
        md_html = md.convert(source)
        md_meta = md.Meta
        toc = md.toc

        # prepare the basic static files
        css_base, js_base = self.prepare_static_files()

        # get title from init、meta、markdown source
        title = self._title or md_meta.get("title", [""])[0]
        title = title or self.parse_title(source)

        # try to get more static files from markdown source
        css_more_list, js_more_list = self.parse_static_files(md_meta)
        css_more_str = "\n".join(css_more_list)
        js_more_str = "\n".join(js_more_list)

        html = self.gen_html(title, md_html, css_base, js_base, toc, css_more_str, js_more_str)
        return html

    def convert_file(self, spath):
        """
        convert markdown to html with TOC
        :param str spath: path of source file
        """
        with open(spath) as f:
            mdstring = f.read()
        return self.convert(mdstring)

    def save_file(self, tpath):
        """
        write to file
        :param str tpath: path of target file
        :return:
        """
        with open(tpath, "w") as f:
            f.write(self._html)
        return tpath


# Exported Funcs
def convert_file(**kwargs):
    """
    :param dict kwargs:
    :return:
    """
    source = kwargs["source"]
    target = kwargs.get("target")

    mdtree = MdTree(**kwargs)
    html = mdtree.convert_file(source)
    html = utf8(html)
    if target:
        mdtree.save_file(target)
    else:
        if PY3:
            sys.stdout.buffer.write(html)
        else:
            sys.stdout.write(html)
    return html
