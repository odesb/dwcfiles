import shutil
from math import ceil
from django.db.models import Q
from dwcfiles.settings import MEDIA_ROOT
from django.views.generic import CreateView
from hamlpy.views.generic import DetailView
from .forms import FileUploadForm
from .models import UserFile


class HomeView(CreateView):
    template_name = 'filesharer/home.haml'
    form_class = FileUploadForm
    success_url = '/{id}'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['last_multimedia'] = UserFile.objects.filter(Q(mime_type__contains='image') | Q(mime_type__contains='video')).order_by('-pub_date')[:5] 
        context['last_files'] = UserFile.objects.exclude(mime_type__contains='image').exclude(mime_type__contains='video').order_by('-pub_date')
        fs_info = shutil.disk_usage(MEDIA_ROOT)
        context['used_space'] = ceil(fs_info[1] / 1024 / 1024 / 1024)
        context['total_space'] = ceil(fs_info[0] / 1024 / 1024 / 1024)
        context['percent_space'] = ceil(fs_info[1] / fs_info[0] * 100)
        return context


class UserFileView(DetailView):
    model = UserFile

    def get_object(self):
        return UserFile.objects.get(id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(UserFileView, self).get_context_data(**kwargs)
        context['filesize'] = '{:.2f} KB'.format(self.object.actualfile.size / 1024)
        return context


