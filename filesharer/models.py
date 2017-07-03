import magic
import os
from django.db import models
from hashid_field import HashidAutoField


#def upload_path(instance, filename):
#    return '{0}{1}'.format(instance.id, os.path.splitext(filename)[1])


class UserFile(models.Model):
    id = HashidAutoField(primary_key=True)
    actualfile = models.FileField()#upload_to=upload_path
    mime_type = models.CharField(max_length=30, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
        
    def save(self, *args, **kwargs):
        if self.title is None:
            self.title = self.actualfile.name
        self.mime_type = magic.from_buffer(self.actualfile.read(), mime=True)
        super(UserFile, self).save(*args, **kwargs)
    
