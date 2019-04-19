from django.contrib import admin
from .models import *

admin.site.register(Question)
admin.site.register(Lecture)
admin.site.register(Lecturer)
admin.site.register(Participant)
admin.site.register(QuestionVote)
admin.site.register(Moderator)
admin.site.register(Administrator)
admin.site.register(DirectMessage)
admin.site.register(Location)
# Register your models here.
