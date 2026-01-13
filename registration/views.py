from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import translation, timezone
from django.conf import settings
from django.urls import translate_url, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json
import logging
from .models import (
    Household, Collector, Admin, Province, District, Sector, Cell, Village,
    WasteCategory, WastePickupRequest, Notification, OTP
)

logger = logging.getLogger(__name__)


def set_language(request):
    """Set language preference"""
    if request.method == 'POST':
        language = request.POST.get('language')
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        if language and language in dict(settings.LANGUAGES):
            translation.activate(language)
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            response = HttpResponseRedirect(next_url)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            return response
    # If GET request or invalid language, redirect to landing page
    return redirect('registration:landing')


def landing_page(request):
    """Landing page view"""
    from django.contrib.messages import get_messages
    provinces = Province.objects.all()
    waste_categories = WasteCategory.objects.all()
    
    context = {
        'messages': list(get_messages(request)),
        'provinces': provinces,
        'waste_categories': waste_categories,
    }
    return render(request, 'landing.html', context)


def contact_form_submit(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        # Here you can add logic to save the contact form data or send an email
        # For now, we'll just show a success message
        messages.success(request, "Thank you for your message! We will get back to you soon.")
        return redirect('registration:landing')
    return redirect('registration:landing')


def registration_selection(request):
    """Registration selection page - choose user type"""
    from django.contrib.messages import get_messages
    
    context = {
        'messages': list(get_messages(request)),
    }
    return render(request, 'registration/registration_selection.html', context)


# Household Views
def household_signup(request):
    """Household registration view with OTP verification"""
    provinces = Province.objects.all()
    
    # Define context early so it's available in all code paths
    context = {
        'provinces': provinces,
        'messages': list(messages.get_messages(request)),
    }
    
    if request.method == 'POST':
        # Check if OTP is verified (frontend sends this after OTP verification)
        otp_verified = request.POST.get('otp_verified') == 'true'
        phone_number = request.POST.get('phone_number')
        otp_code = request.POST.get('otp_code')
        
        if not otp_verified:
            messages.error(request, "Please verify your phone number with OTP first.")
        else:
            # Normalize phone number for comparison
            normalized_phone = phone_number.strip()
            if not normalized_phone.startswith('+'):
                if normalized_phone.startswith('0'):
                    normalized_phone = '+250' + normalized_phone[1:]
                elif normalized_phone.startswith('250'):
                    normalized_phone = '+' + normalized_phone
                else:
                    normalized_phone = '+250' + normalized_phone
            
            # Verify OTP one more time on server side for security
            # Check if OTP code matches the phone number and is not expired
            otp = OTP.objects.filter(
                otp=otp_code,
                phoneNumber=normalized_phone
            ).order_by('-created_at').first()
            
            if not otp:
                messages.error(request, "Invalid OTP code. Please verify your phone number again.")
                context['messages'] = list(messages.get_messages(request))
                return render(request, 'registration/household_signup.html', context)
            
            if timezone.now() >= otp.expires_at:
                messages.error(request, "OTP has expired. Please request a new OTP.")
                context['messages'] = list(messages.get_messages(request))
                return render(request, 'registration/household_signup.html', context)
            
            # Mark as verified if not already
            if not otp.is_verified:
                otp.is_verified = True
                otp.save()
            
            # OTP is valid, proceed with registration
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            email = request.POST.get('email')
            
            # Validate inputs
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                # Check if email/phone already exists
                from django.contrib.auth.models import User
                if User.objects.filter(email=email).exists():
                    messages.error(request, "An account with this email already exists.")
                elif Household.objects.filter(phone_number=normalized_phone).exists():
                    messages.error(request, "An account with this phone number already exists.")
                else:
                    try:
                        with transaction.atomic():
                            # Create user
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                password=password,
                                first_name=request.POST.get('full_name', '').split()[0] if request.POST.get('full_name') else '',
                                last_name=' '.join(request.POST.get('full_name', '').split()[1:]) if len(request.POST.get('full_name', '').split()) > 1 else '',
                            )
                            
                            # Create household profile with verified phone
                            household = Household.objects.create(
                                user=user,
                                phone_number=normalized_phone,
                                province_id=request.POST.get('province') or None,
                                district_id=request.POST.get('district') or None,
                                sector_id=request.POST.get('sector') or None,
                                cell_id=request.POST.get('cell') or None,
                                village_id=request.POST.get('village') or None,
                                street_address=request.POST.get('street_address', ''),
                                is_verified=True,  # Mark as verified after OTP
                            )
                            
                            messages.success(request, "Registration successful! Please login.")
                            return redirect('registration:household_login')
                    except Exception as e:
                        messages.error(request, f"Registration failed: {str(e)}")
    
    # Update context with latest messages before rendering
    context['messages'] = list(messages.get_messages(request))
    return render(request, 'registration/household_signup.html', context)


def household_login(request):
    """Household login view"""
    if request.user.is_authenticated:
        try:
            request.user.household_profile
            return redirect('registration:household_dashboard')
        except Household.DoesNotExist:
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                user.household_profile
                login(request, user)
                return redirect('registration:household_dashboard')
            except Household.DoesNotExist:
                messages.error(request, "This account is not registered as a household.")
        else:
            messages.error(request, "Invalid username or password.")
    
    context = {
        'messages': list(messages.get_messages(request)),
    }
    return render(request, 'registration/household_login.html', context)


