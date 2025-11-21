# interviews/forms.py
from django import forms
from .models import Interview, InterviewRescheduleRequest
from django.utils import timezone
from datetime import datetime, timedelta


class ScheduleInterviewForm(forms.ModelForm):
    """
    Formulario para programar una nueva entrevista
    """
    class Meta:
        model = Interview
        fields = [
            'candidate', 'job_title', 'title', 'description',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'interview_type', 'platform', 'meeting_url', 'meeting_id', 'meeting_password',
            'location_address', 'location_instructions',
            'requires_sign_language_interpreter', 'requires_accessible_location',
            'requires_screen_reader_support', 'requires_captioning',
            'other_accessibility_needs', 'company_notes'
        ]
        widgets = {
            'candidate': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Seleccione el candidato'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Desarrollador Frontend Senior',
                'aria-label': 'Título del puesto'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Primera entrevista técnica',
                'aria-label': 'Título de la entrevista'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa los temas a tratar, expectativas, etc.',
                'aria-label': 'Descripción de la entrevista'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'aria-label': 'Fecha de la entrevista'
            }),
            'scheduled_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'aria-label': 'Hora de la entrevista'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '15',
                'max': '240',
                'step': '15',
                'aria-label': 'Duración en minutos'
            }),
            'interview_type': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Tipo de entrevista'
            }),
            'platform': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Plataforma de reunión'
            }),
            'meeting_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/123456789',
                'aria-label': 'URL de la reunión'
            }),
            'meeting_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 456 789',
                'aria-label': 'ID de la reunión'
            }),
            'meeting_password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña opcional',
                'aria-label': 'Contraseña de la reunión'
            }),
            'location_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa para entrevistas presenciales',
                'aria-label': 'Dirección'
            }),
            'location_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instrucciones sobre cómo llegar, piso, oficina, etc.',
                'aria-label': 'Instrucciones de ubicación'
            }),
            'requires_sign_language_interpreter': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'requires_accessible_location': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'requires_screen_reader_support': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'requires_captioning': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'other_accessibility_needs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa cualquier otra necesidad de accesibilidad',
                'aria-label': 'Otras necesidades de accesibilidad'
            }),
            'company_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas internas (no visibles para el candidato)',
                'aria-label': 'Notas de la empresa'
            }),
        }
        labels = {
            'candidate': 'Candidato',
            'job_title': 'Título del puesto',
            'title': 'Título de la entrevista',
            'description': 'Descripción',
            'scheduled_date': 'Fecha',
            'scheduled_time': 'Hora',
            'duration_minutes': 'Duración (minutos)',
            'interview_type': 'Tipo de entrevista',
            'platform': 'Plataforma de reunión',
            'meeting_url': 'URL de la reunión',
            'meeting_id': 'ID de la reunión',
            'meeting_password': 'Contraseña',
            'location_address': 'Dirección',
            'location_instructions': 'Instrucciones de ubicación',
            'requires_sign_language_interpreter': 'Requiere intérprete de lengua de señas',
            'requires_accessible_location': 'Requiere ubicación accesible',
            'requires_screen_reader_support': 'Requiere soporte para lector de pantalla',
            'requires_captioning': 'Requiere subtítulos en tiempo real',
            'other_accessibility_needs': 'Otras necesidades de accesibilidad',
            'company_notes': 'Notas internas',
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar candidatos disponibles
        if company:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.fields['candidate'].queryset = User.objects.filter(user_type='candidate')
    
    def clean_scheduled_date(self):
        """Validar que la fecha sea futura"""
        date = self.cleaned_data.get('scheduled_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('La fecha de la entrevista debe ser futura.')
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        interview_type = cleaned_data.get('interview_type')
        platform = cleaned_data.get('platform')
        meeting_url = cleaned_data.get('meeting_url')
        location_address = cleaned_data.get('location_address')
        
        # Validar campos según tipo de entrevista
        if interview_type == 'online':
            if not platform:
                self.add_error('platform', 'Debe seleccionar una plataforma para entrevistas en línea.')
            if not meeting_url:
                self.add_error('meeting_url', 'Debe proporcionar la URL de la reunión.')
        
        if interview_type == 'in_person':
            if not location_address:
                self.add_error('location_address', 'Debe proporcionar una dirección para entrevistas presenciales.')
        
        return cleaned_data


class ConfirmInterviewForm(forms.Form):
    """
    Formulario para confirmar una entrevista (candidato)
    """
    confirm = forms.BooleanField(
        required=True,
        label='Confirmo mi asistencia a esta entrevista',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    notes = forms.CharField(
        required=False,
        label='Notas o comentarios (opcional)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Añada cualquier comentario o pregunta',
            'aria-label': 'Notas o comentarios'
        })
    )


class CancelInterviewForm(forms.Form):
    """
    Formulario para cancelar una entrevista
    """
    reason = forms.CharField(
        required=True,
        label='Razón de cancelación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Por favor explique la razón de la cancelación',
            'aria-label': 'Razón de cancelación'
        })
    )


class RescheduleInterviewForm(forms.ModelForm):
    """
    Formulario para solicitar reprogramación
    """
    class Meta:
        model = InterviewRescheduleRequest
        fields = ['reason', 'proposed_date', 'proposed_time']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explique la razón de la reprogramación',
                'aria-label': 'Razón de reprogramación'
            }),
            'proposed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'aria-label': 'Nueva fecha propuesta'
            }),
            'proposed_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'aria-label': 'Nueva hora propuesta'
            }),
        }
        labels = {
            'reason': 'Razón de la reprogramación',
            'proposed_date': 'Nueva fecha propuesta',
            'proposed_time': 'Nueva hora propuesta',
        }
    
    def clean_proposed_date(self):
        """Validar que la fecha propuesta sea futura"""
        date = self.cleaned_data.get('proposed_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('La fecha propuesta debe ser futura.')
        return date


class InterviewFeedbackForm(forms.Form):
    """
    Formulario para feedback post-entrevista
    """
    feedback = forms.CharField(
        required=True,
        label='Comentarios sobre la entrevista',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Comparta sus comentarios sobre cómo fue la entrevista',
            'aria-label': 'Comentarios'
        })
    )
    
    rating = forms.ChoiceField(
        required=False,
        label='Calificación (opcional)',
        choices=[
            ('', 'Sin calificar'),
            ('1', '⭐ - Muy insatisfecho'),
            ('2', '⭐⭐ - Insatisfecho'),
            ('3', '⭐⭐⭐ - Neutral'),
            ('4', '⭐⭐⭐⭐ - Satisfecho'),
            ('5', '⭐⭐⭐⭐⭐ - Muy satisfecho'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Calificación'
        })
    )


class InterviewSearchForm(forms.Form):
    """
    Formulario para buscar entrevistas
    """
    search = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por candidato, título...',
            'aria-label': 'Buscar entrevistas'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos')] + Interview.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Filtrar por estado'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        label='Desde',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'aria-label': 'Fecha desde'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        label='Hasta',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'aria-label': 'Fecha hasta'
        })
    )