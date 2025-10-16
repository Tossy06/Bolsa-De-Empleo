// static/js/job-posting.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('jobForm');
    const sections = document.querySelectorAll('.form-section, .accessibility-highlight, .legal-compliance');
    const nextBtn = document.querySelector('.btn-next');
    const prevBtn = document.querySelector('.btn-prev');
    const steps = document.querySelectorAll('.step');
    const salaryMin = document.getElementById('id_salary_min');
    const salaryMax = document.getElementById('id_salary_max');
    
    let currentSection = 0;
    let formModified = false;

    // ==========================================
    // NAVEGACIÓN ENTRE SECCIONES
    // ==========================================
    function showSection(index) {
        sections.forEach((s, i) => s.classList.toggle('active', i === index));
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
            step.classList.toggle('completed', i < index);
        });
        prevBtn.disabled = index === 0;
        nextBtn.disabled = index === sections.length - 1;
        sections[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    nextBtn?.addEventListener('click', () => {
        if (currentSection < sections.length - 1) showSection(++currentSection);
    });

    prevBtn?.addEventListener('click', () => {
        if (currentSection > 0) showSection(--currentSection);
    });

    // ==========================================
    // VALIDACIÓN VISUAL EN TIEMPO REAL
    // ==========================================
    form.querySelectorAll('input:not([type="checkbox"]), textarea, select').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim()) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
        
        // Marcar formulario como modificado
        input.addEventListener('change', () => formModified = true);
    });

    // ==========================================
    // VALIDACIÓN DE RANGO DE SALARIOS
    // ==========================================
    function validateSalaryRange() {
        if (salaryMin?.value && salaryMax?.value) {
            const min = parseFloat(salaryMin.value);
            const max = parseFloat(salaryMax.value);
            const isValid = max > min;
            
            salaryMax.setCustomValidity(isValid ? '' : 'El salario máximo debe ser mayor al mínimo');
            salaryMax.classList.toggle('is-invalid', !isValid);
            salaryMax.classList.toggle('is-valid', isValid);
        }
    }
    
    if (salaryMin && salaryMax) {
        salaryMin.addEventListener('blur', validateSalaryRange);
        salaryMax.addEventListener('blur', validateSalaryRange);
    }

    // ==========================================
    // CONTADOR DE CARACTERES PARA TEXTAREAS
    // ==========================================
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.style.fontSize = '0.75rem';
        
        function updateCounter() {
            const length = textarea.value.length;
            counter.textContent = `${length} caracteres`;
            counter.style.color = length > 500 ? '#dc3545' : length > 300 ? '#fd7e14' : '#6c757d';
        }
        
        textarea.addEventListener('input', updateCounter);
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        updateCounter();
    });

    // ==========================================
    // VALIDACIÓN ESPECIAL CAMPOS LEGALES
    // (Mínimo de caracteres obligatorio)
    // ==========================================
    const legalFields = {
        'id_reasonable_accommodations': 50,
        'id_workplace_accessibility': 50,
        'id_non_discrimination_statement': 40
    };

    Object.entries(legalFields).forEach(([fieldId, minChars]) => {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        // Crear contador específico para campos legales
        const legalCounter = document.createElement('small');
        legalCounter.className = 'form-text text-end d-block mt-1 fw-bold';
        
        const updateLegalCounter = () => {
            const len = field.value.length;
            legalCounter.textContent = `${len}/${minChars} caracteres mínimos (obligatorio)`;
            legalCounter.style.color = len < minChars ? '#dc3545' : '#28a745';
            
            // Validación visual
            if (len > 0 && len < minChars) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
            } else if (len >= minChars) {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        };
        
        field.addEventListener('input', updateLegalCounter);
        
        // Insertar después del contador normal si existe
        const existingCounter = field.nextSibling;
        if (existingCounter && existingCounter.classList?.contains('form-text')) {
            existingCounter.parentNode.insertBefore(legalCounter, existingCounter.nextSibling);
        } else {
            field.parentNode.appendChild(legalCounter);
        }
        
        updateLegalCounter();
    });

    // ==========================================
    // VALIDACIÓN ANTES DE ENVIAR FORMULARIO
    // ==========================================
    form.addEventListener('submit', function(e) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        
        if (invalidFields.length > 0) {
            e.preventDefault();
            alert('⚠️ Por favor corrige los errores marcados en rojo antes de continuar.\n\nRevisa especialmente los campos de cumplimiento legal que requieren un mínimo de caracteres.');
            invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
        
        // Permitir envío sin alerta de salida
        formModified = false;
    });

    // ==========================================
    // ALERTA AL SALIR SIN GUARDAR
    // ==========================================
    window.addEventListener('beforeunload', function(e) {
        if (formModified) {
            e.preventDefault();
            e.returnValue = '¿Estás seguro? Tienes cambios sin guardar.';
            return e.returnValue;
        }
    });

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    showSection(0);
});