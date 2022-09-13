import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# ModelCropper
#

class ModelCropper(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Model Cropper" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Surface Models"]
    self.parent.dependencies = []
    self.parent.contributors = ["Sebastian Andress (LMU Munich)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
Simple extension that crops a surface model along a roi box.
It uses vtkBooleanOperationPolyDataFilter for the cropping.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was developed by Sebastian Andress (LMU University Hospital Munich, Germany, Department of General -, Trauma- and Reconstructive Surgery).
""" # replace with organization, grant and thanks.

#
# ModelCropperWidget
#

class ModelCropperWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input model selector
    #
    self.inputModelSelector = slicer.qMRMLNodeComboBox()
    self.inputModelSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.inputModelSelector.selectNodeUponCreation = True
    self.inputModelSelector.addEnabled = False
    self.inputModelSelector.removeEnabled = True
    self.inputModelSelector.renameEnabled = True
    self.inputModelSelector.noneEnabled = False
    self.inputModelSelector.showHidden = False
    self.inputModelSelector.showChildNodeTypes = False
    self.inputModelSelector.setMRMLScene( slicer.mrmlScene )
    self.inputModelSelector.setToolTip( "Pick the input model for cropping." )
    parametersFormLayout.addRow("Input Model: ", self.inputModelSelector)

    #
    # output model selector
    #
    self.outputModelSelector = slicer.qMRMLNodeComboBox()
    self.outputModelSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.outputModelSelector.selectNodeUponCreation = True
    self.outputModelSelector.addEnabled = True
    self.outputModelSelector.removeEnabled = True
    self.outputModelSelector.renameEnabled = True
    self.outputModelSelector.noneEnabled = True
    self.outputModelSelector.showHidden = False
    self.outputModelSelector.showChildNodeTypes = False
    self.outputModelSelector.setMRMLScene( slicer.mrmlScene )
    self.outputModelSelector.setToolTip( "Pick the output model to the algorithm." )
    parametersFormLayout.addRow("Output Model: ", self.outputModelSelector)

    #
    # box selector
    #
    self.boxSelector = slicer.qMRMLNodeComboBox()
    self.boxSelector.nodeTypes = ["vtkMRMLMarkupsROINode", "vtkMRMLAnnotationROINode"]
    self.boxSelector.selectNodeUponCreation = True
    self.boxSelector.addEnabled = True
    self.boxSelector.removeEnabled = True
    self.boxSelector.renameEnabled = True
    self.boxSelector.noneEnabled = False
    self.boxSelector.showHidden = False
    self.boxSelector.showChildNodeTypes = False
    self.boxSelector.setMRMLScene( slicer.mrmlScene )
    self.boxSelector.setToolTip( "Pick the cropping box as annotation ROI Node." )
    parametersFormLayout.addRow("Cropping Box: ", self.boxSelector)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.boxSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputModelSelector.currentNode() and self.boxSelector.currentNode()

  def onApplyButton(self):
    logic = ModelCropperLogic()
    logic.run(self.inputModelSelector.currentNode(), self.outputModelSelector.currentNode(), self.boxSelector.currentNode())

#
# ModelCropperLogic
#

class ModelCropperLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def run(self, inputModel, outputModel, roiNode):

    logging.info('Processing started')

    triangleCube = vtk.vtkTriangleFilter()
    cube = vtk.vtkCubeSource()

    if roiNode.IsA("vtkMRMLMarkupsROINode"):
      roiDiameter = roiNode.GetSize()
      cube.SetBounds(-roiDiameter[0]/2, roiDiameter[0]/2, -roiDiameter[1]/2, roiDiameter[1]/2, -roiDiameter[2]/2, roiDiameter[2]/2)
      objectToWorldMatrix = roiNode.GetObjectToWorldMatrix()
      objectToWorld = vtk.vtkTransform()
      objectToWorld.SetMatrix(objectToWorldMatrix)

      transformFilter=vtk.vtkTransformPolyDataFilter()
      transformFilter.SetTransform(objectToWorld)
      transformFilter.SetInputConnection(cube.GetOutputPort())
      triangleCube.SetInputConnection(transformFilter.GetOutputPort())

    else:
      # Annotation ROI
      bounds = [0]*6
      roiNode.GetBounds(bounds)

      cube.SetBounds(bounds)

      if roiNode.GetTransformNodeID():
        trfNode = slicer.mrmlScene.GetNodeByID(roiNode.GetTransformNodeID())
        trfFromWorld = vtk.vtkGeneralTransform()
        trfNode.GetTransformToWorld(trfFromWorld)

        transformFilter=vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(trfFromWorld)
        transformFilter.SetInputConnection(cube.GetOutputPort())

        triangleCube.SetInputConnection(transformFilter.GetOutputPort())

      else:
        triangleCube.SetInputConnection(cube.GetOutputPort())


    triangleInput = vtk.vtkTriangleFilter()

    if inputModel.GetTransformNodeID():
      trfNode = slicer.mrmlScene.GetNodeByID(inputModel.GetTransformNodeID())
      trfFromWorld = vtk.vtkGeneralTransform()
      trfNode.GetTransformToWorld(trfFromWorld)

      transformFilter=vtk.vtkTransformPolyDataFilter()
      transformFilter.SetTransform(trfFromWorld)
      transformFilter.SetInputConnection(inputModel.GetPolyDataConnection())

      triangleInput.SetInputConnection(transformFilter.GetOutputPort())

    else:
      triangleInput.SetInputConnection(inputModel.GetPolyDataConnection())


    boolean = vtk.vtkBooleanOperationPolyDataFilter()
    boolean.SetInputConnection(0, triangleInput.GetOutputPort())
    boolean.SetInputConnection(1, triangleCube.GetOutputPort())
    boolean.SetOperationToIntersection()

    output = vtk.vtkPolyData()

    if inputModel.GetTransformNodeID():
      trfNode = slicer.mrmlScene.GetNodeByID(inputModel.GetTransformNodeID())
      trfFromWorld = vtk.vtkGeneralTransform()
      trfNode.GetTransformFromWorld(trfFromWorld)

      transformFilter=vtk.vtkTransformPolyDataFilter()
      transformFilter.SetTransform(trfFromWorld)
      transformFilter.SetInputConnection(boolean.GetOutputPort())
      transformFilter.Update()
      output.DeepCopy(transformFilter.GetOutput())

    else:
      boolean.Update()
      output.DeepCopy(boolean.GetOutput())

    if outputModel == None:
      modelsLogic = slicer.modules.models.logic()
      outputModel = modelsLogic.AddModel(output)
      outputModel.GetDisplayNode().SetSliceIntersectionVisibility(True)
      outputModel.SetName(inputModel.GetName() + '_cropped')

    else:
      outputModel.SetAndObservePolyData(output)
      if outputModel.GetDisplayNode() == None:
        outputModel.CreateDefaultDisplayNodes()
      outputModel.GetDisplayNode().SetSliceIntersectionVisibility(True)
      #outputModel.SetAndObserveTransformNodeID('')


    if inputModel.GetTransformNodeID():
      outputModel.SetAndObserveTransformNodeID(inputModel.GetTransformNodeID())

    # copy attributes
    names = vtk.vtkStringArray()
    inputModel.GetAttributeNames(names)
    for n in range(names.GetNumberOfValues()):
      outputModel.SetAttribute(names.GetValue(n), inputModel.GetAttribute(names.GetValue(n)))

    logging.info('Processing completed')

    return True


class ModelCropperTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ModelCropper1()

  def test_ModelCropper1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(10)
    sphereSource.SetCenter(0,0,0)
    sphereSource.Update()
    modelsLogic = slicer.modules.models.logic()
    sphereNode = modelsLogic.AddModel(sphereSource.GetOutput())

    roiNode = slicer.vtkMRMLMarkupsROINode()
    slicer.mrmlScene.AddNode(roiNode)
    roiNode.SetXYZ(1,1,1)
    roiNode.SetRadiusXYZ(5,5,5)

    logic = ModelCropperLogic()
    logic.run(sphereNode, None, roiNode)

    self.delayDisplay('Test passed!')
    
