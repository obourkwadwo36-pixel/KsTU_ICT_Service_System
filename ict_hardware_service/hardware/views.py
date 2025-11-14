from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import ServiceRequest
from .forms import ServiceRequestForm
import re


# your models & forms (adjust names if different)
from .models import ServiceRequest, JobUpdate, Technician, ICTOfficer
from .forms import ServiceRequestForm, JobUpdateForm

@login_required
def dashboard(request):
    # Separate dashboards based on user type
    if hasattr(request.user, 'technician'):
        requests = ServiceRequest.objects.filter(assigned_to=request.user.technician)
        return render(request, 'technician_dashboard.html', {'requests': requests})

    elif hasattr(request.user, 'ictofficer'):
        requests = ServiceRequest.objects.all().order_by('-date_requested')
        return render(request, 'ict_officer_dashboard.html', {'requests': requests})

    else:
        # For normal staff
        requests = ServiceRequest.objects.filter(staff=request.user)
        return render(request, 'staff_dashboard.html', {'requests': requests})

@login_required
def create_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.staff = request.user
            service_request.status = 'Pending'
            service_request.save()
            messages.success(request, 'Your request has been submitted successfully!')
            return redirect('staff_dashboard')
    else:
        form = ServiceRequestForm()

    return render(request, 'create_request.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from .models import ServiceRequest

def request_detail(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    return render(request, 'request_detail.html', {'req': req})

@login_required
def add_job_update(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    technician = get_object_or_404(Technician, user=request.user)

    if request.method == "POST":
        form = JobUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.request = service_request
            update.technician = technician
            update.save()

            # Always update status directly
            service_request.status = form.cleaned_data["status"]
            service_request.save()

            messages.success(request, "Job update saved successfully!")
            return redirect("technician_dashboard")
    else:
        form = JobUpdateForm()

    return render(request, "add_job_update.html", {
        "form": form,
        "service_request": service_request
    })



from django.shortcuts import render, get_object_or_404
from .models import ServiceRequest

@login_required
def request_detail(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)

    # Determine which dashboard the user belongs to
    if hasattr(request.user, 'is_ict_officer') and request.user.is_ict_officer:
        back_url = 'ict_officer_dashboard'
    else:
        back_url = 'staff_dashboard'

    return render(request, 'request_detail.html', {
        'req': req,
        'back_url': back_url
    })

from django.shortcuts import render
from urllib.parse import unquote

@login_required
def ict_officer_dashboard(request):
    status_filter = request.GET.get('status')
    if status_filter:
        status_filter = unquote(status_filter)  # ✅ Decode "In%20Progress" → "In Progress"
        requests = ServiceRequest.objects.filter(status=status_filter)
    else:
        requests = ServiceRequest.objects.all()

    return render(request, 'ict_officer_dashboard.html', {'requests': requests})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ServiceRequest
from .forms import ServiceRequestForm

@login_required
def staff_dashboard(request):
    # Get the logged-in user's service requests
    user_requests = ServiceRequest.objects.filter(staff=request.user).order_by('-date_requested')

    # Handle new request submission directly from dashboard
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.staff = request.user   # ✅ Correct field name
            service_request.status = 'Pending'
            service_request.save()
            return redirect('staff_dashboard')

    else:
        form = ServiceRequestForm()

    return render(request, 'staff_dashboard.html', {
        'form': form,
        'requests': user_requests
    })

from django.contrib import messages
from django.shortcuts import render

@login_required
def technician_dashboard(request):
    # Get the technician profile linked to this user
    technician = get_object_or_404(Technician, user=request.user)

    # Fetch all service requests assigned to this technician
    assigned_requests = ServiceRequest.objects.filter(assigned_to=technician)

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        update_text = request.POST.get('update_text')
        new_status = request.POST.get('status')

        service_request = get_object_or_404(ServiceRequest, id=request_id, assigned_to=technician)

        # Save the job update
        JobUpdate.objects.create(
            request=service_request,
            technician=technician,
            update_text=update_text
        )

        # Update the service request status
        if new_status:
            service_request.status = new_status
            service_request.save()

        messages.success(request, "Job update submitted successfully.")
        return redirect('technician_dashboard')

    return render(request, 'technician_dashboard.html', {
        'requests': assigned_requests
    })

from .forms import AssignTechnicianForm

@login_required
def assign_technician(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    technicians = Technician.objects.select_related('user').all()

    if request.method == 'POST':
        selected_tech_id = request.POST.get('technician')
        if selected_tech_id:
            selected_tech = get_object_or_404(Technician, pk=selected_tech_id)
            req.assigned_to = selected_tech
            req.status = 'Assigned'
            req.save()
            messages.success(request, f"{selected_tech} has been assigned to this request.")
            return redirect('ict_officer_dashboard')

    return render(request, 'assign_technician.html', {'req': req, 'technicians': technicians})


@login_required
def ict_officer_job_history(request):
    history = JobUpdate.objects.select_related('request', 'technician').order_by('-date_updated')

    return render(request, 'ict_officer_job_history.html', {'history': history})



@login_required
def technician_job_history(request):
    technician = get_object_or_404(Technician, user=request.user)
    history = JobUpdate.objects.filter(technician=technician).select_related('request').order_by('-date_updated')

    return render(request, 'technician_job_history.html', {'history': history})


@login_required
def delete_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    req.delete()
    messages.success(request, "Request deleted successfully.")
    return redirect('ict_officer_dashboard')


@login_required
def delete_staff_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, staff=request.user)
    req.delete()
    messages.success(request, "Your request has been deleted successfully.")
    return redirect('staff_dashboard')


def landing_page(request):
    return render(request, 'landing_page.html')

def register(request):
    """
    Register a new user. Includes username (full name) and validates institutional email.
    Creates Technician or ICTOfficer objects when appropriate.
    """
    if request.method == 'POST':
        full_name = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'staff')

        # --- Validate inputs ---
        if not full_name:
            messages.error(request, 'Full name is required.')
            return redirect('register')

        if not re.match(r'^[\w\.\-]+@kstu\.edu\.gh$', email):
            messages.error(request, 'Only institutional emails (example@kstu.edu.gh) are allowed.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return redirect('register')

        # --- Create user ---
        user = User.objects.create_user(
            username=email,   # keep institutional email as login username
            email=email,
            password=password,
            first_name=full_name   # store the person's full name here
        )
        user.save()

        # --- Assign role ---
        if role == 'technician':
            Technician.objects.create(user=user)
        elif role == 'ict_officer':
            ICTOfficer.objects.create(user=user)
        # Staff are plain users

        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')

    return render(request, 'register.html')
    
def login_view(request):
    """
    Authenticate and redirect users to their role dashboard.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)

            # Role-based redirect:
            # Check for role-specific related objects in this order.
            # (Order matters if a user mistakenly has both objects.)
            if hasattr(user, 'ictofficer'):
                return redirect('ict_officer_dashboard')
            if hasattr(user, 'technician'):
                return redirect('technician_dashboard')

            # Default for plain users -> staff dashboard
            return redirect('staff_dashboard')

        messages.error(request, 'Invalid email or password.')
        return redirect('login')

    # GET
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('landing_page')

