/**
 * NEURAL NAVIGATOR LAB - Interactive Theme JS
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initMobileMenu();
  initCategoryFiltering();
  initSearchFiltering();
  initReadingProgressBar();
  initCodeCopyButtons();
});

/* 1. Navbar Scroll Blur Effect */
function initNavbarScroll() {
  const navbar = document.querySelector('.site-navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

/* 2. Mobile Menu Toggle */
function initMobileMenu() {
  const toggleBtn = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (!toggleBtn || !navLinks) return;

  toggleBtn.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });
}

/* 3. Category & Tag Interactive Filtering */
function initCategoryFiltering() {
  const categoryBtns = document.querySelectorAll('.category-btn');
  const articleCards = document.querySelectorAll('.article-card');

  if (!categoryBtns.length || !articleCards.length) return;

  categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Set active class
      categoryBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const selectedCategory = btn.getAttribute('data-category');

      articleCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category') || '';
        const cardTags = card.getAttribute('data-tags') || '';

        if (selectedCategory === 'all' || 
            cardCategory.toLowerCase() === selectedCategory.toLowerCase() || 
            cardTags.toLowerCase().includes(selectedCategory.toLowerCase())) {
          card.style.display = 'flex';
          card.style.opacity = '1';
        } else {
          card.style.display = 'none';
          card.style.opacity = '0';
        }
      });
    });
  });
}

/* 4. Live Instant Search */
function initSearchFiltering() {
  const searchInput = document.getElementById('search-input');
  const articleCards = document.querySelectorAll('.article-card');

  if (!searchInput || !articleCards.length) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();

    articleCards.forEach(card => {
      const title = card.querySelector('.article-title')?.textContent.toLowerCase() || '';
      const excerpt = card.querySelector('.article-excerpt')?.textContent.toLowerCase() || '';
      const category = card.getAttribute('data-category')?.toLowerCase() || '';
      const tags = card.getAttribute('data-tags')?.toLowerCase() || '';

      if (title.includes(query) || excerpt.includes(query) || category.includes(query) || tags.includes(query)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

/* 5. Reading Progress Bar for Blog Posts */
function initReadingProgressBar() {
  const progressBar = document.querySelector('.reading-progress-bar');
  if (!progressBar) return;

  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight <= 0) return;
    const progress = (window.scrollY / totalHeight) * 100;
    progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
  });
}

/* 6. Copy Code Snippet Button */
function initCodeCopyButtons() {
  const codeBlocks = document.querySelectorAll('pre');

  codeBlocks.forEach(block => {
    // Avoid duplicate buttons
    if (block.querySelector('.copy-code-btn')) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
    copyBtn.style.cssText = `
      position: absolute;
      top: 10px;
      right: 10px;
      padding: 0.35rem 0.75rem;
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 6px;
      color: #94A3B8;
      font-size: 0.75rem;
      font-family: var(--font-heading, sans-serif);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      z-index: 10;
    `;

    copyBtn.addEventListener('click', () => {
      const code = block.querySelector('code')?.innerText || block.innerText;
      navigator.clipboard.writeText(code).then(() => {
        copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: #10B981;"></i> Copied!';
        setTimeout(() => {
          copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
        }, 2000);
      });
    });

    block.style.position = 'relative';
    block.appendChild(copyBtn);
  });
}
