from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm
from django.db.models import Count

@login_required
def send_message(request):
    unread_count = Message.objects.filter(recipient=request.user, read=False).count()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()

    return render(request, 'messaging/send_message.html', {
        'form': form,
        'unread_count': unread_count
    })


@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    unread_count = received_messages.filter(read=False).count()

    return render(request, 'messaging/inbox.html', {
        'messages': received_messages,
        'unread_count': unread_count,
    })

@login_required
def sent_messages(request):
    sent_messages = Message.objects.filter(sender=request.user)
    unread_count = Message.objects.filter(recipient=request.user, read=False).count()

    return render(request, 'messaging/sent_messages.html', {
        'messages': sent_messages,
        'unread_count': unread_count
    })

@login_required
def view_message(request, pk):
    message = get_object_or_404(Message, pk=pk)

    # Mark the message as read if the recipient is viewing it
    if message.recipient == request.user and not message.read:
        message.read = True
        message.save()

    return render(request, 'messaging/view_message.html', {'message': message})
