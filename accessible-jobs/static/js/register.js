// Script para formulario multi-paso con navegación por teclado

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario original
    const userTypeSelect = document.getElementById('id_user_type');
    const disabilitySection = document.getElementById('disability_section');
    
    // Buscar labels por el atributo for que apunta a los campos
    const labelFirstName = document.querySelector('label[for="' + document.getElementById('id_first_name')?.id + '"]');
    const labelLastName = document.querySelector('label[for="' + document.getElementById('id_last_name')?.id + '"]');
    const labelUsername = document.querySelector('label[for="' + document.getElementById('id_username')?.id + '"]');
    
    // Elementos del formulario multi-paso
    const formSteps = document.querySelectorAll('.form-step');
    const stepIndicators = document.querySelectorAll('.step');
    const progressFill = document.getElementById('progressFill');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const userTypeCards = document.querySelectorAll('.user-type-card');
    
    let currentStep = 1;
    const totalSteps = formSteps.length;
    
    // Función original para cambiar labels según tipo de usuario
    function updateLabels() {
        const userType = userTypeSelect.value;
        
        if (userType === 'company' || userType === 'empresa') {
            // Cambiar labels para empresa
            if (labelFirstName) {
                labelFirstName.innerHTML = 'Nombre de la empresa <span style="color: #dc3545; font-weight: bold;"> *</span>';
            }
            if (labelLastName) {
                labelLastName.innerHTML = 'NIT <span style="color: #dc3545; font-weight: bold;"> *</span>';
            }
            if (labelUsername) {
                labelUsername.innerHTML = 'Nombre de usuario de la empresa <span style="color: #dc3545; font-weight: bold;"> *</span>';
            }
            
            // Ocultar sección de discapacidad
            if (disabilitySection) {
                disabilitySection.style.display = 'none';
            }
        } else {
            // Labels para candidato (por defecto)
            if (labelFirstName) {
                labelFirstName.innerHTML = 'Nombre <span style="color: #dc3545; font-weight: bold;"> *</span>';
            }
            if (labelLastName) {
                labelLastName.innerHTML = 'Apellido <span style="color: #dc3545; font-weight: bold;"> *</span>';
            }
            if (labelUsername) {
                labelUsername.innerHTML = 'Nombre de usuario <span style="color: #dc3545; font-weight: bold;"> *</span>';
            }
            
            // Mostrar sección de discapacidad
            if (disabilitySection) {
                disabilitySection.style.display = 'block';
            }
        }
    }
    
    // Función para verificar si el paso de discapacidad debe ser omitido
    function shouldSkipDisabilityStep() {
        return userTypeSelect.value === 'company' || userTypeSelect.value === 'empresa';
    }
    
    // Función para obtener el número de paso real (considerando pasos omitidos)
    function getRealStepNumber(logicalStep) {
        // Para empresas, mapear pasos lógicos a pasos reales
        if (shouldSkipDisabilityStep()) {
            if (logicalStep <= 2) return logicalStep; // Pasos 1-2 sin cambios
            return logicalStep + 1; // Pasos 3+ se desplazan uno hacia adelante (saltando paso 3)
        }
        return logicalStep; // Para candidatos, no hay cambios
    }
    
    // Función para obtener el número de paso lógico desde el paso real
    function getLogicalStepNumber(realStep) {
        if (shouldSkipDisabilityStep()) {
            if (realStep <= 2) return realStep; // Pasos 1-2 sin cambios
            if (realStep === 3) return -1; // Paso 3 no existe lógicamente para empresas
            return realStep - 1; // Pasos 4+ se mapean hacia atrás
        }
        return realStep; // Para candidatos, no hay cambios
    }
    
    // Función para mostrar paso específico
    function showStep(logicalStep) {
        const realStep = getRealStepNumber(logicalStep);
        
        // Validar que el paso real existe
        if (realStep < 1 || realStep > totalSteps) {
            return;
        }
        
        // Ocultar todos los pasos
        formSteps.forEach((formStep, index) => {
            formStep.classList.remove('active', 'animate-in-left', 'animate-in-right');
            
            if (index + 1 === realStep) {
                // Mostrar paso actual
                formStep.classList.add('active');
                
                // Añadir animación según dirección
                if (logicalStep > currentStep) {
                    formStep.classList.add('animate-in-right');
                } else if (logicalStep < currentStep) {
                    formStep.classList.add('animate-in-left');
                }
            }
        });
        
        // Actualizar indicadores de paso
        updateStepIndicators(logicalStep, realStep);
        
        // Actualizar barra de progreso
        updateProgressBar(logicalStep);
        
        // Actualizar botones de navegación
        updateNavigationButtons(logicalStep);
        
        // Actualizar paso actual
        currentStep = logicalStep;
        
        // Enfocar primer campo del paso actual
        focusFirstField(realStep);
    }
    
    // Función para actualizar indicadores de paso
    function updateStepIndicators(logicalStep, realStep) {
        stepIndicators.forEach((indicator, index) => {
            const stepNum = index + 1;
            indicator.classList.remove('active', 'completed');
            
            // Para empresas, ocultar indicador del paso 3 (discapacidad)
            if (shouldSkipDisabilityStep() && stepNum === 3) {
                indicator.style.display = 'none';
                return;
            } else {
                indicator.style.display = 'flex';
            }
            
            if (stepNum === realStep) {
                indicator.classList.add('active');
            } else if (stepNum < realStep) {
                indicator.classList.add('completed');
            }
        });
    }
    
    // Función para actualizar barra de progreso
    function updateProgressBar(logicalStep) {
        const totalLogicalSteps = getTotalLogicalSteps();
        const progress = ((logicalStep - 1) / (totalLogicalSteps - 1)) * 100;
        progressFill.style.width = progress + '%';
    }
    
    // Función para obtener total de pasos lógicos
    function getTotalLogicalSteps() {
        if (shouldSkipDisabilityStep()) {
            return totalSteps - 1; // Excluir paso de discapacidad
        }
        return totalSteps;
    }
    
    // Función para actualizar botones de navegación
    function updateNavigationButtons(logicalStep) {
        const totalLogicalSteps = getTotalLogicalSteps();
        
        // Botón anterior
        if (logicalStep === 1) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'inline-block';
        }
        
        // Botón siguiente y enviar
        if (logicalStep === totalLogicalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }
    }
    
    // Función para enfocar primer campo del paso actual
    function focusFirstField(realStep) {
        setTimeout(() => {
            const activeStep = document.querySelector('.form-step.active');
            const firstInput = activeStep.querySelector('input, select, textarea');
            if (firstInput && !firstInput.disabled) {
                firstInput.focus();
            }
        }, 300);
    }
    
    // Event listeners para cards de tipo de usuario
    userTypeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remover selección anterior
            userTypeCards.forEach(c => c.classList.remove('selected'));
            
            // Seleccionar card actual
            this.classList.add('selected');
            
            // Actualizar campo oculto
            userTypeSelect.value = this.dataset.value;
            
            // Actualizar labels
            updateLabels();
            
            // Actualizar indicadores de paso si es necesario
            updateStepIndicators(currentStep, getRealStepNumber(currentStep));
            
            // Actualizar botones de navegación
            updateNavigationButtons(currentStep);
        });
        
        // Hacer focuseable
        card.setAttribute('tabindex', '0');
        
        // Accessibility: Enter y Space
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Event listener para botón siguiente
    nextBtn.addEventListener('click', function() {
        nextStep();
    });
    
    // Event listener para botón anterior
    prevBtn.addEventListener('click', function() {
        prevStep();
    });
    
    // Función para avanzar al siguiente paso
    function nextStep() {
        const nextLogicalStep = currentStep + 1;
        const totalLogicalSteps = getTotalLogicalSteps();
        
        if (nextLogicalStep <= totalLogicalSteps) {
            showStep(nextLogicalStep);
        }
    }
    
    // Función para retroceder al paso anterior
    function prevStep() {
        const prevLogicalStep = currentStep - 1;
        
        if (prevLogicalStep >= 1) {
            showStep(prevLogicalStep);
        }
    }
    
    // Navegación por teclado con flechas
    document.addEventListener('keydown', function(e) {
        // Solo permitir navegación si no se está escribiendo en un campo
        if (document.activeElement.tagName === 'INPUT' || 
            document.activeElement.tagName === 'TEXTAREA' ||
            document.activeElement.tagName === 'SELECT') {
            return;
        }
        
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            nextStep();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            prevStep();
        }
    });
    
    // Event listener para el select original (mantener funcionalidad)
    userTypeSelect.addEventListener('change', function() {
        updateLabels();
        // Actualizar indicadores y botones después del cambio
        updateStepIndicators(currentStep, getRealStepNumber(currentStep));
        updateNavigationButtons(currentStep);
    });
    
    // Inicialización
    function init() {
        // Ejecutar funciones originales
        updateLabels();
        
        // Configurar estado inicial del multi-paso
        showStep(1);
        
        // Auto-seleccionar si ya hay valor
        if (userTypeSelect.value) {
            const selectedCard = document.querySelector(`[data-value="${userTypeSelect.value}"]`);
            if (selectedCard) {
                selectedCard.click();
            }
        }
    }
    
    // Ejecutar inicialización
    init();
});