# minit Landing Page - Configuration & Customization Guide

Easily customize the landing page to match your branding and messaging.

## 🎨 Visual Customization

### Colors

**Edit `assets/style.css` - Root Variables:**

```css
:root {
  --primary: #22c55e;           /* Main accent color (green) */
  --primary-dark: #16a34a;      /* Darker shade for hover */
  --primary-light: #4ade80;     /* Lighter shade for highlights */
  --bg-dark: #0f172a;           /* Dark background */
  --bg-darker: #040b04;         /* Darker background */
  --text-primary: #e2e8f0;      /* Main text color */
  --text-secondary: #cbd5e1;    /* Secondary text */
  --text-muted: #94a3b8;        /* Muted/gray text */
  --border-color: #1e293b;      /* Border color */
  --border-light: #475569;      /* Light border */
}
```

**Preset Combinations:**

| Name | Primary | Bg-Dark | Use Case |
|------|---------|---------|----------|
| **Green** (Current) | #22c55e | #0f172a | Tech/Dev tools |
| **Blue** | #3b82f6 | #0c1222 | Enterprise |
| **Purple** | #a855f7 | #1f0933 | Creative |
| **Red** | #ef4444 | #1f0712 | Alert/Urgent |
| **Cyan** | #06b6d4 | #0c1419 | Modern/Fresh |

**Quick Color Change Example - Blue Theme:**

```css
:root {
  --primary: #3b82f6;
  --primary-dark: #1d4ed8;
  --primary-light: #60a5fa;
  --bg-dark: #0c1222;
  --bg-darker: #030812;
}
```

### Fonts

**To use a custom font family instead of monospace:**

```html
<!-- In index.html, add to <head> -->
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
```

```css
/* In assets/style.css, update body */
body {
  font-family: 'Poppins', system-ui, -apple-system, sans-serif;
}

/* Keep monospace for code blocks */
code {
  font-family: 'Courier New', monospace;
}
```

### Spacing & Sizing

Edit these Tailwind classes directly in HTML:
- `p-8` → `p-4` (padding)
- `py-20` → `py-32` (vertical padding)
- `max-w-5xl` → `max-w-7xl` (container width)
- `text-5xl` → `text-6xl` (heading size)

## 📝 Content Changes

### Hero Section
Located in `index.html` around line 120:

```html
<h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
  <span class="text-green-400">Real-Time System</span>
  <br />
  <span class="text-slate-300">Monitoring Made Simple</span>
</h1>

<p class="text-lg sm:text-xl text-slate-400 mb-8">
  minit is a lightning-fast, developer-friendly CLI tool...
</p>
```

### Problem Section
Located around line 190:

Update the 3 problem cards:
```html
<div class="group relative p-8 ...">
  <div class="text-4xl mb-4">⚠️</div>
  <h3 class="text-xl font-bold...">System Blindness</h3>
  <p class="text-slate-400">
    Limited visibility into real-time system metrics...
  </p>
</div>
```

**Available Icons (emoji):**
```
⚠️  ⚡  📊  💻  🌐  🎨  🚀  📈  ✅  🔍  🛡️  ⏱️  🎯
```

### Features Section
Located around line 240:

Edit feature cards (6 total):
```html
<div class="group relative...">
  <div class="text-5xl mb-4">📈</div>
  <h3 class="text-xl font-bold text-green-400">Feature Name</h3>
  <p class="text-slate-300">Feature description here...</p>
</div>
```

### Installation Steps
Located around line 350:

Update the 3 installation steps and commands:
```html
<h3 class="text-xl font-bold text-slate-200">Step Description</h3>
<code class="text-green-400 font-bold">your command here</code>
```

### Links & URLs

All links are easily editable:

```html
<!-- PyPI Link -->
<a href="https://pypi.org/project/minit-cli/" target="_blank">PyPI Package</a>

<!-- GitHub Links (add these) -->
<a href="https://github.com/YOUR_USERNAME/minit-cli" target="_blank">GitHub</a>

<!-- Documentation Links (add these) -->
<a href="https://github.com/YOUR_USERNAME/minit-cli/wiki" target="_blank">Docs</a>
```

## 🖼️ Adding Images & Screenshots

### Customize Logo

The logo is a professional SVG located at `assets/logo.svg`. It features:
- **Circular monitoring ring**: Represents real-time monitoring
- **Graph line**: Shows data visualization
- **Lightning bolt**: Symbolizes speed and performance

Edit the SVG directly to customize colors, size, or design. The current implementation uses:
- Color: `#22c55e` (green-500)
- Background: `#0f172a` (slate-950)

```html
<!-- In Hero section, after title -->
<div class="mt-8 max-w-4xl mx-auto">
  <img 
    src="assets/images/demo.png" 
    alt="minit dashboard screenshot"
    class="rounded-lg shadow-2xl border border-green-900/20"
  />
</div>
```

### Add Feature Screenshots

```html
<!-- In Features section, alongside text -->
<div class="group relative overflow-hidden rounded-xl...">
  <img 
    src="assets/images/feature-1.png"
    alt="Live dashboard feature"
    class="w-full h-64 object-cover rounded"
  />
</div>
```

