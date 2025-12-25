// Funciones para el modal del PDF
function openPdfModal() {
    document.getElementById('pdfModal').classList.add('active');
}

function closePdfModal() {
    document.getElementById('pdfModal').classList.remove('active');
}

// Toggle del acordeón
function toggleAccordion(element) {
    const section = element.parentElement;
    section.classList.toggle('active');
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const pdfModal = document.getElementById('pdfModal');
    const imageModal = document.getElementById('imageModal');

    if (event.target === pdfModal) {
        closePdfModal();
    }
    if (event.target === imageModal) {
        imageModal.classList.remove('active');
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');
    const dropdown = document.querySelector('.dropdown');
    const dropdownToggle = document.querySelector('.dropdown-toggle');

    // Toggle menú móvil
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Toggle dropdown en móvil
    if (dropdownToggle && window.innerWidth <= 768) {
        dropdownToggle.addEventListener('click', (e) => {
            e.preventDefault();
            dropdown.classList.toggle('active');
        });
    }

    // Cerrar menú al hacer clic en un enlace (excepto el dropdown)
    const navLinks = navMenu.querySelectorAll('a:not(.dropdown-toggle)');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                navMenu.classList.remove('active');
            }
        });
    });

    // Manejar resize de ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            navMenu.classList.remove('active');
            dropdown.classList.remove('active');
        }
    });

    // Animación de entrada de secciones
    const sections = document.querySelectorAll('.section:not(.accordion-section)');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';

        setTimeout(() => {
            section.style.transition = 'all 0.6s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Animación del acordeón
    const accordionSection = document.querySelector('.accordion-section');
    if (accordionSection) {
        accordionSection.style.opacity = '0';
        accordionSection.style.transform = 'translateY(20px)';

        setTimeout(() => {
            accordionSection.style.transition = 'all 0.6s ease';
            accordionSection.style.opacity = '1';
            accordionSection.style.transform = 'translateY(0)';
        }, 0);
    }
});

function openImageModal(src) {
    const modal = document.getElementById('imageModal');
    const img = document.getElementById('modalImage');

    img.src = src;
    modal.classList.add('active');
}
