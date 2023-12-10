#!/bin/bash

# Set the input and output directories
input_directory="episode_images"  # Replace with your actual input directory
output_directory="episode_images/collage.jpg"  # Replace with your desired output file

# Create the montage
montage "${input_directory}"/*.png -tile 3x3 -geometry +0+0 "${output_directory}"

echo "Collage created at: ${output_directory}"