@login_required
def household_dashboard(request):
    """Household dashboard view"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    # Get full queryset for statistics (before slicing)
    all_pickup_requests = WastePickupRequest.objects.filter(household=household).order_by('-created_at')
    
    # Calculate statistics using the full queryset
    total_requests = all_pickup_requests.count()
    completed_requests = all_pickup_requests.filter(status='Completed').count()
    pending_requests = all_pickup_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_pickup_requests])
    
    # Calculate statistics by waste category
    from django.db.models import Sum, Count
    category_stats = WastePickupRequest.objects.filter(household=household).values(
        'waste_category__id', 'waste_category__name', 'waste_category__color_code'
    ).annotate(
        total_count=Count('id'),
        total_weight=Sum('quantity'),
        completed_count=Count('id', filter=Q(status='Completed')),
        pending_count=Count('id', filter=Q(status='Pending'))
    ).order_by('-total_count')
    
    # Get scheduled pickups for calendar (with collector info)
    # Include both scheduled pickups and pending requests that might be scheduled
    scheduled_pickups = WastePickupRequest.objects.filter(
        household=household,
        status__in=['Scheduled', 'In Progress'],
        scheduled_date__isnull=False
    ).select_related('collector', 'collector__user', 'waste_category').order_by('scheduled_date')
    
    # Also get pending requests that might be scheduled soon (for display)
    pending_for_calendar = WastePickupRequest.objects.filter(
        household=household,
        status='Pending',
        collector__isnull=False
    ).select_related('collector', 'collector__user', 'waste_category')[:5]
    
    # Generate calendar data for current month
    from datetime import datetime, timedelta
    from calendar import monthrange
    
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Get all scheduled dates for the current month
    scheduled_dates = {}
    for pickup in scheduled_pickups:
        if pickup.scheduled_date:
            pickup_date = pickup.scheduled_date.date()
            if pickup_date.month == current_month and pickup_date.year == current_year:
                day = pickup_date.day
                if day not in scheduled_dates:
                    scheduled_dates[day] = []
                scheduled_dates[day].append(pickup)
    
    # Generate calendar grid
    first_day, num_days = monthrange(current_year, current_month)
    calendar_days = []
    
    # Add empty cells for days before the first day of the month
    for _ in range(first_day):
        calendar_days.append(None)
    
    # Add all days of the month
    for day in range(1, num_days + 1):
        date_obj = datetime(current_year, current_month, day).date()
        is_wednesday = date_obj.weekday() == 2  # Wednesday is 2
        has_pickup = day in scheduled_dates
        is_today = date_obj == today
        
        calendar_days.append({
            'day': day,
            'date': date_obj,
            'is_wednesday': is_wednesday,
            'has_pickup': has_pickup,
            'pickups': scheduled_dates.get(day, []),
            'is_today': is_today
        })
    
    # Get month name
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[current_month - 1]
    
    # Slice for display (only the first 10)
    pickup_requests = all_pickup_requests[:10]
    
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    waste_categories = WasteCategory.objects.all()
    
    context = {
        'household': household,
        'pickup_requests': pickup_requests,
        'scheduled_pickups': scheduled_pickups,
        'pending_for_calendar': pending_for_calendar,
        'notifications': notifications,
        'waste_categories': waste_categories,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'category_stats': category_stats,
        'current_page': 'dashboard',
        'calendar_days': calendar_days,
        'current_month': month_name,
        'current_year': current_year,
    }
    return render(request, 'registration/household_dashboard.html', context)


@login_required
def household_requests(request):
    """Household requests view - shows all pickup requests"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    all_requests = WastePickupRequest.objects.filter(household=household).select_related('waste_category', 'collector', 'collector__user').order_by('-created_at')
    
    # Calculate statistics
    total_requests = all_requests.count()
    completed_requests = all_requests.filter(status='Completed').count()
    pending_requests = all_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_requests])
    
    waste_categories = WasteCategory.objects.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'household': household,
        'pickup_requests': all_requests,
        'waste_categories': waste_categories,
        'notifications': notifications,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'current_page': 'requests',
    }
    return render(request, 'registration/household_dashboard.html', context)


@login_required
def household_notifications(request):
    """Household notifications view"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    all_pickup_requests = WastePickupRequest.objects.filter(household=household)
    total_requests = all_pickup_requests.count()
    completed_requests = all_pickup_requests.filter(status='Completed').count()
    pending_requests = all_pickup_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_pickup_requests])
    
    waste_categories = WasteCategory.objects.all()
    
    context = {
        'household': household,
        'notifications': all_notifications,
        'waste_categories': waste_categories,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'current_page': 'notifications',
    }
    return render(request, 'registration/household_dashboard.html', context)


@login_required
def household_profile(request):
    """Household profile view"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    # Calculate statistics
    all_pickup_requests = WastePickupRequest.objects.filter(household=household)
    total_requests = all_pickup_requests.count()
    completed_requests = all_pickup_requests.filter(status='Completed').count()
    pending_requests = all_pickup_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_pickup_requests])
    
    waste_categories = WasteCategory.objects.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'household': household,
        'waste_categories': waste_categories,
        'notifications': notifications,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'current_page': 'profile',
    }
    return render(request, 'registration/household_dashboard.html', context)


@login_required
def household_history(request):
    """Household history view - shows completed requests"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    completed_requests = WastePickupRequest.objects.filter(
        household=household, 
        status='Completed'
    ).select_related('waste_category', 'collector', 'collector__user').order_by('-completed_date', '-created_at')
    
    # Calculate statistics
    all_pickup_requests = WastePickupRequest.objects.filter(household=household)
    total_requests = all_pickup_requests.count()
    completed_count = completed_requests.count()
    pending_requests = all_pickup_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_pickup_requests])
    
    waste_categories = WasteCategory.objects.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'household': household,
        'pickup_requests': completed_requests,
        'waste_categories': waste_categories,
        'notifications': notifications,
        'total_requests': total_requests,
        'completed_requests': completed_count,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'current_page': 'history',
    }
    return render(request, 'registration/household_dashboard.html', context)


@login_required
def household_settings(request):
    """Household settings view"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    # Calculate statistics
    all_pickup_requests = WastePickupRequest.objects.filter(household=household)
    total_requests = all_pickup_requests.count()
    completed_requests = all_pickup_requests.filter(status='Completed').count()
    pending_requests = all_pickup_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_pickup_requests])
    
    waste_categories = WasteCategory.objects.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'household': household,
        'waste_categories': waste_categories,
        'notifications': notifications,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'current_page': 'settings',
    }
    return render(request, 'registration/household_dashboard.html', context)


