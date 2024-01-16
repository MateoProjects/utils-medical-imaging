import os
import nibabel as nib
import pydicom 
import numpy as np
from skimage.transform import resize
from scipy import ndimage

# this function reads a dicom image and return the total ct scan
def get_dicoms(folder):
    """
    Loads all the images in dicom format and convert to a numpy array. 
    @param folder: folder where dicoms are located
    """
    images = []
    for file in os.listdir(folder):
        ds = pydicom.dcmread(os.path.join(folder, file))
        image = ds.pixel_array
        # for resizing image to desired size.
        img = resize(image, (512,512))
        # the two lines below ara util when you need that data be normalized in ranges 0-255 and type uint8
        #img = ((img - np.min(img)) / (np.max(img) - np.min(img))) * 255
        #img = img.astype(np.uint8) 
        images.append(img)
    return np.array(images)


def dicom_to_nifti(dicoms, output_nifti):
    """
    convert dicom files to nifti file
    @param dicoms : List of all images that compose the ct scan. 
    """
    # sometimes its necessari change the axis like [x,y,z] (w,h,d) to [z,x,z] (d,w,d)
    #dicoms = np.transpose(dicoms, (1, 2, 0))
    
    # Crea un objeto Nifti1Image desde el array 3D
    nifti_img = nib.Nifti1Image(dicoms, affine=np.eye(4))

    # Guarda el objeto Nifti1Image como archivo .nii
    nib.save(nifti_img, output_nifti)


def read_nifti_file(filepath):
    """Read and load volume"""
    # Read file
    scan = nib.load(filepath)
    # Get raw data
    img = scan.get_fdata()
    return img , scan


def normalize(volume):
    """Normalize the volume"""
    min = -1000
    max = 400
    volume[volume < min] = min
    volume[volume > max] = max
    volume = (volume - min) / (max - min)
    volume = volume.astype("float32")
    return volume


def resize_volume(img, depth):
    """Resize across z-axis
    Increase or decrease the images of the ct scan. 
    Function ndimage.zoom: The array is zoomed using spline interpolation of the requested order.
    """
    # Set the desired depth
    desired_depth = depth
    desired_width = 512
    desired_height = 512
    # Get current depth
    current_depth = img.shape[-1]
    current_width = img.shape[0]
    current_height = img.shape[1]
    # Compute depth factor
    depth = current_depth / desired_depth
    width = current_width / desired_width
    height = current_height / desired_height
    depth_factor = 1 / depth
    width_factor = 1 / width
    height_factor = 1 / height
    # Rotate
    #img = ndimage.rotate(img, 90, reshape=False)
    # Resize across z-axis
    img = ndimage.zoom(img, (width_factor, height_factor, depth_factor), order=1)
    return img


def process_scan(path, depth):
    """Read and resize volume"""
    # Read scan
    volume, scan = read_nifti_file(path)
    # Normalize
    volume = normalize(volume)
    # Resize width, height and depth
    volume = resize_volume(volume, depth)
    return volume, scan