#!/usr/bin/env python
# coding=utf-8
import sys
import re
import os
import base64
from markdown.inlinepatterns import ImagePattern, IMAGE_LINK_RE

RE_REMOTEIMG = re.compile('^(http|https):.+')

_meta_data_fence_pattern = re.compile(r'^---[\ \t]*\n', re.MULTILINE)
_meta_data_pattern = re.compile(
    r'^(?:---[\ \t]*\n)?(.*:\s+>\n\s+[\S\s]+?)(?=\n\w+\s*:\s*\w+\n|\Z)|([\S\w]+\s*:(?! >)[ \t]*.*\n?)(?:---[\ \t]*\n)?',
    re.MULTILINE)


def unique_list(alist):
    return list(set(alist))


def clean_list(alist):
    """
    clean items
    :param list alist: a list
    :return:
    """
    alist = list(map(lambda x: str(x).strip(), alist))
    alist = list(filter(lambda x: x != "", alist))
    return unique_list(alist)


def get_first(alist):
    rlist = clean_list(alist) or [None]
    return rlist[0]


def to_bool(value):
    if isinstance(value, (list, tuple)):
        value = value[0]
    value = str(value)
    if value.strip() in [0, None, "None", "False", "", "0"]:
        return False
    return True


# Code from tornado.escape
PY3 = sys.version_info.major == 3
bytes_type = bytes
if PY3:
    unicode_type = str
    basestring_type = str
else:
    unicode_type = unicode
    basestring_type = basestring

_UTF8_TYPES = (bytes, type(None))


def utf8(value):
    # type: (typing.Union[bytes,unicode_type,None])->typing.Union[bytes,None]
    """Converts a string argument to a byte string.

    If the argument is already a byte string or None, it is returned unchanged.
    Otherwise it must be a unicode string and is encoded as utf8.
    """
    if isinstance(value, _UTF8_TYPES):
        return value
    if not isinstance(value, unicode_type):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.encode("utf-8")


_TO_UNICODE_TYPES = (unicode_type, type(None))


def to_unicode(value):
    """Converts a string argument to a unicode string.

    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.decode("utf-8")


# to_unicode was previously named _unicode not because it was private,
# but to avoid conflicts with the built-in unicode() function/type
_unicode = to_unicode

# When dealing with the standard library across python 2 and 3 it is
# sometimes useful to have a direct conversion to the native string type
if str is unicode_type:
    to_native_str = to_unicode
else:
    to_native_str = utf8

to_str = to_native_str

_BASESTRING_TYPES = (basestring_type, type(None))


def to_basestring(value):
    """Converts a string argument to a subclass of basestring.

    In python2, byte and unicode strings are mostly interchangeable,
    so functions that deal with a user-supplied argument in combination
    with ascii string constants can use either and should return the type
    the user supplied.  In python3, the two types are not interchangeable,
    so this method is needed to convert byte strings to unicode.
    """
    if isinstance(value, _BASESTRING_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.decode("utf-8")


def recursive_unicode(obj):
    """Walks a simple data structure, converting byte strings to unicode.

    Supports lists, tuples, and dictionaries.
    """
    if isinstance(obj, dict):
        return dict((recursive_unicode(k), recursive_unicode(v)) for (k, v) in obj.items())
    elif isinstance(obj, list):
        return list(recursive_unicode(i) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(recursive_unicode(i) for i in obj)
    elif isinstance(obj, bytes):
        return to_unicode(obj)
    else:
        return obj


def convert_img_to_b64(src, base_dir=None):
    if RE_REMOTEIMG.match(src):
        return src

    src = os.path.expanduser(src)
    if base_dir:
        base_dir = os.path.expanduser(base_dir)
        src = os.path.join(base_dir, src)

    if not os.path.exists(src):
        raise ValueError("file does not exists on: %s" % src)

    ext = "png"
    if os.path.splitext(src)[1] in [".jpg", "jpeg"]:
        ext = "jpeg"

    with open(src, "rb") as f:
        data = f.read()

    img_data = base64.b64encode(data)
    res = "data:image/%s;base64,%s" % (ext, img_data)
    return res


def handle_image_element(node, base):
    src = node.attrib.get('src')
    if src and not RE_REMOTEIMG.match(src):
        node.set("src", convert_img_to_b64(src, base))
    return node


class ImageCheckPattern(ImagePattern):
    def __init__(self, base, md_inst=None, pattern=IMAGE_LINK_RE):
        super(ImageCheckPattern, self).__init__(pattern, md_inst)
        self.__base_dir = base

    def handleMatch(self, m):
        node = ImagePattern.handleMatch(self, m)
        node = handle_image_element(node, self.__base_dir)
        return node


def parse_title(mdstring):
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
