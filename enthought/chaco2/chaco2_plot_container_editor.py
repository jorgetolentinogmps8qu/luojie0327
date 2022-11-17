""" Deprecated alias for ComponentEditor.
"""

import warnings

from enthought.enable2.component_editor import ComponentEditor


class PlotContainerEditor(ComponentEditor):
    """ Deprecated alias for ComponentEditor.
    """

    def __init__(self, *args, **kwds):
        super(PlotContainerEditor, self).__init__(*args, **kwds)
        warnings.warn("DEPRECATED: Use enthought.enable2.component_editor"
            ".ComponentEditor instead.", DeprecationWarning)

