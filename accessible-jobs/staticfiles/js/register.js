document.addEventListener("DOMContentLoaded", () => {
    const steps = document.querySelectorAll(".step");
    const nextBtn = document.getElementById("nextStep");
    const prevBtn = document.getElementById("prevStep");
    const progressFill = document.getElementById("progressFill");
    const stepCircles = document.querySelectorAll(".step-circle");
    const userTypeCards = document.querySelectorAll(".user-type-card");
    let currentStep = 1;
  
    const showStep = (step) => {
      steps.forEach(s => s.classList.remove("active"));
      document.querySelector(`.step[data-step="${step}"]`).classList.add("active");
      progressFill.style.width = `${(step - 1) * 25}%`;
      stepCircles.forEach(c => c.classList.toggle("active", parseInt(c.dataset.step) === step));
    };
  
    nextBtn.addEventListener("click", () => {
      if (currentStep < steps.length) currentStep++;
      showStep(currentStep);
    });
  
    prevBtn.addEventListener("click", () => {
      if (currentStep > 1) currentStep--;
      showStep(currentStep);
    });
  
    // Permitir usar flechas ← y →
    document.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight" && currentStep < steps.length) {
        currentStep++;
        showStep(currentStep);
      } else if (e.key === "ArrowLeft" && currentStep > 1) {
        currentStep--;
        showStep(currentStep);
      }
    });
  
    // Detectar tipo de usuario seleccionado
    userTypeCards.forEach(card => {
      card.addEventListener("click", () => {
        userTypeCards.forEach(c => c.classList.remove("active"));
        card.classList.add("active");
  
        const radio = card.querySelector('input[type="radio"]');
        radio.checked = true;
  
        if (radio.value === "candidate") {
          document.querySelectorAll(".candidate-only").forEach(el => el.style.display = "flex");
          document.querySelectorAll(".company-only").forEach(el => el.style.display = "none");
        } else {
          document.querySelectorAll(".candidate-only").forEach(el => el.style.display = "none");
          document.querySelectorAll(".company-only").forEach(el => el.style.display = "block");
        }
      });
    });
  });
  