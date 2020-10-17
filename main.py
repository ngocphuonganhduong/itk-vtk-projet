# coding=utf-8
import itk
from render import render

DIR = './'
FILEPATH = DIR + "BRATS_HG0015_T1C.mha"
OUTPUT_PATH = DIR + "output.mha"


def save_image(image_type, image_data):
	writer = itk.ImageFileWriter[image_type].New()
	writer.SetFileName(OUTPUT_PATH)
	writer.SetInput(image_data)
	writer.Update()


def main():
	# ITK version should < 5.1 to use ImageToVTKImageFilter
	print("ITK version: ", itk.Version.GetITKVersion())
	
	input_pixel_type = itk.ctype('float')
	output_pixel_type = itk.ctype('short')
	dim = 3
	output_image_type = itk.Image[output_pixel_type, dim]
	input_image_type = itk.Image[input_pixel_type, dim]
	
	reader = itk.ImageFileReader[input_image_type].New()
	reader.SetFileName(FILEPATH)
	reader.Update()
	
	# segmentation
	prefilter = itk.GradientAnisotropicDiffusionImageFilter[input_image_type, input_image_type].New()
	prefilter.SetInput(reader.GetOutput())
	prefilter.SetNumberOfIterations(20)
	prefilter.SetConductanceParameter(3)
	prefilter.SetTimeStep(0.04)

	segment = itk.ConnectedThresholdImageFilter[input_image_type, input_image_type].New()
	segment.SetInput(prefilter.GetOutput())
	segment.SetSeed([75, 80, 100])
	segment.SetUpper(1500)
	segment.SetLower(900)

	rescaler = itk.RescaleIntensityImageFilter[input_image_type, input_image_type].New()
	rescaler.SetInput(segment.GetOutput())
	rescaler.SetOutputMinimum(0)
	rescaler.SetOutputMaximum(255)

	structuring_element_type = itk.FlatStructuringElement[dim]
	element1 = structuring_element_type.Ball(3)
	element2 = structuring_element_type.Ball(2)

	closing = itk.GrayscaleMorphologicalClosingImageFilter[input_image_type, 
    	input_image_type, structuring_element_type].New()
	closing.SetInput(rescaler.GetOutput())
	closing.SetKernel(element1)
  
	opening = itk.GrayscaleMorphologicalOpeningImageFilter[input_image_type, 
    	input_image_type, structuring_element_type].New()
	opening.SetInput(closing.GetOutput())
	opening.SetKernel(element2)

	cast = itk.CastImageFilter[input_image_type, output_image_type].New()
	cast.SetInput(opening.GetOutput())
     	
	segmented_image_data = cast.GetOutput()
	save_image(output_image_type, segmented_image_data)
	
	# render volume and slices
	render(output_image_type, segmented_image_data)


if __name__ == "__main__":
	main()
