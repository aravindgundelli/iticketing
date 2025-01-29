import random
import string
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from .form import CreateTicketForm, AssignTicketForm
from .models import Ticket

User = get_user_model()

# Create your views here ticket model

# Create a ticket
def create_ticket(request):
    if request.method == 'POST':
        form = CreateTicketForm(request.POST)
        if form.is_valid():
            var = form.save(commit=False)
            var.customer = request.user
            while not var.ticket_id:
                id = ''.join(random.choices(string.digits, k=7))
                try:
                    var.ticket_id = id
                    var.save()
                    # send email func
                    subject = f'{var.ticket_title} #{var.ticket_id}'
                    message = 'Thank you for Creating Ticket, we will assign engineer soon..'
                    email_from = 'admin@email.com'
                    recipient_list = [request.user.email, ]
                    send_mail(subject, message, email_from, recipient_list)
                    messages.success(request, 'Your ticket has been Submitted, A Support Engineer would reach out soon..')
                    return redirect('customer-active-tickets')
                except IntegrityError:
                    continue
        else:
            messages.warning(request, 'Something went wrong, Please check form errors')
            return redirect('create-ticket')
    else:
        form = CreateTicketForm()
        context = {'form':form}
        return render(request, 'ticket/create_ticket.html', context)
        

# see all created active tickets
def customer_active_tickets(request):
    tickets = Ticket.objects.filter(customer=request.user, is_resolved=False).order_by('-created_on')
    context = {'tickets':tickets}
    return render(request, 'ticket/customer_active_tickets.html', context)


# see all created resolved tickets
def customer_resolved_tickets(request):
    tickets = Ticket.objects.filter(customer=request.user, is_resolved=True).order_by('-created_on')
    context = {'tickets':tickets}
    return render(request, 'ticket/customer_resolved_tickets.html', context)


# Engineer can see all his/her created active tickets
def engineer_active_tickets(request):
    tickets = Ticket.objects.filter(engineer=request.user, is_resolved=False).order_by('-created_on')
    context = {'tickets':tickets}
    return render(request, 'ticket/engineer_active_tickets.html', context)


# Engineer can see all his/her created resolved tickets
def engineer_resolved_tickets(request):
    tickets = Ticket.objects.filter(engineer=request.user, is_resolved=True).order_by('-created_on')
    context = {'tickets':tickets}
    return render(request, 'ticket/engineer_resolved_tickets.html', context)


# Assign Ticket to Engineers
def assign_ticket(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    if request.method == 'POST':
        form = AssignTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            var = form.save(commit=False)
            var.is_assigned_to_engineer = True
            var.status = 'Active'
            var.save()
            messages.success(request, f'Ticket has been assigned to {var.engineer}')
            return redirect('ticket-queue')
        else:
            messages.warning(request, 'Something went wrong. Please check form input')
            return redirect('assign-ticket')
    else:
        form = AssignTicketForm(instance=ticket)
        form.fields['engineer'].queryset = User.objects.filter(is_engineer=True)
        context = {'form':form, 'ticket':ticket}
        return render(request, 'ticket/assign_ticket.html', context)


# Ticket details
def ticket_details(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    context = {'ticket':ticket}
    return render(request, 'ticket/ticket_details.html', context)



# Ticket queue (for only admins)
def ticket_queue(request):
    tickets =Ticket.objects.filter(is_assigned_to_engineer=False)
    context = {'tickets':tickets}
    return render(request, 'ticket/ticket_queue.html', context)


# Resolved Tickets
def resolve_ticket(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    if request.method == 'POST':
        rs = request.POST.get('rs')
        ticket.resolution_steps = rs
        ticket.is_resolved = True
        ticket.status = 'Resolved'
        ticket.save()
        messages.success(request, 'Ticket is now resolved and closed')
        return redirect('dashboard')
    

# All Active Tickets
def allactivetickets(request):
    tickets = Ticket.objects.all()
    context = {'tickets':tickets}
    return render(request, 'ticket/allactive_tickets.html', context)