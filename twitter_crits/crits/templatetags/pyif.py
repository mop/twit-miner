from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

class PyIfNode(template.Node):
    def __init__(self, nodeslist):
        self.nodeslist = nodeslist

    def __repr__(self):
        return "<PyIf node>"

    def render(self, context):
        for e, nodes in self.nodeslist:
            clist = list(context)
            clist.reverse()
            d = {}
            d['_'] = _
            for c in clist:
                d.update(c)
            v = eval(e, d)
            if v:
                return nodes.render(context)
        return ''

def do_pyif(parser, token):
    nodeslist = []
    while 1:
        v = token.contents.split(None, 1)
        if v[0] == 'endif':
            break
        if v[0] in ('pyif', 'elif'):
            if len(v) < 2:
                raise template.TemplateSyntaxError, "'pyif' statement requires at least one argument"
        if len(v) == 2:
            tagname, arg = v
        else:
            tagname, arg = v[0], 'True'
        nodes = parser.parse(('else', 'endif', 'elif'))
        nodeslist.append((arg, nodes))
        token = parser.next_token()
#    parser.delete_first_token()
    return PyIfNode(nodeslist)
do_pyif = register.tag("pyif", do_pyif)