@login_required
def household_help(request):
    """Household help & FAQ view"""
    try:
        household = request.user.household_profile
    except Household.DoesNotExist:
        messages.error(request, "Household profile not found.")
        return redirect('registration:household_login')
    
    all_pickup_requests = WastePickupRequest.objects.filter(household=household)
    total_requests = all_pickup_requests.count()
    completed_requests = all_pickup_requests.filter(status='Completed').count()
    pending_requests = all_pickup_requests.filter(status='Pending').count()
    total_weight = sum([req.quantity for req in all_pickup_requests])
    
    waste_categories = WasteCategory.objects.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    faqs = [
        {
            "question": "How do I request a pickup?",
            "answer": "Go to the Dashboard and use the 'Request Pickup' form on the right side. Select a waste category, quantity, and your address, then submit."
        },
        {
            "question": "How do I know when my waste will be collected?",
            "answer": "Check the Upcoming Pickups section on your Dashboard. It shows the scheduled date, time, waste type, and assigned collector."
        },
        {
            "question": "What if I need to change or cancel a request?",
            "answer": "Use the contact form on this page to reach support, and include your request ID and details of the change."
        },
    ]
    
    context = {
        'household': household,
        'waste_categories': waste_categories,
        'notifications': notifications,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_weight': total_weight,
        'faqs': faqs,
        'current_page': 'help',
    }
    return render(request, 'registration/household_dashboard.html', context)


# Collector Views
def collector_signup(request):
    """Collector registration view with OTP verification"""
    provinces = Province.objects.all()
    
    # Define context early so it's available in all code paths
    context = {
        'provinces': provinces,
        'messages': list(messages.get_messages(request)),
    }
    
    if request.method == 'POST':
        # Check if OTP is verified
        otp_verified = request.POST.get('otp_verified') == 'true'
        phone_number = request.POST.get('phone_number')
        otp_code = request.POST.get('otp_code')
        
        if not otp_verified:
            messages.error(request, "Please verify your phone number with OTP first.")
        else:
            # Normalize phone number for comparison
            normalized_phone = phone_number.strip()
            if not normalized_phone.startswith('+'):
                if normalized_phone.startswith('0'):
                    normalized_phone = '+250' + normalized_phone[1:]
                elif normalized_phone.startswith('250'):
                    normalized_phone = '+' + normalized_phone
                else:
                    normalized_phone = '+250' + normalized_phone
            
            # Verify OTP one more time on server side for security
            # Check if OTP code matches the phone number and is not expired
            otp = OTP.objects.filter(
                otp=otp_code,
                phoneNumber=normalized_phone
            ).order_by('-created_at').first()
            
            if not otp:
                messages.error(request, "Invalid OTP code. Please verify your phone number again.")
                context['messages'] = list(messages.get_messages(request))
                return render(request, 'registration/collector_signup.html', context)
            
            if timezone.now() >= otp.expires_at:
                messages.error(request, "OTP has expired. Please request a new OTP.")
                context['messages'] = list(messages.get_messages(request))
                return render(request, 'registration/collector_signup.html', context)
            
            # Mark as verified if not already
            if not otp.is_verified:
                otp.is_verified = True
                otp.save()
            
            # OTP is valid, proceed with registration
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            email = request.POST.get('email')
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                # Check if email/phone already exists
                from django.contrib.auth.models import User
                if User.objects.filter(email=email).exists():
                    messages.error(request, "An account with this email already exists.")
                elif Collector.objects.filter(phone_number=normalized_phone).exists():
                    messages.error(request, "An account with this phone number already exists.")
                else:
                    try:
                        with transaction.atomic():
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                password=password,
                                first_name=request.POST.get('full_name', '').split()[0] if request.POST.get('full_name') else '',
                                last_name=' '.join(request.POST.get('full_name', '').split()[1:]) if len(request.POST.get('full_name', '').split()) > 1 else '',
                            )
                            
                            collector = Collector.objects.create(
                                user=user,
                                phone_number=normalized_phone,
                                license_number=request.POST.get('license_number', ''),
                                vehicle_number=request.POST.get('vehicle_number', ''),
                                is_verified=True,  # Mark as verified after OTP
                            )
                            
                            messages.success(request, "Registration successful! Please login.")
                            return redirect('registration:collector_login')
                    except Exception as e:
                        messages.error(request, f"Registration failed: {str(e)}")
    
    # Update context with latest messages before rendering
    context['messages'] = list(messages.get_messages(request))
    return render(request, 'registration/collector_signup.html', context)


def collector_login(request):
    """Collector login view"""
    if request.user.is_authenticated:
        try:
            request.user.collector_profile
            return redirect('registration:collector_dashboard')
        except Collector.DoesNotExist:
            pass
    
    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')

        # Allow login by username, email, or collector phone number
        user = None
        if identifier:
            user = User.objects.filter(
                Q(username=identifier) |
                Q(email=identifier) |
                Q(collector_profile__phone_number=identifier)
            ).first()

        if user:
            auth_user = authenticate(request, username=user.username, password=password)
        else:
            auth_user = None
        
        if auth_user is not None:
            try:
                auth_user.collector_profile
                login(request, auth_user)
                return redirect('registration:collector_dashboard')
            except Collector.DoesNotExist:
                messages.error(request, "This account is not registered as a collector.")
        else:
            messages.error(request, "Invalid email/phone or password.")
    
    context = {
        'messages': list(messages.get_messages(request)),
    }
    return render(request, 'registration/collector_login.html', context)


