# Imports
from cgitb import text
from PIL import Image
from random import randrange
import numpy as np
import sys

def text_to_binary(file_path):

    # Read in file
    ground_truth = np.loadtxt(file_path, dtype="str", delimiter="\n")

    # Clean data
    ground_truth = np.char.strip(ground_truth)
    ground_truth = np.char.replace(ground_truth, " ", "-")

    # Create binary representations for each question
    # The following code has snippits from: https://www.geeksforgeeks.org/python-convert-string-to-binary/ (lines marked)
    bin_reps = []
    for entry in ground_truth:
        binary = ''.join(format(ord(i), '08b') for i in entry) # Code taken from site linked above 
        bin_reps.append([binary[i:i+8] for i in range(0, len(binary), 8)]) # Code taken from site linked above

    # End of code taken from https://www.geeksforgeeks.org/python-convert-string-to-binary/

    # Add null characters to fill out array
    for entry in bin_reps:
        arr_len = len(entry)
        for i in range(arr_len, 8):
            entry.append('00000000')

    return bin_reps

def generate_barcodes(bin_arr):

    barcodes = dict()
    x = 1;

    # Loop through each questions in the test set
    for question in bin_arr:

        # Create two pixel edge in a different color for edge detection
        bounds = [127 for i in range(28)]
        barcode = [bounds, bounds]

        # Loop through each binary representation within a question
        for entry in question:

            # Representing each binary character as a 3 pixel x 3 pixel dot. Starting each dot with an edge boundary
            row1 = [127, 127]
            row2 = [127, 127]
            row3 = [127, 127]

            # Loop through each character in the binary string for that data value
            for c in entry:
                for i in range(3):

                    # Check the value of 'c' to see if it is a 0 or 1 and then assign the pixel value based on that
                    val = 0 if c == '1' else 255

                    # Add the value to each row
                    row1.append(val)
                    row2.append(val)
                    row3.append(val)
                
            # Add edge boundary onto the end of each row once they are finished being created
            for i in range(2):
                row1.append(127)
                row2.append(127)
                row3.append(127)

            # Add the 3 rows together to create a single entry in the barcode
            barcode.extend([row1, row2, row3])

        # Add the bottom boundary to the barcode
        barcode.extend([bounds, bounds])

        # Convert the barcode to an numpy array to easily create an image
        barcode = np.array(barcode)

        # Create the image and save it
        im = Image.fromarray(np.uint8(barcode), mode="L")
        barcodes[x] = im
        # im.save(save_file_path_and_name + f"-{x}.png")
        
        x+=1
    
    return barcodes


def read_barcode(file_path):
    # Read in image and convert it to an array
    im = Image.open(file_path)
    im = im.convert('L')
    barcode = np.array(im)

    values = []

    x = 0

    # Fixed width and height loop that 'scans' a barcode
    while x < 28:
        val_string = ''
        y = 0

        while y < 28:

            # Check pixel values to determine what binary representation they are
            if barcode[x][y] >= 0 and barcode[x][y] <= 30:
                val_string+='1'

                # Since we have found a pixel, skip ahead 3 since each bit is represented in a 3 pixel x 3 pixel domain
                y+=3

            elif barcode[x][y] <= 255 and barcode[x][y] >= 190:
                val_string+='0'

                # Since we have found a pixel, skip ahead 3 since each bit is represented in a 3 pixel x 3 pixel domain
                y+=3

            else:

                # We didn't find a matching binary representation (most likely an edge or noise), so just increment the loop as normal
                y+=1
        
        # If our value string was an actual binary representation (i.e. not a null character), add it to our values
        if val_string != '':
            values.append(val_string)

            # Since we found a row that had a binary representation, skip down 3 rows since each bit is represented in a 3 pixel x 3 pixel domain
            x+=3

        else:

            # We didn't find a valid binary string (i.e. a null character), so just increment the loop as normal
            x+=1


    # Code below taken from: https://www.kite.com/python/answers/how-to-convert-binary-to-string-in-python
    # and adapted to fit our use case
    ascii_string = ""
    letter_flag = False
    invalid_barcode_flag = False

    for value in values:

        # Convert the value from base 2 to an integer
        ac = int(value, 2)

        # Handle null characters
        if ac == 0:
            continue;

        # Check to see if we are on the letter part of the answer
        if letter_flag:
            # Check for letters outside of the range of A-E
            if ac < 65 or ac > 69:
                invalid_barcode_flag = True

        # Convert the integer representation of a character to an actual character 
        ac = chr(ac)

        # Revert '-' to spaces
        if ac == "-":
            # Handle noise by excluding numbers higher than 85 and lower than 1
            if int(ascii_string) > 85 or int(ascii_string) < 1:
                invalid_barcode_flag = True
            else:
                ascii_string+=" "
                letter_flag = True
        else:
            ascii_string+=ac

    # End of taken code

    if invalid_barcode_flag:
        raise ValueError(f"Corrupted barcode. Couldn't not decipher answer fully. Best guess: {ascii_string}")
        
    return ascii_string    

if __name__ == '__main__':
    # Open blank form
    im = Image.open(sys.argv[1])
    im = im.convert("L")

    # Generate barcodes
    binary_array = text_to_binary(sys.argv[2])
    barcodes = generate_barcodes(binary_array)

    cur_index = [555,657]

    for n in range(1, 30):
        # temp_im = Image.open(f"test-images/a3-barcodes/answer-{n}.png")
        arr = np.array(barcodes[n])

        x = 0
        for i in range(cur_index[1], cur_index[1]+28):
            row = arr[x]
            y = 0
            for j in range(cur_index[0], cur_index[0]+28):
                im.putpixel((j, i), int(row[y]))
                y+=1
            x+=1

        cur_index[1]+= randrange(49,51,1)

    cur_index[0] += 449
    cur_index[1] = 657

    for n in range(30, 59):
        # temp_im = Image.open(f"test-images/a3-barcodes/answer-{n}.png")
        arr = np.array(barcodes[n])

        x = 0
        for i in range(cur_index[1], cur_index[1]+28):
            row = arr[x]
            y = 0
            for j in range(cur_index[0], cur_index[0]+28):
                im.putpixel((j, i), int(row[y]))
                y+=1
            x+=1

        cur_index[1]+= randrange(49,51,1)

    cur_index[0] += 449
    cur_index[1] = 657

    for n in range(59, 86):
        # temp_im = Image.open(f"test-images/a3-barcodes/answer-{n}.png")
        arr = np.array(barcodes[n])

        x = 0
        for i in range(cur_index[1], cur_index[1]+28):
            row = arr[x]
            y = 0
            for j in range(cur_index[0], cur_index[0]+28):
                im.putpixel((j, i), int(row[y]))
                y+=1
            x+=1

        cur_index[1]+= randrange(49,51,1)

    im.save(sys.argv[3])