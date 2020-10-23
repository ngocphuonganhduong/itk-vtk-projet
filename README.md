# itk-vtk-projet
Tumor segmentation and visualisation by Kathialina Va and Ngoc Phuong Anh DUONG.

There are 2 renderers, one for the volume and one for the slicer concept. In the slider renderer, right click to switch the viewing axis.
```
USAGE:
python main.py [--help|-h] [--save|-s] [--output|-o <OutputPath>] [--norendering]

OPTIONS:
-s, --save         save image
-o, --output       path for output segmented mask
--norendering      program will not run vtk visualisation
```

## References:
- Visualisation is inspired by [3D Slicer](https://www.slicer.org/)
- VTK interactions and observers: [here](https://vtk.org/Wiki/VTK/Examples/Python/Interaction/MouseEventsObserver)
- Image Slicing: [here](https://vtk.org/gitweb?p=VTK.git;a=blob;f=Examples/ImageProcessing/Python/ImageSlicing.py)
- Slider 2D widget: [here](https://vtk.org/Wiki/VTK/Examples/Cxx/Widgets/Slider2D)
- Discussion about switching interactor style: [here](http://vtk.1045678.n5.nabble.com/VTK5-6-1-One-render-window-multiple-renders-and-auto-interactor-style-solution-td4358940.html)
- Multiple renderers in a window: [here](https://cmake.org/Wiki/VTK/Examples/Cxx/Images/ImageMask)
