from django.contrib import admin

from blogs import models

admin.site.register(models.Blogs)
admin.site.register(models.Tags)
admin.site.register(models.Posts)
admin.site.register(models.Comments)