@login_required
def collector_dashboard(request):
    """Collector dashboard - main page"""
    try:
        collector = request.user.collector_profile
    except Collector.DoesNotExist:
        messages.error(request, "Collector profile not found.")
        return redirect('registration:collector_login')
    
    assigned_pickups = WastePickupRequest.objects.filter(collector=collector).order_by('-created_at')
    available_pickups = WastePickupRequest.objects.filter(status='Pending', collector__isnull=True).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'collector': collector,
        'assigned_pickups': assigned_pickups,
        'available_pickups': available_pickups,
        'notifications': notifications,
        'current_page': 'dashboard',
    }
    return render(request, 'registration/collector_dashboard.html', context)


@login_required
def collector_available(request):
    """Collector view - Available pickups page"""
    try:
        collector = request.user.collector_profile
    except Collector.DoesNotExist:
        messages.error(request, "Collector profile not found.")
        return redirect('registration:collector_login')

    assigned_pickups = WastePickupRequest.objects.filter(collector=collector).order_by('-created_at')
    available_pickups = WastePickupRequest.objects.filter(status='Pending', collector__isnull=True).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]

    context = {
        'collector': collector,
        'assigned_pickups': assigned_pickups,
        'available_pickups': available_pickups,
        'notifications': notifications,
        'current_page': 'available',
    }
    return render(request, 'registration/collector_dashboard.html', context)


@login_required
def collector_assigned(request):
    """Collector view - My assignments page"""
    try:
        collector = request.user.collector_profile
    except Collector.DoesNotExist:
        messages.error(request, "Collector profile not found.")
        return redirect('registration:collector_login')

    assigned_pickups = WastePickupRequest.objects.filter(collector=collector).order_by('-created_at')
    available_pickups = WastePickupRequest.objects.filter(status='Pending', collector__isnull=True).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]

    context = {
        'collector': collector,
        'assigned_pickups': assigned_pickups,
        'available_pickups': available_pickups,
        'notifications': notifications,
        'current_page': 'assigned',
    }
    return render(request, 'registration/collector_dashboard.html', context)


@login_required
def collector_profile_view(request):
    """Collector view - Profile page"""
    try:
        collector = request.user.collector_profile
    except Collector.DoesNotExist:
        messages.error(request, "Collector profile not found.")
        return redirect('registration:collector_login')

    assigned_pickups = WastePickupRequest.objects.filter(collector=collector).order_by('-created_at')
    available_pickups = WastePickupRequest.objects.filter(status='Pending', collector__isnull=True).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]

    context = {
        'collector': collector,
        'assigned_pickups': assigned_pickups,
        'available_pickups': available_pickups,
        'notifications': notifications,
        'current_page': 'profile',
    }
    return render(request, 'registration/collector_dashboard.html', context)


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('registration:landing')


