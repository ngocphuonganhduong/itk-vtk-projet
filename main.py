# coding=utf-8
import itk
import sys
import getopt
from render import render

FILENAME = "BRATS_HG0015_T1C.mha"
USAGE = 'USAGE:\n' \
        'python main.py [--help|-h] [--save|-s] [--output|-o <OutputPath>] [--norendering]\n\n' \
        'OPTIONS:\n' \
        '-s, --save         save image\n' \
        '-o, --output       path for output segmented mask\n' \
        '--norendering      program will not run vtk visualisation\n'


def save_image(image_type, image_data, output_path):
	print("saving image in", output_path)
	writer = itk.ImageFileWriter[image_type].New()
	writer.SetFileName(output_path)
	writer.SetInput(image_data)
	writer.Update()


def main(output_path, is_saved, is_rendering):
	print("ITK version: ", itk.Version.GetITKVersion())
	print("Start processing image " + FILENAME)
	
	dim = 3
	float_pixel_type = itk.ctype('float')
	float_image_type = itk.Image[float_pixel_type, dim]
	short_pixel_type = itk.ctype('short')
	short_image_type = itk.Image[short_pixel_type, dim]
	
	# Read image
	reader = itk.ImageFileReader[short_image_type].New()
	reader.SetFileName(FILENAME)
	reader.Update()
	input_image_data = reader.GetOutput()

	# SEGMENTATION
	# -------------------------------------------------------------------------

    # Cast pixels from short to float to use filters
	# (float to use filters, short because of 3D volume)
	cast1 = itk.CastImageFilter[short_image_type, float_image_type].New()
	cast1.SetInput(input_image_data)
	
	# Apply a gradient anisotropic diffusion filter to reduce noise
	prefilter = itk.GradientAnisotropicDiffusionImageFilter[float_image_type, float_image_type].New()
	prefilter.SetInput(cast1.GetOutput())
	prefilter.SetNumberOfIterations(20)
	prefilter.SetConductanceParameter(3)
	prefilter.SetTimeStep(0.04)

	# Segment the tumor with a connected threshold filter
	segment = itk.ConnectedThresholdImageFilter[float_image_type, float_image_type].New()
	segment.SetInput(prefilter.GetOutput())
	segment.SetSeed([75, 80, 100])
	segment.SetUpper(1500)
	segment.SetLower(900)

	# Rescale image intensity from 0 to 255
	rescaler = itk.RescaleIntensityImageFilter[float_image_type, float_image_type].New()
	rescaler.SetInput(segment.GetOutput())
	rescaler.SetOutputMinimum(0)
	rescaler.SetOutputMaximum(255)

	# Define some structuring elements for mathematical morphology
	structuring_element_type = itk.FlatStructuringElement[dim]
	element1 = structuring_element_type.Ball(3) # a ball of radius 3
	element2 = structuring_element_type.Ball(2) # a ball of radius 2

	# Apply morphological closing to remove holes in segmented tumor
	closing = itk.GrayscaleMorphologicalClosingImageFilter[float_image_type, float_image_type, structuring_element_type].New()
	closing.SetInput(rescaler.GetOutput())
	closing.SetKernel(element1)

	# Apply morphological opening to remove noise around segmented tumor
	opening = itk.GrayscaleMorphologicalOpeningImageFilter[float_image_type, float_image_type, structuring_element_type].New()
	opening.SetInput(closing.GetOutput())
	opening.SetKernel(element2)

	# Cast pixels from float to short to get initial type
	# (float to use filters, short because of 3D volume)
	cast2 = itk.CastImageFilter[float_image_type, short_image_type].New()
	cast2.SetInput(opening.GetOutput())

	segmented_image_data = cast2.GetOutput()
	if is_saved:
		save_image(short_image_type, segmented_image_data, output_path)
	# -------------------------------------------------------------------------
	
	# render volume and slices
	if is_rendering:
		print("Render image - right click to switch axis")
		render(short_image_type, input_image_data, segmented_image_data)


if __name__ == "__main__":
	output_path = "output.mha"
	is_saved = False
	is_rendering = True
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hso:", ["help", "save", "output=", "norendering"])
	except getopt.GetoptError:
		print(USAGE)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(USAGE)
			sys.exit()
		elif opt in ('-s', '--save'):
			is_saved = True
		elif opt == '--norendering':
			is_rendering = False
		elif opt in ("-o", "--output"):
			output_path = arg

	main(output_path, is_saved, is_rendering)
