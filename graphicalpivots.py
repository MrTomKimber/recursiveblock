import networkx as nx
import pandas as pd
from math import sqrt, ceil
import re

def partition_scheme(data, query, fields):
    #print(query, fields)
    return sorted(list(set([str(dict(r.items())) for i,r in data.query(query)[fields].iterrows()])))

def qwrap(v):
    if isinstance(v, str):
        return f"\'{v}\'"
    else:
        return v

def process_template_string(t_string, data):
    dpc_rx=re.compile("(%%(.*?)%%)+")
    qstring=t_string

    for m in dpc_rx.findall(t_string):
        qstring=qstring.replace(m[0], str(data[m[1]]))
    return qstring


class AbstractParameterLiterals(object):
    valid_values=None
    def __init__(self):
        pass

class ValidLayoutMethods(AbstractParameterLiterals):
    valid_values = ["xy", "crosstab", "grid", "spiral", "dot", "spring", "treemap", "function"]


class KwargClass(object):
    """meta-class used to establish common utility methods for instantiating
    child classes"""

    kwargspec = { "name" : { "type" : str }}

    def __init__(self, **kwargs):
        self._assigned_kwargs=set()
        self._all_kwargs=set(kwargs.keys())

        for k,v in kwargs.items():
            if k in self.kwargspec.keys():
                #print(v,self.kwargspec[k]["type"])
                #assert KwargClass._typechecker(v,self.kwargspec[k]["type"])
                self.__dict__[k]=v
                self._assigned_kwargs.add(k)
        unassigned_kwargs_left = self._all_kwargs - self._assigned_kwargs
        if len (unassigned_kwargs_left)>0:
            print( "Unassigned:", unassigned_kwargs_left)
            # Just assign them? No type checking this way
            for k in unassigned_kwargs_left:
                self.__dict__[k]=kwargs[k]

    def _set_defaults(self):
        for k in self.defaults:
            if k not in self.__dict__.keys():
                self.__dict__[k]=self.defaults[k]


    def to_dict(self):
        return self.__dict__
        #return {k:self.__dict__[k] for k in self._assigned_kwargs}

    @staticmethod
    def _typechecker(t,c):
        if isinstance(c,type):
            if issubclass(c,AbstractParameterLiterals):
                print (c.valid_values)
                return t in c.valid_values
            else :
                return isinstance(t,c)
        else:
            if c is None:
                return t is None
            else:
                c_type = type(c)
                print(c_type)
                return isinstance(t,c_type)

class LayoutMethod(KwargClass):

    def _method_string_mappings(self):
        self.method_string_mappings = { "columns" : self.ColumnLayout,
          "rows"    : self.RowLayout,
          "matrix"  : self.MatrixLayout,
          "fill"    : self.FillLayout,
          "block"   : self.BlockLayout,
        }

    def __init__(self,method):
        self._method_string_mappings()
        self.method=self.method_string_mappings.get(method, None)



    @staticmethod
    def safe_div(n,d):
        return n/d if d else 0

    @staticmethod
    def cumsum(i):
        a=0
        for v in i:
            a=a+v
            yield a

    @staticmethod
    def spacing_props(n, spacing=None, p=None):
        if spacing is None:
            sp=1/n
        else:
            sp=spacing
        if p is None:
            p=[1 for a in range(n)]
        p=[0]+[x for e,a in enumerate(range(n)) for x in (p[e],sp)][:-1]
        return p

    @staticmethod
    def layout_linear_partition(i, n, spacing=None, p=None):
        p=LayoutMethod.spacing_props(n, spacing, p)
        csp=LayoutMethod.cumsum(p)
        b_range=[v/sum(p) for v in csp]
        return b_range[i*2], b_range[(i*2)+1]-b_range[i*2], b_range[(i*2)+1]

    @staticmethod
    def layout_block_partition(i, n, spacing=None, p=None, ar=None):
        if ar is None:
            ar=1
        if p is None:
            p = [1 for x in range(0,n)]
        cols=ceil((sqrt(n))*ar)
        rows=ceil(LayoutMethod.safe_div(n,cols))
        c,r = i%cols, i//cols
        x, w, sx = LayoutMethod.layout_linear_partition(r, rows, spacing, p)
        y, h, sy = LayoutMethod.layout_linear_partition(c, cols, spacing, p)
        return (x,y,w,h)

    @staticmethod
    def layout_matrix_partition(i, j, m, n, spacing=None, p=None):
        x, w, sx = LayoutMethod.layout_linear_partition(i, m, spacing, p)
        y, h, sy = LayoutMethod.layout_linear_partition(j, n, spacing, p)
        return (x, y, w, h)

    @staticmethod
    def ColumnLayout(i,n,spacing=None,p=None):
        x,w,_=LayoutMethod.layout_linear_partition(i,n,spacing,p)
        y,h=0,1
        return (x,y,w,h)

    @staticmethod
    def RowLayout(i,n,spacing=None,p=None):
        y,h,_=LayoutMethod.layout_linear_partition(i,n,spacing,p)
        x,w=0,1
        return (x,y,w,h)

    @staticmethod
    def FillLayout(i,n):
        x,y,w,h = (0,0,1,1)
        return (x,y,w,h)

    @staticmethod
    def BlockLayout(i,n,spacing=None,p=None):
        return LayoutMethod.layout_block_partition(i,n,spacing,p)

    @staticmethod
    def MatrixLayout(i,j,m,n,spacing=None,p=None):
        x,w,_=LayoutMethod.layout_matrix_partition(i,j,m,n,spacing,p)
        y,h=0,1
        return (x,y,w,h)


