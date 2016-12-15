from django.contrib import admin
import ncl_app.models as models

# Register your models here.
admin.site.register(models.League)
admin.site.register(models.Conference)
admin.site.register(models.Division)
admin.site.register(models.Team)
admin.site.register(models.Schedule)
admin.site.register(models.Day)
admin.site.register(models.Series)
admin.site.register(models.Match)


