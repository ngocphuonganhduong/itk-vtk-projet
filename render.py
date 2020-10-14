# coding=utf-8
import itk
import vtk
from multiprocessing import Process


def render_volume(volume):
	# render volume
	ren = vtk.vtkRenderer()
	ren_win = vtk.vtkRenderWindow()
	ren_win.AddRenderer(ren)
	ren_win.SetSize(300, 300)
	
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(ren_win)
	iren.GetInteractorStyle().SetDefaultRenderer(ren)
	
	ren.AddVolume(volume)
	ren.ResetCamera()
	
	iren.Initialize()
	ren_win.Render()
	iren.Start()


class CustomRender:
	axes_name = ["axial - x", "coronal - y", "sagittal - z"]
	
	def __set_up_filter(self, reader):
		self.filter = vtk.vtkImageReslice()
		self.filter.SetInputConnection(reader.GetOutputPort())
		self.filter.SetOutputDimensionality(2)
		self.filter.SetResliceAxes(self.axes[self.axis])
		self.filter.SetInterpolationModeToLinear()
	
	def __set_up_drawing_actor(self):
		table = vtk.vtkLookupTable()
		table.SetRange(0, 2000)  # image intensity range
		table.SetValueRange(0.0, 1.0)  # from black to white
		table.SetSaturationRange(0.0, 0.0)  # no color saturation
		table.SetRampToLinear()
		table.Build()
		
		# Map the image through the lookup table
		color = vtk.vtkImageMapToColors()
		color.SetLookupTable(table)
		color.SetInputConnection(self.filter.GetOutputPort())
		
		# Display the image
		self.actor = vtk.vtkImageActor()
		self.actor.GetMapper().SetInputConnection(color.GetOutputPort())
	
	def __set_up_renderer(self):
		self.ren = vtk.vtkRenderer()
		self.ren.AddActor(self.actor)
		
		self.win = vtk.vtkRenderWindow()
		self.win.AddRenderer(self.ren)
		
		self.style = vtk.vtkInteractorStyleImage()
		self.style.AddObserver("RightButtonReleaseEvent", self.switch_axis_call_back)
		
		self.iren = vtk.vtkRenderWindowInteractor()
		self.iren.SetInteractorStyle(self.style)
		self.win.SetInteractor(self.iren)
	
	def __set_up_slider(self):
		minv, maxv = 0.0, 100.0
		self.slider_rep = vtk.vtkSliderRepresentation2D()
		self.slider_rep.SetMinimumValue(minv)
		self.slider_rep.SetMaximumValue(maxv)
		self.slider_rep.SetValue((maxv - minv) / 2.0)
		self.slider_rep.GetSliderProperty().SetColor(0, 0, 1)
		self.slider_rep.GetTitleProperty().SetColor(0, 0, 1)
		self.slider_rep.GetLabelProperty().SetColor(0, 0, 1)
		self.slider_rep.GetSelectedProperty().SetColor(1, 0, 0)
		self.slider_rep.GetCapProperty().SetColor(1, 0, 0)
		self.slider_rep.GetTubeProperty().SetColor(1, 0, 0)
		self.slider_rep.GetTubeProperty().SetColor(1, 0, 0)
		self.slider_rep.GetTubeProperty().SetColor(1, 0, 0)
		self.slider_rep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
		self.slider_rep.GetPoint1Coordinate().SetValue(20, 40)
		self.slider_rep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
		self.slider_rep.GetPoint2Coordinate().SetValue(300, 40)
		self.slider_rep.SetTitleText(self.axes_name[self.axis])
		
		self.slider_wid = vtk.vtkSliderWidget()
		self.slider_wid.SetInteractor(self.iren)
		self.slider_wid.SetRepresentation(self.slider_rep)
		self.slider_wid.SetAnimationModeToAnimate()
		self.slider_wid.EnabledOn()
		self.slider_wid.AddObserver("InteractionEvent", self.slider_call_back)
	
	def __init__(self, reader, default_axis=0):
		min_x, max_x, min_y, max_y, min_z, max_z = reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))
		spacing = reader.GetOutput().GetSpacing()
		self.origin = reader.GetOutput().GetOrigin()
		self.size = [(max_x - min_x) * spacing[0], (max_y - min_y) * spacing[1], (max_z - min_z) * spacing[2]]
		center = [self.origin[0] + 0.5 * self.size[0],
		          self.origin[1] + 0.5 * self.size[1],
		          self.origin[2] + 0.5 * self.size[2]]
		
		self.axes = [vtk.vtkMatrix4x4(), vtk.vtkMatrix4x4(), vtk.vtkMatrix4x4()]
		# axial
		self.axes[0].DeepCopy((1, 0, 0, center[0],
		                       0, 1, 0, center[1],
		                       0, 0, 1, center[2],
		                       0, 0, 0, 1))
		# coronal
		self.axes[1].DeepCopy((1, 0, 0, center[0], 0, 0, 1, center[1], 0, -1, 0, center[2], 0, 0, 0, 1))
		
		# sagittal
		self.axes[2].DeepCopy((0, 0, -1, center[0], 1, 0, 0, center[1], 0, -1, 0, center[2], 0, 0, 0, 1))
		
		self.axis = default_axis
		
		self.__set_up_filter(reader)
		
		self.__set_up_drawing_actor()
		self.__set_up_renderer()
		self.__set_up_slider()
	
	def render(self):
		self.iren.Initialize()
		self.win.Render()
		self.iren.Start()
	
	def slider_call_back(self, obj, event):
		cur_pos = self.slider_wid.GetSliderRepresentation().GetValue()
		ratio = (cur_pos - self.slider_rep.GetMinimumValue()) / self.slider_rep.GetMaximumValue()
		self.filter.Update()
		matrix = self.filter.GetResliceAxes()
		matrix.SetElement(2 - self.axis, 3, self.origin[self.axis] + ratio * self.size[self.axis])
		self.win.Render()
	
	def switch_axis_call_back(self, obj, event):
		self.axis = (self.axis + 1) % 3
		self.filter.SetResliceAxes(self.axes[self.axis])
		self.slider_rep.SetValue((self.slider_rep.GetMaximumValue() - self.slider_rep.GetMinimumValue()) / 2.0)
		self.win.Render()


def render_slicer(vtk_image_data):
	cast_filter = vtk.vtkImageCast()
	cast_filter.SetInputData(vtk_image_data)
	cast_filter.Update()

	custom_ren = CustomRender(cast_filter)
	custom_ren.render()


def render(image_type, image_data):
	# convert itk image to vtk image data
	itk_to_vtk_filter = itk.ImageToVTKImageFilter[image_type].New()
	itk_to_vtk_filter.SetInput(image_data)
	itk_to_vtk_filter.Update()
	
	vtk_image_data = itk_to_vtk_filter.GetOutput()
	
	# create volume from image data
	volume = vtk.vtkVolume()
	mapper = vtk.vtkSmartVolumeMapper()
	mapper.SetInputData(vtk_image_data)
	volume.SetMapper(mapper)
	
	color_func = vtk.vtkColorTransferFunction()
	opacity_func = vtk.vtkPiecewiseFunction()
	volume_property = vtk.vtkVolumeProperty()
	volume_property.SetColor(color_func)
	volume_property.SetScalarOpacity(opacity_func)
	volume_property.SetInterpolationTypeToLinear()
	
	volume.SetProperty(volume_property)
	volume.SetMapper(mapper)
	
	p = Process(target=render_volume, args=(volume,))
	q = Process(target=render_slicer, args=(vtk_image_data,))
	q.start()
	p.start()
	q.join()
	p.join()
