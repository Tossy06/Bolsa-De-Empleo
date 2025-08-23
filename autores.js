const repoOwner = "Tossy06";
const repoName = "Bolsa-De-Empleo";

async function cargarAutores() {
  const contenedor = document.getElementById("autores-cards");
  if (!contenedor) return;

  // Autor principal fijo
  const autorCardPrincipal = document.createElement("div");
  autorCardPrincipal.className = "autor-card";
  autorCardPrincipal.innerHTML = `
    <img src="https://github.com/${repoOwner}.png" alt="Avatar de ${repoOwner}" />
    <h3>${repoOwner}</h3>
    <a href="https://github.com/${repoOwner}" target="_blank" rel="noopener">Ver perfil</a>
  `;
  contenedor.appendChild(autorCardPrincipal);

  // Traer colaboradores
  try {
    const response = await fetch(
      `https://api.github.com/repos/${repoOwner}/${repoName}/contributors`
    );
    if (!response.ok) throw new Error(`Error GitHub API: ${response.status}`);

    const autores = await response.json();

    // 🔎 Ver si trae colaboradores
    console.log("Colaboradores encontrados!!!:", autores);

    autores.forEach((autor) => {
      if (autor?.login && autor.login !== repoOwner) {
        const autorCard = document.createElement("div");
        autorCard.className = "autor-card";
        autorCard.innerHTML = `
          <img src="${autor.avatar_url}" alt="Avatar de ${autor.login}" />
          <h3>${autor.login}</h3>
          <a href="${autor.html_url}" target="_blank" rel="noopener">Ver perfil</a>
        `;
        contenedor.appendChild(autorCard);
      }
    });
  } catch (err) {
    console.error(err);
    const msg = document.createElement("p");
    msg.className = "msg-error";
    msg.textContent = "No pudimos cargar colaboradores ahora.";
    contenedor.appendChild(msg);
  }
}

document.addEventListener("DOMContentLoaded", cargarAutores);


function escribirYBorrarDescripcion() {
  const parrafo = document.querySelector("#overview p");
  if (!parrafo) return;

  const texto = `Nuestro proyecto consiste en una plataforma web que actúa como intermediario entre las personas con discapacidad que buscan empleo y las empresas que necesitan cumplir con la legislación vigente y, al mismo tiempo, mejorar sus prácticas de inclusión laboral. Este proyecto busca cumplir con los ODS de Trabajo Decente y Crecimiento Económico.`;

  let index = 0;
  let escribiendo = true;

  function escribirOBorrar() {
    if (escribiendo) {
      parrafo.textContent = texto.substring(0, index);
      index++;
      if (index > texto.length) {
        escribiendo = false;
        setTimeout(escribirOBorrar, 1000); // Pausa antes de borrar
        return;
      }
    } else {
      parrafo.textContent = texto.substring(0, index);
      index--;
      if (index < 0) {
        escribiendo = true;
        setTimeout(escribirOBorrar, 1000); // Pausa antes de volver a escribir
        return;
      }
    }
    setTimeout(escribirOBorrar, 20); // Velocidad de animación
  }

  escribirOBorrar();
}

document.addEventListener("DOMContentLoaded", () => {
  cargarAutores();
  escribirYBorrarDescripcion();
});
