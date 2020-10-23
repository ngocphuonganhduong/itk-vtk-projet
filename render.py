# coding=utf-8
import itk
import vtk


class CustomRender:
	axes_name = ["Axial - x", "Coronal - y", "Sagittal - z"]
	
	def __set_up_filter(self, reader, mask_reader):
		self.filter = vtk.vtkImageReslice()
		self.filter.SetInputConnection(reader.GetOutputPort())
		self.filter.SetOutputDimensionality(2)
		self.filter.SetResliceAxes(self.axes[self.axis])
		self.filter.SetInterpolationModeToLinear()
		
		self.mask_filter = vtk.vtkImageReslice()
		self.mask_filter.SetInputConnection(mask_reader.GetOutputPort())
		self.mask_filter.SetOutputDimensionality(2)
		self.mask_filter.SetResliceAxes(self.axes[self.axis])
		self.mask_filter.SetInterpolationModeToLinear()
	
	def __set_up_drawing_actor(self):
		table = vtk.vtkLookupTable()
		table.SetRange(0, 1000)
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
		
		# mask
		mask_lut = vtk.vtkLookupTable()
		mask_lut.SetNumberOfTableValues(2)
		mask_lut.SetTableValue(0, 0.0, 0.0, 0.0, 1.0)
		mask_lut.SetTableValue(1, 1.0, 0.0, 0.0, 1.0)

		color = vtk.vtkImageMapToColors()
		color.SetLookupTable(mask_lut)
		color.SetInputConnection(self.mask_filter.GetOutputPort())

		self.mask_actor = vtk.vtkImageActor()
		self.mask_actor.GetMapper().SetInputConnection(color.GetOutputPort())
		self.mask_actor.SetOpacity(0.7)
	
	def __set_up_renderer(self, volume, mask_volume):
		self.img_ren = vtk.vtkRenderer()
		self.img_ren.AddActor(self.actor)
		self.img_ren.AddActor(self.mask_actor)
		self.img_ren.ResetCamera()
		self.img_ren.SetViewport([0.0, 0.0, 1.0, 0.5])
		
		self.vol_ren = vtk.vtkRenderer()
		self.vol_ren.AddVolume(volume)
		self.vol_ren.AddVolume(mask_volume)
		self.vol_ren.ResetCamera()
		self.vol_ren.SetViewport(0.0, 0.5, 1.0, 1.0)
		self.vol_ren.SetBackground(0.0, 0.01, 0.05)
		
		self.win = vtk.vtkRenderWindow()
		self.win.SetSize(400, 800)
		self.win.AddRenderer(self.img_ren)
		self.win.AddRenderer(self.vol_ren)
		
		self.iren = vtk.vtkRenderWindowInteractor()
		self.iren.SetRenderWindow(self.win)
		
		# set styles for interactor
		self.image_style = vtk.vtkInteractorStyleImage()
		self.image_style.AddObserver("RightButtonReleaseEvent", self.switch_axis_call_back)
		self.image_style.SetDefaultRenderer(self.img_ren)
		
		self.volume_style = vtk.vtkInteractorStyleSwitch()
		self.volume_style.SetDefaultRenderer(self.vol_ren)
		
		self.iren.AddObserver("MouseMoveEvent", self.switch_interactor_style)
	
	def __set_up_slider(self):
		minv, maxv = 0.0, 100.0
		self.slider_rep = vtk.vtkSliderRepresentation2D()
		self.slider_rep.SetMinimumValue(minv)
		self.slider_rep.SetMaximumValue(maxv)
		self.slider_rep.SetValue((maxv - minv) / 2.0)
		self.slider_rep.SetTitleText(self.axes_name[self.axis] + " - right click to switch axis")
		
		self.slider_rep.GetSliderProperty().SetColor(1, 1, 0.1)
		self.slider_rep.GetSelectedProperty().SetColor(0, 1, 0)
		self.slider_rep.GetCapProperty().SetColor(0, 0.2, 0.5)
		self.slider_rep.GetTubeProperty().SetColor(0, 0.1, 0.4)
		self.slider_rep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
		self.slider_rep.GetPoint1Coordinate().SetValue(60, 450)
		self.slider_rep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
		self.slider_rep.GetPoint2Coordinate().SetValue(260, 450)
		
		self.slider_wid = vtk.vtkSliderWidget()
		self.slider_wid.SetInteractor(self.iren)
		self.slider_wid.SetRepresentation(self.slider_rep)
		self.slider_wid.SetAnimationModeToAnimate()
		self.slider_wid.EnabledOn()
		self.slider_wid.AddObserver(vtk.vtkCommand.InteractionEvent, self.slider_call_back)
	
	def __init__(self, input_reader, mask_reader, volume, mask_volume, default_axis=0):
		min_x, max_x, min_y, max_y, min_z, max_z = mask_reader.GetExecutive().GetWholeExtent(
			mask_reader.GetOutputInformation(0))
		spacing = mask_reader.GetOutput().GetSpacing()
		self.origin = mask_reader.GetOutput().GetOrigin()
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
		
		self.__set_up_filter(input_reader, mask_reader)
		
		self.__set_up_drawing_actor()
		self.__set_up_renderer(volume, mask_volume)
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
	
	def switch_axis_call_back(self, obj, event):
		self.axis = (self.axis + 1) % 3
		self.filter.SetResliceAxes(self.axes[self.axis])
		self.mask_filter.SetResliceAxes(self.axes[self.axis])
		self.slider_rep.SetValue((self.slider_rep.GetMaximumValue() - self.slider_rep.GetMinimumValue()) / 2.0)
		self.slider_rep.SetTitleText(self.axes_name[self.axis] + " - right click to switch axis")
		self.win.Render()
	
	def switch_interactor_style(self, obj, event):
		last_pos = self.iren.GetLastEventPosition()
		cur_pos = self.iren.GetEventPosition()
		ren = self.iren.FindPokedRenderer(cur_pos[0], last_pos[1])
		if ren == self.img_ren:
			self.iren.SetInteractorStyle(self.image_style)
		else:
			self.iren.SetInteractorStyle(self.volume_style)


