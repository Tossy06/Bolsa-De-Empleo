document.addEventListener('DOMContentLoaded', function() {
    // Mejorar la experiencia del usuario con validación en tiempo real
    const form = document.getElementById('jobForm');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            // Agregar clases visuales para campos válidos/inválidos
            if (this.value.trim()) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    });

    // Validación de rango de salarios
    const salaryMin = document.getElementById('id_salary_min');
    const salaryMax = document.getElementById('id_salary_max');
    
    function validateSalaryRange() {
        if (salaryMin.value && salaryMax.value) {
            const min = parseFloat(salaryMin.value);
            const max = parseFloat(salaryMax.value);
            
            if (min >= max) {
                salaryMax.setCustomValidity('El salario máximo debe ser mayor al mínimo');
                salaryMax.classList.add('is-invalid');
            } else {
                salaryMax.setCustomValidity('');
                salaryMax.classList.remove('is-invalid');
                salaryMax.classList.add('is-valid');
            }
        }
    }
    
    if (salaryMin && salaryMax) {
        salaryMin.addEventListener('blur', validateSalaryRange);
        salaryMax.addEventListener('blur', validateSalaryRange);
    }

    // Contador de caracteres para textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.style.fontSize = '0.75rem';
        
        function updateCounter() {
            const length = textarea.value.length;
            counter.textContent = `${length} caracteres`;
            
            if (length > 500) {
                counter.style.color = '#dc3545';
            } else if (length > 300) {
                counter.style.color = '#fd7e14';
            } else {
                counter.style.color = '#6c757d';
            }
        }
        
        textarea.addEventListener('input', updateCounter);
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        updateCounter();
    });
});