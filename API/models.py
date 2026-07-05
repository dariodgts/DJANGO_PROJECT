from django.db import models
from django.conf import settings
from django.utils import timezone

class ServicePackage(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.IntegerField()
    category = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='box')  # Lucide icon identifier
    features = models.TextField(help_text="Separate features with newlines")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ServiceTemplateTask(models.Model):
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='template_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    estimated_hours = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.package.name} - {self.title}"

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    package = models.ForeignKey(ServicePackage, on_delete=models.SET_NULL, null=True, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # Percentage 0-100
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} ({self.client.username})"

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'Por Hacer'),
        ('in_progress', 'En Progreso'),
        ('review', 'En Revisión'),
        ('done', 'Completado'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
    ]
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='invoices')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, unique=True)
    date_created = models.DateField(default=timezone.now)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=250)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author.username} on task {self.task.title}"