### Create Image Folder

```bash
mkdir -p landing/assets/images
# Place your screenshot files here:
# - demo.png
# - feature-1.png
# - feature-2.png
```

## 🎨 Dark/Light Mode Toggle

Add a theme switcher (optional):

```html
<!-- In navigation -->
<button id="theme-toggle" class="text-2xl">🌙</button>
```

```javascript
// In assets/script.js

const themeToggle = document.getElementById('theme-toggle');

// Check saved preference
const prefersDark = localStorage.getItem('theme') === 'dark' ?? true;
document.documentElement.classList.toggle('dark', prefersDark);

themeToggle?.addEventListener('click', () => {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  themeToggle.textContent = isDark ? '☀️' : '🌙';
});
```

## 📱 Breakpoints & Responsive Design

Tailwind breakpoints used:
- `sm` - 640px (tablets)
- `md` - 768px (small laptops)
- `lg` - 1024px (desktops)

**Example - Responsive Classes:**
```html
<!-- Text size: small on mobile, large on desktop -->
<h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl">

<!-- Hidden on mobile, visible on desktop -->
<div class="hidden md:block">Desktop only content</div>

<!-- Visible on mobile, hidden on desktop -->
<div class="md:hidden">Mobile only content</div>

<!-- Grid: 1 column mobile, 2 columns tablet, 3 columns desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```

## ⚙️ Animation Customization

**Edit animation durations in `assets/style.css`:**

```css
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(30px);  /* Change distance */
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Changes animation speed */
.fade-in-up {
  animation: fade-in-up 0.8s ease-out;  /* Change 0.8s to desired duration */
}
```

**Preset durations:**
- `0.3s` - Quick (UI interactions)
- `0.6s` - Medium (page transitions)
- `0.8s` - Slow (entrance animations)
- `1.2s` - Very slow (hero sections)

## 🔊 Sound Effects (Optional)

Add notification sounds on button clicks:

```html
<!-- Add audio file -->
<audio id="click-sound" preload="auto">
  <source src="assets/sounds/click.mp3" type="audio/mpeg">
</audio>
```

```javascript
// In assets/script.js
const clickSound = document.getElementById('click-sound');

document.querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', () => {
    clickSound.currentTime = 0;
    clickSound.play().catch(() => {}); // Ignore if autoplay blocked
  });
});
```

## 🌐 Multilingual Support

**Add language switcher (optional):**

```html
<!-- Language selector in nav -->
<select id="lang-select">
  <option value="en">English</option>
  <option value="es">Español</option>
  <option value="fr">Français</option>
</select>
```

```javascript
// translations.js
const translations = {
  en: {
    'hero-title': 'Real-Time System Monitoring',
    'hero-desc': 'minit is a lightning-fast CLI tool...',
  },
  es: {
    'hero-title': 'Monitoreo de Sistema en Tiempo Real',
    'hero-desc': 'minit es una herramienta CLI ultrarrápida...',
  }
};
```

## 📊 Analytics Tracking Events

Add custom tracking to important actions:

```javascript
// In assets/script.js

// Track feature views
function trackEvent(eventName, category) {
  if (window.gtag) {
    gtag('event', eventName, {
      'event_category': category
    });
  }
}

// Track button clicks
document.querySelectorAll('a[href*="pypi"]').forEach(link => {
  link.addEventListener('click', () => {
    trackEvent('pypi_click', 'engagement');
  });
});

// Track section views
document.querySelectorAll('section[id]').forEach(section => {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        trackEvent(`section_${section.id}`, 'page_view');
      }
    });
  });
  observer.observe(section);
});
```

## 🔗 SEO Configuration

**Update meta tags:**

```html
<!-- In <head> -->
<title>minit - Your Custom Title Here</title>
<meta name="description" content="Your custom description here" />
<meta name="keywords" content="your, keywords, here" />
<meta property="og:title" content="Your title" />
<meta property="og:description" content="Your description" />
<meta property="og:image" content="https://your-domain.com/image.png" />
<link rel="canonical" href="https://your-domain.com" />
```

**Add JSON-LD Schema:**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "minit",
  "description": "Real-time system monitoring CLI",
  "applicationCategory": "SystemUtility",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
</script>
```

## ✅ Configuration Checklist

- [ ] Updated all color variables
- [ ] Changed fonts if desired
- [ ] Updated all copy/text content
- [ ] Changed links (PyPI, GitHub, docs)
- [ ] Added custom images
- [ ] Updated meta tags & SEO
- [ ] Updated favicon
- [ ] Tested on mobile
- [ ] Tested all links work
- [ ] Checked animations smooth

## 🚀 Ready to Deploy!

Once customized:

1. Test locally: `python -m http.server 8000`
2. Run Lighthouse check (target 90+ score)
3. Test on mobile device
4. Deploy using one of the options from `DEPLOYMENT.md`

---

**Questions? Check the main README.md for more info!** 📚
