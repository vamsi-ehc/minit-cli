# minit Landing Page 🚀

A beautiful, responsive, SEO-optimized landing page for the minit system monitoring CLI tool.

## 📁 Folder Structure

```
landing/
├── index.html          # Main landing page
├── assets/
│   ├── style.css      # Custom styles & animations
│   └── script.js      # Interactive features & animations
└── README.md          # This file
```

## ✨ Features

### 🎨 Design & UI
- **Dark Theme**: Modern dark UI optimized for developer audiences
- **Responsive Design**: Perfect on mobile, tablet, and desktop
- **Smooth Animations**: Fade-in, slide-in, and parallax effects
- **Green Accent Colors**: Matches minit dashboard aesthetic
- **Tailwind CSS**: Utility-based styling with custom animations

### 📱 Responsive & Mobile-First
- Mobile hamburger navigation
- Touch-friendly buttons and links
- Optimized typography for all screen sizes
- Flexible grid layouts

### ⚡ Performance
- Lightweight CSS (custom + Tailwind via CDN)
- No heavy JavaScript frameworks
- Vanilla JS for interactions
- Optimized asset loading

### 🔍 SEO & Accessibility
- **Meta Tags**: OpenGraph, Twitter Card, descriptions
- **Semantic HTML**: Proper heading hierarchy
- **Keyboard Navigation**: Tab, Enter, Escape support
- **Focus Indicators**: Visible focus states for accessibility
- **Alt Text Ready**: Structure supports image optimization
- **Structured Data Ready**: Can add JSON-LD

### 💬 Copy to Clipboard
- One-click command copying
- Visual feedback with checkmark
- Supports installation commands and URLs

### 🎯 Smooth Scrolling
- Anchor link smooth navigation
- Active section highlighting
- Parallax effects on hero section

## 🚀 How to Use

### Local Development

1. **Open with Live Server:**
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Or use your editor's "Live Server" extension
   ```

2. **Open in Browser:**
   - Navigate to `http://localhost:8000/landing/`

### Deployment

#### Option 1: Static File Hosting
- Upload the `landing` folder to GitHub Pages, Netlify, Vercel, or any static host
- No build process needed!

#### Option 2: GitHub Pages
```bash
# In your GitHub repo settings, set Pages source to the landing folder
# Your page will be live at: https://yourusername.github.io/minit-cli/landing/
```

#### Option 3: Docker (Optional)
```dockerfile
FROM nginx:alpine
COPY landing /usr/share/nginx/html
EXPOSE 80
```

#### Option 4: Include in Python Project
You can serve this as static files from your minit web dashboard:
```python
# In your Flask/FastAPI app
from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/landing/')
def landing():
    return send_from_directory('landing', 'index.html')

@app.route('/landing/<path:path>')
def landing_assets(path):
    return send_from_directory('landing', path)
```

## 🎯 Sections

### 1. **Navigation**
- Fixed sticky header
- Mobile hamburger menu
- Direct links to sections
- CTA button to PyPI

### 2. **Hero Section**
- Eye-catching headline
- Problem statement
- CTA buttons
- Quick install command with copy button
- Scroll indicator

### 3. **Problem Section**
- 3 key problems solved
- Problem cards with icons
- Solution summary

### 4. **Features Section**
- 6 feature cards with icons
- Hover animations
- Grid layout (responsive)
- Feature highlights

### 5. **Installation Section**
- Step-by-step quick start
- Numbered steps
- Copy-able commands
- Direct PyPI link

### 6. **Footer**
- Links to PyPI
- GitHub repository links
- Copyright info

## 🎨 Customization

### Colors
Edit the CSS variables in `assets/style.css`:
```css
:root {
  --primary: #22c55e;           /* Green accent */
  --bg-dark: #0f172a;           /* Dark background */
  --text-primary: #e2e8f0;      /* Light text */
  /* ... more colors ... */
}
```