# Admin Views
def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        try:
            request.user.admin_profile
            return redirect('registration:admin_dashboard')
        except Admin.DoesNotExist:
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                user.admin_profile
                login(request, user)
                return redirect('registration:admin_dashboard')
            except Admin.DoesNotExist:
                if user.is_superuser:
                    # Create admin profile for superuser
                    Admin.objects.create(user=user, role='Super Admin')
                    login(request, user)
                    return redirect('registration:admin_dashboard')
                messages.error(request, "This account is not registered as an admin.")
        else:
            messages.error(request, "Invalid username or password.")
    
    context = {
        'messages': list(messages.get_messages(request)),
    }
    return render(request, 'registration/admin_login.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard - main page"""
    try:
        admin_profile = request.user.admin_profile
    except Admin.DoesNotExist:
        if request.user.is_superuser:
            admin_profile = Admin.objects.create(user=request.user, role='Super Admin')
        else:
            messages.error(request, "Admin profile not found.")
            return redirect('registration:admin_login')
    
    # Statistics
    total_households = Household.objects.count()
    total_collectors = Collector.objects.count()
    total_pickups = WastePickupRequest.objects.count()
    pending_pickups = WastePickupRequest.objects.filter(status='Pending').count()
    completed_pickups = WastePickupRequest.objects.filter(status='Completed').count()
    
    recent_pickups = WastePickupRequest.objects.all().order_by('-created_at')[:10]
    recent_households = Household.objects.all().order_by('-created_at')[:5]
    recent_collectors = Collector.objects.all().order_by('-created_at')[:5]
    
    context = {
        'admin_profile': admin_profile,
        'total_households': total_households,
        'total_collectors': total_collectors,
        'total_pickups': total_pickups,
        'pending_pickups': pending_pickups,
        'completed_pickups': completed_pickups,
        'recent_pickups': recent_pickups,
        'recent_households': recent_households,
        'recent_collectors': recent_collectors,
        'current_page': 'dashboard',
    }
    return render(request, 'registration/admin_dashboard.html', context)


@login_required
def admin_pickups(request):
    """Admin view - Pickups page with multiple tables"""
    try:
        admin_profile = request.user.admin_profile
    except Admin.DoesNotExist:
        if request.user.is_superuser:
            admin_profile = Admin.objects.create(user=request.user, role='Super Admin')
        else:
            messages.error(request, "Admin profile not found.")
            return redirect('registration:admin_login')

    # Get all pickup requests with related data
    all_pickups = WastePickupRequest.objects.select_related(
        'household__user', 'collector__user', 'waste_category'
    ).all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        all_pickups = all_pickups.filter(status=status_filter)
    
    # Filter by province/district if provided
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    if province_id:
        all_pickups = all_pickups.filter(household__province_id=province_id)
    if district_id:
        all_pickups = all_pickups.filter(household__district_id=district_id)
    
    # Categorize pickups
    pending_pickups = WastePickupRequest.objects.filter(status='Pending').select_related(
        'household__user', 'waste_category'
    ).order_by('-created_at')
    
    scheduled_pickups = WastePickupRequest.objects.filter(status='Scheduled').select_related(
        'household__user', 'collector__user', 'waste_category'
    ).order_by('scheduled_date')
    
    in_progress_pickups = WastePickupRequest.objects.filter(status='In Progress').select_related(
        'household__user', 'collector__user', 'waste_category'
    ).order_by('-updated_at')
    
    completed_pickups = WastePickupRequest.objects.filter(status='Completed').select_related(
        'household__user', 'collector__user', 'waste_category'
    ).order_by('-completed_date')[:50]  # Limit to recent 50
    
    # Missed pickups: scheduled but not completed, and scheduled_date has passed
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    missed_pickups_list = WastePickupRequest.objects.filter(
        status__in=['Scheduled', 'In Progress'],
        scheduled_date__lt=now
    ).select_related(
        'household__user', 'collector__user', 'waste_category'
    ).order_by('scheduled_date')
    
    # Add days overdue to each missed pickup
    missed_pickups = []
    for pickup in missed_pickups_list:
        days_overdue = (now.date() - pickup.scheduled_date.date()).days if pickup.scheduled_date else 0
        missed_pickups.append({
            'pickup': pickup,
            'days_overdue': days_overdue
        })
    
    # Assigned collectors with their pickup assignments
    assigned_collectors = Collector.objects.filter(
        assigned_pickups__isnull=False
    ).distinct().select_related('user', 'province', 'district').prefetch_related(
        'assigned_pickups__household__user', 'assigned_pickups__waste_category'
    )
    
    # Group assignments by collector
    collector_assignments = []
    for collector in assigned_collectors:
        assignments = WastePickupRequest.objects.filter(
            collector=collector,
            status__in=['Scheduled', 'In Progress']
        ).select_related('household__user', 'waste_category').order_by('scheduled_date')
        if assignments.exists():
            collector_assignments.append({
                'collector': collector,
                'assignments': assignments,
                'total_assigned': assignments.count(),
                'pending_count': assignments.filter(status='Scheduled').count(),
                'in_progress_count': assignments.filter(status='In Progress').count(),
            })
    
    # Pickups by waste category
    from django.db.models import Count
    pickups_by_category = WastePickupRequest.objects.values(
        'waste_category__name', 'waste_category__id'
    ).annotate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='Pending')),
        scheduled=Count('id', filter=Q(status='Scheduled')),
        in_progress=Count('id', filter=Q(status='In Progress')),
        completed=Count('id', filter=Q(status='Completed')),
    ).order_by('-total')
    
    # Get all provinces for filter dropdown
    all_provinces = Province.objects.all().order_by('name')
    districts = []
    if province_id:
        districts = District.objects.filter(province_id=province_id).order_by('name')
    
    # Statistics
    total_households = Household.objects.count()
    total_collectors = Collector.objects.count()
    total_pickups = WastePickupRequest.objects.count()
    pending_count = WastePickupRequest.objects.filter(status='Pending').count()
    completed_count = WastePickupRequest.objects.filter(status='Completed').count()

    context = {
        'admin_profile': admin_profile,
        'total_households': total_households,
        'total_collectors': total_collectors,
        'total_pickups': total_pickups,
        'pending_pickups': pending_count,
        'completed_pickups': completed_count,
        'all_pickups': all_pickups,
        'pending_pickups_list': pending_pickups,
        'scheduled_pickups': scheduled_pickups,
        'in_progress_pickups': in_progress_pickups,
        'completed_pickups_list': completed_pickups,
        'missed_pickups': missed_pickups,
        'collector_assignments': collector_assignments,
        'pickups_by_category': pickups_by_category,
        'all_provinces': all_provinces,
        'districts': districts,
        'selected_province': province_id,
        'selected_district': district_id,
        'selected_status': status_filter,
        'current_page': 'pickups',
    }
    return render(request, 'registration/admin_dashboard.html', context)


@login_required
def admin_households(request):
    """Admin view - Households page with filtering"""
    try:
        admin_profile = request.user.admin_profile
    except Admin.DoesNotExist:
        if request.user.is_superuser:
            admin_profile = Admin.objects.create(user=request.user, role='Super Admin')
        else:
            messages.error(request, "Admin profile not found.")
            return redirect('registration:admin_login')

    # Get all households with related user and location data
    households_query = Household.objects.select_related('user', 'province', 'district', 'sector', 'cell', 'village').all()
    
    # Apply filters based on GET parameters
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    sector_id = request.GET.get('sector')
    cell_id = request.GET.get('cell')
    village_id = request.GET.get('village')
    
    if province_id:
        households_query = households_query.filter(province_id=province_id)
    if district_id:
        households_query = households_query.filter(district_id=district_id)
    if sector_id:
        households_query = households_query.filter(sector_id=sector_id)
    if cell_id:
        households_query = households_query.filter(cell_id=cell_id)
    if village_id:
        households_query = households_query.filter(village_id=village_id)
    
    # Order by province, district, then name
    all_households = households_query.order_by('province__name', 'district__name', 'user__first_name', 'user__last_name', 'user__username')
    
    # Get all provinces for filter dropdown
    all_provinces = Province.objects.all().order_by('name')
    
    # Get districts for selected province (if any)
    districts = []
    if province_id:
        districts = District.objects.filter(province_id=province_id).order_by('name')
    
    # Get sectors for selected district (if any)
    sectors = []
    if district_id:
        sectors = Sector.objects.filter(district_id=district_id).order_by('name')
    
    # Get cells for selected sector (if any)
    cells = []
    if sector_id:
        cells = Cell.objects.filter(sector_id=sector_id).order_by('name')
    
    # Get villages for selected cell (if any)
    villages = []
    if cell_id:
        villages = Village.objects.filter(cell_id=cell_id).order_by('name')
    
    # Statistics
    total_households = Household.objects.count()
    total_collectors = Collector.objects.count()
    total_pickups = WastePickupRequest.objects.count()
    pending_pickups = WastePickupRequest.objects.filter(status='Pending').count()
    completed_pickups = WastePickupRequest.objects.filter(status='Completed').count()

    context = {
        'admin_profile': admin_profile,
        'total_households': total_households,
        'total_collectors': total_collectors,
        'total_pickups': total_pickups,
        'pending_pickups': pending_pickups,
        'completed_pickups': completed_pickups,
        'all_households': all_households,
        'all_provinces': all_provinces,
        'districts': districts,
        'sectors': sectors,
        'cells': cells,
        'villages': villages,
        'selected_province': province_id,
        'selected_district': district_id,
        'selected_sector': sector_id,
        'selected_cell': cell_id,
        'selected_village': village_id,
        'current_page': 'households',
    }
    return render(request, 'registration/admin_dashboard.html', context)


