from django import forms

class VideoUploadForm(forms.Form):

    upload_video_file = forms.FileField(label="Select Video", required=True,widget=forms.FileInput(attrs={"accept": "video/*","class": "form-control"}))
    sequence_length = forms.IntegerField(label="Sequence Length", required=True)
