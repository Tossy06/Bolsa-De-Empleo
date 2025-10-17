document.addEventListener('DOMContentLoaded', function() {
    const fields = ['title', 'description', 'responsibilities', 'requirements',
                    'accessibility_features', 'benefits', 'reasonable_accommodations',
                    'workplace_accessibility', 'non_discrimination_statement'];
    
    let errors = {};
    
    fields.forEach(name => {
        const field = document.querySelector(`[name="${name}"]`);
        if (!field) return;
        
        field.addEventListener('input', function() {
            clearTimeout(this.timer);
            this.timer = setTimeout(() => validate(name, this.value), 500);
        });
    });
    
    async function validate(name, text) {
        if (!text.trim()) {
            clearError(name);
            return;
        }
        
        const formData = new FormData();
        formData.append('text', text);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        const response = await fetch('/companies/validate-language/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.issues && data.issues.length > 0) {
            errors[name] = data.issues;
            showError(name, data.issues);
        } else {
            clearError(name);
        }
        
        updateButton();
    }
    
    function showError(name, issues) {
        const field = document.querySelector(`[name="${name}"]`);
        field.style.borderColor = '#dc3545';
        field.style.borderWidth = '2px';
        field.style.backgroundColor = '#fff5f5';
        
        let div = field.parentElement.querySelector('.error-msg');
        if (!div) {
            div = document.createElement('div');
            div.className = 'error-msg alert alert-danger mt-2';
            field.parentElement.appendChild(div);
        }
        
        let html = '<strong>⚠️ Términos no inclusivos:</strong><ul class="mb-0">';
        issues.forEach(i => {
            html += `<li>"<strong>${i.term}</strong>" → ${i.suggestion}</li>`;
        });
        html += '</ul>';
        div.innerHTML = html;
    }
    
    function clearError(name) {
        delete errors[name];
        
        const field = document.querySelector(`[name="${name}"]`);
        field.style.borderColor = '';
        field.style.borderWidth = '';
        field.style.backgroundColor = '';
        
        const div = field.parentElement.querySelector('.error-msg');
        if (div) div.remove();
        
        updateButton();
    }
    
    function updateButton() {
        const btn = document.querySelector('button[type="submit"]');
        const hasErrors = Object.keys(errors).length > 0;
        
        btn.disabled = hasErrors;
        btn.style.opacity = hasErrors ? '0.5' : '1';
        btn.innerHTML = hasErrors 
            ? '🚫 Corrija los errores' 
            : '<i class="fas fa-paper-plane me-2"></i>Publicar Oferta';
    }
    
    document.getElementById('jobForm').addEventListener('submit', function(e) {
        if (Object.keys(errors).length > 0) {
            e.preventDefault();
            alert('No puede enviar. Corrija los términos marcados en rojo.');
        }
    });
});