@login_required
def admin_collectors(request):
    """Admin view - Collectors page with filtering"""
    try:
        admin_profile = request.user.admin_profile
    except Admin.DoesNotExist:
        if request.user.is_superuser:
            admin_profile = Admin.objects.create(user=request.user, role='Super Admin')
        else:
            messages.error(request, "Admin profile not found.")
            return redirect('registration:admin_login')

    # Get all collectors with related user and location data
    collectors_query = Collector.objects.select_related('user', 'province', 'district').all()
    
    # Apply filters based on GET parameters
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    sector_id = request.GET.get('sector')
    cell_id = request.GET.get('cell')
    village_id = request.GET.get('village')
    
    if province_id:
        collectors_query = collectors_query.filter(province_id=province_id)
    if district_id:
        collectors_query = collectors_query.filter(district_id=district_id)
    if sector_id:
        # Note: Collectors don't have sector directly, but we can filter by district's sectors
        collectors_query = collectors_query.filter(district__sectors__id=sector_id).distinct()
    if cell_id:
        collectors_query = collectors_query.filter(district__sectors__cells__id=cell_id).distinct()
    if village_id:
        collectors_query = collectors_query.filter(district__sectors__cells__villages__id=village_id).distinct()
    
    # Order by province, district, then name
    all_collectors = collectors_query.order_by('province__name', 'district__name', 'user__first_name', 'user__last_name', 'user__username')
    
    # Get all provinces for filter dropdown
    all_provinces = Province.objects.all().order_by('name')
    
    # Get districts for selected province (if any)
    districts = []
    if province_id:
        districts = District.objects.filter(province_id=province_id).order_by('name')
    
    # Get sectors for selected district (if any)
    sectors = []
    if district_id:
        sectors = Sector.objects.filter(district_id=district_id).order_by('name')
    
    # Get cells for selected sector (if any)
    cells = []
    if sector_id:
        cells = Cell.objects.filter(sector_id=sector_id).order_by('name')
    
    # Get villages for selected cell (if any)
    villages = []
    if cell_id:
        villages = Village.objects.filter(cell_id=cell_id).order_by('name')
    
    # Statistics
    total_households = Household.objects.count()
    total_collectors = Collector.objects.count()
    total_pickups = WastePickupRequest.objects.count()
    pending_pickups = WastePickupRequest.objects.filter(status='Pending').count()
    completed_pickups = WastePickupRequest.objects.filter(status='Completed').count()

    context = {
        'admin_profile': admin_profile,
        'total_households': total_households,
        'total_collectors': total_collectors,
        'total_pickups': total_pickups,
        'pending_pickups': pending_pickups,
        'completed_pickups': completed_pickups,
        'all_collectors': all_collectors,
        'all_provinces': all_provinces,
        'districts': districts,
        'sectors': sectors,
        'cells': cells,
        'villages': villages,
        'selected_province': province_id,
        'selected_district': district_id,
        'selected_sector': sector_id,
        'selected_cell': cell_id,
        'selected_village': village_id,
        'current_page': 'collectors',
    }
    return render(request, 'registration/admin_dashboard.html', context)


@login_required
def admin_quick_actions(request):
    """Admin view - Quick actions page"""
    try:
        admin_profile = request.user.admin_profile
    except Admin.DoesNotExist:
        if request.user.is_superuser:
            admin_profile = Admin.objects.create(user=request.user, role='Super Admin')
        else:
            messages.error(request, "Admin profile not found.")
            return redirect('registration:admin_login')

    total_households = Household.objects.count()
    total_collectors = Collector.objects.count()
    total_pickups = WastePickupRequest.objects.count()
    pending_pickups = WastePickupRequest.objects.filter(status='Pending').count()
    completed_pickups = WastePickupRequest.objects.filter(status='Completed').count()

    recent_pickups = WastePickupRequest.objects.all().order_by('-created_at')[:10]
    recent_households = Household.objects.all().order_by('-created_at')[:5]
    recent_collectors = Collector.objects.all().order_by('-created_at')[:5]

    context = {
        'admin_profile': admin_profile,
        'total_households': total_households,
        'total_collectors': total_collectors,
        'total_pickups': total_pickups,
        'pending_pickups': pending_pickups,
        'completed_pickups': completed_pickups,
        'recent_pickups': recent_pickups,
        'recent_households': recent_households,
        'recent_collectors': recent_collectors,
        'current_page': 'quick_actions',
    }
    return render(request, 'registration/admin_dashboard.html', context)


