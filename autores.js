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
