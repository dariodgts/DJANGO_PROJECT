import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from .models import ServicePackage, ServiceTemplateTask, Project, Task, Invoice, InvoiceItem, TaskComment

# HTML view for the SPA
def index_view(request):
    return render(request, 'index.html')

# Auth views
@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'username': user.username,
                    'is_staff': user.is_staff,
                    'email': user.email
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Credenciales inválidas'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'El usuario ya existe'}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'username': user.username,
                'is_staff': user.is_staff,
                'email': user.email
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})

def api_user_info(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'username': request.user.username,
                'is_staff': request.user.is_staff,
                'email': request.user.email
            }
        })
    return JsonResponse({'authenticated': False})

# Packages
def api_list_packages(request):
    packages = ServicePackage.objects.filter(is_active=True)
    data = []
    for p in packages:
        data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price),
            'delivery_days': p.delivery_days,
            'category': p.category,
            'icon': p.icon,
            'features': [f.strip() for f in p.features.split('\n') if f.strip()],
            'template_tasks': list(p.template_tasks.values('title', 'estimated_hours'))
        })
    return JsonResponse({'packages': data})

# Checkout / Buy
@csrf_exempt
def api_checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        package_id = data.get('package_id')
        package = ServicePackage.objects.get(id=package_id)
        
        # Create Project
        project = Project.objects.create(
            client=request.user,
            package=package,
            title=f"Proyecto: {package.name}",
            description=f"Proyecto contratado por {request.user.username} para el servicio {package.name}.",
            status='active',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=package.delivery_days)).date(),
            total_price=package.price
        )
        
        # Copy template tasks
        templates = ServiceTemplateTask.objects.filter(package=package)
        for t in templates:
            Task.objects.create(
                project=project,
                title=t.title,
                description=t.description,
                status='todo',
                order=t.order
            )
            
        # Create Invoice
        import datetime
        invoice_number = f"INV-{datetime.datetime.now().strftime('%Y%m%d')}-{project.id:04d}"
        invoice = Invoice.objects.create(
            project=project,
            client=request.user,
            invoice_number=invoice_number,
            due_date=(timezone.now() + timezone.timedelta(days=15)).date(),
            subtotal=package.price,
            tax=package.price * 0.19,  # 19% IVA (Alegra style)
            total=package.price * 1.19,
            status='sent'
        )
        
        # Create Invoice Item
        InvoiceItem.objects.create(
            invoice=invoice,
            description=f"Servicio contratado: {package.name}",
            quantity=1,
            unit_price=package.price,
            total_price=package.price
        )
        
        return JsonResponse({
            'success': True,
            'project_id': project.id,
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Projects
def api_list_projects(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    if request.user.is_staff:
        projects = Project.objects.all().order_by('-id')
    else:
        projects = Project.objects.filter(client=request.user).order_by('-id')
        
    data = []
    for p in projects:
        data.append({
            'id': p.id,
            'client': p.client.username,
            'package_name': p.package.name if p.package else "Servicio Personalizado",
            'title': p.title,
            'description': p.description,
            'status': p.status,
            'progress': p.progress,
            'start_date': p.start_date.strftime('%Y-%m-%d') if p.start_date else "",
            'end_date': p.end_date.strftime('%Y-%m-%d') if p.end_date else "",
            'total_price': float(p.total_price)
        })
    return JsonResponse({'projects': data})

def api_project_detail(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        if request.user.is_staff:
            project = Project.objects.get(id=project_id)
        else:
            project = Project.objects.get(id=project_id, client=request.user)
            
        tasks = project.tasks.all().order_by('order', 'id')
        tasks_data = []
        for t in tasks:
            tasks_data.append({
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else "",
                'priority': t.priority,
                'assigned_to': t.assigned_to.username if t.assigned_to else ""
            })
            
        invoices = project.invoices.all().order_by('-id')
        invoices_data = []
        for inv in invoices:
            invoices_data.append({
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'date_created': inv.date_created.strftime('%Y-%m-%d'),
                'due_date': inv.due_date.strftime('%Y-%m-%d'),
                'total': float(inv.total),
                'status': inv.status
            })
            
        project_data = {
            'id': project.id,
            'title': project.title,
            'client': project.client.username,
            'package_name': project.package.name if project.package else "Servicio Personalizado",
            'description': project.description,
            'status': project.status,
            'progress': project.progress,
            'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else "",
            'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else "",
            'total_price': float(project.total_price),
            'tasks': tasks_data,
            'invoices': invoices_data
        }
        return JsonResponse({'project': project_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Tasks operations
@csrf_exempt
def api_create_task(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        if request.user.is_staff:
            project = Project.objects.get(id=project_id)
        else:
            project = Project.objects.get(id=project_id, client=request.user)
            
        task = Task.objects.create(
            project=project,
            title=data.get('title'),
            description=data.get('description', ''),
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date') or None
        )
        
        update_project_progress(project)
        return JsonResponse({'success': True, 'task_id': task.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def api_update_task(request, task_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        task = Task.objects.get(id=task_id)
        
        # Check permissions
        if not request.user.is_staff and task.project.client != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
            
        if 'status' in data:
            task.status = data['status']
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = data['due_date'] or None
            
        task.save()
        update_project_progress(task.project)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def api_delete_task(request, task_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST' and request.method != 'DELETE':
        return JsonResponse({'error': 'POST/DELETE required'}, status=405)
    try:
        task = Task.objects.get(id=task_id)
        if not request.user.is_staff and task.project.client != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
            
        project = task.project
        task.delete()
        update_project_progress(project)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def update_project_progress(project):
    total = project.tasks.count()
    if total == 0:
        project.progress = 0
    else:
        done = project.tasks.filter(status='done').count()
        project.progress = int((done / total) * 100)
    project.save()

# Invoices
def api_list_invoices(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    if request.user.is_staff:
        invoices = Invoice.objects.all().order_by('-id')
    else:
        invoices = Invoice.objects.filter(client=request.user).order_by('-id')
        
    data = []
    for inv in invoices:
        items = list(inv.items.values('description', 'quantity', 'unit_price', 'total_price'))
        data.append({
            'id': inv.id,
            'invoice_number': inv.invoice_number,
            'client': inv.client.username,
            'project_title': inv.project.title if inv.project else "General",
            'date_created': inv.date_created.strftime('%Y-%m-%d'),
            'due_date': inv.due_date.strftime('%Y-%m-%d'),
            'subtotal': float(inv.subtotal),
            'tax': float(inv.tax),
            'total': float(inv.total),
            'status': inv.status,
            'items': items
        })
    return JsonResponse({'invoices': data})

@csrf_exempt
def api_pay_invoice(request, invoice_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        inv = Invoice.objects.get(id=invoice_id)
        if not request.user.is_staff and inv.client != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
            
        inv.status = 'paid'
        inv.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Dashboard Stats (Alegra style metrics + Asana overview)
def api_dashboard_stats(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    if request.user.is_staff:
        # Admin gets global financial and operational metrics
        total_sales = Invoice.objects.filter(status='paid').aggregate(Sum('total'))['total__sum'] or 0.0
        receivables = Invoice.objects.filter(status__in=['sent', 'overdue']).aggregate(Sum('total'))['total__sum'] or 0.0
        
        projects_count = Project.objects.count()
        active_projects_count = Project.objects.filter(status='active').count()
        tasks_status = Task.objects.values('status').annotate(count=Count('id'))
        
        # Recent sales
        recent_sales = []
        invoices = Invoice.objects.all().order_by('-id')[:5]
        for inv in invoices:
            recent_sales.append({
                'number': inv.invoice_number,
                'client': inv.client.username,
                'total': float(inv.total),
                'status': inv.status,
                'date': inv.date_created.strftime('%Y-%m-%d')
            })
            
        # Recent projects
        recent_projects = []
        projects = Project.objects.all().order_by('-id')[:5]
        for p in projects:
            recent_projects.append({
                'id': p.id,
                'title': p.title,
                'progress': p.progress,
                'status': p.status
            })
    else:
        # Client gets their own metrics
        total_sales = Invoice.objects.filter(client=request.user, status='paid').aggregate(Sum('total'))['total__sum'] or 0.0
        receivables = Invoice.objects.filter(client=request.user, status__in=['sent', 'overdue']).aggregate(Sum('total'))['total__sum'] or 0.0
        
        projects_count = Project.objects.filter(client=request.user).count()
        active_projects_count = Project.objects.filter(client=request.user, status='active').count()
        tasks_status = Task.objects.filter(project__client=request.user).values('status').annotate(count=Count('id'))
        
        recent_sales = []
        invoices = Invoice.objects.filter(client=request.user).order_by('-id')[:5]
        for inv in invoices:
            recent_sales.append({
                'number': inv.invoice_number,
                'client': inv.client.username,
                'total': float(inv.total),
                'status': inv.status,
                'date': inv.date_created.strftime('%Y-%m-%d')
            })
            
        recent_projects = []
        projects = Project.objects.filter(client=request.user).order_by('-id')[:5]
        for p in projects:
            recent_projects.append({
                'id': p.id,
                'title': p.title,
                'progress': p.progress,
                'status': p.status
            })

    # Structure tasks stats
    tasks_stats = {'todo': 0, 'in_progress': 0, 'review': 0, 'done': 0}
    for item in tasks_status:
        tasks_stats[item['status']] = item['count']

    # Simulated monthly revenue for chart (last 6 months)
    import datetime
    chart_data = []
    today = datetime.datetime.now()
    # Simple generation: for past months, sum invoices
    for i in range(5, -1, -1):
        m_date = today - datetime.timedelta(days=i*30)
        m_name = m_date.strftime('%b')
        # Filter paid invoices in that month
        if request.user.is_staff:
            m_total = Invoice.objects.filter(status='paid', date_created__month=m_date.month, date_created__year=m_date.year).aggregate(Sum('total'))['total__sum'] or 0.0
        else:
            m_total = Invoice.objects.filter(client=request.user, status='paid', date_created__month=m_date.month, date_created__year=m_date.year).aggregate(Sum('total'))['total__sum'] or 0.0
        
        # Add seed values to chart so it looks visually interesting
        seed_value = 0.0
        if i == 5: seed_value = 1200.0
        elif i == 4: seed_value = 2400.0
        elif i == 3: seed_value = 1800.0
        elif i == 2: seed_value = 3500.0
        elif i == 1: seed_value = 2800.0
        elif i == 0: seed_value = float(total_sales)
        
        chart_data.append({
            'month': m_name,
            'revenue': max(seed_value, float(m_total))
        })

    return JsonResponse({
        'financials': {
            'total_sales': float(total_sales),
            'receivables': float(receivables),
        },
        'operations': {
            'projects_count': projects_count,
            'active_projects_count': active_projects_count,
            'tasks': tasks_stats
        },
        'recent_sales': recent_sales,
        'recent_projects': recent_projects,
        'chart_data': chart_data
    })
