const repoOwner = "Tossy06";
const repoName = "Bolsa-De-Empleo";

async function cargarAutores() {
  const contenedor = document.getElementById("autores-cards");

  // Autor principal fijo
  const autor-card = document.createElement("div");
  autor-card.classList.add("autor-card");
  autor-card.innerHTML = `
    <img src="https://github.com/${repoOwner}.png" alt="${repoOwner}">
    <h3>${repoOwner}</h3>
    <a href="https://github.com/${repoOwner}" target="_blank">Ver perfil</a>
  `;
  contenedor.appendChild(autor-card);

  // Intentar traer colaboradores
  const response = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/contributors`);
  const autores = await response.json();

  autores.forEach(autor => {
    if (autor.login !== repoOwner) { // evitar duplicar
      console.log("Autor!!!", autor);
      const autor-card = document.createElement("div");
      autor-card.classList.add("autor-card");
      autor-card.innerHTML = `
        <img src="${autor.avatar_url}" alt="${autor.login}">
        <h3>${autor.login}</h3>
        <a href="${autor.html_url}" target="_blank">Ver perfil</a>
      `;
      contenedor.appendChild(autor-card);
    }
  });
}

cargarAutores();
