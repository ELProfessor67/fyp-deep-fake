from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.shortcuts import render
import torch
import torch.nn.functional as F
from PIL import Image
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image
import numpy as np
import warnings
import base64
import io


warnings.filterwarnings("ignore")

DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'

# Using BASE_DIR from settings
BASE_DIR = settings.BASE_DIR



def numpy_image_to_base64(image_array):
    # Ensure the image is in a format suitable for encoding
    success, buffer = cv2.imencode('.jpg', image_array)

    if success:
        # Encode the byte array to Base64
        base64_image = base64.b64encode(buffer).decode('utf-8')
        return base64_image
    else:
        raise ValueError("Image encoding failed.")
    



mtcnn = MTCNN(
    select_largest=False,
    post_process=False,
    device=DEVICE
).to(DEVICE).eval()

model = InceptionResnetV1(
    pretrained="vggface2",
    classify=True,
    num_classes=1,
    device=DEVICE
)

checkpoint = torch.load(BASE_DIR / "models/resnetinceptionv1_epoch_32.pth", map_location=torch.device('cpu'))
model.load_state_dict(checkpoint['model_state_dict'])
model.to(DEVICE)
model.eval()


def predictImage(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'})

        image = Image.open(uploaded_file)

        face = mtcnn(image)
        if face is None:
            return JsonResponse({'error': 'No face detected'})

        face = face.unsqueeze(0)
        face = F.interpolate(face, size=(256, 256), mode='bilinear', align_corners=False)


        # convert the face into a numpy array to be able to plot it
        prev_face = face.squeeze(0).permute(1, 2, 0).cpu().detach().int().numpy()
        prev_face = prev_face.astype('uint8')
        
        face = face.to(DEVICE)
        face = face.to(torch.float32)
        face = face / 255.0
        face_image_to_plot = face.squeeze(0).permute(1, 2, 0).cpu().detach().int().numpy()

        target_layers = [model.block8.branch1[-1]]
        
        # Correct usage
        cam = GradCAM(model=model, target_layers=target_layers)
        
        targets = [ClassifierOutputTarget(0)]
        
        grayscale_cam = cam(input_tensor=face, targets=targets, eigen_smooth=True)
        grayscale_cam = grayscale_cam[0, :]
        visualization = show_cam_on_image(face_image_to_plot, grayscale_cam, use_rgb=True)
        face_with_mask = cv2.addWeighted(prev_face, 1, visualization, 0.5, 0)
        face_with_mask_base64 = numpy_image_to_base64(face_with_mask)
        face_with_mask_base64 = f"data:image/png;base64, {face_with_mask_base64}"
        
        with torch.no_grad():
            output = torch.sigmoid(model(face).squeeze(0))
            prediction = "real" if output.item() < 0.5 else "fake"
            real_prediction = 1 - output.item()
            fake_prediction = output.item()
            
            confidences = {
                'real': round(real_prediction * 100),
                'fake': round(fake_prediction * 100)
            }
        
        context = {'prediction': prediction, 'confidences': confidences,'face_with_mask':face_with_mask_base64}
        return render(request, 'image.html',context)
    return JsonResponse({'error': 'Invalid request method'})
