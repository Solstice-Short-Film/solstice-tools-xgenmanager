#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to manage XGen workflow in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe

# Defines ID of the tool
TOOL_ID = 'solstice-tools-xgenmanager'

# We skip the reloading of this module when launching the tool
no_reload = True


class XgenManagerTool(artellapipe.Tool, object):
    def __init__(self, *args, **kwargs):
        super(XgenManagerTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = artellapipe.Tool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'XGen Manager',
            'id': 'solstice-tools-xgenmanager',
            'logo': 'xgenmanager_logo',
            'icon': 'xgenmanager',
            'help_url': 'https://solstice-short-film.github.io/solstice-docs/pipeline/pipeline/tools/xgenmanager/',
            'kitsu_login': False,
            'tooltip': 'Tool to manage XGen workflow in Solstice',
            'tags': ['artella', 'manager', 'xgen', 'fur', 'groom'],
            'sentry_id': 'https://1cd7be48a69848d68a251b95f4889bee@sentry.io/1764700',
            'is_checkable': False,
            'is_checked': False,
            'menu_ui': {'label': 'XGen Manager', 'load_on_startup': False, 'color': '', 'background_color': ''},
            'menu': [
                {'label': 'Groom',
                 'type': 'menu', 'children': [{'id': 'solstice-tools-xgenmanager', 'type': 'tool'}]}],
            'shelf': [
                {'name': 'Groom',
                 'children': [{'id': 'solstice-tools-xgenmanager', 'display_label': False, 'type': 'tool'}]}
            ]
        }
        base_tool_config.update(tool_config)

        return base_tool_config


class XgenManagerToolset(artellapipe.Toolset, object):
    ID = TOOL_ID

    def __init__(self, *args, **kwargs):
        super(XgenManagerToolset, self).__init__(*args, **kwargs)

    def contents(self):

        from solstice.tools.xgenmanager.widgets import xgenmanager

        xgen_manager = xgenmanager.ControlXgenUi(
            project=self._project, config=self._config, settings=self._settings, parent=self)
        return [xgen_manager]
