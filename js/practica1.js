// Funciones para el modal del PDF
function openPdfModal() {
    document.getElementById('pdfModal').classList.add('active');
}

function closePdfModal() {
    document.getElementById('pdfModal').classList.remove('active');
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

// Función para abrir visor de imágenes
function openImageViewer(imageId) {
    // TODO: Implementar la lógica para mostrar la imagen específica
    document.getElementById('imageModal').classList.add('active');
    console.log('Abriendo imagen:', imageId);
}

// Animación de entrada
document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('.section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';

        setTimeout(() => {
            section.style.transition = 'all 0.6s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
});