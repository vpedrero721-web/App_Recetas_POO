const imageByCategory = [
  "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=600&q=80",
  "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=600&q=80",
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80",
  "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=600&q=80",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=600&q=80",
];
const categoryEmojis = ["🍲", "🥗", "🍽️", "🥬", "🥘"];
const favoriteKey = "cocina-de-casa-favoritas";

const state = {
  recipes: [],
  selectedId: null,
  category: "Todas",
  view: "explorar",
  favorites: new Set(JSON.parse(localStorage.getItem(favoriteKey) || "[]")),
  editingId: null,
};

const elements = {
  grid: document.querySelector("#recipe-grid"),
  empty: document.querySelector("#empty-state"),
  detail: document.querySelector("#detail-content"),
  panel: document.querySelector("#recipe-panel"),
  dialog: document.querySelector("#recipe-dialog"),
  form: document.querySelector("#recipe-form"),
  formTitle: document.querySelector("#form-title"),
  formError: document.querySelector("#form-error"),
  search: document.querySelector("#search-input"),
  sort: document.querySelector("#sort-select"),
  favoriteCount: document.querySelector("#favorite-count"),
  toast: document.querySelector("#toast"),
};

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function categoryFor(recipe) {
  return recipe.categorias?.[0] || "Casera";
}

function categoryIndex(recipe) {
  const category = categoryFor(recipe).toLocaleLowerCase("es");
  if (category.includes("sopa") || category.includes("caldo")) return 1;
  if (category.includes("postre") || category.includes("dulce")) return 2;
  if (category.includes("entrada") || category.includes("snack")) return 3;
  if (category.includes("parrilla") || category.includes("principal")) return 4;
  return recipe.id_receta % imageByCategory.length;
}

function recipeImage(recipe) {
  return recipe.imagen_url || imageByCategory[categoryIndex(recipe)];
}

function recipeEmoji(recipe) {
  return categoryEmojis[categoryIndex(recipe)];
}

function imageMarkup(recipe, extraClass = "") {
  return `<img class="${extraClass}" src="${escapeHtml(recipeImage(recipe))}" alt="${escapeHtml(recipe.nombre)}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'cover-placeholder',textContent:'${recipeEmoji(recipe)}'}))">`;
}

function isMatch(recipe, term) {
  const haystack = [
    recipe.nombre, recipe.descripcion, categoryFor(recipe),
    ...(recipe.ingredientes || []).map((ingredient) => ingredient.nombre),
  ].join(" ").toLocaleLowerCase("es");
  const matchesSearch = haystack.includes(term);
  const matchesCategory = state.category === "Todas"
    || categoryFor(recipe).toLocaleLowerCase("es").includes(state.category.toLocaleLowerCase("es"));
  const matchesFavorite = state.view !== "favoritas" || state.favorites.has(recipe.id_receta);
  return matchesSearch && matchesCategory && matchesFavorite;
}

function visibleRecipes() {
  const term = elements.search.value.trim().toLocaleLowerCase("es");
  const recipes = state.recipes.filter((recipe) => isMatch(recipe, term));
  if (elements.sort.value === "quick") recipes.sort((a, b) => a.tiempo_preparacion - b.tiempo_preparacion);
  if (elements.sort.value === "name") recipes.sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
  return recipes;
}

function recipeCard(recipe) {
  const category = categoryFor(recipe);
  const favorite = state.favorites.has(recipe.id_receta);
  return `
    <article class="recipe-card" data-recipe="${recipe.id_receta}">
      <div class="card-cover">
        ${imageMarkup(recipe)}
        <span class="card-category">${escapeHtml(category)}</span>
        <button class="favorite-button ${favorite ? "is-favorite" : ""}" data-favorite="${recipe.id_receta}" aria-label="${favorite ? "Quitar de favoritas" : "Guardar en favoritas"}">${favorite ? "♥" : "♡"}</button>
      </div>
      <div class="card-body" data-select="${recipe.id_receta}" role="button" tabindex="0" aria-label="Ver ${escapeHtml(recipe.nombre)}">
        <h3 class="card-title">${escapeHtml(recipe.nombre)}</h3>
        <p class="card-description">${escapeHtml(recipe.descripcion)}</p>
        <div class="card-meta"><span>◷ ${recipe.tiempo_preparacion} min</span><span class="difficulty">${escapeHtml(recipe.dificultad)}</span></div>
      </div>
    </article>`;
}

function renderGrid() {
  const recipes = visibleRecipes();
  elements.grid.innerHTML = recipes.map(recipeCard).join("");
  elements.empty.hidden = recipes.length > 0;
  elements.grid.hidden = recipes.length === 0;
  elements.favoriteCount.textContent = state.favorites.size;
  if (state.selectedId && !state.recipes.some((recipe) => recipe.id_receta === state.selectedId)) {
    state.selectedId = null;
    renderDetail();
  }
}

