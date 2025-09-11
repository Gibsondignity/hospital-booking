// Appointment Booking JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Appointment booking script loaded');
    // DOM Elements
    const hospitalSelect = document.getElementById('hospitalId');
    const serviceSelect = document.getElementById('serviceId');
    const doctorSelect = document.getElementById('doctorId');
    const dateInput = document.getElementById('date');
    const timeSelect = document.getElementById('time');
    const submitBtn = document.getElementById('submit-btn');
    const appointmentForm = document.getElementById('appointment-form');

    // API Endpoints
    const HOSPITALS_API = '/api/hospitals/';
    const DOCTORS_API = '/api/doctors/';
    const SERVICES_API = '/api/services/';
    const APPOINTMENTS_API = '/api/appointments/';

    // Initialize the form
    initializeForm();

    function initializeForm() {
        // Load hospitals on page load
        loadHospitals();

        // Set up event listeners
        hospitalSelect.addEventListener('change', handleHospitalChange);
        doctorSelect.addEventListener('change', handleDoctorChange);
        dateInput.addEventListener('change', handleDateChange);
        appointmentForm.addEventListener('submit', handleFormSubmit);

        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
    }

    async function loadHospitals() {
        try {
            const response = await fetch(HOSPITALS_API);
            const hospitals = await response.json();

            // Clear existing options except the first one
            hospitalSelect.innerHTML = '<option value="">Select a hospital</option>';

            // Add hospitals to dropdown
            hospitals.forEach(hospital => {
                const option = document.createElement('option');
                option.value = hospital.id;
                option.textContent = hospital.name;
                hospitalSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading hospitals:', error);
            showError('Failed to load hospitals. Please refresh the page.');
        }
    }

    async function handleHospitalChange() {
        const hospitalId = hospitalSelect.value;

        if (!hospitalId) {
            // Reset form when no hospital is selected
            resetServiceSelection();
            resetDoctorSelection();
            return;
        }

        // Enable service and doctor selections and load data for this hospital
        serviceSelect.disabled = false;
        doctorSelect.disabled = false;
        await Promise.all([
            loadServices(hospitalId),
            loadDoctors(hospitalId)
        ]);
    }

    async function loadServices(hospitalId) {
        try {
            const response = await fetch(`${SERVICES_API}?hospitalId=${hospitalId}`);
            const services = await response.json();

            // Clear existing options
            serviceSelect.innerHTML = '<option value="">Select a service (optional)</option>';

            // Add services to dropdown
            services.forEach(service => {
                const option = document.createElement('option');
                option.value = service.id;
                option.textContent = `${service.name} (${service.duration} min)`;
                serviceSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading services:', error);
            showError('Failed to load services for this hospital.');
        }
    }

    async function loadDoctors(hospitalId) {
        try {
            const response = await fetch(`${DOCTORS_API}?hospitalId=${hospitalId}`);
            const doctors = await response.json();

            // Clear existing options
            doctorSelect.innerHTML = '<option value="">Select a doctor</option>';

            // Add doctors to dropdown
            doctors.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = doctor.name;
                doctorSelect.appendChild(option);
            });

            // Reset date and time selections
            resetDateTimeSelection();
        } catch (error) {
            console.error('Error loading doctors:', error);
            showError('Failed to load doctors for this hospital.');
        }
    }

    function handleDoctorChange() {
        const doctorId = doctorSelect.value;

        if (!doctorId) {
            resetDateTimeSelection();
            return;
        }

        // Enable date selection
        dateInput.disabled = false;
    }

    function handleDateChange() {
        const selectedDate = dateInput.value;
        const doctorId = doctorSelect.value;

        if (!selectedDate || !doctorId) {
            return;
        }

        // Enable time selection and load available times
        timeSelect.disabled = false;
        loadAvailableTimes(doctorId, selectedDate);
    }

    async function loadAvailableTimes(doctorId, selectedDate) {
        try {
            // Get booked time slots for this doctor and date
            const response = await fetch(`/api/booked-times/?doctorId=${doctorId}&date=${selectedDate}`);
            const bookedTimes = await response.json();

            // Default time slots
            const allTimeSlots = [
                '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
            ];

            // Filter out booked times
            const availableSlots = allTimeSlots.filter(time => !bookedTimes.includes(time));

            // Clear existing options
            timeSelect.innerHTML = '<option value="">Select a time</option>';

            if (availableSlots.length === 0) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No available times for this date';
                option.disabled = true;
                timeSelect.appendChild(option);
                showError('No available time slots for the selected date. Please choose another date.');
                return;
            }

            // Add available time slots to dropdown
            availableSlots.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                option.textContent = time;
                timeSelect.appendChild(option);
            });

            // Enable submit button if all required fields are filled
            checkFormValidity();
        } catch (error) {
            console.error('Error loading available times:', error);
            // Fallback to showing all time slots if API call fails
            const allTimeSlots = [
                '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
            ];

            timeSelect.innerHTML = '<option value="">Select a time</option>';
            allTimeSlots.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                option.textContent = time;
                timeSelect.appendChild(option);
            });
            
            showError('Unable to check time availability. Please verify your selection before booking.');
        }
    }

    function checkFormValidity() {
        const requiredFields = [
            document.getElementById('fullName'),
            document.getElementById('email'),
            document.getElementById('phone'),
            hospitalSelect,
            doctorSelect,
            dateInput,
            timeSelect,
            document.getElementById('reason')
        ];

        const allFilled = requiredFields.every(field => field.value.trim() !== '');
        submitBtn.disabled = !allFilled;

        if (allFilled) {
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    async function handleFormSubmit(event) {
        event.preventDefault();

        // Get form data
        const formData = {
            full_name: document.getElementById('fullName').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            hospital_id: hospitalSelect.value,
            service_id: serviceSelect.value || null, // Optional service
            doctor_id: doctorSelect.value,
            date: dateInput.value,
            time: timeSelect.value,
            reason: document.getElementById('reason').value
        };

        try {
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.textContent = 'Booking...';

            const response = await fetch(APPOINTMENTS_API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                // Show success message
                showSuccess('Appointment booked successfully!');

                // Reset form
                appointmentForm.reset();
                resetFormState();

                // Redirect to success page with appointment ID
                setTimeout(() => {
                    window.location.href = `/appointment-success/${result.appointmentId}/`;
                }, 1500);
            } else {
                throw new Error(result.error || 'Failed to book appointment');
            }
        } catch (error) {
            console.error('Error booking appointment:', error);
            alert(error.message || 'Failed to book appointment. Please try again.');
            showError(error.message || 'Failed to book appointment. Please try again.');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.textContent = 'Book Appointment';
        }
    }

    function resetServiceSelection() {
        serviceSelect.innerHTML = '<option value="">Select a service (optional)</option>';
        serviceSelect.disabled = true;
    }

    function resetDoctorSelection() {
        doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
        doctorSelect.disabled = true;
        resetDateTimeSelection();
    }

    function resetDateTimeSelection() {
        dateInput.value = '';
        dateInput.disabled = true;
        timeSelect.innerHTML = '<option value="">Select a time</option>';
        timeSelect.disabled = true;
        submitBtn.disabled = true;
    }

    function resetFormState() {
        resetServiceSelection();
        resetDoctorSelection();
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }

    function getCSRFToken() {
        // Get CSRF token from cookie
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showSuccess(message) {
        // Remove any existing notifications first
        removeExistingNotifications();
        
        // Create and show success message
        const successDiv = document.createElement('div');
        successDiv.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-8 py-4 rounded-lg shadow-2xl z-[9999] max-w-md text-center border-2 border-green-400';
        successDiv.innerHTML = `
            <div class="flex items-center justify-center space-x-3">
                <i class="fas fa-check-circle text-xl"></i>
                <span class="font-medium">${message}</span>
            </div>
        `;
        successDiv.setAttribute('data-notification', 'true');
        document.body.appendChild(successDiv);

        // Add animation
        successDiv.style.animation = 'slideInFromTop 0.5s ease-out';

        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.style.animation = 'slideOutToTop 0.5s ease-in';
                setTimeout(() => successDiv.remove(), 500);
            }
        }, 4000);
    }

    function showError(message) {
        // Remove any existing notifications first
        removeExistingNotifications();
        
        // Create and show error message with enhanced visibility
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-8 py-4 rounded-lg shadow-2xl z-[9999] max-w-md text-center border-2 border-red-400';
        errorDiv.innerHTML = `
            <div class="flex items-center justify-center space-x-3">
                <i class="fas fa-exclamation-triangle text-xl"></i>
                <div>
                    <div class="font-bold text-sm">Booking Error</div>
                    <div class="text-sm">${message}</div>
                </div>
            </div>
        `;
        errorDiv.setAttribute('data-notification', 'true');
        document.body.appendChild(errorDiv);

        // Add animation
        errorDiv.style.animation = 'slideInFromTop 0.5s ease-out';

        // Auto-remove after 7 seconds (longer for errors so user can read)
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.style.animation = 'slideOutToTop 0.5s ease-in';
                setTimeout(() => errorDiv.remove(), 500);
            }
        }, 7000);

        // Also log to console for debugging
        console.error('Booking Error:', message);
        
        // Scroll to top so user sees the notification
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function removeExistingNotifications() {
        const existingNotifications = document.querySelectorAll('[data-notification="true"]');
        existingNotifications.forEach(notification => notification.remove());
    }

    // Add input event listeners to check form validity
    const inputs = ['fullName', 'email', 'phone', 'reason'];
    inputs.forEach(id => {
        document.getElementById(id).addEventListener('input', checkFormValidity);
    });

    // Initial form validity check
    checkFormValidity();
});

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInFromTop {
        from {
            opacity: 0;
            transform: translate(-50%, -100%);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
    
    @keyframes slideOutToTop {
        from {
            opacity: 1;
            transform: translate(-50%, 0);
        }
        to {
            opacity: 0;
            transform: translate(-50%, -100%);
        }
    }
    
    /* Ensure notifications are always visible */
    [data-notification="true"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
    }
`;
document.head.appendChild(style);