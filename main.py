# coding=utf-8
import vtk

DIR = './'
FILEPATH = DIR + "BRATS_HG0015_T1C.mha"


def main():
	reader = vtk.vtkMetaImageReader()
	reader.SetFileName(FILEPATH)
	reader.Update()
	
	# create volume from metadata
	volume = vtk.vtkVolume()
	mapper = vtk.vtkSmartVolumeMapper()
	mapper.SetInputConnection(reader.GetOutputPort())
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
