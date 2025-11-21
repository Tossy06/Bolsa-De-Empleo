// =============================================
// BOLSA DE EMPLEO INCLUSIVA - AUTORES.JS
// Carga colaboradores desde GitHub API
// =============================================

const repoOwner = "Tossy06";
const repoName = "Bolsa-De-Empleo";

async function cargarAutores() {
  const contenedor = document.getElementById("autores-cards");
  if (!contenedor) {
    console.warn("⚠️ No se encontró el contenedor #autores-cards");
    return;
  }

  const loadingMsg = document.createElement("p");
  loadingMsg.className = "loading-msg";
  loadingMsg.textContent = "⏳ Cargando colaboradores...";
  loadingMsg.style.cssText = "color: #fff; text-align: center; width: 100%; font-size: 1.1rem;";
  contenedor.appendChild(loadingMsg);

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

  try {
    const response = await fetch(
      `https://api.github.com/repos/${repoOwner}/${repoName}/contributors`
    );

    if (!response.ok) {
      throw new Error(`Error GitHub API: ${response.status}`);
    }

    const autores = await response.json();

    if (loadingMsg.parentNode) {
      loadingMsg.remove();
    }

    console.log("✅ Colaboradores encontrados:", autores.length);

    const colaboradores = autores.filter(autor => autor?.login && autor.login !== repoOwner);

    if (colaboradores.length === 0) {
      const noColabMsg = document.createElement("p");
      noColabMsg.style.cssText = "color: #fff; text-align: center; width: 100%; opacity: 0.9; font-size: 1rem;";
      noColabMsg.textContent = "Actualmente solo hay un colaborador en el proyecto.";
      contenedor.appendChild(noColabMsg);
      return;
    }

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
    
    if (loadingMsg.parentNode) {
      loadingMsg.remove();
    }

    const msg = document.createElement("p");
    msg.className = "msg-error";
    msg.innerHTML = `
      <strong>⚠️ Error al cargar colaboradores</strong><br>
      No pudimos conectar con GitHub en este momento.
    `;
    msg.style.cssText = `
      max-width: 500px;
      margin: 1rem auto;
      padding: 1rem;
      background: #7a1f1f;
      color: #ffd2d2;
      border-radius: 10px;
      text-align: center;
    `;
    contenedor.appendChild(msg);
  }
}

function escribirYBorrarDescripcion() {
  const parrafo = document.querySelector("#overview .overview-content > p");
  if (!parrafo) return;

  const textoOriginal = parrafo.textContent;
  const texto = textoOriginal.trim();
  
  let index = 0;
  let escribiendo = true;
  let timeoutId;

  function escribirOBorrar() {
    if (escribiendo) {
      parrafo.textContent = texto.substring(0, index);
      index++;
      
      if (index > texto.length) {
        escribiendo = false;
        timeoutId = setTimeout(escribirOBorrar, 3000);
        return;
      }
      
      timeoutId = setTimeout(escribirOBorrar, 30);
    } else {
      parrafo.textContent = texto.substring(0, index);
      index--;
      
      if (index < 0) {
        escribiendo = true;
        timeoutId = setTimeout(escribirOBorrar, 2000);
        return;
      }
      
      timeoutId = setTimeout(escribirOBorrar, 15);
    }
  }

  escribirOBorrar();

  window.addEventListener('beforeunload', () => {
    if (timeoutId) clearTimeout(timeoutId);
  });
}

function configurarNavegacionSuave() {
  const enlaces = document.querySelectorAll('a[href^="#"]');
  
  enlaces.forEach(enlace => {
    enlace.addEventListener('click', (e) => {
      const href = enlace.getAttribute('href');
      
      if (href === '#' || href === '#login' || href === '#register') return;
      
      e.preventDefault();
      const targetId = href.substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        const headerOffset = 80;
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

function animarTarjetas() {
  const tarjetas = document.querySelectorAll('.card, .stat-card, .model-card, .app-card');
  
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
    width: 0;
  `;
  document.body.appendChild(indicador);

  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrollPercentage = (scrollTop / scrollHeight) * 100;
    indicador.style.width = scrollPercentage + '%';
  });
}

function crearBotonVolverArriba() {
  const boton = document.createElement('button');
  boton.id = 'btn-volver-arriba';
  boton.innerHTML = '↑';
  boton.setAttribute('aria-label', 'Volver arriba');
  boton.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 50px;
    height: 50px;
    background: #175058;
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 1.5rem;
    cursor: pointer;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 999;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  `;
  
  boton.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
      boton.style.opacity = '1';
      boton.style.visibility = 'visible';
    } else {
      boton.style.opacity = '0';
      boton.style.visibility = 'hidden';
    }
  });

  boton.addEventListener('mouseenter', () => {
    boton.style.transform = 'scale(1.1)';
  });

  boton.addEventListener('mouseleave', () => {
    boton.style.transform = 'scale(1)';
  });

  document.body.appendChild(boton);
}

function animarAlScroll() {
  const elementos = document.querySelectorAll('section');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  });

  elementos.forEach(elemento => {
    observer.observe(elemento);
  });
}

function añadirEstilosDinamicos() {
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

    section {
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }

    section.visible {
      opacity: 1;
      transform: translateY(0);
    }

    #btn-volver-arriba:hover {
      background: #1e6b75;
    }

    @media (max-width: 768px) {
      #btn-volver-arriba {
        bottom: 1rem;
        right: 1rem;
        width: 45px;
        height: 45px;
      }
    }
  `;
  document.head.appendChild(style);
}

function mostrarInfoDebug() {
  console.log(`
  ╔═══════════════════════════════════════════╗
  ║   BOLSA DE EMPLEO INCLUSIVA - v1.0.0     ║
  ║   Plataforma de Inclusión Laboral        ║
  ╠═══════════════════════════════════════════╣
  ║   Repo: ${repoName}                       
  ║   Owner: ${repoOwner}                     
  ║   Tech: Django 5.1 + JavaScript Vanilla  ║
  ╚═══════════════════════════════════════════╝
  `);
  
  console.log("📊 Estado de la página:");
  console.log("- Secciones:", document.querySelectorAll('section').length);
  console.log("- Tarjetas:", document.querySelectorAll('.card').length);
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 Inicializando Bolsa de Empleo Inclusiva...");
  
  mostrarInfoDebug();
  añadirEstilosDinamicos();
  cargarAutores();
  escribirYBorrarDescripcion();
  configurarNavegacionSuave();
  animarTarjetas();
  crearIndicadorScroll();
  crearBotonVolverArriba();
  animarAlScroll();
  
  console.log("✅ Sitio cargado correctamente");
});

window.addEventListener('error', (e) => {
  console.error('❌ Error global:', e.message);
});

window.addEventListener('load', () => {
  if (window.performance) {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    console.log(`⚡ Tiempo de carga: ${pageLoadTime}ms`);
  }
});
