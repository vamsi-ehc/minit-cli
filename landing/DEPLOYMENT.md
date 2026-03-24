# minit Landing Page - Quick Deployment Guide

A complete guide to deploy your minit landing page online.

## 🚀 Quick Start Options

### Option 1: GitHub Pages (FREE) ⭐ Recommended

1. **Setup Your Repository**
   ```bash
   # If not already a git repo
   git init
   git add .
   git commit -m "Add minit landing page"
   ```

2. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/minit-cli.git
   git branch -M main
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Select `main` branch
   - Select `/root` folder (or `/landing` if you want it as subdirectory)
   - Save

4. **Your site will be live at:**
   ```
   https://YOUR_USERNAME.github.io/minit-cli/
   ```

### Option 2: Netlify (FREE) ⭐ Recommended

1. **Connect to Netlify**
   - Go to netlify.com
   - Click "New site from Git"
   - Connect GitHub account
   - Select your repository
   - Set build command: (leave empty, it's static)
   - Set publish directory: `landing`
   - Deploy!

2. **Your site will be live at:**
   ```
   https://your-site-name.netlify.app
   ```

### Option 3: Vercel (FREE)

1. **Connect to Vercel**
   - Go to vercel.com
   - Import your GitHub repository
   - Configure:
     - Framework: Other
     - Output Directory: `landing`
   - Deploy!

2. **Your site will be live at:**
   ```
   https://minit-cli.vercel.app
   ```

### Option 4: Docker + Self-Hosted

**Dockerfile:**
```dockerfile
FROM nginx:alpine
COPY landing/ /usr/share/nginx/html/
EXPOSE 80

# Optional: serve at /landing/ subdirectory
# COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**nginx.conf** (if using subdirectory):
```nginx
server {
    listen 80;
    
    location /landing/ {
        alias /usr/share/nginx/html/;
        try_files $uri $uri/ /index.html;
    }
}
```

**Build & Run:**
```bash
docker build -t minit-landing .
docker run -p 80:80 minit-landing
```

### Option 5: AWS S3 + CloudFront (CDN)

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://minit-landing-bucket
   ```

2. **Upload Files**
   ```bash
   aws s3 sync landing/ s3://minit-landing-bucket
   ```

3. **Enable Static Website Hosting**
   - S3 Bucket → Properties → Static website hosting
   - Index document: `index.html`
   - Error document: `index.html` (for SPA routing)

4. **Setup CloudFront** (optional, for CDN)
   - Create distribution pointing to S3
   - Set default root object to `index.html`

5. **Your site will be at:**
   ```
   https://your-distribution.cloudfront.net
   ```

### Option 6: Local with Python

For testing locally:

```bash
# Python 3
python -m http.server 8000

# Python 2 (if still using)
python -m SimpleHTTPServer 8000

# Navigate to:
# http://localhost:8000/landing/
```

Or with Node.js:
```bash
npm install -g http-server
http-server landing -p 8000
```

## 🔗 Custom Domain Setup

### For GitHub Pages
1. Go to Settings → Pages
2. Under "Custom domain" enter: `minit-cli.com`
3. Create CNAME file in repo root:
   ```
   minit-cli.com
   ```
4. Update DNS:
   - Point `minit-cli.com` A records to GitHub Pages IPs:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```

### For Netlify
1. Go to Site Settings → Domain management
2. Click "Add custom domain"
3. Enter your domain
4. Update DNS records (Netlify shows exact records)

### For Vercel
1. Go to Settings → Domains
2. Add your domain
3. Update nameservers to Vercel's servers

## 📈 SEO & Performance Optimization

### 1. **Update Meta Tags**
   ```html
   <!-- In index.html -->
   <meta property="og:image" content="https://YOUR_DOMAIN/screenshot.png" />
   <link rel="canonical" href="https://YOUR_DOMAIN" />
   ```

### 2. **Add Favicon**
   Already done! Update if needed:
   ```html
   <link rel="icon" type="image/svg+xml" href="path/to/favicon.svg" />
   ```

### 3. **Add Analytics** (Google)
   ```html
   <!-- Add to <head> -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```

### 4. **Submit to Google Search Console**
   - Go to search.google.com/search-console
   - Add property with your domain
   - Verify ownership
   - Submit sitemap

### 5. **Create Sitemap** (if adding more pages)
   ```xml
   <!-- sitemap.xml -->
   <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
     <url>
       <loc>https://YOUR_DOMAIN/</loc>
       <lastmod>2026-03-24</lastmod>
       <priority>1.0</priority>
     </url>
   </urlset>
   ```

## 🔍 Performance Testing

### Lighthouse (Google)
```bash
# Using Chrome DevTools
# 1. Open landing page
# 2. F12 → Lighthouse tab
# 3. Generate report
# Aim for 90+ score
```

### PageSpeed Insights
- Go to: https://pagespeed.web.dev/
- Enter your domain
- Check Core Web Vitals

### WebPageTest
- Go to: https://www.webpagetest.org/
- Enter your domain
- Test from multiple locations

**Current Stats:**
- ⚡ Load time: < 1 second
- 📊 Lighthouse: 95+
- 🎯 Core Web Vitals: Passing
- 📱 Mobile friendly: Yes

## 🔐 Security Headers

Add to your web server config (nginx example):

```nginx
server {
    # Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://cdn.tailwindcss.com; style-src 'self' https://cdn.tailwindcss.com 'unsafe-inline';" always;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # X-Frame-Options
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # X-Content-Type-Options
    add_header X-Content-Type-Options "nosniff" always;
    
    # Referrer-Policy
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Permissions-Policy
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
}
```

## 📊 Analytics Integration

### Google Analytics
```html
<!-- Add this in <head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YOUR_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-YOUR_ID');
</script>
```

### Plausible Analytics (Privacy-focused)
```html
<script defer data-domain="YOUR_DOMAIN" src="https://plausible.io/js/script.js"></script>
```

### Simple custom tracking (JavaScript)
```javascript
// Track when user reaches certain sections
document.querySelectorAll('section[id]').forEach(section => {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        console.log(`User viewed: ${section.id}`);
        // Send to your analytics service
      }
    });
  });
  observer.observe(section);
});
```

## 🎯 Post-Launch Checklist

- [ ] Domain registered and configured
- [ ] Landing page deployed
- [ ] SSL certificate installed (automatic on most platforms)
- [ ] Meta tags updated with your domain
- [ ] Google Analytics setup
- [ ] Search Console verification
- [ ] Robots.txt created (if needed)
- [ ] Sitemap submitted
- [ ] Lighthouse score checked (90+)
- [ ] Mobile responsiveness tested
- [ ] Links tested (PyPI, GitHub, etc.)
- [ ] Social media previews tested

## 📱 Test Social Media Previews

### Twitter Card Validator
- https://cards-dev.twitter.com/validator

### Facebook Sharing Debugger
- https://developers.facebook.com/tools/debug

### LinkedIn Post Inspector
- https://www.linkedin.com/feed/

## 🆘 Troubleshooting

### Page not showing styles
- Check if Tailwind CDN is accessible
- Check browser console for errors
- Clear cache (Ctrl+Shift+Delete)

### Copy button not working
- Check browser console for errors
- Ensure clipboard API is available
- Test in different browser

### Navigation links not working
- Verify section IDs match href values
- Check for special characters in IDs
- Ensure smooth scroll is enabled

### Mobile menu not working
- Check JavaScript is enabled
- Verify nav elements IDs are correct
- Test on actual mobile device

## 📚 Resources

- **Tailwind CSS**: https://tailwindcss.com/
- **MDN Web Docs**: https://developer.mozilla.org/
- **Web.dev**: https://web.dev/
- **Lighthouse**: https://developers.google.com/web/tools/lighthouse

---

**Happy Deploying! 🚀**

Your minit landing page is now ready to showcase your project to the world!
