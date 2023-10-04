import nibabel as nib
import os
import SimpleITK as sitk
import six
import pandas as pd
from radiomics import featureextractor

params = {}



extractor = featureextractor.RadiomicsFeatureExtractor("settings.yml")
folder_path = "your_folder"

all_patients_results = []

for file in os.listdir(folder_path):
    if file.endswith(".nii") and not file.endswith("mask.nii"):
        image_path = os.path.join(folder_path, file)
        mask_path = os.path.join(folder_path, file.replace(".nii", "_mask.nii"))


        # Extract features
        result = extractor.execute(image_path, mask_path)
        result['id_patient'] = file.replace(".nii", "")
        result['type_rupture'] = "no_broken"
        # Print the features
        for key, value in result.items():
            print(f"{key}: {value}")

        # Append the result dictionary to the list
        all_patients_results.append(result)

df = pd.DataFrame(all_patients_results)

# Save the DataFrame to a CSV file
csv_file_path = "radiomics_features.csv"
df.to_csv(csv_file_path, index=False)

print("All features have been saved to the CSV file.")