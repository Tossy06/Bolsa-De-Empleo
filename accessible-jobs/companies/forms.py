# jobs/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'job_type', 'location', 'is_remote', 
            'description', 'responsibilities', 'requirements',
            'experience_level', 'salary_min', 'salary_max',
            'disability_focus', 'accessibility_features', 
            'benefits', 'application_deadline', 'is_active', 'featured'
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer algunos campos requeridos
        self.fields['responsibilities'].required = True
        self.fields['requirements'].required = True
        
        # Personalizar labels y help_text
        self.fields['is_remote'].label = "¿Es trabajo remoto o híbrido?"
        self.fields['featured'].label = "Destacar esta oferta"
        self.fields['featured'].help_text = "Las ofertas destacadas aparecen primero en los resultados"
        
        # Agregar clases CSS adicionales
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs.update({'class': f'{current_classes} mb-2'.strip()})

    def clean(self):
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
        title = self.cleaned_data.get('title')
        if title and len(title) < 10:
            raise ValidationError('El título debe tener al menos 10 caracteres')
        return title