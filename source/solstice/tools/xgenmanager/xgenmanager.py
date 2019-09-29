#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to import/export XGen data
"""

from __future__ import print_function, division, absolute_import

# from artellapipe.shadermanager.widgets import shaderexporter

__author__ = "Enrique Velasco"
__license__ = "MIT"
__maintainer__ = "Enrique Velasco"
__email__ = "enriquevelmai@hotmail.com"

import os
import json
import stat
import shutil
import logging.config
from functools import partial

from Qt.QtWidgets import *

import maya.cmds as mc

import xgenm as xg
import xgenm.XgExternalAPI as xge
import xgenm.xgGlobal as xgg

import artellapipe
import artellapipe.tools.xgenmanager
from artellapipe.core import defines
from artellapipe.gui import window

logging.config.fileConfig(artellapipe.tools.xgenmanager.get_logging_config(), disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(artellapipe.tools.xgenmanager.get_logging_level())

########################################################################################################################
# class definition
########################################################################################################################
class ControlXgenUi(window.ArtellaWindow, object):

    LOGO_NAME = 'xgen_manager'

    ####################################################################################################################
    # class constructor
    ####################################################################################################################
    def __init__(self, project):

        self.shaders_dict = dict()
        self.scalps_list = list()
        self.collection_name = None

        super(ControlXgenUi, self).__init__(
            project=project,
            name='xgenmanager',  # Do not change or UI load'll fail and Maya'll crash painfully
            title='XGen Manager',
            size=(500, 400),
            load_ui=True
        )

    ####################################################################################################################
    # ui definitions
    ####################################################################################################################
    def ui(self):
        super(ControlXgenUi, self).ui()

        self._populate_data()
        self._connect_componets_to_actions()

    def _populate_data(self):
        self.qtui.collection_cbx.addItems(self._get_all_collections())
        self.qtui.renderer_cbx.addItems(["None", "Arnold Renderer"])
        self.qtui.renderer_cbx.setCurrentIndex(1)
        self.qtui.renderer_mode_cbx.addItems(["Live", "Batch Render"])
        self.qtui.renderer_mode_cbx.setCurrentIndex(1)
        self.qtui.motion_blur_cbx.addItems(["Use Global Settings", "On", "Off"])
        self.qtui.extra_depth_sbx.setValue(16)
        self.qtui.extra_samples_sbx.setValue(0)

        characters_to_set = os.listdir(os.path.join(self.project.get_assets_path(), "Characters"))
        characters_to_set.insert(0, "")
        self.qtui.export_character_cbx.addItems(characters_to_set)
        self.qtui.import_character_cbx.addItems(characters_to_set)

    def _connect_componets_to_actions(self):
        self.qtui.export_go_btn.clicked.connect(self._do_export)
        self.qtui.importer_go_btn.clicked.connect(self._do_import)
        self.qtui.path_browse_btn.clicked.connect(self._save_file)
        self.qtui.groom_file_browser_btn.clicked.connect(self._open_file)
        self.qtui.geometry_scalpt_grp_btn.clicked.connect(
            partial(self._load_selection_to_line, self.qtui.geometry_scalpt_grp_txf))
        self.qtui.export_character_cbx.currentIndexChanged.connect(partial(self._set_path, self.qtui.export_character_cbx, self.qtui.path_txf))
        self.qtui.import_character_cbx.currentIndexChanged.connect(partial(self._set_path, self.qtui.import_character_cbx, self.qtui.groom_package_txf))

    ####################################################################################################################
    # UI functions set
    ####################################################################################################################
    def _set_path(self, driver, setter, k):
        """
        Sets path to the text widget
        """
        asset_name = driver.currentText()
        if asset_name:
            save_path = os.path.join(self.project.get_assets_path(), "Characters", asset_name, "__working__",
                                        "groom", "groom_package.groom")
            setter.setText(save_path)
            return
        setter.setText("")

    def _load_selection_to_line(self, qt_object):
        """
        Load selection into the given texfiled
        :param qt_object: QTexField object where to set the selected items
        """
        # set the string to load
        selection = mc.ls(sl=True)
        text_to_add = '"{}"'.format(selection[0])
        if len(selection) > 1:
            for obj in selection[1:]:
                text_to_add += ';"{}"'.format(obj)

        # set text to the object
        qt_object.setText(text_to_add)

    def _get_all_collections(self):
        """
        Get all collections in the maya scene
        :return: list, with the collection names
        """
        collections_list = list()
        for item in xg.palettes():
            collections_list.append(item)
        return collections_list

    def _open_file(self):
        """
        Open file dialog, and sets the path to the QTexField
        """
        file_path, _ext = QFileDialog.getOpenFileName(self, dir=os.environ['HOME'], filter='Folder(.groom)')
        self.qtui.groom_package_txf.setText(str(file_path))

    def _save_file(self):
        """
        Save file dialog, and sets the path to the QTexField
        :return:
        """
        file_path, _ext = QFileDialog.getSaveFileName(self, dir=os.environ['HOME'], filter='Folder(.groom)')
        self.qtui.path_txf.setText(str(file_path))

    ####################################################################################################################
    # class core functions
    ####################################################################################################################
    def _do_export(self):
        """
        Executes the export of the choose collection
        """

        # Get data from ui
        self.collection_name = self.qtui.collection_cbx.currentText()
        self.shaders_dict = self._get_shaders()
        self.scalps_list = self._get_scalps()
        ptx_folder = self._get_root_folder()
        export_path = self.qtui.path_txf.text()
        self.character = self.qtui.export_character_cbx.currentText()
        comment = self.qtui.comment_pte.toPlainText()

        # analise if there is an export folder
        if not export_path:
            if not self.character:
                raise ValueError("export path must be specified")

        ################################################################################################################
        # Export objects into a .groom folder
        ################################################################################################################
        # generate export path
        if export_path:
            self.export_path_folder = export_path
            if not '.groom' in export_path:
                self.export_path_folder = export_path + '.groom'
        else:
            self.export_path_folder = os.path.join(self.proje.get_asses_path(), "Characters", self.character, defines.ARTELLA_WORKING_FOLDER, "groom", "groom_package.groom")

        # if the folder already exists delete it, and create a new one
        self.delete_artella_folder(self.export_path_folder)
        os.makedirs(self.export_path_folder)

        # get the ptx path
        if '${PROJECT}' in ptx_folder:
            project_path = str(mc.workspace(fullName=True, q=True))
            ptx_folder = os.path.join(project_path, ptx_folder.replace('${PROJECT}', ''))
        self.project.logger.debug("XGEN || All data parsed")
        self.qtui.progress_lbl.setText("Exporting Files (PTX)")
        # copy the ptx files
        shutil.copytree(ptx_folder, os.path.join(self.export_path_folder, self.collection_name))
        self.project.logger.debug("XGEN || PTEX files exported")

        # export xgen file
        xg.exportPalette(palette=str(self.collection_name),
                         fileName=str("{}/{}.xgen".format(self.export_path_folder, self.collection_name)))
        self.qtui.progress_lbl.setText("Exporting Files (.XGEN)")
        self.project.logger.debug("XGEN || Collection file exported")

        # export sculpts
        mc.select(self.scalps_list, replace=True)
        mc.file(rename=os.path.join(self.export_path_folder, 'scalps.ma'))
        mc.file(es=True, type='mayaAscii')
        mc.select(cl=True)
        self.qtui.progress_lbl.setText("Exporting Scalps (.MA)")
        self.project.logger.debug("XGEN || Sculpts Exported")

        # export material
        exporter = shaderexporter.ShaderExporter(project=self._project, shaders=self.shaders_dict.values(), parent=self)
        exporter.export_shaders(publish=comment)

        self.qtui.progress_lbl.setText("Exporting Material (.sshader)")
        self.project.logger.debug("XGEN || Material Exported")

        # export mapping
        with open(os.path.join(self.export_path_folder, 'shader.json'), 'w') as fp:
            json.dump(self.shaders_dict, fp)
        self.qtui.progress_lbl.setText("Exporting Mapping (.JSON)")
        self.project.logger.debug("XGEN || Mapping Exported")

        # add file to artella
        if comment:
            self._add_file_to_artella(file_path_global=self.export_path_folder, comment=comment)
            self.project.logger.debug("XGEN || Files added to artella")
        else:
            self.project.logger.warning("XGEN || Files are not been loaded to Artella. Do it manually")

    def _do_import(self):
        """
        Imports the groom into the scene
        """
        # todo: query if is it the last version
        import_folder = self.qtui.groom_package_txf.text()
        self.character = self.qtui.import_character_cbx.currentText()

        if not import_folder:
            raise ValueError("Import path must be specified")

        # build scene
        mc.loadPlugin('xgenToolkit.mll')

        import_path_folder = import_folder.replace('.zip', '')
        _, groom_asset = os.path.split(import_path_folder)
        xgen_file = [f for f in os.listdir(import_path_folder) if f.endswith('.xgen')][-1]
        xgen_file = os.path.join(import_path_folder, xgen_file).replace('\\', '/')
        map_folder = [os.path.join(import_path_folder, d) for d in os.listdir(import_path_folder) if
                      os.path.isdir(os.path.join(import_path_folder, d))][0]

        # import maya scenes
        mc.file(os.path.join(import_folder, 'scalps.ma'), i=True, type="mayaAscii", ignoreVersion=True,
                mergeNamespacesOnClash=False, gl=True, namespace=self.character, options="v=0", groupReference=False)

        # load mapping
        in_data = dict()
        with open(os.path.join(import_path_folder, 'mapping.json'), 'r') as fp:
            in_data = json.load(fp)

        # import xgen
        try:
            xg.importPalette(fileName=str(xgen_file), deltas=[], nameSpace=str(self.character))
        except Exception:
            logger.warning('Not found maps folder')
        # set path to xgen
        xg.setAttr('xgDataPath', str(map_folder), xg.palettes()[0])

        # todo: remember shader is not imported, it will be imported by the shader import tool

        # Get the description editor first.
        # Changes in the groom itself, guides, and so on
        de = xgg.DescriptionEditor
        #
        #
        #
        #
        # Do a full UI refresh
        de.refresh("Full")

        # place anim
        # todo: if there is any scalp group, create a blendshape
        # scalp_grp = self.qtui.geometry_scalpt_grp_txf.text()
        # if scalp_grp:
        #     mc.blendShape(scalp_grp, )

    def _get_root_folder(self):
        """
        Gets the xgen root folder
        :return: String with the xgen folder path
        """
        return xg.getAttr('xgDataPath', str(self.collection_name))

    def delete_artella_folder(self, p):
        self.qtui.progress_bar.setValue(0)
        self.qtui.progress_lbl.setText("Locking Files")
        i = 0
        for root, dirs, files in os.walk(p):
            for file in files:
                i += 1
        if i == 0:
            return
        j = 0
        self.qtui.progress_bar.setMinimum(0)
        self.qtui.progress_bar.setMaximum(i - 1)
        for root, dirs, files in os.walk(p):
            for file in files:
                self.project.lock_file(file_path=os.path.join(root, file))
                self.qtui.progress_bar.setValue((j / float(i)) * 100)
                self.project.logger.debug("XGEN || {} file locked".format(file))
                j += 1
        shutil.rmtree(p, onerror=self._on_rm_error)
        self.project.logger.debug("XGEN || {} path deleted".format(p))

    def _add_file_to_artella(self, file_path_global, comment):
        """
        Method that adds all the files of a given path to the artella system
        :param file_path_global: String with the base path to ad
        :param comment: String with the comment to add
        """
        self.qtui.progress_bar.setValue(0)
        self.qtui.progress_lbl.setText("Uploading Files")
        i = 0
        for root, dirs, files in os.walk(file_path_global):
            for file in files:
                i += 1
        j = 0
        self.qtui.progress_bar.setMinimum(0)
        self.qtui.progress_bar.setMaximum(i - 1)
        for root, dirs, files in os.walk(file_path_global):
            for file in files:
                self.project.upload_working_version(os.path.join(root, file), comment=comment, force=True)
                self.qtui.progress_bar.setValue((j / float(i)) * 100)
                self.project.logger.debug("XGEN || {} file added".format(file))
                j += 1

    def _get_shaders(self):
        """
        Gets a dictionary with the used materials for each description
        :return: Dictionary with the shader --> description mapping
        """
        import pymel.core as pm
        material_dict = dict()
        for description in xg.descriptions(str(self.collection_name)):
            pm.select(description)
            pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
            for shd in pm.selected(materials=True):
                if [c for c in shd.classification() if 'shader/surface' in c]:
                    material_dict[description] = shd.name()
        return material_dict

    def _get_scalps(self):
        """
        Gets a list with the used scalps in the descriptions
        :return: List with the scalps names
        """
        scalps = list()
        for description in xg.descriptions(str(self.collection_name)):
            scalpt = xg.boundGeometry(str(self.collection_name), str(description))[0]
            if scalpt not in scalps:
                scalps.append(scalpt)

        return scalps

    def _on_rm_error(func, path, exc_info):
        # path contains the path of the file that couldn't be removed
        # let's just assume that it's read-only and unlink it.
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)


def run():
    """
    Runs the Xgen manager GUI
    :return: QWindow object
    """
    win = ControlXgenUi(project=artellapipe.solstice)
    win.show()

    return win
