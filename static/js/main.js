/**
 * Main JavaScript file for the Study Assistant application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Year is now set directly in the base template

    // File upload validation and input enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.value.split('\\').pop();
            
            // Check file extension
            if (fileName) {
                const fileExtension = fileName.split('.').pop().toLowerCase();
                const allowedExtensions = ['pdf', 'txt', 'docx'];
                
                if (!allowedExtensions.includes(fileExtension)) {
                    alert(`File type not supported. Please upload ${allowedExtensions.join(', ')} files.`);
                    this.value = ''; // Clear the file input
                }
            }
        });
    });

    // Form validation for required fields
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let valid = true;
            
            // Check if file or text is provided in forms that require one or the other
            if (form.querySelector('input[type="file"]') && form.querySelector('textarea')) {
                const fileInput = form.querySelector('input[type="file"]');
                const textInput = form.querySelector('textarea');
                
                // If the form requires at least one input source but neither is provided
                if (fileInput.hasAttribute('required') && textInput.hasAttribute('required') &&
                    !fileInput.files.length && !textInput.value.trim()) {
                    alert('Please either upload a file or enter text directly.');
                    valid = false;
                }
            }
            
            if (!valid) {
                event.preventDefault();
            }
        });
    });

    // Add loading indicators for form submissions
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                // Store the original button content
                const originalContent = submitButton.innerHTML;
                
                // Update button to show loading state
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
                submitButton.disabled = true;
                
                // Reset button after 30 seconds (in case the form submission takes too long or fails)
                setTimeout(() => {
                    if (submitButton.disabled) {
                        submitButton.innerHTML = originalContent;
                        submitButton.disabled = false;
                    }
                }, 30000);
            }
        });
    });
});
