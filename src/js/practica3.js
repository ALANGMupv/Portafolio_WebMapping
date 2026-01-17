function openPdfModalWithFile(pdfPath) {
    const iframe = document.querySelector('#pdfModal .pdf-viewer');
    iframe.src = pdfPath;
    document.getElementById('pdfModal').classList.add('active');
}
