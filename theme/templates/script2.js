// --- SHARED UTILITY FUNCTIONS ---

/**
 * Toggles the mobile navigation menu.
 */
document.addEventListener('DOMContentLoaded', () => {
  const navbarToggle = document.getElementById('navbar-toggle');
  const navbarMobile = document.getElementById('navbar-mobile');

  if (navbarToggle && navbarMobile) {
    navbarToggle.addEventListener('click', () => {
      navbarMobile.classList.toggle('hidden');
    });
  }
});

/**
 * Gets a parameter from the URL query string.
 * @param {string} name The name of the parameter to get.
 * @returns {string} The value of the parameter.
 */
function getUrlParameter(name) {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  const results = regex.exec(location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}


// --- STATIC DATA (Temporary In-Memory Database) ---
// In a real application, this data would be fetched from a backend API.

const hospitals = [
  {
    id: '1',
    name: 'Korle Bu Teaching Hospital',
    location: 'Accra',
    address: 'Guggisberg Ave, Accra',
    phoneNumber: '+233 30 266 5401',
    email: 'info@kbth.gov.gh',
    description: 'The Korle Bu Teaching Hospital is the premier healthcare facility in Ghana. It is the only public tertiary hospital in the southern part of the country.',
    image: 'images/korle-bu.jpg',
    equipment: [
      { name: 'MRI Machine', description: 'Advanced magnetic resonance imaging for detailed internal body scans.' },
      { name: 'CT Scanner', description: 'Computed tomography for cross-sectional imaging.' },
      { name: 'X-Ray Machine', description: 'Digital X-ray for bone and tissue imaging.' }
    ]
  },
  {
    id: '2',
    name: '37 Military Hospital',
    location: 'Accra',
    address: 'Liberation Rd, Accra',
    phoneNumber: '+233 30 277 6111',
    email: 'info@37militaryhospital.com.gh',
    description: 'A specialist hospital located in Accra, providing high-quality medical services to military personnel and the general public.',
    image: 'images/37-military.jpg',
    equipment: [
      { name: 'Ultrasound Scanner', description: 'High-frequency sound waves to create images of organs and structures inside the body.' },
      { name: 'Ventilator', description: 'Provides mechanical ventilation by moving breathable air into and out of the lungs.' },
      { name: 'Dialysis Machine', description: 'For patients with kidney failure.' }
    ]
  },
  {
    id: '3',
    name: 'Komfo Anokye Teaching Hospital',
    location: 'Kumasi',
    address: 'Okomfo Anokye Rd, Kumasi',
    phoneNumber: '+233 32 202 2321',
    email: 'info@kathhsp.org',
    description: 'The second-largest hospital in Ghana, located in Kumasi. It is the main referral hospital for the Ashanti, Brong Ahafo, and northern regions of Ghana.',
    image: 'images/komfo-anokye.jpg',
    equipment: [
      { name: 'Incubator', description: 'For providing a controlled environment for premature infants.' },
      { name: 'ECG Machine', description: 'Electrocardiogram to record the electrical signal from the heart.' },
      { name: 'Surgical Microscope', description: 'For high-precision microsurgery.' }
    ]
  },
  {
    id: '4',
    name: 'Ridge Hospital',
    location: 'Accra',
    address: 'Castle Rd, Accra',
    phoneNumber: '+233 30 222 8382',
    email: 'info@ridgehospital.gov.gh',
    description: 'The Greater Accra Regional Hospital, also known as Ridge Hospital, is a major public hospital with modern facilities.',
    image: 'images/ridge-hospital.jpg',
    equipment: [
      { name: 'MRI Machine', description: 'Advanced magnetic resonance imaging for detailed internal body scans.' },
      { name: 'Laparoscopic Instruments', description: 'For minimally invasive surgery.' },
      { name: 'Anesthesia Machine', description: 'Delivers a precisely-known but variable gas mixture.' }
    ]
  }
];

const doctors = [
  {
    id: '101',
    hospitalId: '1',
    name: 'Dr. Ama Mensah',
    specialty: 'Cardiology',
    title: 'Senior Cardiologist',
    experience: 15,
    bio: 'Dr. Ama Mensah is a renowned cardiologist with over 15 years of experience in treating cardiovascular diseases. She is known for her patient-centric approach and dedication to cardiac care.',
    education: 'University of Ghana Medical School, Fellowship at Johns Hopkins Hospital',
    image: 'images/doctor-ama-mensah.jpg',
    availability: {
      "Monday": ["09:00 AM", "10:00 AM", "11:00 AM"],
      "Wednesday": ["02:00 PM", "03:00 PM"],
      "Friday": ["09:00 AM", "10:00 AM"]
    }
  },
  {
    id: '102',
    hospitalId: '1',
    name: 'Dr. Kwaku Osei',
    specialty: 'Neurology',
    title: 'Consultant Neurologist',
    experience: 12,
    bio: 'Dr. Kwaku Osei specializes in the diagnosis and treatment of neurological disorders, including stroke, epilepsy, and multiple sclerosis.',
    education: 'KNUST School of Medical Sciences, Residency at Cleveland Clinic',
    image: 'images/doctor-kwaku-osei.jpg',
    availability: {
      "Tuesday": ["10:00 AM", "11:00 AM", "12:00 PM"],
      "Thursday": ["01:00 PM", "02:00 PM"]
    }
  },
  {
    id: '201',
    hospitalId: '2',
    name: 'Dr. Esi Addo',
    specialty: 'Pediatrics',
    title: 'Senior Pediatrician',
    experience: 20,
    bio: 'With two decades of experience, Dr. Esi Addo is a leading expert in child health, from infancy through adolescence.',
    education: 'University of Cape Coast School of Medical Sciences',
    image: 'images/doctor-esi-addo.jpg',
    availability: {
      "Monday": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
      "Wednesday": ["09:00 AM", "10:00 AM"],
      "Friday": ["02:00 PM", "03:00 PM"]
    }
  },
  {
    id: '202',
    hospitalId: '2',
    name: 'Dr. Ben Carter',
    specialty: 'Orthopedics',
    title: 'Orthopedic Surgeon',
    experience: 18,
    bio: 'Dr. Ben Carter is a highly skilled orthopedic surgeon specializing in joint replacement and sports injuries.',
    education: 'University of Ghana Medical School',
    image: 'images/doctor-ben-carter.jpg',
    availability: {
      "Tuesday": ["08:00 AM", "09:00 AM", "10:00 AM"],
      "Thursday": ["08:00 AM", "09:00 AM", "10:00 AM"]
    }
  },
  {
    id: '301',
    hospitalId: '3',
    name: 'Dr. Fatima Al-Hassan',
    specialty: 'Dermatology',
    title: 'Consultant Dermatologist',
    experience: 10,
    bio: 'Dr. Al-Hassan provides expert care for a wide range of skin conditions, with a focus on both medical and cosmetic dermatology.',
    education: 'UDS School of Medicine, Tamale',
    image: 'images/doctor-fatima.jpg',
    availability: {
      "Monday": ["01:00 PM", "02:00 PM", "03:00 PM"],
      "Wednesday": ["10:00 AM", "11:00 AM"],
      "Friday": ["10:00 AM", "11:00 AM"]
    }
  },
  {
    id: '401',
    hospitalId: '4',
    name: 'Dr. John Appiah',
    specialty: 'General Surgery',
    title: 'Chief of Surgery',
    experience: 25,
    bio: 'Dr. John Appiah is a veteran general surgeon with extensive experience in a wide variety of surgical procedures.',
    education: 'University of Ghana Medical School',
    image: 'images/doctor-john-appiah.jpg',
    availability: {
      "Tuesday": ["09:00 AM", "11:00 AM"],
      "Thursday": ["09:00 AM", "11:00 AM"]
    }
  }
];


// Note: The 'hidden' class toggle for the mobile menu assumes you have a CSS rule like:
/*
.navbar-mobile.hidden {
  display: none;
}
*/

// In your styles.css, you might need to add this if it's not already there.
// The mobile menu is often hidden by default on larger screens using media queries.
/*
.navbar-mobile {
  display: none; // Hidden by default
}
.navbar-mobile:not(.hidden) {
  display: block; // Shown when not hidden
}
*/