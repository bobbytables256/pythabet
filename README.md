# pythabet
Genetic font generator written in Python

# Dependencies
* tested with python 2.7
* python imaging library
* pyocr and a compatible library (only tesseract has been tested)
* imagemagick command-line utils, for font creation only
* fonts

# Make sample images
* Edit fontlist.txt to include the name of fonts you'd like to render (use `convert -list font` to get a list of available fonts).
* Run makeset.py (make sure the letter directory exists)

# Create a font
* Edit main.py to set 
  * `for letter in "abcd"`
  * `OCR_REPEAT`
  * `GEN_SIZE`
  * `GEN_NUM = 12`
* run main.py and wait...

# TODO:
* Refactoring and abstraction
* Better config
* Multiprocessing
* Move to Python 3
* Move OCR to the GPU
* Configurable image sizes
* Rework genetic code
* Better generation statistics and generation resets

