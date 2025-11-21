# training/management/commands/populate_training_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from training.models import SocialSkillsCourse, CourseLesson


class Command(BaseCommand):
    help = 'Puebla la base de datos con cursos ficticios de habilidades sociales'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando población de cursos...'))

        # Limpiar datos anteriores (opcional)
        # SocialSkillsCourse.objects.all().delete()

        # CURSO 1: Comunicación Efectiva
        course1, created = SocialSkillsCourse.objects.get_or_create(
            slug='comunicacion-efectiva-en-el-trabajo',
            defaults={
                'title': 'Comunicación Efectiva en el Trabajo',
                'description': 'Aprende técnicas de comunicación verbal y no verbal para mejorar tus relaciones laborales. Este curso te enseñará a expresar ideas claramente, escuchar activamente y adaptar tu mensaje a diferentes audiencias.',
                'category': 'communication',
                'difficulty': 'beginner',
                'duration_hours': 3,
                'is_active': True,
                'order': 1,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Curso creado: {course1.title}'))
            
            # Lecciones del curso 1
            CourseLesson.objects.create(
                course=course1,
                title='Introducción a la Comunicación Efectiva',
                content_type='video',
                content='En esta lección aprenderás los fundamentos de la comunicación efectiva. Conocerás los elementos clave: emisor, receptor, mensaje, canal y retroalimentación. También exploraremos las barreras comunes que impiden una buena comunicación.',
                video_duration_minutes=15,
                transcript='Bienvenidos al curso de Comunicación Efectiva. La comunicación es una habilidad fundamental en cualquier entorno laboral...',
                order=1,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course1,
                title='Escucha Activa: Más Allá de Oír',
                content_type='text',
                content='La escucha activa implica prestar atención completa al interlocutor, comprender su mensaje y responder apropiadamente. Técnicas: mantener contacto visual, asentir, parafrasear y hacer preguntas clarificadoras.',
                order=2,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course1,
                title='Comunicación No Verbal',
                content_type='video',
                content='El lenguaje corporal representa más del 50% de la comunicación. Aprende a interpretar gestos, posturas y expresiones faciales. También descubrirás cómo tu propio lenguaje corporal afecta el mensaje que transmites.',
                video_duration_minutes=20,
                transcript='La comunicación no verbal incluye gestos, expresiones faciales, postura corporal...',
                order=3,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course1,
                title='Cuestionario Final',
                content_type='quiz',
                content='Pon a prueba tus conocimientos sobre comunicación efectiva con este cuestionario de 10 preguntas.',
                order=4,
                is_mandatory=True
            )

        # CURSO 2: Trabajo en Equipo
        course2, created = SocialSkillsCourse.objects.get_or_create(
            slug='fundamentos-del-trabajo-en-equipo',
            defaults={
                'title': 'Fundamentos del Trabajo en Equipo',
                'description': 'Desarrolla habilidades para colaborar efectivamente con otros. Aprende sobre roles de equipo, resolución de conflictos y cómo contribuir al logro de objetivos comunes.',
                'category': 'teamwork',
                'difficulty': 'beginner',
                'duration_hours': 4,
                'is_active': True,
                'order': 2,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Curso creado: {course2.title}'))
            
            CourseLesson.objects.create(
                course=course2,
                title='¿Qué es el Trabajo en Equipo?',
                content_type='video',
                content='Un equipo es más que un grupo de personas. Requiere objetivos compartidos, interdependencia y compromiso mutuo. Exploraremos las características de equipos exitosos.',
                video_duration_minutes=18,
                transcript='El trabajo en equipo es una competencia esencial en el mundo laboral moderno...',
                order=1,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course2,
                title='Roles en un Equipo',
                content_type='text',
                content='Según Meredith Belbin, existen 9 roles en un equipo: Coordinador, Impulsor, Cerebro, Investigador, Cohesionador, Implementador, Finalizador, Especialista y Monitor Evaluador. Cada rol aporta fortalezas únicas.',
                order=2,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course2,
                title='Resolución de Conflictos',
                content_type='video',
                content='Los conflictos son inevitables en cualquier equipo. Aprende estrategias para abordarlos constructivamente: comunicación abierta, búsqueda de soluciones ganar-ganar y mediación.',
                video_duration_minutes=25,
                transcript='Conflicto no significa fracaso. Cuando se maneja adecuadamente...',
                order=3,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course2,
                title='Ejercicio Práctico: Análisis de Caso',
                content_type='interactive',
                content='Analiza un caso real de conflicto en un equipo de trabajo. Identifica los problemas, propone soluciones y reflexiona sobre tu propio estilo de colaboración.',
                order=4,
                is_mandatory=False
            )

        # CURSO 3: Resolución de Problemas
        course3, created = SocialSkillsCourse.objects.get_or_create(
            slug='resolucion-creativa-de-problemas',
            defaults={
                'title': 'Resolución Creativa de Problemas',
                'description': 'Desarrolla pensamiento crítico y creatividad para enfrentar desafíos laborales. Aprende metodologías como Design Thinking y el método de los 5 porqués.',
                'category': 'problem_solving',
                'difficulty': 'intermediate',
                'duration_hours': 5,
                'is_active': True,
                'order': 3,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Curso creado: {course3.title}'))
            
            CourseLesson.objects.create(
                course=course3,
                title='Introducción a la Resolución de Problemas',
                content_type='video',
                content='La resolución de problemas es un proceso sistemático que incluye: identificación, análisis, generación de alternativas, evaluación e implementación de soluciones.',
                video_duration_minutes=20,
                transcript='Resolver problemas efectivamente es una habilidad que se puede aprender y perfeccionar...',
                order=1,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course3,
                title='El Método de los 5 Porqués',
                content_type='text',
                content='Desarrollado por Toyota, este método ayuda a identificar la causa raíz de un problema preguntando "¿por qué?" cinco veces consecutivas. Ejemplo: Problema: La entrega llegó tarde. ¿Por qué? Porque el camión se retrasó...',
                order=2,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course3,
                title='Design Thinking para Problemas Complejos',
                content_type='video',
                content='Design Thinking es un enfoque centrado en el usuario con 5 fases: Empatizar, Definir, Idear, Prototipar y Testear. Ideal para problemas ambiguos o mal definidos.',
                video_duration_minutes=30,
                transcript='Design Thinking nació en Stanford y se ha convertido en una metodología global...',
                order=3,
                is_mandatory=True
            )

        # CURSO 4: Gestión del Tiempo
        course4, created = SocialSkillsCourse.objects.get_or_create(
            slug='gestion-efectiva-del-tiempo',
            defaults={
                'title': 'Gestión Efectiva del Tiempo',
                'description': 'Aprende a priorizar tareas, evitar la procrastinación y maximizar tu productividad. Descubre técnicas como Pomodoro, Matriz de Eisenhower y GTD (Getting Things Done).',
                'category': 'time_management',
                'difficulty': 'beginner',
                'duration_hours': 3,
                'is_active': True,
                'order': 4,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Curso creado: {course4.title}'))
            
            CourseLesson.objects.create(
                course=course4,
                title='Por Qué es Importante Gestionar el Tiempo',
                content_type='video',
                content='El tiempo es el recurso más valioso y no renovable. Una buena gestión reduce el estrés, aumenta la productividad y mejora el equilibrio vida-trabajo.',
                video_duration_minutes=12,
                order=1,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course4,
                title='La Matriz de Eisenhower',
                content_type='text',
                content='Clasifica tareas en cuatro cuadrantes: 1) Urgente e Importante (hacer ya), 2) Importante pero no urgente (planificar), 3) Urgente pero no importante (delegar), 4) Ni urgente ni importante (eliminar).',
                order=2,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course4,
                title='Técnica Pomodoro',
                content_type='video',
                content='Trabaja en bloques de 25 minutos (pomodoros) seguidos de 5 minutos de descanso. Cada 4 pomodoros, toma un descanso más largo de 15-30 minutos.',
                video_duration_minutes=15,
                order=3,
                is_mandatory=True
            )

        # CURSO 5: Liderazgo
        course5, created = SocialSkillsCourse.objects.get_or_create(
            slug='liderazgo-inclusivo',
            defaults={
                'title': 'Liderazgo Inclusivo',
                'description': 'Desarrolla habilidades de liderazgo que valoran la diversidad y promueven la inclusión. Aprende a motivar equipos, delegar efectivamente y crear ambientes de trabajo positivos.',
                'category': 'leadership',
                'difficulty': 'advanced',
                'duration_hours': 6,
                'is_active': True,
                'order': 5,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Curso creado: {course5.title}'))
            
            CourseLesson.objects.create(
                course=course5,
                title='¿Qué es el Liderazgo Inclusivo?',
                content_type='video',
                content='El liderazgo inclusivo reconoce y valora las diferencias individuales. Los líderes inclusivos crean ambientes donde todos se sienten respetados, escuchados y valorados.',
                video_duration_minutes=22,
                order=1,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course5,
                title='Estilos de Liderazgo',
                content_type='text',
                content='Existen múltiples estilos: Autocrático, Democrático, Laissez-faire, Transformacional, Transaccional y Situacional. El líder efectivo adapta su estilo según el contexto y las personas.',
                order=2,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course5,
                title='Inteligencia Emocional en el Liderazgo',
                content_type='video',
                content='Daniel Goleman identifica 5 componentes: autoconciencia, autorregulación, motivación, empatía y habilidades sociales. Los líderes emocionalmente inteligentes conectan mejor con sus equipos.',
                video_duration_minutes=28,
                order=3,
                is_mandatory=True
            )

        # CURSO 6: Resolución de Conflictos
        course6, created = SocialSkillsCourse.objects.get_or_create(
            slug='resolucion-constructiva-de-conflictos',
            defaults={
                'title': 'Resolución Constructiva de Conflictos',
                'description': 'Aprende a manejar desacuerdos y tensiones de forma constructiva. Desarrolla habilidades de negociación, mediación y comunicación asertiva.',
                'category': 'conflict_resolution',
                'difficulty': 'intermediate',
                'duration_hours': 4,
                'is_active': True,
                'order': 6,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Curso creado: {course6.title}'))
            
            CourseLesson.objects.create(
                course=course6,
                title='Tipos de Conflictos Laborales',
                content_type='text',
                content='Conflictos intrapersonales (internos), interpersonales (entre personas), intragrupales (dentro de un equipo) e intergrupales (entre equipos). Cada tipo requiere estrategias específicas.',
                order=1,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course6,
                title='Comunicación Asertiva',
                content_type='video',
                content='La asertividad es expresar opiniones y necesidades de forma clara y respetuosa. Técnica DESC: Describir, Expresar, Sugerir, Consecuencias.',
                video_duration_minutes=18,
                order=2,
                is_mandatory=True
            )
            
            CourseLesson.objects.create(
                course=course6,
                title='Negociación Ganar-Ganar',
                content_type='video',
                content='En lugar de ver el conflicto como una competencia, busca soluciones que beneficien a ambas partes. Identifica intereses subyacentes, no solo posiciones.',
                video_duration_minutes=25,
                order=3,
                is_mandatory=True
            )

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Población de cursos completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de cursos creados: {SocialSkillsCourse.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Total de lecciones creadas: {CourseLesson.objects.count()}'))