# library/management/commands/populate_library_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from library.models import ResourceCategory, BestPracticeResource


class Command(BaseCommand):
    help = 'Puebla la biblioteca con categorías y recursos de ejemplo'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando población de biblioteca...'))

        # CATEGORÍAS
        categories_data = [
            {
                'name': 'Reclutamiento Inclusivo',
                'description': 'Guías y recursos para implementar procesos de reclutamiento que promuevan la diversidad y la inclusión.',
                'icon': 'bi-person-check',
                'order': 1
            },
            {
                'name': 'Onboarding y Adaptación',
                'description': 'Recursos para integrar exitosamente a personas con discapacidad en tu organización.',
                'icon': 'bi-door-open',
                'order': 2
            },
            {
                'name': 'Accesibilidad en el Lugar de Trabajo',
                'description': 'Mejores prácticas para crear espacios de trabajo físicos y digitales accesibles.',
                'icon': 'bi-universal-access',
                'order': 3
            },
            {
                'name': 'Políticas y Normativas',
                'description': 'Información sobre leyes, regulaciones y políticas de inclusión laboral.',
                'icon': 'bi-file-text',
                'order': 4
            },
            {
                'name': 'Capacitación y Sensibilización',
                'description': 'Recursos para capacitar a tu equipo en temas de inclusión y diversidad.',
                'icon': 'bi-mortarboard',
                'order': 5
            },
            {
                'name': 'Casos de Éxito',
                'description': 'Historias reales de empresas que han implementado políticas inclusivas exitosamente.',
                'icon': 'bi-trophy',
                'order': 6
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ResourceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order']
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Categoría creada: {category.name}'))

        # RECURSOS
        resources_data = [
            # Reclutamiento Inclusivo
            {
                'title': 'Guía Completa de Reclutamiento Inclusivo',
                'category': 'Reclutamiento Inclusivo',
                'resource_type': 'guide',
                'description': 'Manual paso a paso para implementar procesos de reclutamiento que garanticen igualdad de oportunidades para personas con discapacidad.',
                'content': '''Esta guía proporciona un marco completo para transformar tus procesos de reclutamiento:

1. ANÁLISIS DE REQUISITOS DEL PUESTO
   - Identifica requisitos esenciales vs. deseables
   - Elimina barreras innecesarias
   - Enfócate en competencias, no en métodos

2. REDACCIÓN DE OFERTAS INCLUSIVAS
   - Usa lenguaje neutral e inclusivo
   - Especifica disponibilidad de ajustes razonables
   - Evita términos discriminatorios

3. CANALES DE DIFUSIÓN
   - Publica en plataformas especializadas
   - Colabora con organizaciones de personas con discapacidad
   - Usa tecnología accesible

4. PROCESO DE SELECCIÓN
   - Ofrece formatos alternativos para pruebas
   - Capacita al equipo de selección
   - Implementa entrevistas estructuradas

5. DECISIÓN Y RETROALIMENTACIÓN
   - Basa decisiones en criterios objetivos
   - Proporciona retroalimentación constructiva
   - Documenta el proceso''',
                'author': 'Ministerio de Trabajo de Colombia',
                'tags': 'reclutamiento, inclusión, contratación, diversidad',
                'is_featured': True,
                'is_accessible': True,
                'accessibility_notes': 'Documento compatible con lectores de pantalla. Incluye texto alternativo en todas las imágenes.'
            },
            {
                'title': 'Checklist: Ofertas de Empleo Inclusivas',
                'category': 'Reclutamiento Inclusivo',
                'resource_type': 'checklist',
                'description': 'Lista de verificación práctica para asegurar que tus ofertas de empleo sean inclusivas y accesibles.',
                'content': '''CHECKLIST DE OFERTA INCLUSIVA

✓ LENGUAJE Y REDACCIÓN
□ Usa lenguaje neutral de género
□ Evita términos discriminatorios (ej: "persona normal")
□ Menciona explícitamente la apertura a personas con discapacidad
□ Especifica disponibilidad de ajustes razonables

✓ REQUISITOS DEL PUESTO
□ Diferencia entre requisitos esenciales y deseables
□ Enfoca en resultados, no en métodos específicos
□ Evita requisitos físicos innecesarios
□ Permite experiencia equivalente

✓ ACCESIBILIDAD
□ El portal de empleo es accesible (WCAG 2.1)
□ Ofrece formatos alternativos para aplicar
□ Proporciona información de contacto para solicitar ajustes
□ El proceso de aplicación es simple y claro

✓ INFORMACIÓN ADICIONAL
□ Describe la cultura inclusiva de la empresa
□ Menciona beneficios y apoyos disponibles
□ Incluye declaración de igualdad de oportunidades
□ Proporciona información sobre el proceso de selección

✓ DIFUSIÓN
□ Publica en plataformas especializadas
□ Comparte con organizaciones de personas con discapacidad
□ Usa múltiples canales de difusión''',
                'author': 'OIT - Organización Internacional del Trabajo',
                'tags': 'checklist, reclutamiento, ofertas, inclusión',
                'is_accessible': True
            },
            
            # Onboarding
            {
                'title': 'Plan de Onboarding Inclusivo: Template',
                'category': 'Onboarding y Adaptación',
                'resource_type': 'template',
                'description': 'Plantilla descargable para diseñar un proceso de onboarding adaptado a las necesidades de cada empleado.',
                'content': '''TEMPLATE: PLAN DE ONBOARDING INCLUSIVO

INFORMACIÓN DEL EMPLEADO
- Nombre: _______________________
- Puesto: _______________________
- Fecha de inicio: _______________
- Necesidades de ajuste: _________

FASE 1: PRE-INGRESO (1-2 semanas antes)
□ Contacto inicial con RRHH
□ Evaluación de necesidades de ajuste
□ Preparación del espacio de trabajo
□ Configuración de tecnología asistiva
□ Asignación de mentor/buddy

FASE 2: PRIMER DÍA
□ Bienvenida personalizada
□ Tour accesible de las instalaciones
□ Entrega de materiales en formato accesible
□ Configuración de equipos y accesos
□ Presentación del equipo

FASE 3: PRIMERA SEMANA
□ Capacitación en herramientas
□ Reuniones 1:1 con supervisor
□ Presentación de proyectos iniciales
□ Revisión de políticas y procedimientos
□ Check-in diario

FASE 4: PRIMER MES
□ Evaluación de ajustes razonables
□ Retroalimentación bidireccional
□ Integración en proyectos de equipo
□ Capacitación adicional si es necesaria
□ Evaluación de adaptación

SEGUIMIENTO CONTINUO
□ Reuniones mensuales primer trimestre
□ Ajustes según necesidad
□ Evaluación de satisfacción
□ Documentación de aprendizajes''',
                'author': 'Accessible Jobs Platform',
                'tags': 'onboarding, integración, plantilla, adaptación',
                'is_accessible': True
            },
            
            # Accesibilidad
            {
                'title': 'Guía de Accesibilidad Web WCAG 2.1',
                'category': 'Accesibilidad en el Lugar de Trabajo',
                'resource_type': 'guide',
                'description': 'Guía práctica para implementar las Pautas de Accesibilidad para el Contenido Web (WCAG 2.1) en tu organización.',
                'content': '''GUÍA WCAG 2.1 - NIVEL AA

PRINCIPIO 1: PERCEPTIBLE
La información debe ser presentable de formas que los usuarios puedan percibir.

1.1 Alternativas de texto
- Proporciona texto alternativo para contenido no textual
- Describe imágenes, íconos y gráficos significativos

1.2 Medios tempodependientes
- Subtítulos para videos y audio
- Transcripciones textuales disponibles

1.3 Adaptable
- El contenido se puede presentar de diferentes maneras
- El orden de lectura es lógico

1.4 Distinguible
- Contraste de color mínimo 4.5:1
- El texto se puede redimensionar hasta 200%
- No uses solo el color para transmitir información

PRINCIPIO 2: OPERABLE
Los componentes de la interfaz deben ser operables.

2.1 Accesible por teclado
- Toda la funcionalidad disponible con teclado
- Orden de tabulación lógico
- Atajos de teclado documentados

2.2 Tiempo suficiente
- Permite extender límites de tiempo
- Opciones para pausar o detener movimiento

2.3 Convulsiones
- Evita contenido que parpadee más de 3 veces por segundo

2.4 Navegable
- Títulos de página descriptivos
- Enlaces con texto significativo
- Múltiples formas de navegar

PRINCIPIO 3: COMPRENSIBLE
La información y el manejo de la interfaz deben ser comprensibles.

3.1 Legible
- Identifica el idioma de la página
- Define términos inusuales

3.2 Predecible
- Navegación consistente
- Comportamiento predecible

3.3 Entrada de datos asistida
- Instrucciones claras
- Prevención y corrección de errores

PRINCIPIO 4: ROBUSTO
El contenido debe ser suficientemente robusto para funcionar con tecnologías asistivas.

4.1 Compatible
- HTML válido y semántico
- Atributos ARIA cuando sea necesario''',
                'author': 'W3C - World Wide Web Consortium',
                'tags': 'accesibilidad, web, WCAG, tecnología',
                'is_featured': True,
                'is_accessible': True
            },
            {
                'title': 'Ajustes Razonables: Ejemplos Prácticos',
                'category': 'Accesibilidad en el Lugar de Trabajo',
                'resource_type': 'document',
                'description': 'Catálogo de ajustes razonables comunes en el lugar de trabajo con ejemplos específicos por tipo de discapacidad.',
                'content': '''CATÁLOGO DE AJUSTES RAZONABLES

DISCAPACIDAD VISUAL
- Software lector de pantalla (JAWS, NVDA)
- Magnificadores de pantalla
- Línea braille
- Documentos en formatos accesibles (TXT, DOCX)
- Iluminación ajustable
- Mobiliario con contraste de color

DISCAPACIDAD AUDITIVA
- Intérprete de lengua de señas
- Subtitulado en tiempo real
- Videoconferencias con subtítulos
- Alarmas visuales
- Amplificadores de sonido
- Aplicaciones de transcripción

DISCAPACIDAD MOTRIZ
- Teclados ergonómicos o adaptados
- Mouse adaptado o trackball
- Software de reconocimiento de voz
- Mobiliario ajustable en altura
- Rampas y pasillos amplios
- Puertas automáticas
- Baños accesibles

DISCAPACIDAD COGNITIVA/PSICOSOCIAL
- Instrucciones escritas paso a paso
- Recordatorios y alarmas
- Entorno de trabajo tranquilo
- Flexibilidad de horarios
- Trabajo remoto parcial o total
- Apoyo de tutor/mentor
- Pausas frecuentes

CONSIDERACIONES GENERALES
- Evaluación individualizada de necesidades
- Proceso de prueba y ajuste
- Revisión periódica de efectividad
- Documentación del proceso
- Capacitación del equipo''',
                'author': 'Ministerio de Trabajo de Colombia',
                'tags': 'ajustes razonables, adaptaciones, accesibilidad, inclusión',
                'is_accessible': True
            },
            
            # Políticas y Normativas
            {
                'title': 'Ley 1618 de 2013: Resumen Ejecutivo',
                'category': 'Políticas y Normativas',
                'resource_type': 'article',
                'description': 'Resumen de las disposiciones clave de la Ley Estatutaria 1618 de 2013 sobre derechos de personas con discapacidad en Colombia.',
                'content': '''LEY 1618 DE 2013 - PUNTOS CLAVE

OBJETO DE LA LEY
Garantizar el ejercicio efectivo de los derechos de las personas con discapacidad mediante la adopción de medidas de inclusión, acción afirmativa y ajustes razonables.

DEFINICIONES IMPORTANTES
- Discapacidad: Deficiencias físicas, mentales, intelectuales o sensoriales que al interactuar con barreras limitan la participación plena y efectiva.
- Ajustes razonables: Modificaciones necesarias para garantizar el goce de derechos sin imponer una carga desproporcionada.
- Acciones afirmativas: Políticas para corregir situaciones de desigualdad histórica.

OBLIGACIONES PARA EMPLEADORES
1. No discriminación en procesos de selección
2. Garantizar accesibilidad en el lugar de trabajo
3. Realizar ajustes razonables necesarios
4. Proporcionar igualdad de oportunidades de desarrollo
5. Implementar políticas de inclusión laboral

SANCIONES POR INCUMPLIMIENTO
- Multas económicas
- Cierre temporal del establecimiento
- Inhabilitación para contratar con el Estado
- Sanciones penales en casos graves

INCENTIVOS PARA EMPRESAS INCLUSIVAS
- Preferencia en contratación pública
- Descuentos tributarios
- Reconocimiento público
- Prelación en trámites''',
                'author': 'Congreso de la República de Colombia',
                'tags': 'ley, normativa, derechos, Colombia, legislación',
                'is_featured': True,
                'is_accessible': True
            },
            
            # Capacitación
            {
                'title': 'Módulo de Sensibilización en Discapacidad',
                'category': 'Capacitación y Sensibilización',
                'resource_type': 'guide',
                'description': 'Contenido para capacitar a equipos de trabajo sobre conciencia de discapacidad, lenguaje inclusivo y mejores prácticas de interacción.',
                'content': '''MÓDULO DE SENSIBILIZACIÓN

OBJETIVO
Desarrollar conciencia sobre discapacidad y habilidades para interactuar respetuosamente con personas con discapacidad.

MÓDULO 1: CONCEPTOS BÁSICOS
- Modelo social vs. modelo médico de discapacidad
- Tipos de discapacidad
- Terminología apropiada
- Mitos y realidades

MÓDULO 2: LENGUAJE INCLUSIVO
✓ Di: "Persona con discapacidad"
✗ Evita: "Discapacitado", "minusválido"

✓ Di: "Persona con discapacidad visual"
✗ Evita: "Ciego", "invidente"

✓ Di: "Persona usuaria de silla de ruedas"
✗ Evita: "Confinado a silla de ruedas"

✓ Di: "Persona con discapacidad auditiva"
✗ Evita: "Sordomudo"

MÓDULO 3: ETIQUETA EN LA INTERACCIÓN
- Dirígete directamente a la persona, no a su acompañante
- Pregunta antes de ayudar
- No toques dispositivos de asistencia sin permiso
- Habla en tono normal (no grites a personas con discapacidad auditiva)
- Describe el entorno a personas con discapacidad visual cuando sea relevante

MÓDULO 4: ACCESIBILIDAD PRÁCTICA
- No bloquees rampas o espacios accesibles
- Mantén pasillos despejados
- Usa lenguaje claro en comunicaciones
- Proporciona información en múltiples formatos

ACTIVIDAD PRÁCTICA
- Role-playing de situaciones comunes
- Ejercicio de empatía (simulación de discapacidad)
- Discusión de casos reales''',
                'author': 'ONU - Convención sobre los Derechos de las Personas con Discapacidad',
                'tags': 'capacitación, sensibilización, lenguaje, etiqueta',
                'is_accessible': True
            },
            
            # Casos de Éxito
            {
                'title': 'Caso de Éxito: Inclusión en Microsoft',
                'category': 'Casos de Éxito',
                'resource_type': 'case_study',
                'description': 'Estudio del programa de inclusión de Microsoft y su impacto en la innovación y cultura organizacional.',
                'content': '''CASO DE ÉXITO: MICROSOFT

CONTEXTO
Microsoft ha sido reconocida como una de las empresas más inclusivas del mundo, con más del 5% de su fuerza laboral compuesta por personas con discapacidad.

ESTRATEGIAS IMPLEMENTADAS

1. HIRING INITIATIVES
- "Autism Hiring Program" desde 2015
- Procesos de entrevista adaptados
- Evaluaciones basadas en habilidades prácticas
- Períodos de prueba extendidos

2. CULTURA ORGANIZACIONAL
- Capacitación obligatoria en inclusión para todos los empleados
- Employee Resource Groups (ERGs) para personas con discapacidad
- Liderazgo visible y comprometido

3. TECNOLOGÍA Y ACCESIBILIDAD
- Inversión en tecnologías asistivas
- Diseño inclusivo desde el inicio
- "Accessibility Checker" en productos Office
- Xbox Adaptive Controller

4. AJUSTES RAZONABLES
- Equipo dedicado de "Workplace Accommodations"
- Proceso simplificado para solicitar ajustes
- Presupuesto específico sin límites arbitrarios

RESULTADOS MEDIBLES
- Retención de empleados: 95% vs. 59% promedio industria
- Incremento en innovación de productos
- Mejora en satisfacción de clientes con discapacidad
- Reducción de 30% en tiempo de desarrollo por diseño inclusivo
- Incremento en ventas de productos accesibles

LECCIONES APRENDIDAS
1. La inclusión impulsa la innovación
2. El compromiso debe venir desde la alta dirección
3. Los ajustes razonables benefician a todos
4. La accesibilidad debe ser parte del diseño, no una adaptación posterior
5. Medir el impacto es fundamental para mejorar

CITAS DESTACADAS
"Cuando diseñamos para personas con discapacidad, creamos productos mejores para todos." - Jenny Lay-Flurrie, Chief Accessibility Officer''',
                'author': 'Microsoft Corporation',
                'tags': 'caso éxito, Microsoft, tecnología, innovación',
                'is_featured': True,
                'is_accessible': True
            },
        ]

        for resource_data in resources_data:
            category = categories[resource_data['category']]
            
            resource, created = BestPracticeResource.objects.get_or_create(
                title=resource_data['title'],
                defaults={
                    'category': category,
                    'resource_type': resource_data['resource_type'],
                    'description': resource_data['description'],
                    'content': resource_data['content'],
                    'author': resource_data.get('author', ''),
                    'tags': resource_data.get('tags', ''),
                    'is_featured': resource_data.get('is_featured', False),
                    'is_accessible': resource_data.get('is_accessible', True),
                    'accessibility_notes': resource_data.get('accessibility_notes', ''),
                    'is_published': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Recurso creado: {resource.title}'))

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Población de biblioteca completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de categorías: {ResourceCategory.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Total de recursos: {BestPracticeResource.objects.count()}'))