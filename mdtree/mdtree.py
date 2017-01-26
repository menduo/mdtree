#!/usr/bin/env python
# coding=utf-8
"""
mdtree, convert markdown to html with TOC(table of contents) tree. https://github.com/menduo/mdtree
"""
import sys, os, re
import markdown

_d_static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

PY2 = sys.version_info.major == 2

if PY2:
    unicode_type = unicode
else:
    unicode_type = str


def _clean_list(alist):
    """
    clean items
    :param list alist: a list
    :return:
    """
    return [str(i).strip() for i in alist if str(i).strip()]


__all__ = ["MdTree", "convert_file"]


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
            # "markdown.extensions.codehilite",
        ]

        self._js_base = ""
        self._css_base = ""
        self._html = ""

        self._js_more = _clean_list(kwargs.get("js", "").split(","))
        self._css_more = _clean_list(kwargs.get("css", "").split(","))
        self._title = kwargs.get("title", "")
        self._zt_is_auto_number = kwargs.get("z_is_auto_number", "false")
        self._z_opts = kwargs.get("z_opts", "")

        exts = kwargs.get("exts", [])
        exts = _clean_list(exts)

        self._md_meta = None
        self._md_extensions = _clean_list(list(set(self._md_extensions + exts)))

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

        _z_opt = "is_auto_number: %s" % self._zt_is_auto_number
        if self._z_opts:
            _z_opt += "," + self._z_opts

        self._js_base += """
            jQuery(document).ready(function () {
                    jQuery('#tree').ztree_toc({
                        %s
                    });
            });
            """ % _z_opt

        return self._css_base, self._js_base

    def append_static_files(self):
        """
        Get more static files
        """
        css_more = self._css_more + _clean_list(self._md_meta.get("css", []))
        js_more = self._js_more + _clean_list(self._md_meta.get("js", []))

        css_more = list(set(css_more))
        js_more = list(set(js_more))

        css = ["""<link href="%s" rel="stylesheet" type="text/css" />""" % c for c in
               css_more]

        js = ["""<script type="text/javascript" src="%s"></script>""" % j for j in
              js_more]

        return "\n".join(css), "\n".join(js)

    def parse_title(self, mdstring):
        """
        get title
        """
        mdstring = mdstring.lstrip("\n").lstrip(" ")
        head_pattern1 = re.compile(r'^ *(#{1}) *([^\n]+?) *#* *(?:\n+|$)')
        m = re.match(head_pattern1, mdstring)

        if m:
            return m.group(2)

        head_pattern2 = re.compile(r'^([^\n]+)\n *(=|-)+ *(?:\n+|$)')
        m = re.match(head_pattern2, mdstring)

        if m:
            return m.group(1)

        return "MdTree"

    def parse_md_config(self, source):
        """
        parse exts config from markdown file and update the markdown object

        exts source: https://pythonhosted.org/Markdown/extensions/
        :return:
        """
        md = markdown.Markdown(extensions=["markdown.extensions.meta"])
        md.convert(source)
        self._md_meta = md.Meta

        exts = self._md_meta.get("exts", [])
        self._md_extensions = _clean_list(list(set(self._md_extensions + exts)))
        self._md = markdown.Markdown(extensions=self._md_extensions)

    def convert(self, source):
        """
        convert markdown to html with TOC
        :param str source: contents of markdown file
        :return:
        """
        if not isinstance(source, unicode_type):
            source = source.decode("utf-8")

        self.parse_md_config(source)

        md_html = self._md.convert(source)

        css_base, js_base = self.prepare_static_files()

        title = self._title or self._md_meta.get("title", [""])[0]
        title = title or self.parse_title(source)

        with open(os.path.join(_d_static_path, "html/template.html")) as f:
            _tpl = f.read()
            _tpl = _tpl.decode("utf-8")

        css_more, js_more = self.append_static_files()

        html = _tpl.format(title=title, content=md_html, css_base=css_base,
                           js_base=js_base, css_more=css_more, js_more=js_more)

        self._html = html
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
    :param kwargs:
    :return:
    """
    source = kwargs["source"]
    target = kwargs.get("target")

    mdtree = MdTree(**kwargs)
    html = mdtree.convert_file(source)
    if target:
        mdtree.save_file(target)
    else:
        if PY2:
            sys.stdout.write(html)
        else:
            sys.stdout.buffer.write(html)
    return html
