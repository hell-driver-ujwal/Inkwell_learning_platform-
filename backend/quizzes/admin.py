"""Read-only inspection of quizzes records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from quizzes.models import Answer, Option, Question

admin.site.register(Question, InspectionAdmin)
admin.site.register(Option, InspectionAdmin)
admin.site.register(Answer, InspectionAdmin)