function renderDetail() {
  const recipe = state.recipes.find((item) => item.id_receta === state.selectedId);
  if (!recipe) {
    elements.detail.innerHTML = '<div class="detail-placeholder"><span>🍲</span><h2>Elige algo rico</h2><p>Selecciona una receta para ver sus ingredientes y preparación.</p></div>';
    return;
  }
  const ingredients = (recipe.ingredientes || []).map((item) => {
    const amount = item.cantidad === "1" && item.unidad_medida === "unidad"
      ? ""
      : [item.cantidad, item.unidad_medida].filter(Boolean).join(" ");
    return `<li>${escapeHtml(item.nombre)}${amount ? ` <span>${escapeHtml(amount)}</span>` : ""}</li>`;
  }).join("");
  const instructions = (recipe.instrucciones || []).filter(Boolean).map((step) => `<li>${escapeHtml(step)}</li>`).join("");
  const favorite = state.favorites.has(recipe.id_receta);
  elements.detail.innerHTML = `
    <div class="detail-cover">${imageMarkup(recipe)}<span class="card-category">${escapeHtml(categoryFor(recipe))}</span></div>
    <div class="detail-heading"><h2>${escapeHtml(recipe.nombre)}</h2><button class="favorite-button ${favorite ? "is-favorite" : ""}" data-favorite="${recipe.id_receta}" aria-label="${favorite ? "Quitar de favoritas" : "Guardar en favoritas"}">${favorite ? "♥" : "♡"}</button></div>
    <span class="detail-category">${escapeHtml(categoryFor(recipe))}</span>
    <p class="detail-description">${escapeHtml(recipe.descripcion)}</p>
    <div class="detail-stats">
      <div class="detail-stat"><strong>◷ ${recipe.tiempo_preparacion} min</strong>Preparación</div>
      <div class="detail-stat"><strong>♧ ${recipe.porciones}</strong>Porciones</div>
      <div class="detail-stat"><strong>${escapeHtml(recipe.dificultad)}</strong>Dificultad</div>
    </div>
    <section class="detail-block"><div class="detail-block-heading"><h3>Ingredientes</h3><span>${recipe.ingredientes?.length || 0} ingredientes</span></div>
      ${ingredients ? `<ul class="ingredient-list">${ingredients}</ul>` : '<p class="detail-description">Aún no se agregaron ingredientes.</p>'}
    </section>
    <section class="detail-block"><div class="detail-block-heading"><h3>Preparación</h3><span>${recipe.instrucciones?.length || 0} pasos</span></div>
      ${instructions ? `<ol class="instruction-list">${instructions}</ol>` : '<p class="detail-description">Aún no se agregaron instrucciones.</p>'}
    </section>
    <div class="detail-actions"><button class="secondary-button" data-edit="${recipe.id_receta}">Editar</button><button class="secondary-button delete-button" data-delete="${recipe.id_receta}">Eliminar</button></div>`;
}

function setCategory(category) {
  state.category = category;
  document.querySelectorAll("[data-category]").forEach((button) => {
    button.classList.toggle("active", button.dataset.category === category);
  });
  renderGrid();
}

function toggleFavorite(id) {
  if (state.favorites.has(id)) state.favorites.delete(id);
  else state.favorites.add(id);
  localStorage.setItem(favoriteKey, JSON.stringify([...state.favorites]));
  renderGrid();
  renderDetail();
}

function selectRecipe(id) {
  state.selectedId = id;
  renderDetail();
  elements.panel.classList.add("open");
}

function setView(view) {
  state.view = view;
  const favoriteView = view === "favoritas";
  document.querySelectorAll(".nav-link").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  document.querySelector("#breadcrumb-current").textContent = favoriteView ? "Mis favoritas" : "Explorar";
  document.querySelector("#page-title").innerHTML = favoriteView ? "Tus recetas <em>favoritas</em>" : "¿Qué cocinamos <em>hoy?</em>";
  document.querySelector("#list-eyebrow").textContent = favoriteView ? "TUS GUARDADAS" : "PARA INSPIRARTE";
  document.querySelector("#list-title").innerHTML = favoriteView ? "Un menú hecho por ti <span class=\"heading-sparkle\">♥</span>" : "Recetas para descubrir <span class=\"heading-sparkle\">✳</span>";
  renderGrid();
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("visible"), 2600);
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "No se pudo completar la solicitud.");
  return result;
}

async function loadRecipes() {
  elements.grid.innerHTML = '<p class="detail-description">Cargando recetas…</p>';
  try {
    state.recipes = await request("/api/recetas");
    renderGrid();
    renderDetail();
    if (!state.recipes.length) showToast("Aún no hay recetas. ¡Agrega la primera!");
    else selectRecipe(state.recipes[0].id_receta);
  } catch (error) {
    elements.grid.innerHTML = `<p class="form-error">${escapeHtml(error.message)}</p>`;
    elements.empty.hidden = true;
  }
}