class Panel(KwargClass):
    defaults = { "x" : 0.0, "y" : 0.0, "w" : 1.0, "h" : 1.0, "local_pos" : (0.0,0.0,1.0,1.0)}
    kwargspec = { "name" : { "type" : str },
                  "template" : { "type" : str },
                  "data" : { "type" : pd.DataFrame },
                  "specification" : { "type" : dict },
                  "style" : { "type" : dict },
                  "parent" : { "type" : str },
                  "query" : { "type" : str },
                  "x" : { "type" : (float,int) },
                  "y" : { "type" : (float,int) },
                  "w" : { "type" : (float,int) },
                  "h" : { "type" : (float,int) },


                  }
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        #self.style = self.specification.get(self.template,{}).get('style')
        self._set_defaults()

    def get_label(self):
        data_pool = self.data.query(self.query)
        data_pool = [{k:v for i,r in data_pool.iterrows() for k,v in r.items()}]
        if len(data_pool)==0:
            data_pool = [{}]
        label = process_template_string(self.specification[self.template].get("label", "Untitled"), dict(data_pool[0]))
        return label

    def __repr__(self):
        return str((self.name, self.template, len(self.children), self.x, self.y))

    def calculate_graph(self):
        dg=nx.DiGraph()
        spec=self.specification
        for k in spec.keys():
            obj=spec[k]
            partition=spec[k].get('partition',{})
            if 'template' in partition.keys():
                dg.add_edge(k, partition['template'])
            else:
                dg.add_node(k)
        return dg

    def partition(self):
        if 'partition' in self.specification[self.template].keys():
            return partition_scheme(self.data,
                                      self.query,
                                      self.specification[self.template]['partition']['fields'])
        else:
            return []

    def resolve_position_on_canvas(self, local_pos):

        px,py,pw,ph=self.x, self.y, self.w, self.h
        cx,cy,cw,ch = (px + (pw * self.style['margin_left']) + self.style['canvas']['x'],
                      py + (ph * self.style['margin_top']) + self.style['canvas']['y'],
                      (pw - (pw * (self.style['margin_left'] + self.style['margin_right'])) ) * self.style['canvas']['w'],
                      (ph - (ph * (self.style['margin_top'] + self.style['margin_bottom']))) * self.style['canvas']['h'])
        lx, ly, lw, lh = local_pos
        x = cx + (cw*lx)
        y = cy + (ch*ly)
        w = cw * lw
        h = ch * lh
        #print((px,py,pw,ph), (cx,cy,cw,ch), (lx, ly, lw, lh), (x,y,w,h))
        return x,y,w,h



    def genchildren(self, specification, styles):
        children=[]
        graph = self.calculate_graph()
        for s in graph.successors(self.template):
            child_spec=specification[s]
            partition = self.partition()
            n = len(partition)
            for i,p in enumerate(partition):
#                print(p)
                #local_pos = self.specification[self.template]['partition']['layout']
                try: # In case there are no partition details - default local_pos to (0,0,1,1)
#                    print("`", child_spec['partition']['layout'], "`")
                    #layout_m = LayoutMethod(child_spec['partition']['layout'])
                    layout_m = LayoutMethod(specification[self.template]['partition']['layout'])
                    spacing = specification[self.template]['partition'].get('spacing')
#                    print(i,n, layout_m.method(i,n))
                    if spacing is None:
                        local_pos = layout_m.method(i,n)
                    else:
                        local_pos = layout_m.method(i,n, spacing=spacing)
                    # Get the name of the style, this is either resolvable to
                    # a set of styles directly, or might be a reference to a field
                    # in the data, that would reference a style at an individual level.


                except KeyError as e:
                    print("!")
                    print(s, self.name)
                    local_pos = (0.1,0.1,1,1)

                child_style = styles.get(child_spec['style'])

                x,y,w,h = self.resolve_position_on_canvas(local_pos)

                c_query = " and ".join([self.query,
                        " and ".join([f"({k}=={qwrap(v)})" for k,v in eval(p).items()])])

                c_label = self.data.query(c_query)




                child = Panel(**{"name":p,
                               "template":s,
                               "parent":self.name,
                               "query":c_query,
                               "data":self.data,
                               "specification":specification,
                               "local_pos":local_pos,
                               "style" : child_style,
                               "x" : x,
                               "y" : y,
                               "w" : w,
                               "h" : h})

                child.genchildren(specification, styles)
                children.append(child)

        self.children=children
        return children

    def walk_children(self):

        for c in self.children:
            wc = c.walk_children()
            for w in wc:
                yield w
        yield self
