import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'API_PRUEBA.settings')
django.setup()

from API.models import ServicePackage, ServiceTemplateTask
from django.contrib.auth.models import User

# Check if packages exist
if not ServicePackage.objects.exists():
    # 1. Landing Page
    lp = ServicePackage.objects.create(
        name="Plan Inicial: Landing Page Premium",
        description="Una página de aterrizaje moderna y de conversión rápida, diseñada para capturar leads y presentar tu producto o servicio con un diseño de clase mundial.",
        price=499.00,
        delivery_days=7,
        category="Desarrollo",
        icon="layout",
        features="Diseño UX/UI personalizado\nOptimización SEO\nIntegración de analíticas\nAdaptable a móviles\nSoporte por 30 días"
    )
    ServiceTemplateTask.objects.create(package=lp, title="Definición de requerimientos y wireframes", description="Reunión con el cliente para detallar la estructura y contenido de la página.", estimated_hours=4, order=1)
    ServiceTemplateTask.objects.create(package=lp, title="Diseño de interfaz en Figma", description="Diseño visual y de experiencia de usuario en Figma para revisión y feedback.", estimated_hours=8, order=2)
    ServiceTemplateTask.objects.create(package=lp, title="Desarrollo Frontend Responsivo", description="Codificación limpia en HTML, CSS y JS moderno.", estimated_hours=16, order=3)
    ServiceTemplateTask.objects.create(package=lp, title="Configuración de Formularios y Analytics", description="Integración con Google Analytics y envío de correos de contacto.", estimated_hours=6, order=4)
    ServiceTemplateTask.objects.create(package=lp, title="Optimización SEO y Despliegue", description="Pruebas finales, auditoría de velocidad lighthouse y publicación del sitio.", estimated_hours=4, order=5)

    # 2. E-commerce
    ec = ServicePackage.objects.create(
        name="Plan Crecimiento: E-commerce Completo",
        description="Una tienda en línea profesional con catálogo autoadministrable, carrito de compras integrado y procesamiento de pagos seguros.",
        price=1499.00,
        delivery_days=21,
        category="E-commerce",
        icon="shopping-bag",
        features="Hasta 100 productos\nPasarela de pagos (Stripe/PayPal)\nPanel de administración de inventario\nNotificaciones por email\nSoporte prioritario"
    )
    ServiceTemplateTask.objects.create(package=ec, title="Estructuración de Catálogo e Inventario", description="Definición de categorías de productos, variantes y atributos.", estimated_hours=8, order=1)
    ServiceTemplateTask.objects.create(package=ec, title="Diseño de Vistas del Carrito e Interfaz", description="Diseño del flujo de compra desde el producto hasta el checkout.", estimated_hours=12, order=2)
    ServiceTemplateTask.objects.create(package=ec, title="Integración de Stripe y Pasarela de Pago", description="Configuración segura de procesamiento de tarjetas de crédito y tokens.", estimated_hours=20, order=3)
    ServiceTemplateTask.objects.create(package=ec, title="Desarrollo del Panel de Administración", description="Sección para gestionar pedidos, stock de productos y clientes.", estimated_hours=24, order=4)
    ServiceTemplateTask.objects.create(package=ec, title="Pruebas de Seguridad y Carga", description="Auditoría de seguridad en cobros y simulación de transacciones.", estimated_hours=8, order=5)

    # 3. SaaS Kit
    saas = ServicePackage.objects.create(
        name="Plan SaaS Starter Kit",
        description="Acelera el lanzamiento de tu startup con una infraestructura de software sólida: autenticación multi-usuario, pasarela de suscripciones recurrentes y dashboard operacional.",
        price=2499.00,
        delivery_days=30,
        category="SaaS",
        icon="layers",
        features="Autenticación y roles de usuario\nFacturación recurrentes (Suscripciones)\nDashboard de analíticas\nIntegración de APIs de terceros\nSoporte dedicado"
    )
    ServiceTemplateTask.objects.create(package=saas, title="Modelado y Arquitectura Multitenant", description="Arquitectura de base de datos para aislamiento de inquilinos y seguridad.", estimated_hours=16, order=1)
    ServiceTemplateTask.objects.create(package=saas, title="Módulo de Autenticación y Perfiles", description="Implementación de inicio de sesión, roles de usuario, permisos y seguridad OAuth.", estimated_hours=20, order=2)
    ServiceTemplateTask.objects.create(package=saas, title="Configuración de Cobros Recurrentes (Suscripciones)", description="Integración con webhook para planes mensuales/anuales.", estimated_hours=32, order=3)
    ServiceTemplateTask.objects.create(package=saas, title="Desarrollo del Dashboard Principal", description="Módulo visual interactivo con KPI y gráficos sobre consumo y ventas.", estimated_hours=24, order=4)
    ServiceTemplateTask.objects.create(package=saas, title="Pruebas unitarias de cobertura > 80%", description="Implementación de test unitarios para asegurar robustez en producción.", estimated_hours=16, order=5)

    print("Seed data loaded successfully!")
else:
    print("Seed data already exists.")
