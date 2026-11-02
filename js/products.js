(function () {
  'use strict';
  var container = document.getElementById('featured-products');
  if (!container) return;

  // Only local assets and pages are allowed; this catalog never contacts GoDaddy.
  function localPath(value) {
    return typeof value === 'string' && value.trim() === value &&
      /^(?!\/|[a-z][a-z\d+.-]*:)[^\\\s]+$/i.test(value) ? value : null;
  }
  var products = Array.isArray(window.SWIFTALYN_PRODUCTS) ?
    window.SWIFTALYN_PRODUCTS.filter(function (product) {
      return product && typeof product.name === 'string' && product.name.trim();
    }) : [];
  if (!products.length) return;
  container.replaceChildren();
  products.forEach(function (product) {
    var card = document.createElement('article');
    card.className = 'local-product';
    var imagePath = localPath(product.image);
    if (imagePath) {
      var image = document.createElement('img');
      image.src = imagePath;
      image.alt = product.imageAlt || product.name;
      image.loading = 'lazy';
      image.width = 600;
      image.height = 600;
      card.appendChild(image);
    }
    var title = document.createElement('h3');
    var target = localPath(product.href);
    if (target) {
      var link = document.createElement('a');
      link.href = target;
      link.textContent = product.name;
      title.appendChild(link);
    } else {
      title.textContent = product.name;
    }
    card.appendChild(title);
    if (typeof product.price === 'number' && Number.isFinite(product.price) && product.price >= 0 &&
        typeof product.currency === 'string' && /^[A-Z]{3}$/.test(product.currency)) {
      var price = document.createElement('p');
      price.className = 'local-product-price';
      try {
        price.textContent = new Intl.NumberFormat('en-GB', {
          style: 'currency', currency: product.currency
        }).format(product.price);
        card.appendChild(price);
      } catch (_) { /* Leave invalid currencies undisplayed. */ }
    }
    if (typeof product.description === 'string' && product.description) {
      var description = document.createElement('p');
      description.textContent = product.description;
      card.appendChild(description);
    }
    container.appendChild(card);
  });
}());
