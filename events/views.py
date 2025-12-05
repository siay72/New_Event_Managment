from django.shortcuts import render, redirect,get_object_or_404
from events.models import Event, Category
from django.utils import timezone
from django.db.models import Q, Count,Sum
from events.forms import EventModelForm, CategoryModelForm
from datetime import date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
User = get_user_model()


def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()


def is_organizer_or_admin(user):
    return user.is_superuser or user.groups.filter(name='Organizer').exists()


@login_required
def dashboard(request):
    if is_organizer(request.user):
        return redirect('organizer-dashboard')
    elif is_participant(request.user):
        return redirect('user-dashboard')
    return redirect('no-permission')





def home(request):
    query = request.GET.get('q', '').strip()  #
    events = Event.objects.all()

    if query:
        events = events.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    context = {
        'events': events,
        'query': query,
    }
    return render(request, 'home.html', context)


@login_required
@user_passes_test(is_organizer_or_admin,login_url=('no_permission'))
def organizer_dashboard(request):
    now = timezone.localtime()
    today = now.date()
    now_time = now.time()

 
    upcoming_filter = Q(date__gt=today) | (Q(date=today) & Q(time__gte=now_time))
    past_filter = Q(date__lt=today) | (Q(date=today) & Q(time__lt=now_time))

    
    base_qs = (
        Event.objects
        .select_related("category")
        .prefetch_related("participants")
        .annotate(num_participants=Count("participants", distinct=True))
    )

    list_type = request.GET.get("type", "all")
    if list_type == "upcoming":
        events = base_qs.filter(upcoming_filter)
    elif list_type == "past":
        events = base_qs.filter(past_filter)
    else:
        events = base_qs

    category_id = request.GET.get("category")
    if category_id:
        events = events.filter(category_id=category_id)

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])

    # Today’s events
    todays_events = base_qs.filter(date=today).order_by("time")

    
    aggregated = base_qs.aggregate(
        total_events=Count("id", distinct=True),
        total_participants_all_events_sum=Sum("num_participants")
    )

    total_participants_distinct = User.objects.count()
    upcoming_events_count = base_qs.filter(upcoming_filter).count()
    past_events_count = base_qs.filter(past_filter).count()

    context = {
        "counts": {
            "total_events": aggregated["total_events"],
            "upcoming_events": upcoming_events_count,
            "past_events": past_events_count,
            "total_participants_distinct": total_participants_distinct,
            "total_participants_all_events_sum": aggregated["total_participants_all_events_sum"] or 0,
        },
        "events": events.order_by("-date", "-time"),
        "todays_events": todays_events,
        "list_type": list_type,
        "categories": Category.objects.all(),
        "selected_category": category_id,
    }

    return render(request, "dashboard/dashboard.html", context)



@login_required
@permission_required("events.add_event", login_url='no_permission')
def create_event(request):
    event_form = EventModelForm()

    if request.method == "POST":
        event_form = EventModelForm(request.POST,request.FILES )

        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Created Successfully")
            return redirect('create_event') 

    context = {
        "event_form": event_form,
        "title": "Create Event",
    }

    return render(request, "dashboard/event_form.html", context)



@login_required
@permission_required("events.change_event", login_url='no_permission')
def update_event(request, id):
    event = Event.objects.get(id=id)
    event_form = EventModelForm(instance=event)

    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES, instance=event)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('update_event',id)
        else:
            messages.error(request,"Something went Wrong")

    context= {
        "event_form": event_form,
        "event": event,
        "title": "Update Event"
    }
    return render(request, "dashboard/event_form.html",context)




@login_required
def delete_event(request, id):
    if request.method == "POST":
        try:
            event = Event.objects.get(id=id)
            event.delete()
            messages.success(request, "Event Deleted Successfully")
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
        return redirect('dashboard')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('dashboard')
    



@login_required
def event_detail(request, id):
    event = (
        Event.objects
        .select_related("category")
        .prefetch_related("participants")
        .filter(id=id)
        .first()
    )

    if not event:
        messages.error(request, "Event not found.")
        return redirect("user-dashboard")

    user_rsvp = event.participants.filter(id=request.user.id).exists()


    if request.method == "POST":
        action = request.POST.get("action", "").strip().lower()

        # RSVP
        if action == "rsvp":
            if user_rsvp:
                messages.warning(request, "You have already RSVP to this event.")
                return redirect("event-detail", id=event.id)
            event.participants.add(request.user)

            messages.success(request, "RSVP successful!")
            return redirect("event-detail", id=event.id)

        # CANCEL RSVP
        elif action == "cancel":
            if not user_rsvp:
                messages.warning(request, "You are not RSVP to this event.")
                return redirect("event-detail", id=event.id)

            event.participants.remove(request.user)
            messages.success(request, "Your RSVP has been cancelled.")
            return redirect("event-detail", id=event.id)

        else:
            messages.error(request, "Invalid action.")
            return redirect("event-detail", id=event.id)


    return render(request, "event_details.html", {
        "event": event,
        "user_rsvp": user_rsvp,
    })




@login_required
@permission_required("events.add_category", login_url='no_permission')
def add_category(request):
  
    if request.method == 'POST':
        form = CategoryModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('add_category')
    else:
        form = CategoryModelForm()

    return render(request, 'dashboard/add_category.html', {'form': form})







