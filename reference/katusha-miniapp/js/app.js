/**
 * Демо-логика локальной вёрстки (без Telegram SDK).
 * Данные совпадают с mock-каталогом киоска.
 */
const CATEGORIES = [
  { id: "", name: "Все" },
  { id: "berry", name: "Ягода" },
  { id: "dairy", name: "Молочка" },
  { id: "honey", name: "Мёд" },
  { id: "veg", name: "Овощи" },
  { id: "other", name: "Прочее" },
];

const PRODUCTS = [
  { id: "1", cat: "berry", name: "Клубника", price: 450, stock: 12, unit: "кг", img: "../../assets/demo_products/1.jpg" },
  { id: "2", cat: "berry", name: "Малина", price: 520, stock: 8, unit: "кг", img: "../../assets/demo_products/2.jpg" },
  { id: "3", cat: "berry", name: "Черника", price: 680, stock: 0, unit: "кг", img: "../../assets/demo_products/3.jpg" },
  { id: "4", cat: "dairy", name: "Молоко 3,2%", price: 95, stock: 30, unit: "л", img: "../../assets/demo_products/4.jpg" },
  { id: "5", cat: "dairy", name: "Творог домашний", price: 180, stock: 15, unit: "шт", img: "../../assets/demo_products/5.jpg" },
  { id: "6", cat: "dairy", name: "Сметана 20%", price: 120, stock: 20, unit: "шт", img: "../../assets/demo_products/6.jpg" },
  { id: "7", cat: "honey", name: "Мёд липовый", price: 850, stock: 10, unit: "банка", img: "../../assets/demo_products/7.jpg" },
  { id: "8", cat: "honey", name: "Мёд гречишный", price: 780, stock: 6, unit: "банка", img: "../../assets/demo_products/8.jpg" },
  { id: "9", cat: "veg", name: "Картофель", price: 45, stock: 50, unit: "кг", img: "../../assets/demo_products/9.jpg" },
  { id: "10", cat: "veg", name: "Морковь", price: 55, stock: 40, unit: "кг", img: "../../assets/demo_products/10.jpg" },
  { id: "11", cat: "other", name: "Яйца С0", price: 110, stock: 24, unit: "десяток", img: "../../assets/demo_products/11.jpg" },
  { id: "12", cat: "other", name: "Зелень укроп", price: 60, stock: 5, unit: "пучок", img: "../../assets/demo_products/12.jpg" },
];

const cart = new Map();
let activeCategory = "";

function formatPrice(n) {
  return `${Number.isInteger(n) ? n : n.toFixed(2)} ₽`;
}

function cartStats() {
  let count = 0;
  let total = 0;
  for (const [id, qty] of cart) {
    const p = PRODUCTS.find((x) => x.id === id);
    if (!p) continue;
    count += qty;
    total += p.price * qty;
  }
  return { count, total };
}

function renderCategories() {
  const el = document.getElementById("categories");
  el.innerHTML = CATEGORIES.map(
    (c) =>
      `<button type="button" class="cat-pill${c.id === activeCategory ? " active" : ""}" data-cat="${c.id}">${c.name}</button>`
  ).join("");
  el.querySelectorAll(".cat-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeCategory = btn.dataset.cat;
      renderCategories();
      renderProducts();
    });
  });
}

function renderProducts() {
  const grid = document.getElementById("product-grid");
  const list = PRODUCTS.filter((p) => !activeCategory || p.cat === activeCategory);
  grid.innerHTML = list
    .map((p) => {
      const qty = cart.get(p.id) || 0;
      const oos = p.stock <= 0;
      return `
      <article class="product-card${oos ? " out-of-stock" : ""}" data-id="${p.id}">
        <div class="product-image">
          <img src="${p.img}" alt="${p.name}" loading="lazy" onerror="this.style.display='none'">
        </div>
        <div class="product-body">
          <h3 class="product-name">${p.name}</h3>
          <div class="product-meta">за ${p.unit}</div>
          <div class="product-price">${formatPrice(p.price)}</div>
          <div class="product-actions">
            ${
              oos
                ? '<div class="oos-label">Нет в наличии</div>'
                : `
              <button type="button" class="btn-add" data-action="add" style="display:${qty > 0 ? "none" : "block"}">Добавить</button>
              <div class="qty-row${qty > 0 ? " visible" : ""}">
                <button type="button" class="counter-btn" data-action="dec">−</button>
                <span class="qty-value">${qty}</span>
                <button type="button" class="counter-btn" data-action="inc">+</button>
              </div>`
            }
          </div>
        </div>
      </article>`;
    })
    .join("");

  grid.querySelectorAll(".product-card").forEach((card) => {
    const id = card.dataset.id;
    card.querySelectorAll("[data-action]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const p = PRODUCTS.find((x) => x.id === id);
        if (!p || p.stock <= 0) return;
        let q = cart.get(id) || 0;
        if (btn.dataset.action === "add" || btn.dataset.action === "inc") {
          if (q < p.stock) cart.set(id, q + 1);
        } else if (btn.dataset.action === "dec") {
          q -= 1;
          if (q <= 0) cart.delete(id);
          else cart.set(id, q);
        }
        renderProducts();
        renderBottomBar();
      });
    });
  });
}

function renderBottomBar() {
  const { count, total } = cartStats();
  document.getElementById("cart-count").textContent = count;
  document.getElementById("cart-total").textContent = formatPrice(total);
  document.getElementById("btn-checkout").disabled = count === 0;
}

document.getElementById("btn-checkout").addEventListener("click", () => {
  if (cartStats().count === 0) return;
  alert("Демо: переход к оплате (в киоске — PyQt6 PaymentMethodScreen)");
});

// ?kiosk=1 — превью под вертикальный экран 1080
if (new URLSearchParams(location.search).has("kiosk")) {
  document.body.classList.add("kiosk-preview");
}

renderCategories();
renderProducts();
renderBottomBar();
