# coding=utf-8
import itk
from render import render

DIR = './'
FILENAME = "BRATS_HG0015_T1C.mha"
FILEPATH = DIR + FILENAME
OUTPUT_PATH = DIR + "output.mha"


def save_image(image_type, image_data):
	writer = itk.ImageFileWriter[image_type].New()
	writer.SetFileName(OUTPUT_PATH)
	writer.SetInput(image_data)
	writer.Update()


def main():
	# ITK version should < 5.1 to use ImageToVTKImageFilter
	print("ITK version: ", itk.Version.GetITKVersion())
	print("Start processing image " + FILENAME)
	
	dim = 3
	input_pixel_type = itk.ctype('float')
	input_image_type = itk.Image[input_pixel_type, dim]
	output_pixel_type = itk.ctype('short')
	output_image_type = itk.Image[output_pixel_type, dim]
	
	# Read image
	reader = itk.ImageFileReader[input_image_type].New()
	reader.SetFileName(FILEPATH)
	reader.Update()
	input_image_data = reader.GetOutput()

	# SEGMENTATION
	# -------------------------------------------------------------------------

	# Apply a gradient anisotropic diffusion filter to reduce noise
	prefilter = itk.GradientAnisotropicDiffusionImageFilter[input_image_type, input_image_type].New()
	prefilter.SetInput(input_image_data)
	prefilter.SetNumberOfIterations(20)
	prefilter.SetConductanceParameter(3)
	prefilter.SetTimeStep(0.04)

	# Segment the tumor with a connected threshold filter
	segment = itk.ConnectedThresholdImageFilter[input_image_type, input_image_type].New()
	segment.SetInput(prefilter.GetOutput())
	segment.SetSeed([75, 80, 100])
	segment.SetUpper(1500)
	segment.SetLower(900)

	# Rescale image intensity from 0 to 255
	rescaler = itk.RescaleIntensityImageFilter[input_image_type, input_image_type].New()
	rescaler.SetInput(segment.GetOutput())
	rescaler.SetOutputMinimum(0)
	rescaler.SetOutputMaximum(255)

	# Define some structuring elements for mathematical morphology
	structuring_element_type = itk.FlatStructuringElement[dim]
	element1 = structuring_element_type.Ball(3) # a ball of radius 3
	element2 = structuring_element_type.Ball(2) # a ball of radius 2

	# Apply morphological closing to remove holes in segmented tumor
	closing = itk.GrayscaleMorphologicalClosingImageFilter[input_image_type, 
    	input_image_type, structuring_element_type].New()
	closing.SetInput(rescaler.GetOutput())
	closing.SetKernel(element1)

	# Apply morphological opening to remove noise around segmented tumor
	opening = itk.GrayscaleMorphologicalOpeningImageFilter[input_image_type, 
    	input_image_type, structuring_element_type].New()
	opening.SetInput(closing.GetOutput())
	opening.SetKernel(element2)

    # Cast pixels from float to short 
	# (float to use filters, short because of 3D volume)
	cast = itk.CastImageFilter[input_image_type, output_image_type].New()
	cast.SetInput(opening.GetOutput())
     	
	segmented_image_data = cast.GetOutput()
	save_image(output_image_type, segmented_image_data)
	# -------------------------------------------------------------------------
	
	# render volume and slices
	print("Render image - right click to switch axis")
	render(input_image_type, input_image_data, output_image_type, segmented_image_data)


if __name__ == "__main__":
	main()
