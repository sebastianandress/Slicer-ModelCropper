# Model Cropper

Extension for [3D Slicer](https://www.slicer.org/)

This simple Extension allows for cropping a [vtkMRMLModelNode](https://apidocs.slicer.org/v4.8/classvtkMRMLModelNode.html) in the boundaries of a [vtkMRMLAnnotationROINode](https://apidocs.slicer.org/v4.8/classvtkMRMLAnnotationROINode.html).
It creates a [vtkCubeSource](https://vtk.org/doc/nightly/html/classvtkCubeSource.html) and applies an [vtkBooleanOperationPolyDataFilter](https://vtk.org/doc/nightly/html/classvtkBooleanOperationPolyDataFilter.html) in Intersection Mode to the Model, resulting in a cropped model.

![Screenshot](https://github.com/sebastianandress/Slicer-ModelCropper/raw/master/Screenshots/Screenshot%20Model%20Cropper.png "Screenshot")