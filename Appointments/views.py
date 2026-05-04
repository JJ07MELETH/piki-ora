from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import User, Doctor, AppointmentSlot, Appointment
from .forms import RegisterForm, LoginForm, DoctorForm, SlotForm


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Auth ─────────────────────────────────────────────────────────────────────

def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_patient = True
            user.is_admin = False
            user.save()
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('admin_dashboard' if user.is_admin else 'patient_dashboard')
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Patient ───────────────────────────────────────────────────────────────────

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(
        patient=request.user, status='confirmed'
    ).select_related('slot__doctor').order_by('slot__date', 'slot__start_time')
    return render(request, 'patient_dashboard.html', {'appointments': appointments})


@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})


@login_required
def available_slots(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slots = AppointmentSlot.objects.filter(doctor=doctor, is_booked=False).order_by('date', 'start_time')
    return render(request, 'available_slots.html', {'doctor': doctor, 'slots': slots})


@login_required
def book_appointment(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    if slot.is_booked:
        messages.error(request, 'Sorry, that slot has just been booked.')
        return redirect('available_slots', doctor_id=slot.doctor.id)
    if request.method == 'POST':
        try:
            slot.is_booked = True
            slot.save()
            Appointment.objects.create(patient=request.user, slot=slot, status='confirmed')
            messages.success(request, 'Appointment booked successfully!')
            return redirect('my_appointments')
        except IntegrityError:
            messages.error(request, 'That slot was just taken. Please choose another.')
            return redirect('available_slots', doctor_id=slot.doctor.id)
    return render(request, 'book_appointment.html', {'slot': slot})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('slot__doctor').order_by('-slot__date')
    return render(request, 'my_appointments.html', {'appointments': appointments})


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.slot.is_booked = False
        appointment.slot.save()
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
    return redirect('my_appointments')


# ── Admin dashboard ───────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    context = {
        'total_doctors': Doctor.objects.count(),
        'total_slots': AppointmentSlot.objects.count(),
        'total_appointments': Appointment.objects.filter(status='confirmed').count(),
        'total_patients': User.objects.filter(is_patient=True).count(),
        'recent_appointments': Appointment.objects.select_related(
            'patient', 'slot__doctor'
        ).order_by('-created_at')[:5],
    }
    return render(request, 'admin_dashboard.html', context)


@admin_required
def manage_doctors(request):
    doctors = Doctor.objects.all()
    return render(request, 'manage_doctors.html', {'doctors': doctors})


@admin_required
def add_doctor(request):
    form = DoctorForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Doctor added.')
        return redirect('manage_doctors')
    return render(request, 'doctor_form.html', {'form': form, 'title': 'Add Doctor'})


@admin_required
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        messages.success(request, 'Doctor updated.')
        return redirect('manage_doctors')
    return render(request, 'doctor_form.html', {'form': form, 'title': 'Edit Doctor'})


@admin_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor deleted.')
    return redirect('manage_doctors')


@admin_required
def manage_slots(request):
    slots = AppointmentSlot.objects.select_related('doctor').order_by('date', 'start_time')
    return render(request, 'manage_slots.html', {'slots': slots})


@admin_required
def add_slot(request):
    form = SlotForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Slot added.')
        return redirect('manage_slots')
    return render(request, 'slot_form.html', {'form': form, 'title': 'Add Slot'})


@admin_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Slot deleted.')
    return redirect('manage_slots')


@admin_required
def all_appointments(request):
    appointments = Appointment.objects.select_related(
        'patient', 'slot__doctor'
    ).order_by('-created_at')
    return render(request, 'all_appointments.html', {'appointments': appointments})


@admin_required
def admin_cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.slot.is_booked = False
        appointment.slot.save()
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
    return redirect('all_appointments')


@admin_required
def manage_patients(request):
    patients = User.objects.filter(is_patient=True)
    return render(request, 'manage_patients.html', {'patients': patients})


@admin_required
def delete_patient(request, user_id):
    patient = get_object_or_404(User, id=user_id, is_patient=True)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient deleted.')
    return redirect('manage_patients')