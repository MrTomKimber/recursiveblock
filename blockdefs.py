# Blockdef contains core properties for defining a block
import numbers
#from typing import Literal
from typing_extensions import Literal
import pandas as pd



class LocatableObject(object):
    def __init__(self, **kwargs):
        # These x,y,w,h coordinates operate in a local (0,1) space to the object's parent
        # In the special case of a top-level Panel, these (0,1) coordinates will be scaled
        # For rendering - and which point, all the underlying or dependent xy values will be
        # updated.

        # When determining a panel's true location, its x,y,w,h will be determined from the
        # its ancestors.

        # Different sub-classes of Panel might require additional attributes such as
        # Title, Properties, and Canvas - each of which will be sub-classes of Panel themselves
        self._assigned_kwargs=set()
        self._all_kwargs=set(kwargs.keys())

        for k,v in kwargs.items():
            if k in PanelKwargs.keys():
                assert _typechecker(v,PanelKwargs[k]["type"])
                self.__dict__[k]=v
                self._assigned_kwargs.add(k)
        unassigned_kwargs_left = self._all_kwargs - self._assigned_kwargs
        print( "Unassigned:", unassigned_kwargs_left)

    def _set_defaults(self):
        for k,v in PanelKwargs.items():
            if any([issubclass(self.__class__, c) for c in v['defaults'].keys()]) :
                d_class = [c for c in v['defaults'].keys() if issubclass(self.__class__, c)][0]
                #print (self.__class__, v['defaults'])
                self.__dict__[k]=v['defaults'][d_class]
                self._assigned_kwargs.add(k)

    def to_dict(self):
        return {k:self.__dict__[k] for k in self._assigned_kwargs}


class Panel(LocatableObject):
    def __init__(self, **kwargs):
        super(Panel, self).__init__(**kwargs)

class Pane(LocatableObject):
    # A Pane is a locatable object that appears within a parent block.
    # Some panels might contain only textual content, This might be reserved for
    # titles, key-value pair lists, and descriptive text.
    # x,y,w,h are all strictly expressed in parent terms and will be resolved at render time,
    # after taking into account parent location and margin values
    def __init__(self, **kwargs):
        super(Pane, self).__init__(**kwargs)

class RootPanel(Panel):
    # The root panel is a special panel in that it has no parent - probably, it might make sense not
    # to make this special, so maybe refactor later on.
    def __init__(self, **kwargs):
        super(RootPanel, self).__init__(**kwargs)

class SubPanel(Panel):
    # A sub-panel is a panel that lives within a parent.
    # Additionally, it acts as a canvas for subsequent drawing items, and can host children within
    # the bounds defined within its margins.
    # All sub-panels have margins
    def __init__(self, **kwargs):
        super(SubPanel, self).__init__(**kwargs)






class AbstractParameterLiterals(object):
    valid_values=None
    def __init__(self):
        pass

class LayoutMethods(AbstractParameterLiterals):
    valid_values = ["xy", "crosstab", "grid", "spiral", "dot", "spring", "treemap", "function"]



# (Type, mandatory, default)
PanelKwargs = {

    "id" : {"type":str,
            "defaults" : {},
            "mandatory" : {Panel:"panel"} },
    "margin_left" : {"type":numbers.Real,
                     "defaults" : {Panel:0.01},
                     "mandatory" : [] },
    "margin_right" : {"type":numbers.Real,
                      "defaults" : {Panel:0.01},
                      "mandatory" : [] },
    "margin_top" : {"type":numbers.Real,
                    "defaults" : {Panel:0.01},
                    "mandatory" : [] },
    "margin_bottom" : {"type":numbers.Real,
                       "defaults" : {Panel:0.01},
                       "mandatory" : [] },
    "layout" : {"type":LayoutMethods,
                "defaults" : {Panel:"grid"},
                "mandatory" : [] },
    "parent" : {"type": Panel,
                "defaults" : {RootPanel:None},
                "mandatory" : [SubPanel] },
    "x"      : {"type" : numbers.Real,
                "defaults" : {RootPanel:0.0,Pane:0.0},
                "mandatory":[]},
    "y"      : {"type" : numbers.Real,
                "defaults" : {RootPanel:0.0,Pane:0.0},
                "mandatory":[]},
    "w"      : {"type" : numbers.Real,
                "defaults" : {RootPanel:1.0,Pane:1.0},
                "mandatory":[]},
    "h"      : {"type" : numbers.Real,
                "defaults" : {RootPanel:1.0,Pane:1.0},
                "mandatory":[]},
    "query"  : {"type" : str,
                "defaults" : {},
                "mandatory":[]},
    "source"   : {"type" : pd.DataFrame,
                "defaults" : {},
                "mandatory":[] },
}


class PanelBuilder(object):
    """The purpose of the PanelBuilder is to accept a specification dictionary,
    and some data source, and use that to generate nested panels.
    PanelBuilder specifications are nestable/composable, and are strictly tree-like."""
    def __init__(self, **kwargs):
        pass

class XYPanelBuilder(PanelBuilder):
    pass

class CrosstabPanelBuilder(PanelBuilder):
    pass

class GridPanelBuilder(PanelBuilder):
    pass




def _typechecker(t,c):
    if isinstance(c,type):
        if issubclass(c,AbstractParameterLiterals):
            return t in c.valid_values
        else :
            return isinstance(t,c)
    else:
        if c is None:
            return t is None
        else:
            c_type = type(c)
            return isinstance(t,c_type)
