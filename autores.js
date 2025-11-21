// ===== CONFIGURACIÓN =====
const repoOwner = "Tossy06";
const repoName = "Bolsa-De-Empleo";

// ===== CARGAR AUTORES DESDE GITHUB =====
async function cargarAutores() {
  const contenedor = document.getElementById("autores-cards");
  if (!contenedor) return;

  // Mostrar mensaje de carga
  const loadingMsg = document.createElement("p");
  loadingMsg.className = "loading-msg";
  loadingMsg.textContent = "⏳ Cargando colaboradores...";
  loadingMsg.style.color = "#fff";
  loadingMsg.style.textAlign = "center";
  loadingMsg.style.width = "100%";
  contenedor.appendChild(loadingMsg);

  // Autor principal fijo
  const autorCardPrincipal = document.createElement("div");
  autorCardPrincipal.className = "autor-card";
  autorCardPrincipal.innerHTML = `
    <img src="https://github.com/${repoOwner}.png" alt="Avatar de ${repoOwner}" loading="lazy" />
    <h3>${repoOwner}</h3>
    <p class="autor-role">Creador del Proyecto</p>
    <a href="https://github.com/${repoOwner}" target="_blank" rel="noopener noreferrer" aria-label="Ver perfil de ${repoOwner} en GitHub">
      Ver perfil
    </a>
  `;
  contenedor.appendChild(autorCardPrincipal);

  // Traer colaboradores desde GitHub API
  try {
    const response = await fetch(
      `https://api.github.com/repos/${repoOwner}/${repoName}/contributors`
    );

    if (!response.ok) {
      throw new Error(`Error GitHub API: ${response.status} - ${response.statusText}`);
    }

    const autores = await response.json();

    // Remover mensaje de carga
    if (loadingMsg.parentNode) {
      loadingMsg.remove();
    }

    // Verificar si hay colaboradores
    console.log("✅ Colaboradores encontrados:", autores.length);

    // Filtrar y mostrar colaboradores (excluir al owner principal)
    const colaboradores = autores.filter(autor => autor?.login && autor.login !== repoOwner);

    if (colaboradores.length === 0) {
      const noColabMsg = document.createElement("p");
      noColabMsg.style.color = "#fff";
      noColabMsg.style.textAlign = "center";
      noColabMsg.style.width = "100%";
      noColabMsg.style.opacity = "0.9";
      noColabMsg.textContent = "Actualmente solo hay un colaborador en el proyecto.";
      contenedor.appendChild(noColabMsg);
      return;
    }

    // Crear tarjetas para cada colaborador
    colaboradores.forEach((autor, index) => {
      const autorCard = document.createElement("div");
      autorCard.className = "autor-card";
      autorCard.style.animationDelay = `${(index + 1) * 0.1}s`;
      
      autorCard.innerHTML = `
        <img src="${autor.avatar_url}" alt="Avatar de ${autor.login}" loading="lazy" />
        <h3>${autor.login}</h3>
        <p class="autor-role">Colaborador</p>
        <p class="autor-contributions">${autor.contributions} contribuciones</p>
        <a href="${autor.html_url}" target="_blank" rel="noopener noreferrer" aria-label="Ver perfil de ${autor.login} en GitHub">
          Ver perfil
        </a>
      `;
      
      contenedor.appendChild(autorCard);
    });

  } catch (err) {
    console.error("❌ Error al cargar colaboradores:", err);
    
    // Remover mensaje de carga
    if (loadingMsg.parentNode) {
      loadingMsg.remove();
    }

    // Mostrar mensaje de error
    const msg = document.createElement("p");
    msg.className = "msg-error";
    msg.innerHTML = `
      <strong>⚠️ Error al cargar colaboradores</strong><br>
      No pudimos conectar con GitHub en este momento. Por favor, intenta más tarde.
    `;
    msg.style.maxWidth = "500px";
    msg.style.margin = "1rem auto";
    contenedor.appendChild(msg);
  }
}

// ===== ANIMACIÓN DE ESCRITURA Y BORRADO =====
function escribirYBorrarDescripcion() {
  const parrafo = document.querySelector("#overview p");
  if (!parrafo) return;

  const texto = `Nuestro proyecto consiste en una plataforma web que actúa como intermediario entre las personas con discapacidad que buscan empleo y las empresas que necesitan cumplir con la legislación vigente y, al mismo tiempo, mejorar sus prácticas de inclusión laboral. Este proyecto busca cumplir con los ODS de Trabajo Decente y Crecimiento Económico.`;
  
  let index = 0;
  let escribiendo = true;
  let timeoutId;

  function escribirOBorrar() {
    if (escribiendo) {
      parrafo.textContent = texto.substring(0, index);
      index++;
      
      if (index > texto.length) {
        escribiendo = false;
        timeoutId = setTimeout(escribirOBorrar, 3000); // Pausa de 3s antes de borrar
        return;
      }
      
      timeoutId = setTimeout(escribirOBorrar, 30); // Velocidad de escritura
    } else {
      parrafo.textContent = texto.substring(0, index);
      index--;
      
      if (index < 0) {
        escribiendo = true;
        timeoutId = setTimeout(escribirOBorrar, 2000); // Pausa de 2s antes de reescribir
        return;
      }
      
      timeoutId = setTimeout(escribirOBorrar, 15); // Velocidad de borrado (más rápido)
    }
  }

  escribirOBorrar();

  // Limpiar timeout si el usuario sale de la página
  window.addEventListener('beforeunload', () => {
    if (timeoutId) clearTimeout(timeoutId);
  });
}

