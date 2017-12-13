#!/usr/bin/env python
# coding=utf-8
import os
import datetime
from mdtree.mdutils import to_unicode, utf8, clean_list

_d_static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def adjust_ext_list(l1, l2):
    """
    remove extensions from l1 which were defined in l2
    :param list l1: source list
    :param list l2: define list
    :return list:
    """
    removed_ext_list = [i for i in l2 if i.startswith("-")]
    return [i for i in l1 if "-%s" % i not in removed_ext_list]


def gen_html(params):
    """
    Generate html
    :return str: html
    """
    with open(os.path.join(_d_static_path, "html/template.html")) as f:
        _tpl = f.read()
        _tpl = to_unicode(_tpl)

    title = to_unicode(params["title"])
    css_more = to_unicode(params["css_more"])
    js_more = to_unicode(params["js_more"])
    css_base = to_unicode(params["css_base"])
    js_base = to_unicode(params["js_base"])
    content = to_unicode(params["content"])
    toc = to_unicode(params["toc"])

    generated_at = """<div id="generated-at">
        Generated at: %s
    </div>
            """ % datetime.datetime.now().replace(microsecond=0).__str__()
    generated_at = to_unicode(generated_at)

    html = _tpl.format(title=title, content=content, css_base=css_base, js_base=js_base,
                       toc_content=toc, css_more=css_more, js_more=js_more,
                       generated_at=generated_at)

    return utf8(html)


def prepare_static_files():
    """
    prepare static files
    """
    __css_file = os.path.join(_d_static_path, "css/mdtree.min.css")
    __js_file = os.path.join(_d_static_path, "js/mdtree.min.js")
    with open(__css_file) as f:
        _css_base = f.read()
    with open(__js_file) as f:
        _js_base = f.read()
    return _css_base, _js_base


def parse_static_files(meta, css_list, js_list):
    """
    Get more static files
    :param dict meta: markdown meta
    :param list css_list: css list
    :param list js_list: js list
    :return tuple: css, js
    """
    css_more = list(set(css_list + clean_list(meta.get("css", []))))
    js_more = list(set(js_list + clean_list(meta.get("js", []))))

    css = ["""<link href="%s" rel="stylesheet" type="text/css" />""" % c for c in css_more]
    js = ["""<script type="text/javascript" src="%s"></script>""" % j for j in js_more]

    css_more_str = "\n".join(css)
    js_more_str = "\n".join(js)

    return css_more_str, js_more_str
