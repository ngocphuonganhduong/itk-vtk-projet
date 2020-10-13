# coding=utf-8
import itk
import vtk

DIR = './'
FILEPATH = DIR + "BRATS_HG0015_T1C.mha"


def main():
	# ITK version should < 5.1 to use ImageToVTKImageFilter
	print("ITK version: ", itk.Version.GetITKVersion())
	
	pixel_type = itk.ctype('short')
	dim = 3
	image_type = itk.Image[pixel_type, dim]
	
	reader = itk.ImageFileReader[image_type].New()
	reader.SetFileName(FILEPATH)
	reader.Update()
	
	# segmentation
	
	
	
	# convert itk image to vtk image data
	itk_to_vtk_filter = itk.ImageToVTKImageFilter[image_type].New()
	itk_to_vtk_filter.SetInput(reader.GetOutput())
	itk_to_vtk_filter.Update()
	
	# create volume from metadata
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
	
	# render volume
	ren = vtk.vtkRenderer()
	ren_win = vtk.vtkRenderWindow()
	ren_win.AddRenderer(ren)
	
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(ren_win)
	iren.GetInteractorStyle().SetDefaultRenderer(ren)
	
	ren_win.SetSize(300, 300)
	ren_win.Render()
	
	ren.AddVolume(volume)
	ren.ResetCamera()
	
	ren_win.Render()
	iren.Initialize()
	iren.Start()


if __name__ == "__main__":
	main()
