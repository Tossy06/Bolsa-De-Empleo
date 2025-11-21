# messaging/forms.py
from django import forms
from .models import Conversation, Message


class StartConversationForm(forms.ModelForm):
    """
    Formulario para iniciar una nueva conversación
    """
    recipient = forms.ModelChoiceField(
        queryset=None,
        label='Destinatario',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Seleccione el destinatario'
        })
    )
    
    message_content = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Escriba su mensaje aquí...',
            'aria-label': 'Contenido del mensaje'
        })
    )
    
    class Meta:
        model = Conversation
        fields = ['subject', 'job_title']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Consulta sobre oferta de empleo',
                'aria-label': 'Asunto de la conversación'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Desarrollador Frontend (opcional)',
                'aria-label': 'Oferta relacionada (opcional)'
            }),
        }
        labels = {
            'subject': 'Asunto',
            'job_title': 'Oferta relacionada (opcional)',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar queryset del destinatario según tipo de usuario
        if user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if user.user_type == 'candidate':
                # Candidatos pueden enviar mensajes a empresas
                self.fields['recipient'].queryset = User.objects.filter(user_type='company')
            elif user.user_type == 'company':
                # Empresas pueden enviar mensajes a candidatos
                self.fields['recipient'].queryset = User.objects.filter(user_type='candidate')
            else:
                self.fields['recipient'].queryset = User.objects.none()


class MessageForm(forms.ModelForm):
    """
    Formulario para enviar un mensaje en una conversación existente
    """
    class Meta:
        model = Message
        fields = ['content', 'attachment', 'attachment_alt_text']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escriba su mensaje aquí...',
                'aria-label': 'Contenido del mensaje',
                'required': True
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'aria-label': 'Archivo adjunto (opcional)',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
            }),
            'attachment_alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del archivo (importante para accesibilidad)',
                'aria-label': 'Descripción del archivo adjunto'
            }),
        }
        labels = {
            'content': 'Mensaje',
            'attachment': 'Archivo adjunto (opcional)',
            'attachment_alt_text': 'Descripción del archivo',
        }
        help_texts = {
            'attachment': 'Formatos permitidos: PDF, DOC, DOCX, JPG, PNG, TXT. Máximo 5MB.',
            'attachment_alt_text': 'Proporcione una descripción del archivo para usuarios con lectores de pantalla.',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        attachment = cleaned_data.get('attachment')
        attachment_alt_text = cleaned_data.get('attachment_alt_text')
        
        # Si hay archivo adjunto, el texto alternativo es obligatorio
        if attachment and not attachment_alt_text:
            raise forms.ValidationError(
                'Por favor proporcione una descripción del archivo adjunto para accesibilidad.'
            )
        
        return cleaned_data


class SearchConversationsForm(forms.Form):
    """
    Formulario para buscar conversaciones
    """
    search = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por asunto o participante...',
            'aria-label': 'Buscar conversaciones'
        })
    )
    
    show_archived = forms.BooleanField(
        required=False,
        label='Mostrar archivadas',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )