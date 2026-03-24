// ──────────────────────────────────────────────────────────────────────
// minit Landing Page - JavaScript
// ──────────────────────────────────────────────────────────────────────

// ──────────────────────────────────────────────────────────────────────
// Mobile Menu Toggle
// ──────────────────────────────────────────────────────────────────────

const navToggle = document.getElementById('nav-toggle');
const mobileMenu = document.getElementById('mobile-menu');
const navMenu = document.getElementById('nav-menu');

navToggle?.addEventListener('click', () => {
  mobileMenu.classList.toggle('hidden');
  navToggle.classList.toggle('text-green-300');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('#mobile-menu a').forEach(link => {
  link.addEventListener('click', () => {
    mobileMenu.classList.add('hidden');
  });
});

// ──────────────────────────────────────────────────────────────────────
// Copy to Clipboard
// ──────────────────────────────────────────────────────────────────────

document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    const text = btn.getAttribute('data-text');
    
    try {
      await navigator.clipboard.writeText(text);
      
      // Visual feedback
      const icon = btn.innerHTML;
      btn.innerHTML = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>';
      btn.classList.add('text-green-400');
      
      setTimeout(() => {
        btn.innerHTML = icon;
        btn.classList.remove('text-green-400');
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  });
});

// ──────────────────────────────────────────────────────────────────────
// Smooth Scroll for Navigation Links
// ──────────────────────────────────────────────────────────────────────

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (href !== '#' && document.querySelector(href)) {
      e.preventDefault();
      
      const target = document.querySelector(href);
      const headerOffset = 80;
      const elementPosition = target.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  });
});

// ──────────────────────────────────────────────────────────────────────
// Intersection Observer for Scroll Animations
// ──────────────────────────────────────────────────────────────────────

const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.animation = 'fade-in-up 0.8s ease-out forwards';
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe all feature cards and sections
document.querySelectorAll('[id^="features"] > div > div > div, [id^="install"] > div > div, [id^="problem"] > div > div > div').forEach(el => {
  el.style.opacity = '0';
  observer.observe(el);
});

// ──────────────────────────────────────────────────────────────────────
// Add feature card class for animations
// ──────────────────────────────────────────────────────────────────────

document.querySelectorAll('[id="features"] ~ * [class*="md:grid"]').forEach(grid => {
  grid.querySelectorAll('[class*="group"]').forEach((card, index) => {
    card.classList.add('feature-card');
    card.style.animation = `fade-in-up 0.8s ease-out ${index * 0.1}s backwards`;
  });
});

// ──────────────────────────────────────────────────────────────────────
// Parallax Effect on Hero Section
// ──────────────────────────────────────────────────────────────────────

const heroSection = document.querySelector('section:first-of-type');
if (heroSection) {
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallaxElements = heroSection.querySelectorAll('[class*="blur-3xl"]');
    
    parallaxElements.forEach((el, index) => {
      const offset = scrolled * (0.3 + index * 0.1);
      el.style.transform = `translateY(${offset}px)`;
    });
  });
}

// ──────────────────────────────────────────────────────────────────────
// Active Navigation Link Highlighting
// ──────────────────────────────────────────────────────────────────────

window.addEventListener('scroll', () => {
  const sections = document.querySelectorAll('section[id]');
  let current = '';
  
  sections.forEach(section => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (scrollY >= sectionTop - 200) {
      current = section.getAttribute('id');
    }
  });

  // Update navigation links
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.classList.remove('text-green-400');
    link.classList.add('text-slate-300');
    
    if (link.getAttribute('href').slice(1) === current) {
      link.classList.remove('text-slate-300');
      link.classList.add('text-green-400');
    }
  });
});

// ──────────────────────────────────────────────────────────────────────
// Page Load Animation
// ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Add fade-in animation to body
  document.body.style.animation = 'fade-in 0.6s ease-out';
  
  // Animate hero title on load
  const heroTitle = document.querySelector('.hero-title');
  if (heroTitle) {
    heroTitle.style.animation = 'fade-in-up 0.8s ease-out';
  }

  // Initialize buttons with smooth interactions
  document.querySelectorAll('button, a[href*="pypi"], a[href*="Get Started"]').forEach(el => {
    el.addEventListener('mouseenter', function() {
      if (this.classList.contains('hover:scale-105')) {
        this.style.transform = 'scale(1.05)';
      }
    });
    
    el.addEventListener('mouseleave', function() {
      this.style.transform = 'scale(1)';
    });
  });
});

// ──────────────────────────────────────────────────────────────────────
// Smooth Loading of External Links
// ──────────────────────────────────────────────────────────────────────

document.querySelectorAll('a[target="_blank"]').forEach(link => {
  link.addEventListener('click', (e) => {
    // Add smooth fade effect before opening
    link.style.transition = 'opacity 0.3s ease';
    
    // Give a visual feedback
    link.style.opacity = '0.8';
    setTimeout(() => {
      link.style.opacity = '1';
    }, 300);
  });
});

// ──────────────────────────────────────────────────────────────────────
// Performance: Lazy load images (if added in future)
// ──────────────────────────────────────────────────────────────────────

if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
}

// ──────────────────────────────────────────────────────────────────────
// Keyboard Navigation Support
// ──────────────────────────────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
  // Esc key to close mobile menu
  if (e.key === 'Escape') {
    mobileMenu?.classList.add('hidden');
  }
  
  // Alt+C to copy installation command (accessibility)
  if (e.altKey && e.key === 'c') {
    const installBtn = document.querySelector('.copy-btn[data-text="pip install minit-cli"]');
    if (installBtn) {
      installBtn.click();
    }
  }
});

// ──────────────────────────────────────────────────────────────────────
// Utils
// ──────────────────────────────────────────────────────────────────────

// Get current section for analytics/tracking
function getCurrentSection() {
  const sections = document.querySelectorAll('section[id]');
  let current = 'hero';
  
  sections.forEach(section => {
    if (section.getBoundingClientRect().top < window.innerHeight / 2) {
      current = section.getAttribute('id');
    }
  });
  
  return current;
}

// Track scroll position for analytics (optional)
let scrollTimeout;
window.addEventListener('scroll', () => {
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => {
    const section = getCurrentSection();
    // Could send analytics event here
    console.debug('Current section:', section);
  }, 100);
});

// ──────────────────────────────────────────────────────────────────────
// PWA Ready (future enhancement)
// ──────────────────────────────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  // Uncomment when service worker is ready
  // navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration failed:', err));
}

console.log('minit Landing Page loaded successfully! 🚀');
