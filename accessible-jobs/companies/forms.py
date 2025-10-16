# jobs/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Job, ComplianceStatus

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'job_type', 'location', 'is_remote', 
            'description', 'responsibilities', 'requirements',
            'experience_level', 'salary_min', 'salary_max',
            'disability_focus', 'accessibility_features', 
            'benefits', 'application_deadline', 'is_active', 'featured',
            #CAMPOS OBLIGATORIOS (Ley 1618)
            'reasonable_accommodations',
            'workplace_accessibility', 
            'non_discrimination_statement'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Desarrollador Frontend Accesible'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bogotá, Colombia'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe brevemente el puesto y la empresa...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Lista las principales responsabilidades del puesto...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Educación, experiencia, habilidades técnicas...'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2000000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3500000'
            }),
            'disability_focus': forms.Select(attrs={
                'class': 'form-select'
            }),
            'accessibility_features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe las adaptaciones disponibles: software accesible, ajustes ergonómicos, etc.'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Seguro médico, capacitaciones, flexibilidad horaria...'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            # WIDGETS PARA CAMPOS LEGALES
            'reasonable_accommodations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ej: Horarios flexibles, trabajo remoto, adaptaciones tecnológicas (lectores de pantalla, software de reconocimiento de voz), ajustes ergonómicos...'
            }),
            'workplace_accessibility': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ej: Rampas de acceso, ascensores, baños adaptados, estacionamiento preferencial, iluminación adecuada, señalización táctil...'
            }),
            'non_discrimination_statement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ej: Nuestra empresa garantiza igualdad de oportunidades y no discrimina por razón de discapacidad. Nos comprometemos a realizar ajustes razonables.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer campos requeridos
        self.fields['responsibilities'].required = True
        self.fields['requirements'].required = True
        
        # CAMPOS LEGALES OBLIGATORIOS
        self.fields['reasonable_accommodations'].required = True
        self.fields['workplace_accessibility'].required = True
        self.fields['non_discrimination_statement'].required = True
        
        # Personalizar labels y help_text
        self.fields['is_remote'].label = "¿Es trabajo remoto o híbrido?"
        self.fields['featured'].label = "Destacar esta oferta"
        self.fields['featured'].help_text = "Las ofertas destacadas aparecen primero en los resultados"
        
        # MENSAJES DE ERROR PERSONALIZADOS
        self.fields['reasonable_accommodations'].error_messages = {
            'required': 'Debe especificar los ajustes razonables disponibles (requerido por Ley 1618)'
        }
        self.fields['workplace_accessibility'].error_messages = {
            'required': 'Debe describir las condiciones de accesibilidad del lugar de trabajo'
        }
        self.fields['non_discrimination_statement'].error_messages = {
            'required': 'Debe incluir una declaración explícita de no discriminación'
        }
        
        # Agregar clases CSS adicionales
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs.update({'class': f'{current_classes} mb-2'.strip()})

    def clean(self):
        """
        Validación global del formulario
        """
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        # Validar rango de salarios
        if salary_min and salary_max:
            if salary_min >= salary_max:
                raise ValidationError({
                    'salary_max': 'El salario máximo debe ser mayor al salario mínimo'
                })
        
        return cleaned_data

    def clean_title(self):
        """Validar título"""
        title = self.cleaned_data.get('title')
        if title and len(title) < 10:
            raise ValidationError('El título debe tener al menos 10 caracteres')
        return title
    
    # VALIDACIONES PARA CAMPOS LEGALES
    
    def clean_reasonable_accommodations(self):
        """
        Valida que se especifiquen ajustes razonables de manera sustancial
        """
        value = self.cleaned_data.get('reasonable_accommodations', '').strip()
        
        if not value:
            raise ValidationError(
                'Este campo es obligatorio según la Ley 1618 de 2013. '
                'Debe especificar los ajustes razonables que puede ofrecer.'
            )
        
        if len(value) < 50:
            raise ValidationError(
                'La descripción de ajustes razonables debe ser más detallada '
                '(mínimo 50 caracteres). Incluya ejemplos específicos.'
            )
        
        # Validar que no sean frases genéricas o copypaste
        generic_phrases = ['ninguno', 'n/a', 'no aplica', 'ninguna']
        if any(phrase in value.lower() for phrase in generic_phrases):
            raise ValidationError(
                'Debe especificar ajustes razonables concretos. '
                'No se aceptan respuestas genéricas como "ninguno" o "N/A".'
            )
        
        return value
    
    def clean_workplace_accessibility(self):
        """
        Valida que se describan condiciones de accesibilidad
        """
        value = self.cleaned_data.get('workplace_accessibility', '').strip()
        
        if not value:
            raise ValidationError(
                'Este campo es obligatorio. Debe describir las características '
                'de accesibilidad física y tecnológica del lugar de trabajo.'
            )
        
        if len(value) < 50:
            raise ValidationError(
                'La descripción de accesibilidad debe ser más detallada '
                '(mínimo 50 caracteres). Incluya características específicas.'
            )
        
        generic_phrases = ['ninguno', 'n/a', 'no aplica', 'ninguna']
        if any(phrase in value.lower() for phrase in generic_phrases):
            raise ValidationError(
                'Debe especificar características de accesibilidad concretas. '
                'Si el lugar no es totalmente accesible, indique qué mejoras planea realizar.'
            )
        
        return value
    
    def clean_non_discrimination_statement(self):
        """
        Valida que exista una declaración explícita de no discriminación
        """
        value = self.cleaned_data.get('non_discrimination_statement', '').strip()
        
        if not value:
            raise ValidationError(
                'Debe incluir una declaración explícita de políticas de inclusión '
                'y no discriminación según la Convención de la ONU.'
            )
        
        if len(value) < 40:
            raise ValidationError(
                'La declaración debe ser más completa (mínimo 40 caracteres). '
                'Incluya un compromiso claro de no discriminación.'
            )
        
        # Verificar palabras clave importantes
        keywords = ['igualdad', 'discrimin', 'inclusión', 'oportunidad', 'compromet']
        has_keywords = any(keyword in value.lower() for keyword in keywords)
        
        if not has_keywords:
            raise ValidationError(
                'La declaración debe incluir términos como "igualdad", "no discriminación", '
                '"inclusión" o "compromiso" para ser válida.'
            )
        
        return value
    
    def save(self, commit=True):
        """
        Override del save para marcar automáticamente como pendiente de revisión
        """
        instance = super().save(commit=False)
        
        # VALIDAR CUMPLIMIENTO LEGAL Y CAMBIAR ESTADO
        is_compliant, missing_fields = instance.validate_legal_compliance()
        
        if not is_compliant:
            # Si faltan campos, marcar como pendiente de revisión
            instance.compliance_status = ComplianceStatus.PENDING_REVIEW
        else:
            # Si tiene todos los campos, también marcar como pendiente
            # (el admin debe aprobar manualmente)
            instance.compliance_status = ComplianceStatus.PENDING_REVIEW
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance