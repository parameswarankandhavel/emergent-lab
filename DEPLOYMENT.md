# Deployment Guide - Burnout Score Checker

This guide explains how to deploy your Burnout Score Checker to various static hosting platforms.

## Prerequisites

- Node.js installed (v14 or higher)
- Yarn package manager

## Build for Production

```bash
cd /app/frontend
yarn build
```

This creates an optimized production build in the `/app/frontend/build` folder.

## Deployment Options

### 1. Netlify (Recommended for Beginners)

**Option A: Drag and Drop**
1. Build your app: `yarn build`
2. Go to [app.netlify.com](https://app.netlify.com)
3. Drag the `build` folder to Netlify's deployment zone
4. Your app is live!

**Option B: CLI Deployment**
```bash
npm install -g netlify-cli
cd /app/frontend
yarn build
netlify deploy --prod
```

### 2. Vercel

```bash
npm install -g vercel
cd /app/frontend
vercel --prod
```

### 3. GitHub Pages

1. Install gh-pages:
```bash
cd /app/frontend
yarn add -D gh-pages
```

2. Add to `package.json`:
```json
"homepage": "https://yourusername.github.io/burnout-checker",
"scripts": {
  "predeploy": "yarn build",
  "deploy": "gh-pages -d build"
}
```

3. Deploy:
```bash
yarn deploy
```

### 4. AWS S3 + CloudFront

```bash
# Build
yarn build

# Upload to S3 bucket
aws s3 sync build/ s3://your-bucket-name

# Configure S3 bucket for static website hosting
aws s3 website s3://your-bucket-name --index-document index.html
```

### 5. Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Select 'build' as your public directory
# Configure as single-page app: Yes
firebase deploy
```

## Custom Domain Setup

After deployment, most platforms allow you to add a custom domain:

- **Netlify**: Domain settings → Add custom domain
- **Vercel**: Project settings → Domains
- **GitHub Pages**: Repository settings → Pages → Custom domain

## Environment Considerations

Since this is a **pure frontend app** with:
- ✅ No backend API
- ✅ No database
- ✅ No authentication
- ✅ No server-side processing

You can deploy it anywhere that serves static HTML/CSS/JS files!

## Post-Deployment Testing

After deployment, test:
1. ✅ All 7 questions display correctly
2. ✅ Form validation (must answer all questions)
3. ✅ Score calculation works
4. ✅ Results display with correct level (Low/Moderate/High)
5. ✅ Personalized insights appear
6. ✅ "Unlock Full Report" button shows alert
7. ✅ "Retake Assessment" resets the form

## Performance Optimization

The build is already optimized with:
- Code splitting
- Minification
- Asset optimization
- Tailwind CSS purging (unused styles removed)

## Monitoring

Consider adding:
- **Google Analytics** for usage tracking
- **Sentry** for error monitoring
- **Hotjar** for user behavior insights

## Cost

All recommended platforms offer **free tiers** perfect for this application:
- Netlify: Free (100GB bandwidth/month)
- Vercel: Free (100GB bandwidth/month)
- GitHub Pages: Free (unlimited for public repos)
- Firebase: Free (10GB storage, 360MB/day transfers)

## Support

For deployment issues:
- Check build logs for errors
- Ensure all dependencies are installed
- Verify Node.js version compatibility
- Clear cache and rebuild if needed

---

**Your app is ready to share with the world! 🚀**
