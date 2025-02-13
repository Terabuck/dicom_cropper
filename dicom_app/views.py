import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from .forms import DicomUploadForm
import pydicom

def upload_dicom(request):
    if request.method == 'POST':
        form = DicomUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dicom_file = form.cleaned_data['dicom_file']

            # Define the correct upload path within MEDIA_ROOT
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_path, exist_ok=True)  # Ensure the directory exists

            # Save the uploaded file
            file_path = os.path.join(upload_path, 'temp.dcm')
            with open(file_path, 'wb+') as destination:
                for chunk in dicom_file.chunks():
                    destination.write(chunk)

            # Read the DICOM file using pydicom (optional, just for confirmation)
            ds = pydicom.dcmread(file_path)
            print("Patient Name:", ds.PatientName)  # Debugging purposes

            # Instead of using MEDIA_URL, return a URL that Django will serve dynamically
            dicom_url = f"/dicom/temp.dcm"
            return render(request, 'dicom_app/display.html', {'dicom_file_url': dicom_url})
    else:
        form = DicomUploadForm()
    return render(request, 'dicom_app/upload.html', {'form': form})

# ✅ New function to serve the DICOM file with the correct MIME type
def serve_dicom_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "uploads", filename)

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/dicom")  # Ensure correct MIME type
            response["Content-Disposition"] = f'inline; filename="{filename}"'
            return response
    else:
        return HttpResponse("File not found", status=404)



from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os
import pydicom
import numpy as np

def crop_dicom(request):
    # Get the cropping coordinates from the frontend
    x1 = int(request.POST.get("x1"))
    y1 = int(request.POST.get("y1"))
    x2 = int(request.POST.get("x2"))
    y2 = int(request.POST.get("y2"))
    
    # Load the original DICOM file (replace with your actual file path)
    dicom_path = 'path_to_your_dicom_file.dcm'
    dicom_data = pydicom.dcmread(dicom_path)
    
    # Get pixel data from DICOM
    pixel_data = dicom_data.pixel_array
    
    # Crop the image using the provided coordinates
    cropped_pixel_data = pixel_data[y1:y2, x1:x2]
    
    # Create a new DICOM file with the cropped image
    cropped_dicom = dicom_data
    cropped_dicom.PixelData = cropped_pixel_data.tobytes()
    cropped_dicom.Rows, cropped_dicom.Columns = cropped_pixel_data.shape
    
    # Generate a file name and save the cropped DICOM
    output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'cropped_image.dcm')
    cropped_dicom.save_as(output_path)

    # Return the file path to the frontend
    return JsonResponse({'cropped_image_url': '/media/outputs/cropped_image.dcm'})