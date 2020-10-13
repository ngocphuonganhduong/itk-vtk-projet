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
	
	pixel_type = itk.ctype('short')
	dim = 3
	image_type = itk.Image[pixel_type, dim]
	
	reader = itk.ImageFileReader[image_type].New()
	reader.SetFileName(FILEPATH)
	reader.Update()
	
	# segmentation
	segment = itk.ConnectedThresholdImageFilter[image_type, image_type].New()
	segment.SetInput(reader.GetOutput())
	segment.SetSeed([100, 100, 100])
	segment.SetUpper(600)
	segment.SetLower(100)

	rescaler = itk.RescaleIntensityImageFilter[image_type, image_type].New()
	rescaler.SetInput(segment.GetOutput())
	rescaler.SetOutputMinimum(0)
	rescaler.SetOutputMaximum(255)
	
	segmented_image_data = rescaler.GetOutput()
	save_image(image_type, segmented_image_data)
	
	# render volume and slices
	render(image_type, segmented_image_data)


if __name__ == "__main__":
	main()
