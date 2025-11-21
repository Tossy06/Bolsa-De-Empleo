# complaints/forms.py
from django import forms
from .models import Complaint, ComplaintComment
from django.core.validators import FileExtensionValidator


class ComplaintForm(forms.ModelForm):
    """
    Formulario para presentar una denuncia
    """
    
    # Campo para confirmar que no es anónima
    provide_contact_info = forms.BooleanField(
        required=False,
        label='Deseo proporcionar mis datos de contacto (opcional)',
        help_text='Si marca esta opción, podremos contactarle para darle seguimiento a su denuncia.'
    )
    
    # Campos de contacto opcionales
    contact_name = forms.CharField(
        max_length=200,
        required=False,
        label='Nombre completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre completo'
        })
    )
    
    contact_email = forms.EmailField(
        required=False,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono (opcional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 300 123 4567'
        })
    )
    
    class Meta:
        model = Complaint
        fields = [
            'complaint_type',
            'subject',
            'description',
            'company_name',
            'job_posting_url',
            'evidence_file1',
            'evidence_file2',
            'evidence_file3',
        ]
        widgets = {
            'complaint_type': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Seleccione el tipo de denuncia'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Oferta discriminatoria por discapacidad',
                'aria-label': 'Asunto de la denuncia'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describa los hechos de manera detallada. Incluya fechas, nombres, circunstancias y cualquier información relevante.',
                'aria-label': 'Descripción detallada de la denuncia'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Empresa ABC S.A.S.',
                'aria-label': 'Nombre de la empresa'
            }),
            'job_posting_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/oferta',
                'aria-label': 'URL de la oferta de empleo'
            }),
            'evidence_file1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
                'aria-label': 'Archivo de evidencia 1'
            }),
            'evidence_file2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
                'aria-label': 'Archivo de evidencia 2'
            }),
            'evidence_file3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
                'aria-label': 'Archivo de evidencia 3'
            }),
        }
        labels = {
            'complaint_type': 'Tipo de denuncia',
            'subject': 'Asunto',
            'description': 'Descripción detallada',
            'company_name': 'Nombre de la empresa',
            'job_posting_url': 'URL de la oferta (opcional)',
            'evidence_file1': 'Evidencia 1 (opcional)',
            'evidence_file2': 'Evidencia 2 (opcional)',
            'evidence_file3': 'Evidencia 3 (opcional)',
        }
        help_texts = {
            'description': 'Mínimo 50 caracteres. Sea lo más específico posible.',
            'evidence_file1': 'Formatos permitidos: PDF, JPG, PNG, DOC, DOCX. Máximo 5MB.',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        provide_contact = cleaned_data.get('provide_contact_info')
        
        # Si el usuario quiere proporcionar datos, validar que al menos el email esté presente
        if provide_contact:
            contact_email = cleaned_data.get('contact_email')
            if not contact_email:
                raise forms.ValidationError(
                    'Si desea proporcionar datos de contacto, debe incluir al menos un correo electrónico.'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        complaint = super().save(commit=False)
        
        # Establecer si es anónima
        provide_contact = self.cleaned_data.get('provide_contact_info')
        complaint.is_anonymous = not provide_contact
        
        # Guardar datos de contacto si se proporcionaron
        if provide_contact:
            complaint.complainant_name = self.cleaned_data.get('contact_name', '')
            complaint.complainant_email = self.cleaned_data.get('contact_email', '')
            complaint.complainant_phone = self.cleaned_data.get('contact_phone', '')
        
        if commit:
            complaint.save()
        
        return complaint


class TrackComplaintForm(forms.Form):
    """
    Formulario para rastrear una denuncia por código
    """
    tracking_code = forms.CharField(
        max_length=12,
        label='Código de seguimiento',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej: ABC123XYZ789',
            'aria-label': 'Ingrese su código de seguimiento'
        }),
        help_text='Ingrese el código de 12 caracteres que recibió al presentar su denuncia.'
    )
    
    def clean_tracking_code(self):
        code = self.cleaned_data.get('tracking_code', '').strip().upper()
        
        if len(code) != 12:
            raise forms.ValidationError('El código de seguimiento debe tener exactamente 12 caracteres.')
        
        # Verificar que existe
        if not Complaint.objects.filter(tracking_code=code).exists():
            raise forms.ValidationError('No se encontró ninguna denuncia con este código.')
        
        return code


class ComplaintCommentForm(forms.ModelForm):
    """
    Formulario para agregar comentarios a una denuncia (solo admins)
    """
    class Meta:
        model = ComplaintComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Agregue un comentario sobre esta denuncia...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'comment': 'Comentario',
            'is_internal': 'Comentario interno (solo visible para administradores)'
        }


class ComplaintStatusUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar el estado de una denuncia (solo admins)
    """
    reason = forms.CharField(
        required=False,
        label='Razón del cambio',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explique brevemente la razón del cambio de estado...'
        })
    )
    
    class Meta:
        model = Complaint
        fields = ['status', 'priority', 'assigned_to', 'admin_response']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Respuesta oficial para el denunciante...'
            })
        }