### Fonts
The page uses `ui-monospace` (system monospace fonts) for a developer feel. To change:
- Edit the `font-mono` class in Tailwind
- Or add custom fonts via `@import` in CSS

### Content
All text is in `index.html`. Edit directly:
- Headings in `<h1>`, `<h2>`, `<h3>` tags
- Descriptions in `<p>` tags
- Links in `<a>` tags

### Icons
Currently using Tailwind/SVG inline icons. The project logo (lightning bolt + monitoring ring) is located in `assets/logo.svg`.

## 📊 SEO Optimization

### Included SEO Features

✅ **Meta Tags**
- Title: SEO-friendly with keywords
- Description: Compelling summary
- Keywords: Relevant search terms
- Author tag
- Robots directive

✅ **Open Graph**
- og:title, og:description
- og:type for social sharing
- og:image ready (update URL after adding image)

✅ **Twitter Card**
- twitter:card for Twitter preview
- twitter:title and description

✅ **Semantic HTML**
- Proper heading hierarchy (h1 → h2)
- Semantic sections with IDs
- Navigation landmarks

### To Improve SEO Further

1. **Add a Logo/Demo Image**
   ```html
   <meta property="og:image" content="path/to/screenshot.png" />
   ```

2. **Add JSON-LD Structured Data**
   ```html
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "SoftwareApplication",
     "name": "minit",
     "description": "Real-time system monitoring",
     "applicationCategory": "SystemUtility"
   }
   </script>
   ```

3. **Setup Sitemap** (if hosting with other pages)

4. **Add Analytics**
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
   ```

## ⌨️ Keyboard Shortcuts

- `Tab` - Navigate through links and buttons
- `Enter` - Activate buttons/links
- `Escape` - Close mobile menu
- `Alt+C` - Copy installation command

## 🔗 Important Links

- **PyPI Official**: https://pypi.org/project/minit-cli/
- **Installation Command**: `pip install minit-cli`
- **Web Dashboard URL**: `http://localhost:7770`

## 🚀 Performance Tips

1. **Lighthouse Score**: Should be 95+ (Core Web Vitals optimized)
2. **Page Load**: < 1 second on modern connections
3. **No Third-Party Scripts**: Only Tailwind CDN (optional to inline)
4. **Mobile Optimized**: Passes mobile performance tests

## 🛠️ Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 15+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ✅ IE not supported (modern standards only)

## 📝 Accessibility Features

- **WCAG 2.1 AA Compliant**
- Keyboard navigation support
- Focus indicators on all interactive elements
- High contrast colors (4.5:1 ratio minimum)
- Proper heading hierarchy
- Semantic HTML structure
- Reduced motion support (`prefers-reduced-motion`)

## 🎬 Animation Details

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| fade-in-up | 0.8s | ease-out | Page load, scroll |
| fade-in | 0.6s | ease-out | Page elements |
| slide-in-left | 0.3s | ease-out | Mobile menu |
| pulse-glow | 2s | ease-in-out | Accent elements |
| float | varies | ease-in-out | Hero section |

## 🔧 Development

### Adding New Sections

1. Add a `<section id="name">` in HTML
2. Create content with proper heading hierarchy
3. Use `.group` class for hover effects
4. Animations happen automatically via scroll observer

### JavaScript Events

The script handles:
- Mobile menu toggle
- Copy to clipboard
- Smooth scroll navigation
- Intersection observer animations
- Parallax scrolling
- Active link highlighting
- Keyboard shortcuts

## 📦 Dependencies

- **Tailwind CSS** (via CDN)
- **Vanilla JavaScript** (no frameworks)
- **Semantic HTML5** (no polyfills needed)

## 🚀 Next Steps

1. Customize the colors and content
2. Add your project logo/screenshot
3. Deploy to your hosting platform
4. Monitor page performance with Lighthouse
5. Setup Google Analytics (optional)
6. Integrate with your existing site

## 📞 Support

For questions or issues, refer to the main minit repository documentation.

---

**Created for minit - Real-Time System Monitoring** ⚡

Made with 💚 for developers, by developers.
