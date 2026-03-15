// ── Theme toggle ──
const themeBtn = document.getElementById('themeBtn');
if (themeBtn) {
  let dark = document.documentElement.getAttribute('data-theme') !== 'light';
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    dark = savedTheme === 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  themeBtn.textContent = dark ? '🌙' : '☀️';
  themeBtn.addEventListener('click', () => {
    dark = !dark;
    const t = dark ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('theme', t);
    themeBtn.textContent = dark ? '🌙' : '☀️';
  });
}

// ── Scroll to Top ──
const scrollToTopBtn = document.getElementById('scrollToTopBtn');
if (scrollToTopBtn) {
  const toggleVisibility = () => {
    const windowScrolled = window.scrollY > 200 || document.documentElement.scrollTop > 200;
    const fpBody = document.getElementById('fpBody');
    const fpScrolled = fpBody && fpBody.scrollTop > 200;
    
    if (windowScrolled || fpScrolled) {
      scrollToTopBtn.classList.add('visible');
    } else {
      scrollToTopBtn.classList.remove('visible');
    }
  };

  window.addEventListener('scroll', toggleVisibility);
  
  // The fpBody might be populated later, but the element exists
  const fpBody = document.getElementById('fpBody');
  if (fpBody) {
    fpBody.addEventListener('scroll', toggleVisibility);
  }

  scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    
    const fpBody = document.getElementById('fpBody');
    if (fpBody) {
      fpBody.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  });

  // Initial check
  toggleVisibility();
}
