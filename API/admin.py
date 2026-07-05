# Register your models here.
from django.contrib import admin

from .models import ServicePackage, ServiceTemplateTask, Project, Task, Invoice, InvoiceItem, TaskComment

admin.site.register(ServicePackage)
admin.site.register(ServiceTemplateTask)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(TaskComment)