# Utility views
@login_required
def create_pickup_request(request):
    """Create a new waste pickup request with geocoding"""
    if request.method == 'POST':
        try:
            household = request.user.household_profile
            address = request.POST.get('address', household.street_address)
            lat = request.POST.get('latitude')
            lon = request.POST.get('longitude')
            
            pickup_request = WastePickupRequest.objects.create(
                household=household,
                waste_category_id=request.POST.get('waste_category'),
                quantity=request.POST.get('quantity', 0),
                address=address,
                notes=request.POST.get('notes', ''),
                latitude=float(lat) if lat else None,
                longitude=float(lon) if lon else None,
            )
            
            # Try to auto-assign nearest collector
            from .geocoding import auto_assign_collector
            if pickup_request.has_location():
                if auto_assign_collector(pickup_request):
                    messages.success(request, "Pickup request created and collector assigned automatically!")
                else:
                    messages.success(request, "Pickup request created! A collector will be assigned soon.")
            else:
                messages.success(request, "Pickup request created successfully!")
        except Household.DoesNotExist:
            messages.error(request, "Household profile not found.")
        except Exception as e:
            messages.error(request, f"Error creating pickup request: {str(e)}")
    
    return redirect('registration:household_dashboard')


@login_required
def assign_pickup(request, pickup_id):
    """Assign a pickup request to a collector"""
    if request.method == 'POST':
        try:
            collector = request.user.collector_profile
            pickup_request = get_object_or_404(WastePickupRequest, id=pickup_id)
            pickup_request.collector = collector
            pickup_request.status = 'Scheduled'
            pickup_request.save()
            messages.success(request, "Pickup request assigned successfully!")
        except Collector.DoesNotExist:
            messages.error(request, "Collector profile not found.")
        except Exception as e:
            messages.error(request, f"Error assigning pickup: {str(e)}")
    
    return redirect('registration:collector_dashboard')


