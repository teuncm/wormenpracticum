import pyqtgraph as pg


def set_global_plot_config():
    """Configure the plot style globally."""
    pg.setConfigOptions(background="w", foreground="k", antialias=True)
