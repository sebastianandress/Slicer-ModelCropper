cmake_minimum_required(VERSION 3.5)

project(ModelCropper)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ModelCropper")
set(EXTENSION_CATEGORY "Surface Models")
set(EXTENSION_CONTRIBUTORS "Sebastian Andreß (LMU Munich)")
set(EXTENSION_DESCRIPTION "Simple extension that crops a surface model along a roi box. It uses vtkBooleanOperationPolyDataFilter for the cropping.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ModelCropper.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ModelCropper/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ModelCropper)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