# AJAX Endpoints for Cascading Dropdowns
@require_http_methods(["GET"])
def get_districts(request):
    """Get districts for a province"""
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse({'error': 'Province ID is required'}, status=400)
    
    try:
        districts = District.objects.filter(province_id=province_id).order_by('name')
        districts_data = [{'id': d.id, 'name': d.name} for d in districts]
        return JsonResponse({'districts': districts_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_sectors(request):
    """Get sectors for a district"""
    district_id = request.GET.get('district_id')
    if not district_id:
        return JsonResponse({'error': 'District ID is required'}, status=400)
    
    try:
        sectors = Sector.objects.filter(district_id=district_id).order_by('name')
        sectors_data = [{'id': s.id, 'name': s.name} for s in sectors]
        return JsonResponse({'sectors': sectors_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_cells(request):
    """Get cells for a sector"""
    sector_id = request.GET.get('sector_id')
    if not sector_id:
        return JsonResponse({'error': 'Sector ID is required'}, status=400)
    
    try:
        cells = Cell.objects.filter(sector_id=sector_id).order_by('name')
        cells_data = [{'id': c.id, 'name': c.name} for c in cells]
        return JsonResponse({'cells': cells_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_villages(request):
    """Get villages for a cell"""
    cell_id = request.GET.get('cell_id')
    if not cell_id:
        return JsonResponse({'error': 'Cell ID is required'}, status=400)
    
    try:
        villages = Village.objects.filter(cell_id=cell_id).order_by('name')
        villages_data = [{'id': v.id, 'name': v.name} for v in villages]
        return JsonResponse({'villages': villages_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# OTP Endpoints
import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import OTP


@csrf_exempt
@require_http_methods(["POST"])
def request_otp(request):
    """Request OTP"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        phone_number = data.get('phoneNumber') or data.get('phone_number')
        
        if not phone_number:
            return JsonResponse({"error": "Phone number is required"}, status=400)
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Create OTP record
        otp = OTP.objects.create(phoneNumber=phone_number, otp=otp_code)
        
        return JsonResponse({"message": "OTP sent", "otp": otp_code, "success": True}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verify_otp(request):
    """Verify OTP"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        otp_code = data.get('otp') or data.get('otp_code')
        phone_number = data.get('phoneNumber') or data.get('phone_number')
        
        if not otp_code:
            return JsonResponse({"error": "OTP code is required"}, status=400)
        
        # Normalize phone number if provided
        if phone_number:
            normalized_phone = phone_number.strip()
            if not normalized_phone.startswith('+'):
                if normalized_phone.startswith('0'):
                    normalized_phone = '+250' + normalized_phone[1:]
                elif normalized_phone.startswith('250'):
                    normalized_phone = '+' + normalized_phone
                else:
                    normalized_phone = '+250' + normalized_phone
            
            # Find OTP that matches both code and phone number
            otp = OTP.objects.filter(
                otp=otp_code,
                phoneNumber=normalized_phone
            ).order_by('-created_at').first()
        else:
            # Fallback: find by code only (for backward compatibility)
            otp = OTP.objects.filter(otp=otp_code, is_verified=False).order_by('-created_at').first()
        
        if otp and timezone.now() < otp.expires_at:
            if not otp.is_verified:
                otp.is_verified = True
                otp.save()
            return JsonResponse({"message": "OTP verified successfully", "success": True}, status=200)
        
        return JsonResponse({"error": "Invalid or expired OTP", "success": False}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """API endpoint for chatbot queries"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({
                'error': 'Question is required',
                'success': False
            }, status=400)
        
        # Import chatbot service
        from .chatbot_service import generate_response
        
        # Generate response
        response = generate_response(question, max_length=256, temperature=0.7)
        
        return JsonResponse({
            'response': response,
            'success': True
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format',
            'success': False
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error processing request: {str(e)}',
            'success': False
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def classify_waste_image(request):
    """Classify waste from uploaded image"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'error': 'No image provided',
                'success': False
            }, status=400)
        
        image_file = request.FILES['image']
        
        # Validate image
        if image_file.size > 10 * 1024 * 1024:  # 10MB limit
            return JsonResponse({
                'error': 'Image too large. Maximum size is 10MB',
                'success': False
            }, status=400)
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Classify waste
        try:
            from .waste_classifier import get_waste_classifier
            classifier = get_waste_classifier()
            result = classifier.classify_from_bytes(image_bytes)
        except Exception as e:
            logger.error(f"Error importing or using waste classifier: {e}")
            # Return a default classification
            result = {
                'category': 'General Waste',
                'confidence': 0.5,
                'all_predictions': [],
                'success': False,
                'error': 'Classification service temporarily unavailable'
            }
        
        # Map category name to category ID
        if result['success']:
            from .models import WasteCategory
            try:
                category = WasteCategory.objects.get(name=result['category'])
                result['category_id'] = category.id
                result['category_name'] = category.name
                result['category_color'] = category.color_code
                result['category_icon'] = category.icon or category.get_icon()
            except WasteCategory.DoesNotExist:
                # Fallback to General Waste
                category = WasteCategory.objects.filter(name='General Waste').first()
                if category:
                    result['category_id'] = category.id
                    result['category_name'] = category.name
                else:
                    result['category_id'] = None
        
        return JsonResponse(result, status=200)
        
    except Exception as e:
        import traceback
        logger.error(f"Error classifying waste image: {e}\n{traceback.format_exc()}")
        return JsonResponse({
            'error': f'Error processing image: {str(e)}',
            'success': False
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_location(request):
    """Update location coordinates for household or collector"""
    try:
        data = json.loads(request.body)
        lat = data.get('latitude')
        lon = data.get('longitude')
        user_type = data.get('user_type', 'household')  # 'household' or 'collector'
        
        if not lat or not lon:
            return JsonResponse({
                'error': 'Latitude and longitude are required',
                'success': False
            }, status=400)
        
        if user_type == 'household':
            try:
                household = request.user.household_profile
                household.latitude = float(lat)
                household.longitude = float(lon)
                household.save()
                return JsonResponse({
                    'message': 'Location updated successfully',
                    'success': True
                }, status=200)
            except Household.DoesNotExist:
                return JsonResponse({
                    'error': 'Household profile not found',
                    'success': False
                }, status=404)
        elif user_type == 'collector':
            try:
                collector = request.user.collector_profile
                collector.latitude = float(lat)
                collector.longitude = float(lon)
                collector.save()
                return JsonResponse({
                    'message': 'Location updated successfully',
                    'success': True
                }, status=200)
            except Collector.DoesNotExist:
                return JsonResponse({
                    'error': 'Collector profile not found',
                    'success': False
                }, status=404)
        else:
            return JsonResponse({
                'error': 'Invalid user type',
                'success': False
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format',
            'success': False
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error updating location: {str(e)}',
            'success': False
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_nearby_collectors(request):
    """Get nearby collectors for a household"""
    try:
        household = request.user.household_profile
        
        if not household.has_location():
            return JsonResponse({
                'error': 'Household location not set',
                'success': False
            }, status=400)
        
        from .geocoding import find_nearby_collectors
        max_distance = float(request.GET.get('max_distance', 10.0))
        
        nearby = find_nearby_collectors(
            float(household.latitude),
            float(household.longitude),
            max_distance_km=max_distance
        )
        
        collectors_data = [{
            'id': item['collector'].id,
            'name': item['collector'].user.get_full_name() or item['collector'].user.username,
            'phone': item['collector'].phone_number,
            'distance_km': item['distance_km'],
            'latitude': float(item['collector'].latitude),
            'longitude': float(item['collector'].longitude),
        } for item in nearby]
        
        return JsonResponse({
            'collectors': collectors_data,
            'success': True
        }, status=200)
        
    except Household.DoesNotExist:
        return JsonResponse({
            'error': 'Household profile not found',
            'success': False
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Error: {str(e)}',
            'success': False
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_nearby_pickups(request):
    """Get nearby pickup requests for a collector"""
    try:
        collector = request.user.collector_profile
        
        if not collector.has_location():
            return JsonResponse({
                'error': 'Collector location not set',
                'success': False
            }, status=400)
        
        from .geocoding import find_nearby_pickups
        max_distance = float(request.GET.get('max_distance', 10.0))
        
        nearby = find_nearby_pickups(
            float(collector.latitude),
            float(collector.longitude),
            max_distance_km=max_distance
        )
        
        pickups_data = [{
            'id': item['pickup'].id,
            'household_name': item['pickup'].household.user.get_full_name() or item['pickup'].household.user.username,
            'address': item['pickup'].address,
            'waste_category': item['pickup'].waste_category.name,
            'quantity': float(item['pickup'].quantity),
            'distance_km': item['distance_km'],
            'latitude': float(item['pickup'].latitude),
            'longitude': float(item['pickup'].longitude),
        } for item in nearby]
        
        return JsonResponse({
            'pickups': pickups_data,
            'success': True
        }, status=200)
        
    except Collector.DoesNotExist:
        return JsonResponse({
            'error': 'Collector profile not found',
            'success': False
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Error: {str(e)}',
            'success': False
        }, status=500)


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with better error handling"""
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('registration:password_reset_done')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, f"No account found with email: {email}. Please check your email address or sign up for a new account.")
            return self.form_invalid(form)
        
        # Call parent to send email
        result = super().form_valid(form)
        messages.success(self.request, f"If an account exists with email {email}, you will receive password reset instructions.")
        return result


@csrf_exempt
@require_http_methods(["POST"])
def resend_otp(request):
    """Resend OTP"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        phone_number = data.get('phoneNumber') or data.get('phone_number')
        
        if not phone_number:
            return JsonResponse({"error": "Phone number is required"}, status=400)
        
        # Generate new 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Create new OTP record
        otp = OTP.objects.create(phoneNumber=phone_number, otp=otp_code)
        
        return JsonResponse({"message": "OTP resent", "otp": otp_code, "success": True}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
