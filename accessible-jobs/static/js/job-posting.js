// static/js/job-posting.js
console.log('🚀 Job posting script cargado');

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
    // VALIDACIÓN DE LENGUAJE INCLUSIVO
    // ==========================================
    console.log('🔍 Inicializando validador de lenguaje inclusivo');
    
    const languageFields = ['title', 'description', 'responsibilities', 'requirements',
                           'accessibility_features', 'benefits', 'reasonable_accommodations',
                           'workplace_accessibility', 'non_discrimination_statement'];
    
    let languageErrors = {};
    
    languageFields.forEach(name => {
        const field = document.querySelector(`[name="${name}"]`);
        if (field) {
            console.log(`✅ Campo para validación: ${name}`);
            field.addEventListener('input', function() {
                clearTimeout(this.languageTimer);
                this.languageTimer = setTimeout(() => {
                    console.log(`🔎 Validando lenguaje en: ${name}`);
                    validateLanguage(name, this.value);
                }, 500);
            });
        } else {
            console.warn(`⚠️ Campo no encontrado: ${name}`);
        }
    });
    
    async function validateLanguage(name, text) {
        if (!text.trim()) {
            clearLanguageError(name);
            return;
        }
        
        const formData = new FormData();
        formData.append('text', text);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        try {
            const response = await fetch('/company/validate-language/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                console.error('❌ Error HTTP:', response.status);
                return;
            }
            
            const data = await response.json();
            console.log('📊 Respuesta:', data);
            
            if (data.issues && data.issues.length > 0) {
                console.log(`🚨 ${data.issues.length} problemas en ${name}`);
                languageErrors[name] = data.issues;
                showLanguageError(name, data.issues);
            } else {
                console.log(`✅ Sin problemas en ${name}`);
                clearLanguageError(name);
            }
            
            updateSubmitButton();
        } catch (error) {
            console.error('❌ Error de red:', error);
        }
    }
    
    function showLanguageError(name, issues) {
        const field = document.querySelector(`[name="${name}"]`);
        field.style.borderColor = '#dc3545';
        field.style.borderWidth = '3px';
        field.style.backgroundColor = '#fff5f5';
        
        // Remover error anterior si existe
        let errorDiv = field.parentElement.querySelector('.language-error-msg');
        if (errorDiv) errorDiv.remove();
        
        // Crear nuevo mensaje de error
        errorDiv = document.createElement('div');
        errorDiv.className = 'language-error-msg alert alert-danger mt-2 mb-0';
        errorDiv.style.borderLeft = '4px solid #dc3545';
        
        let html = '<strong><i class="fas fa-exclamation-triangle me-2"></i>Términos no inclusivos detectados:</strong>';
        html += '<ul class="mb-0 mt-2 ms-3">';
        issues.forEach(issue => {
            html += `<li class="mb-1">`;
            html += `<strong class="text-danger">"${escapeHtml(issue.term)}"</strong> `;
            html += `→ <em class="text-success">${escapeHtml(issue.suggestion)}</em>`;
            html += `</li>`;
        });
        html += '</ul>';
        errorDiv.innerHTML = html;
        
        field.parentElement.appendChild(errorDiv);
    }
    
    function clearLanguageError(name) {
        delete languageErrors[name];
        
        const field = document.querySelector(`[name="${name}"]`);
        if (!field) return;
        
        field.style.borderColor = '';
        field.style.borderWidth = '';
        field.style.backgroundColor = '';
        
        const errorDiv = field.parentElement.querySelector('.language-error-msg');
        if (errorDiv) errorDiv.remove();
        
        updateSubmitButton();
    }
    
    function updateSubmitButton() {
        const submitBtn = document.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        
        const hasLanguageErrors = Object.keys(languageErrors).length > 0;
        
        submitBtn.disabled = hasLanguageErrors;
        submitBtn.style.opacity = hasLanguageErrors ? '0.5' : '1';
        submitBtn.style.cursor = hasLanguageErrors ? 'not-allowed' : 'pointer';
        
        if (hasLanguageErrors) {
            const errorCount = Object.keys(languageErrors).length;
            submitBtn.innerHTML = `🚫 Corrija ${errorCount} campo(s) con lenguaje no inclusivo`;
        } else {
            const isEdit = submitBtn.textContent.includes('Actualizar');
            submitBtn.innerHTML = isEdit 
                ? '<i class="fas fa-paper-plane me-2"></i>Actualizar Oferta'
                : '<i class="fas fa-paper-plane me-2"></i>Publicar Oferta';
        }
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

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
    // ==========================================
    const legalFields = {
        'id_reasonable_accommodations': 50,
        'id_workplace_accessibility': 50,
        'id_non_discrimination_statement': 40
    };

    Object.entries(legalFields).forEach(([fieldId, minChars]) => {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        const legalCounter = document.createElement('small');
        legalCounter.className = 'form-text text-end d-block mt-1 fw-bold';
        
        const updateLegalCounter = () => {
            const len = field.value.length;
            legalCounter.textContent = `${len}/${minChars} caracteres mínimos (obligatorio)`;
            legalCounter.style.color = len < minChars ? '#dc3545' : '#28a745';
            
            if (len > 0 && len < minChars) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
            } else if (len >= minChars) {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        };
        
        field.addEventListener('input', updateLegalCounter);
        
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
        // BLOQUEAR SI HAY ERRORES DE LENGUAJE
        if (Object.keys(languageErrors).length > 0) {
            e.preventDefault();
            e.stopPropagation();
            alert('❌ No puede enviar el formulario.\n\n' +
                  'Se detectaron términos no inclusivos en ' + Object.keys(languageErrors).length + ' campo(s).\n\n' +
                  'Por favor corrija los términos marcados en rojo antes de continuar.');
            console.log('🛑 Envío bloqueado por errores de lenguaje');
            return false;
        }
        
        const invalidFields = form.querySelectorAll('.is-invalid');
        
        if (invalidFields.length > 0) {
            e.preventDefault();
            alert('⚠️ Por favor corrige los errores marcados en rojo antes de continuar.\n\nRevisa especialmente los campos de cumplimiento legal que requieren un mínimo de caracteres.');
            invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
        
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
    console.log('✅ Sistema de validación de lenguaje activo');
});