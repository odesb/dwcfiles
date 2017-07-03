from django.forms import TextInput, ModelForm
from .models import UserFile


class FileUploadForm(ModelForm):
    class Meta:
        model = UserFile
        fields = ['title', 'actualfile']
        widgets = {
                'title': TextInput(attrs={'class': 'input'})
                }
