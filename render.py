# coding=utf-8
import itk
import vtk
from multiprocessing import Process, cpu_count


def render_volume(volume):
	# render volume
	ren = vtk.vtkRenderer()
	ren_win = vtk.vtkRenderWindow()
	ren_win.AddRenderer(ren)
	
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(ren_win)
	iren.GetInteractorStyle().SetDefaultRenderer(ren)
	
	ren_win.SetSize(300, 300)
	# ren_win.Render()
	
	ren.AddVolume(volume)
	ren.ResetCamera()
	
	iren.Initialize()
	ren_win.Render()
	iren.Start()


def render(image_type, image_data):
	# convert itk image to vtk image data
	itk_to_vtk_filter = itk.ImageToVTKImageFilter[image_type].New()
	itk_to_vtk_filter.SetInput(image_data)
	itk_to_vtk_filter.Update()
	
	# create volume from image data
	volume = vtk.vtkVolume()
	mapper = vtk.vtkSmartVolumeMapper()
	mapper.SetInputData(itk_to_vtk_filter.GetOutput())
	volume.SetMapper(mapper)
	
	color_func = vtk.vtkColorTransferFunction()
	opacity_func = vtk.vtkPiecewiseFunction()
	property = vtk.vtkVolumeProperty()
	property.SetColor(color_func)
	property.SetScalarOpacity(opacity_func)
	property.SetInterpolationTypeToLinear()
	
	volume.SetProperty(property)
	volume.SetMapper(mapper)
	
	p = Process(target=render_volume, args=(volume,))
	q = Process(target=render_volume, args=(volume,))
	q.start()
	p.start()
	q.join()
	p.join()