function openForm(recipe = null) {
  state.editingId = recipe?.id_receta ?? null;
  elements.form.reset();
  elements.formTitle.textContent = recipe ? "Editar receta" : "Nueva receta";
  elements.form.elements.namedItem("nombre").value = recipe?.nombre || "";
  elements.form.elements.namedItem("descripcion").value = recipe?.descripcion || "";
  elements.form.elements.namedItem("tiempo_preparacion").value = recipe?.tiempo_preparacion || 30;
  elements.form.elements.namedItem("porciones").value = recipe?.porciones || 4;
  elements.form.elements.namedItem("dificultad").value = recipe?.dificultad || "Fácil";
  elements.form.elements.namedItem("ingredientes").value = (recipe?.ingredientes || []).map((item) => item.nombre).join("\n");
  elements.form.elements.namedItem("instrucciones").value = (recipe?.instrucciones || []).join("\n");
  elements.formError.hidden = true;
  elements.dialog.showModal();
}

function recipePayload(formData) {
  return {
    nombre: formData.get("nombre").trim(),
    descripcion: formData.get("descripcion").trim(),
    tiempo_preparacion: Number(formData.get("tiempo_preparacion")),
    porciones: Number(formData.get("porciones")),
    dificultad: formData.get("dificultad"),
    ingredientes: formData.get("ingredientes").split("\n").map((line) => line.trim()).filter(Boolean),
    instrucciones: formData.get("instrucciones").split("\n").map((line) => line.trim()).filter(Boolean),
  };
}

async function saveRecipe(event) {
  event.preventDefault();
  elements.formError.hidden = true;
  const payload = recipePayload(new FormData(elements.form));
  try {
    const recipe = await request(state.editingId ? `/api/recetas/${state.editingId}` : "/api/recetas", {
      method: state.editingId ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    if (state.editingId) state.recipes = state.recipes.map((item) => item.id_receta === recipe.id_receta ? recipe : item);
    else state.recipes.unshift(recipe);
    elements.dialog.close();
    selectRecipe(recipe.id_receta);
    renderGrid();
    showToast(state.editingId ? "Receta actualizada con éxito" : "Tu receta ya está en la colección");
  } catch (error) {
    elements.formError.textContent = error.message;
    elements.formError.hidden = false;
  }
}

async function deleteRecipe(id) {
  const recipe = state.recipes.find((item) => item.id_receta === id);
  if (!recipe || !window.confirm(`¿Quieres eliminar "${recipe.nombre}"?`)) return;
  try {
    await request(`/api/recetas/${id}`, { method: "DELETE" });
    state.recipes = state.recipes.filter((item) => item.id_receta !== id);
    state.favorites.delete(id);
    localStorage.setItem(favoriteKey, JSON.stringify([...state.favorites]));
    state.selectedId = state.recipes[0]?.id_receta ?? null;
    renderGrid();
    renderDetail();
    showToast("La receta se eliminó de tu colección");
  } catch (error) {
    showToast(error.message);
  }
}

document.querySelectorAll("[data-category]").forEach((button) => button.addEventListener("click", () => setCategory(button.dataset.category)));
document.querySelectorAll(".nav-link").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
elements.search.addEventListener("input", renderGrid);
elements.sort.addEventListener("change", renderGrid);
elements.grid.addEventListener("click", (event) => {
  const favorite = event.target.closest("[data-favorite]");
  if (favorite) return toggleFavorite(Number(favorite.dataset.favorite));
  const selected = event.target.closest("[data-select]");
  if (selected) selectRecipe(Number(selected.dataset.select));
});
elements.grid.addEventListener("keydown", (event) => {
  if ((event.key === "Enter" || event.key === " ") && event.target.matches("[data-select]")) {
    event.preventDefault();
    selectRecipe(Number(event.target.dataset.select));
  }
});
elements.detail.addEventListener("click", (event) => {
  const target = event.target.closest("[data-favorite], [data-edit], [data-delete]");
  if (!target) return;
  if (target.dataset.favorite) toggleFavorite(Number(target.dataset.favorite));
  if (target.dataset.edit) openForm(state.recipes.find((recipe) => recipe.id_receta === Number(target.dataset.edit)));
  if (target.dataset.delete) deleteRecipe(Number(target.dataset.delete));
});
document.querySelector("#add-recipe").addEventListener("click", () => openForm());
document.querySelector("#sidebar-add").addEventListener("click", () => openForm());
document.querySelectorAll("[data-open-form]").forEach((button) => button.addEventListener("click", () => openForm()));
document.querySelector("#featured-button").addEventListener("click", () => {
  const featured = state.recipes[0];
  if (featured) selectRecipe(featured.id_receta);
});
document.querySelector("#close-dialog").addEventListener("click", () => elements.dialog.close());
document.querySelector("#cancel-dialog").addEventListener("click", () => elements.dialog.close());
document.querySelector("#close-detail").addEventListener("click", () => elements.panel.classList.remove("open"));
elements.form.addEventListener("submit", saveRecipe);
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    elements.search.focus();
  }
  if (event.key === "Escape") elements.panel.classList.remove("open");
});
loadRecipes();
