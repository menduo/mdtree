# MdTree #


Convert markdown to html with TOC(table of contents) tree. [https://github.com/menduo/mdtree](https://github.com/menduo/mdtree)

# Install

```bash
pip install mdtree
```

# Usage

## In Python
```python
from mdtree import MdTree
with open(path_of_md_file) as f:
    md_str = f.read()

mt = MdTree()
html = mt.convert(md_str)
fpath = mt.save_file("/tmp/mdtree.html")
```

## In Shell

```bash
mdtree /path/of/markdown/file.md > /tmp/mdtree.html
```

# Meta

mdtree allows you to add more things to the html file:

- css
- js
- title

```markdown
---
title: 这是一个标题
js:
    https://raw.githubusercontent.com/menduo/mdtree/master/static/js/mdtree.min.js
    https://raw.githubusercontent.com/menduo/mdtree/master/static/js/mdtree2.min.js
    https://raw.githubusercontent.com/menduo/mdtree/master/static/js/mdtree3.min.js
css:
    https://raw.githubusercontent.com/menduo/mdtree/master/static/css/mdtree.min.css
    https://raw.githubusercontent.com/menduo/mdtree/master/static/css/mdtree2.min.css
---
```


# Credits
- [Markdown](https://github.com/waylan/Python-Markdown) - A Python implementation of John Gruber’s Markdown
- [i5ting_ztree_toc](https://github.com/i5ting/i5ting_ztree_toc) - a jQuery plugin for preview markdown table of content jQuery