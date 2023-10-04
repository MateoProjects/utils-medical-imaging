import matplotlib.pyplot as plt
import pydicom
import sys
import os   
import pandas as pd
from skimage.transform import resize
from scipy.interpolate import UnivariateSpline
sys.path.append("..")

folder ="your folder" 


def compute_points_of_interes(paths, verbose=0):
    # first image of a ct scan
    image = pydicom.dcmread(os.path.join(folder, paths[0])).pixel_array
    image = resize(image, (512,512))
    plt.imshow(image, cmap='gray')
    plt.show()
    x_A = int(input("Insert x_A: "))
    y_A = int(input("Insert y_A: "))
    
    
    # the middle slice of a ct scan
    num_slices = len(paths)
    mid_idx = int(num_slices/2)
    image = pydicom.dcmread(os.path.join(folder, paths[mid_idx])).pixel_array
    image = resize(image, (512,512))
    plt.imshow(image, cmap='gray')
    plt.show()
    x_M = int(input("Insert x_M: "))
    y_M = int(input("Insert y_M: "))
    
    # last image of a ct scan
    image = pydicom.dcmread(os.path.join(folder, paths[-1])).pixel_array
    image = resize(image, (512,512))
    plt.imshow(image, cmap='gray')
    plt.show()
    x_B = int(input("Insert x_B: "))
    y_B = int(input("Insert y_B: "))

    spline_x = UnivariateSpline([0, mid_idx, num_slices-1], [x_A, x_M, x_B], k=1)
    spline_y = UnivariateSpline([0, mid_idx, num_slices-1], [y_A, y_M, y_B], k=1)

    # Create the points of interest
    points_of_interest = [(int(spline_x(i)), int(spline_y(i))) for i in range(num_slices)]

    for i, image in enumerate(paths):
        if i == 0 or i == (len(paths)-1):
            pass
        else:
            image = pydicom.dcmread(os.path.join(folder, paths[i])).pixel_array
            image = resize(image, (512,512))

            point = [points_of_interest[i][0], points_of_interest[i][1]]
            if verbose == 1:
                print(point[0], point[1])
                plt.imshow(image)
                plt.plot(point[0], point[1], 'ro', markersize=2)
                plt.show()
                ans = input("It's correct the point of interest? ")
                if ans == 'n':
                    x = int(input("Insert new X: "))
                    y = int(input("Insert nww Y: "))
                    points_of_interest[i] = (x, y)
                    

    return points_of_interest

def ask_for_last_image(paths):
    paths.reverse()

    # Iterate through the list of images in reverse order
    for i, image in enumerate(paths):
        # Display the image or its path
        image = pydicom.dcmread(os.path.join(folder, image)).pixel_array
        plt.imshow(image, cmap='gray')
        plt.show()
        # Ask the user if they consider this as the last image
        answer = input("Do you consider this as the last image? (y/n): ")

        # Check the user's response
        if answer.lower() =='y' or answer.lower() == "s":
            # If the answer is 'y', return from 0 to the image marked as the last
            paths = paths[i+1:]
            return paths
    # If the user didn't choose any image as the last, return the full list
    return paths



def save_points_to_csv(points_of_interest, dicom_paths, output_file):
    """
    Save the points of interest into a CSV file along with the corresponding DICOM file paths.
    Parameters:
    points_of_interest (list of tuples): List of points of interest.
    dicom_paths (list of str): List of DICOM file paths.
    output_file (str): Path and name of the output CSV file.

    """
    # Check if the number of points of interest and DICOM file paths match
    if len(points_of_interest) != len(dicom_paths):
        raise ValueError("The number of interest points and DICOM file paths must match.")
    
    # Decompose the points of interest into x and y components
    x_coords = [point[0] for point in points_of_interest]
    y_coords = [point[1] for point in points_of_interest]
    
    # Create a pandas DataFrame
    df = pd.DataFrame(list(zip(dicom_paths, x_coords, y_coords)), columns=['DICOM Path', 'X Coordinate', 'Y Coordinate'])
    
    #Save the DataFrame as a CSV file
    df.to_csv(output_file, index=False)




dicom_paths = [file for file in os.listdir(folder) if not file.endswith(".npy")]
dicom_paths.sort(key=int)
print(dicom_paths, len(dicom_paths))
dicom_paths = ask_for_last_image(dicom_paths)
dicom_paths.reverse()
print(dicom_paths, len(dicom_paths))
points_of_interest = compute_points_of_interes(dicom_paths, verbose=0)
dicom_paths = [os.path.join(folder, path) for path in dicom_paths]
save_points_to_csv(points_of_interest, dicom_paths, 'output_file.csv')