// ===== CONTADOR ANIMADO PARA ESTADÍSTICAS =====
function animarContadores() {
  const contadores = document.querySelectorAll('.stat-number');
  
  contadores.forEach(contador => {
    const target = parseInt(contador.getAttribute('data-target'));
    const duration = 2000; // 2 segundos
    const increment = target / (duration / 16); // 60 FPS
    let current = 0;

    const updateCounter = () => {
      current += increment;
      
      if (current < target) {
        contador.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        contador.textContent = target;
      }
    };

    // Iniciar animación cuando el elemento sea visible
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          updateCounter();
          observer.disconnect();
        }
      });
    }, { threshold: 0.5 });

    observer.observe(contador);
  });
}

// ===== NAVEGACIÓN SUAVE =====
function configurarNavegacionSuave() {
  const enlaces = document.querySelectorAll('a[href^="#"]');
  
  enlaces.forEach(enlace => {
    enlace.addEventListener('click', (e) => {
      const href = enlace.getAttribute('href');
      
      // Evitar interferir con links de login/register
      if (href === '#login' || href === '#register') return;
      
      e.preventDefault();
      const targetId = href.substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        const headerOffset = 80; // Altura del header sticky
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

// ===== ANIMACIÓN DE ENTRADA PARA TARJETAS =====
function animarTarjetas() {
  const tarjetas = document.querySelectorAll('.card, .feature-card, .tech-item');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  tarjetas.forEach(tarjeta => {
    tarjeta.style.opacity = '0';
    tarjeta.style.transform = 'translateY(30px)';
    tarjeta.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(tarjeta);
  });
}

// ===== MENÚ RESPONSIVE =====
function configurarMenuResponsive() {
  const nav = document.querySelector('nav');
  const navLinks = document.querySelector('.nav-links');
  
  // Crear botón de menú móvil si no existe
  if (window.innerWidth <= 768 && !document.querySelector('.menu-toggle')) {
    const menuToggle = document.createElement('button');
    menuToggle.className = 'menu-toggle';
    menuToggle.setAttribute('aria-label', 'Abrir menú de navegación');
    menuToggle.innerHTML = '☰';
    menuToggle.style.cssText = `
      display: none;
      background: none;
      border: 2px solid white;
      color: white;
      font-size: 1.5rem;
      padding: 0.5rem 1rem;
      cursor: pointer;
      border-radius: 5px;
    `;
    
    if (window.innerWidth <= 768) {
      menuToggle.style.display = 'block';
    }
    
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      menuToggle.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
    });
    
    nav.insertBefore(menuToggle, navLinks);
  }
}

// ===== INDICADOR DE SCROLL =====
function crearIndicadorScroll() {
  const indicador = document.createElement('div');
  indicador.id = 'scroll-indicator';
  indicador.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    height: 4px;
    background: linear-gradient(90deg, #175058, #1e6b75);
    z-index: 9999;
    transition: width 0.1s ease;
  `;
  document.body.appendChild(indicador);

  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrollPercentage = (scrollTop / scrollHeight) * 100;
    indicador.style.width = scrollPercentage + '%';
  });
}

// ===== INICIALIZACIÓN =====
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 Inicializando Bolsa de Empleo Inclusiva...");
  
  // Cargar autores
  cargarAutores();
  
  // Animación de escritura
  escribirYBorrarDescripcion();
  
  // Animar contadores
  animarContadores();
  
  // Configurar navegación suave
  configurarNavegacionSuave();
  
  // Animar tarjetas
  animarTarjetas();
  
  // Menú responsive
  configurarMenuResponsive();
  
  // Indicador de scroll
  crearIndicadorScroll();
  
  console.log("✅ Sitio cargado correctamente");
});

// ===== MANEJADORES DE EVENTOS GLOBALES =====
window.addEventListener('resize', () => {
  configurarMenuResponsive();
});

// Añadir estilos adicionales para autor-role y autor-contributions
document.addEventListener("DOMContentLoaded", () => {
  const style = document.createElement('style');
  style.textContent = `
    .autor-role {
      font-size: 0.85rem;
      color: #666;
      font-weight: 500;
      margin: 0.25rem 0;
    }
    
    .autor-contributions {
      font-size: 0.8rem;
      color: #175058;
      font-weight: 600;
      margin: 0.5rem 0;
      background: #EBF3EA;
      padding: 0.3rem 0.6rem;
      border-radius: 12px;
      display: inline-block;
    }
    
    .loading-msg {
      animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  `;
  document.head.appendChild(style);
});
