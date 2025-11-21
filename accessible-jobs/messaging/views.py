# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Max
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from .models import Conversation, Message, MessageNotification
from .forms import StartConversationForm, MessageForm, SearchConversationsForm


@login_required
def inbox_view(request):
    """
    Bandeja de entrada de mensajes
    """
    # Obtener conversaciones del usuario
    if request.user.user_type == 'candidate':
        conversations = Conversation.objects.filter(
            candidate=request.user
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(
                    messages__sender=request.user.company_conversations.first().company if request.user.company_conversations.exists() else None,
                    messages__is_read=False
                )
            )
        )
    elif request.user.user_type == 'company':
        conversations = Conversation.objects.filter(
            company=request.user
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(
                    messages__sender=request.user.candidate_conversations.first().candidate if request.user.candidate_conversations.exists() else None,
                    messages__is_read=False
                )
            )
        )
    else:
        conversations = Conversation.objects.none()
    
    # Filtros
    search_form = SearchConversationsForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search', '')
        show_archived = search_form.cleaned_data.get('show_archived', False)
        
        if search_query:
            conversations = conversations.filter(
                Q(subject__icontains=search_query) |
                Q(job_title__icontains=search_query) |
                Q(candidate__first_name__icontains=search_query) |
                Q(candidate__last_name__icontains=search_query) |
                Q(company__first_name__icontains=search_query) |
                Q(company__last_name__icontains=search_query)
            )
        
        if not show_archived:
            if request.user.user_type == 'candidate':
                conversations = conversations.filter(is_archived_by_candidate=False)
            else:
                conversations = conversations.filter(is_archived_by_company=False)
    
    # Ordenar por última actualización
    conversations = conversations.order_by('-updated_at')
    
    # Paginación
    paginator = Paginator(conversations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contar mensajes no leídos totales
    total_unread = sum([conv.get_unread_count_for_candidate() if request.user.user_type == 'candidate' else conv.get_unread_count_for_company() for conv in conversations])
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_unread': total_unread,
    }
    
    return render(request, 'messaging/inbox.html', context)


@login_required
def start_conversation_view(request):
    """
    Iniciar una nueva conversación
    """
    if request.method == 'POST':
        form = StartConversationForm(request.POST, user=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            job_title = form.cleaned_data.get('job_title', '')
            message_content = form.cleaned_data['message_content']
            
            # Verificar si ya existe una conversación similar
            if request.user.user_type == 'candidate':
                existing_conv = Conversation.objects.filter(
                    candidate=request.user,
                    company=recipient,
                    subject=subject
                ).first()
            else:
                existing_conv = Conversation.objects.filter(
                    candidate=recipient,
                    company=request.user,
                    subject=subject
                ).first()
            
            if existing_conv:
                messages.warning(request, 'Ya existe una conversación con este asunto. Se ha redirigido a ella.')
                return redirect('messaging:conversation_detail', pk=existing_conv.pk)
            
            # Crear nueva conversación
            if request.user.user_type == 'candidate':
                conversation = Conversation.objects.create(
                    candidate=request.user,
                    company=recipient,
                    subject=subject,
                    job_title=job_title
                )
            else:
                conversation = Conversation.objects.create(
                    candidate=recipient,
                    company=request.user,
                    subject=subject,
                    job_title=job_title
                )
            
            # Crear primer mensaje
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_content
            )
            
            # Enviar notificación
            send_message_notification(message)
            
            messages.success(request, 'Conversación iniciada correctamente.')
            return redirect('messaging:conversation_detail', pk=conversation.pk)
    else:
        form = StartConversationForm(user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'messaging/start_conversation.html', context)


@login_required
def conversation_detail_view(request, pk):
    """
    Vista detallada de una conversación
    """
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Verificar que el usuario sea parte de la conversación
    if request.user not in [conversation.candidate, conversation.company]:
        messages.error(request, 'No tienes permiso para ver esta conversación.')
        return redirect('messaging:inbox')
    
    # Marcar conversación como leída
    conversation.mark_as_read_by_user(request.user)
    
    # Marcar mensajes como leídos
    unread_messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    for msg in unread_messages:
        msg.mark_as_read()
    
    # Procesar envío de nuevo mensaje
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Enviar notificación
            send_message_notification(message)
            
            messages.success(request, 'Mensaje enviado correctamente.')
            return redirect('messaging:conversation_detail', pk=conversation.pk)
    else:
        form = MessageForm()
    
    # Obtener todos los mensajes
    conversation_messages = conversation.messages.all()
    
    context = {
        'conversation': conversation,
        'messages': conversation_messages,
        'form': form,
        'other_participant': conversation.get_other_participant(request.user),
    }
    
    return render(request, 'messaging/conversation_detail.html', context)


@login_required
def archive_conversation_view(request, pk):
    """
    Archivar una conversación
    """
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Verificar permisos
    if request.user not in [conversation.candidate, conversation.company]:
        messages.error(request, 'No tienes permiso para archivar esta conversación.')
        return redirect('messaging:inbox')
    
    # Archivar según tipo de usuario
    if request.user == conversation.candidate:
        conversation.is_archived_by_candidate = not conversation.is_archived_by_candidate
        action = 'archivada' if conversation.is_archived_by_candidate else 'desarchivada'
    else:
        conversation.is_archived_by_company = not conversation.is_archived_by_company
        action = 'archivada' if conversation.is_archived_by_company else 'desarchivada'
    
    conversation.save()
    
    messages.success(request, f'Conversación {action} correctamente.')
    return redirect('messaging:inbox')


def send_message_notification(message):
    """
    Envía notificación de nuevo mensaje
    """
    recipient = message.get_recipient()
    
    # Crear notificación en la base de datos
    notification, created = MessageNotification.objects.get_or_create(
        user=recipient,
        message=message
    )
    
    # Enviar email
    if not notification.is_email_sent:
        try:
            subject = f'Nuevo mensaje en: {message.conversation.subject}'
            body = f"""
            Has recibido un nuevo mensaje de {message.sender.get_full_name()}.
            
            Asunto: {message.conversation.subject}
            
            Para ver el mensaje completo, ingresa a la plataforma:
            {settings.SITE_URL}/mensajes/conversacion/{message.conversation.pk}/
            """
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=True,
            )
            
            notification.is_email_sent = True
            notification.save()
        except Exception as e:
            print(f"Error enviando email: {e}")


@login_required
def notifications_view(request):
    """
    Vista de notificaciones de mensajes
    """
    notifications = MessageNotification.objects.filter(
        user=request.user
    ).select_related('message', 'message__conversation').order_by('-created_at')[:50]
    
    # Marcar como leídas
    notifications.update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'messaging/notifications.html', context)