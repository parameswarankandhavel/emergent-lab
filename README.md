# Burnout Score Checker

A simple, clean single-page web application for working professionals to assess their burnout levels.

## Features

- **7 Question Assessment**: Quick evaluation covering key burnout indicators
  - Mental exhaustion after work
  - Work thoughts outside hours
  - Morning motivation levels
  - Task overwhelm
  - Work-life balance satisfaction
  - Sleep quality
  - Sense of meaning in work

- **Instant Results**: 
  - Burnout score (0-100 scale)
  - Burnout level classification (Low, Moderate, High)
  - Personalized insights based on score

- **Simple & Clean UI**: Minimal, professional design with neutral colors

- **No Backend Required**: Pure frontend application - no database, no login

## How It Works

1. User answers 7 multiple-choice questions
2. Each question has 4 options (Never/Sometimes/Often/Always or equivalent)
3. Answers are scored and totaled
4. Score is converted to 0-100 scale
5. Results displayed with level and personalized insight

## Scoring System

- **Low Burnout (0-33)**: Managing well, low risk
- **Moderate Burnout (34-66)**: Some warning signs, take preventive action
- **High Burnout (67-100)**: High risk, immediate action recommended

## Running the Application

### Start the application:
```bash
sudo supervisorctl start frontend
```

### Check status:
```bash
sudo supervisorctl status
```

### View logs:
```bash
tail -f /var/log/supervisor/frontend.out.log
```

### Restart if needed:
```bash
sudo supervisorctl restart frontend
```

## Tech Stack

- **React 18**: Frontend framework
- **Tailwind CSS**: Styling
- **No backend**: Pure client-side application

## Deployment

This application can be deployed as a static site to any hosting platform:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront
- Any static hosting service

Simply run `yarn build` in the `/app/frontend` directory and deploy the `build` folder.

## Future Enhancements (Placeholder)

- Full burnout report with detailed analysis
- Personalized recommendations
- Progress tracking over time
- Downloadable PDF reports

---

**Disclaimer**: This tool is for informational purposes only and is not a substitute for professional medical or psychological advice.
