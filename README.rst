artellapipe-tools-xgenmanager
============================================================

Tool to manage XGen workflow in Solstice

.. code-block:: python

    # Modules will be reloaded. Useful for development in DCCs.
    do_reload = True

    # Load module and initialize all dependant modules (by passing True to import_libs argument)
    from solstice import core as solstice_core
    solstice_core.init(do_reload=do_reload, import_libs=True)

    # You can enable logger debug
    # os.environ['SOLSTICE.TOOLS.XGENMANAGER_DEV'] = 'true'
    from solstice.tools import xgenmanager
    xgenmanager.run(do_reload=do_reload)