document.addEventListener('DOMContentLoaded', function() {
  // Set copyright year
  document.getElementById('current-year').innerText = new Date().getFullYear();
  
  const form = document.getElementById('appointment-form');
  const hospitalSelect = document.getElementById('hospitalId');
  const doctorSelect = document.getElementById('doctorId');
  const dateInput = document.getElementById('date');
  const timeSelect = document.getElementById('time');
  const submitBtn = document.getElementById('submit-btn');
  const availableDaysInfo = document.getElementById('available-days');
  const daysList = document.getElementById('days-list');
  
  let currentDoctors = []; // To store doctors of the selected hospital
  
  // Set minimum date to today
  const today = new Date().toISOString().split('T')[0];
  dateInput.min = today;
  
  // Fetch and populate hospitals from backend API
  fetch('http://localhost:5000/api/hospitals')
    .then(response => response.json())
    .then(hospitals => {
      hospitals.forEach(hospital => {
        const option = document.createElement('option');
        option.value = hospital.id;
        option.textContent = hospital.name;
        hospitalSelect.appendChild(option);
      });
    })
    .catch(error => {
      console.error('Error fetching hospitals:', error);
      alert('Could not load hospitals. Please try again.');
    });
  
  // When hospital changes, update doctors
  hospitalSelect.addEventListener('change', function() {
    const hospitalId = this.value;

    // Reset and disable subsequent fields
    doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
    doctorSelect.disabled = true;
    dateInput.value = '';
    dateInput.disabled = true;
    timeSelect.innerHTML = '<option value="">Select a time</option>';
    timeSelect.disabled = true;
    submitBtn.disabled = true;
    availableDaysInfo.classList.add('hidden');

    if (!hospitalId) return;

    // Fetch doctors from backend
    fetch(`http://localhost:5000/api/doctors?hospitalId=${hospitalId}`)
      .then(response => response.json())
      .then(doctors => {
        currentDoctors = doctors; // Store the fetched doctors
        doctors.forEach(doctor => {
          const option = document.createElement('option');
          option.value = doctor.id;
          option.textContent = `${doctor.name} - ${doctor.specialty}`;
          doctorSelect.appendChild(option);
        });
        doctorSelect.disabled = false;
      })
      .catch(error => {
        console.error('Error fetching doctors:', error);
        alert('Could not load doctors for this hospital.');
      });
  });

  // When doctor changes, enable date input and show availability
  doctorSelect.addEventListener('change', function() {
    const doctorId = this.value;
    
    // Reset date and time
    dateInput.value = '';
    dateInput.disabled = true;
    timeSelect.innerHTML = '<option value="">Select a time</option>';
    timeSelect.disabled = true;
    submitBtn.disabled = true;
    availableDaysInfo.classList.add('hidden');

    if (!doctorId) return;

    const selectedDoctor = currentDoctors.find(d => d.id == doctorId);
    if (selectedDoctor && selectedDoctor.availability) {
      const availableDays = Object.keys(selectedDoctor.availability);
      daysList.textContent = availableDays.join(', ');
      availableDaysInfo.classList.remove('hidden');
      dateInput.disabled = false;
      // Store availability on the date input for later use
      dateInput.dataset.availability = JSON.stringify(selectedDoctor.availability);
    }
  });

  // When date changes, populate available times
  dateInput.addEventListener('change', function() {
    timeSelect.innerHTML = '<option value="">Select a time</option>';
    timeSelect.disabled = true;
    const selectedDate = new Date(this.value + 'T00:00:00'); // Use T00:00:00 to avoid timezone issues
    const dayOfWeek = selectedDate.toLocaleDateString('en-US', { weekday: 'long' });
    const availability = JSON.parse(this.dataset.availability || '{}');

    if (availability[dayOfWeek]) {
      availability[dayOfWeek].forEach(time => {
        const option = document.createElement('option');
        option.value = time;
        option.textContent = time;
        timeSelect.appendChild(option);
      });
      timeSelect.disabled = false;
    }
  });

  
  // When time changes, enable submit button
  timeSelect.addEventListener('change', function() {
    submitBtn.disabled = !this.value;
  });
  
  // Handle form submission
  form.addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = {
      full_name: document.getElementById('fullName').value,
      email: document.getElementById('email').value,
      phone: document.getElementById('phone').value,
      hospital_id: hospitalSelect.value,
      doctor_id: doctorSelect.value,
      date: dateInput.value,
      time: timeSelect.value,
      reason: document.getElementById('reason').value
    };

    // Send data to backend API
    fetch('http://localhost:5000/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          alert('Appointment booked successfully!');
          form.reset();
        } else {
          alert('Failed to book appointment.');
        }
      })
      .catch(error => {
        console.error('Error booking appointment:', error);
        alert('An error occurred while booking. Please try again.');
      });
  });
});