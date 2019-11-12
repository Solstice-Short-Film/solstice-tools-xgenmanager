solstice-tools-xgenmanager
============================================================

Tool to manage XGen workflow in Solstice

.. image:: https://travis-ci.com/Solstice-Short-Film/solstice-tools-xgenmanager.svg?branch=master&kill_cache=1
    :target: https://travis-ci.com/Solstice-Short-Film/solstice-tools-xgenmanager

.. image:: https://coveralls.io/repos/github/Solstice-Short-Film/solstice-tools-xgenmanager/badge.svg?branch=master&kill_cache=1
    :target: https://coveralls.io/github/Solstice-Short-Film/solstice-tools-xgenmanager?branch=master

.. image:: https://img.shields.io/badge/docs-sphinx-orange
    :target: https://solstice.github.io/solstice-tools-xgenmanager/

.. image:: https://img.shields.io/github/license/Solstice-Short-Film/solstice-tools-xgenmanager
    :target: https://github.com/Solstice-Short-Film/solstice-tools-xgenmanager/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/solstice-tools-xgenmanager?branch=master&kill_cache=1
    :target: https://pypi.org/project/solstice-tools-xgenmanager/

.. image:: https://img.shields.io/badge/code_style-pep8-blue
    :target: https://www.python.org/dev/peps/pep-0008/

.. code-block:: python

    import artellapipe
    import plottwist.loader
    plottwist.loader.init()

    artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'xgenmanager', do_reload=False, debug=False)