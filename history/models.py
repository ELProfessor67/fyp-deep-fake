# models.py

from django.db import models
from django.contrib.auth.models import User  # Assuming you're using Django's built-in User model
from django.utils import timezone
import json


class UserImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    original_image = models.TextField(blank=True, null=True)
    processed_image = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)  # Timestamp when the image was uploaded
    result =  models.TextField(blank=True, null=True)
    fake_prediction =  models.FloatField(blank=True, null=True)
    real_prediction =  models.FloatField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"



class VideoProcessingResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preprocessed_images = models.TextField()  # Store list of image paths as a string
    faces_cropped_images = models.TextField()  # Store list of image paths as a string
    heatmap_images = models.TextField()  # Store list of image paths as a string
    original_video = models.CharField(max_length=255)
    models_location = models.CharField(max_length=255)
    output = models.TextField()
    confidence = models.FloatField()

    def set_preprocessed_images(self, image_list):
        self.preprocessed_images = json.dumps(image_list)

    def get_preprocessed_images(self):
        return json.loads(self.preprocessed_images)

    def set_faces_cropped_images(self, image_list):
        self.faces_cropped_images = json.dumps(image_list)

    def get_faces_cropped_images(self):
        return json.loads(self.faces_cropped_images)

    def set_heatmap_images(self, image_list):
        self.heatmap_images = json.dumps(image_list)

    def get_heatmap_images(self):
        return json.loads(self.heatmap_images)

    def __str__(self):
        return f"Processing result for {self.user.username} - {self.original_video}"