def _from_itk_to_vtk(image_type, image_data):
	itk_to_vtk = itk.ImageToVTKImageFilter[image_type].New()
	itk_to_vtk.SetInput(image_data)
	itk_to_vtk.Update()
	
	vtk_image_data = itk_to_vtk.GetOutput()
	
	cast_filter = vtk.vtkImageCast()
	cast_filter.SetInputData(vtk_image_data)
	cast_filter.Update()
	return cast_filter, vtk_image_data


def render(input_image_type, input_image_data, seg_mask_type, seg_mask_data):
	# convert itk image to vtk image data
	input_cast_filter, vtk_input_image_data = _from_itk_to_vtk(input_image_type, input_image_data)
	seg_cast_filter, vtk_seg_mask_data = _from_itk_to_vtk(seg_mask_type, seg_mask_data)
	
	# create volume from mask data
	mask_volume = vtk.vtkVolume()
	mapper = vtk.vtkSmartVolumeMapper()
	mapper.SetInputData(vtk_seg_mask_data)
	mask_volume.SetMapper(mapper)
	
	color_func = vtk.vtkColorTransferFunction()
	color_func.AddRGBPoint(100, 0.4, 0.0, 0.0)
	color_func.AddRGBPoint(255, 0.8, 0.0, 0.0)
	opacity_func = vtk.vtkPiecewiseFunction()
	
	volume_property = vtk.vtkVolumeProperty()
	volume_property.SetColor(color_func)
	volume_property.SetScalarOpacity(opacity_func)
	volume_property.SetInterpolationTypeToLinear()
	
	mask_volume.SetProperty(volume_property)
	mask_volume.SetMapper(mapper)
	
	volume = vtk.vtkVolume()
	mapper = vtk.vtkSmartVolumeMapper()
	mapper.SetInputData(vtk_input_image_data)
	volume.SetMapper(mapper)
	
	color_func = vtk.vtkColorTransferFunction()
	opacity_func = vtk.vtkPiecewiseFunction()
	opacity_func.AddPoint(100, 0.0)
	opacity_func.AddPoint(151, 0.3)
	opacity_func.AddPoint(255, 0.5)
	
	volume_property = vtk.vtkVolumeProperty()
	volume_property.SetColor(color_func)
	volume_property.SetScalarOpacity(opacity_func)
	volume_property.SetInterpolationTypeToLinear()
	
	volume.SetProperty(volume_property)
	volume.SetMapper(mapper)
	
	custom_ren = CustomRender(input_cast_filter, seg_cast_filter, volume, mask_volume)
	custom_ren.render()
