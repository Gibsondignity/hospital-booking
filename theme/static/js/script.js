const hospitalSelect = document.getElementById('hospitalId');
const doctorSelect = document.getElementById('doctorId');
const dateInput = document.getElementById('date');
const timeSelect = document.getElementById('time');
const submitBtn = document.getElementById('submit-btn');
const form = document.getElementById('appointment-form');
let doctors = [];

// Fetch hospitals
fetch(HOSPITALS_API)
  .then(response => response.json())
  .then(hospitals => {
    hospitals.forEach(hospital => {
      const option = document.createElement('option');
      option.value = hospital.id;
      option.textContent = hospital.name;
      hospitalSelect.appendChild(option);
    });
  });

hospitalSelect.addEventListener('change', function() {
  const hospitalId = this.value;
  doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
  doctorSelect.disabled = true;
  dateInput.disabled = true;
  timeSelect.disabled = true;
  submitBtn.disabled = true;

  fetch(`${DOCTORS_API}?hospitalId=${hospitalId}`)
    .then(response => response.json())
    .then(data => {
      doctors = data;
      doctors.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor.id;
        option.textContent = `${doctor.name} - ${doctor.specialty}`;
        doctorSelect.appendChild(option);
      });
      doctorSelect.disabled = false;
    });
});

doctorSelect.addEventListener('change', function() {
  dateInput.disabled = !this.value;
  timeSelect.disabled = true;
  submitBtn.disabled = true;
});

dateInput.addEventListener('change', function() {
  const selectedDate = this.value;
  const selectedDoctorId = doctorSelect.value;

  timeSelect.innerHTML = '<option value="">Select a time</option>';
  timeSelect.disabled = true;
  submitBtn.disabled = true;

  if (selectedDate && selectedDoctorId) {
    const selectedDoctor = doctors.find(d => d.id == selectedDoctorId);
    const dayOfWeek = new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long' });

    const availableTimes = selectedDoctor.availability[dayOfWeek];

    if (availableTimes && availableTimes.length > 0) {
      availableTimes.forEach(time => {
        const option = document.createElement('option');
        option.value = time;
        option.textContent = time;
        timeSelect.appendChild(option);
      });
      timeSelect.disabled = false;
    } else {
      const option = document.createElement('option');
      option.value = "";
      option.textContent = "Doctor not available on this day";
      timeSelect.appendChild(option);
    }
  }
});

timeSelect.addEventListener('change', function() {
  submitBtn.disabled = !this.value;
});

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

  fetch(APPOINTMENTS_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        alert('Appointment booked successfully!');
        form.reset();
        doctorSelect.disabled = true;
        dateInput.disabled = true;
        timeSelect.disabled = true;
        submitBtn.disabled = true;
      } else {
        alert('Failed to book appointment.');
      }
    })
    .catch(error => {
      console.error('Error booking appointment:', error);
      alert('An error occurred while booking.');
    });
});
