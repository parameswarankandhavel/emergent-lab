# 🚀 Quick Start - Testing Your Burnout App

## ✅ **ISSUE FIXED!**

Registration was failing because the app tried to send an email OTP automatically, but Resend API key isn't configured yet. I've fixed it so registration succeeds even without the email service.

---

## 🎯 **HOW TO TEST NOW**

### **Step 1: Open Two Terminal Windows**

**Terminal 1 - Monitor OTP Codes:**
```bash
# This will show you the OTP codes as they're generated
tail -f /var/log/supervisor/backend.out.log | grep "🔑 OTP"
```

**Terminal 2 - Or use the helper script:**
```bash
/app/scripts/monitor_otp.sh
```

### **Step 2: Open the App**

Go to: **http://localhost:3000**

### **Step 3: Register**

1. Fill in your details:
   - Name: John Doe
   - Email: test@example.com
   - Mobile: +1234567890

2. Click **"Continue"**

3. ✅ **Registration should now succeed!**

### **Step 4: Get Email OTP**

1. The app will show "Verify Your Email" page
2. Click **"Send OTP"** or **"Resend OTP"** button
3. **Check Terminal 1** - you'll see something like:
   ```
   🔑 OTP GENERATED [EMAIL]: 123456 for test@example.com
   ```
4. Copy that 6-digit code
5. Paste it in the form
6. Click "Verify Email"

### **Step 5: Mobile OTP**

For mobile OTP, since it's in **mock mode**:
- Click "Send OTP"
- Enter **ANY** 6-digit code (e.g., "123456")
- Click "Verify Mobile"
- ✅ It will work!

### **Step 6: Complete Assessment**

Answer all 7 questions and submit

### **Step 7: See Preview**

You'll see your burnout score and a preview insight

### **Step 8: Testing Payment Flow**

When you click "Unlock Report", it will try to redirect to Gumroad.

**To test without actually paying:**
1. Note your session ID (visible in browser console or backend logs)
2. Manually visit this URL in your browser:
   ```
   http://localhost:3000/payment-return?payment=success&session_id=YOUR_SESSION_ID
   ```
3. The app will generate the AI report and display it!

---

## 🔍 **Finding Your Session ID**

**Option 1 - Browser Console:**
- Press F12 in browser
- Go to Console tab
- Look for session_id in the logs

**Option 2 - Backend Logs:**
```bash
tail -20 /var/log/supervisor/backend.out.log | grep "session:"
```

**Option 3 - MongoDB:**
```bash
mongosh burnout_checker
db.sessions.find().sort({created_at: -1}).limit(1)
```

---

## 📋 **Quick Reference**

### Services Status:
```bash
sudo supervisorctl status
```

### Backend Logs (errors):
```bash
tail -f /var/log/supervisor/backend.err.log
```

### Backend Logs (info):
```bash
tail -f /var/log/supervisor/backend.out.log
```

### Frontend Logs:
```bash
tail -f /var/log/supervisor/frontend.out.log
```

### Restart Services:
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

---

## ✅ **What's Working**

- ✅ Registration (fixed!)
- ✅ Email OTP generation (visible in logs)
- ✅ Mobile OTP (mock - any code works)
- ✅ Assessment submission
- ✅ Score calculation
- ✅ Payment flow (Gumroad redirect)
- ✅ AI report generation (Emergent LLM Key)
- ✅ Report display

## ⚠️ **What's NOT Working (Expected)**

- ❌ Actual email sending (needs Resend API key)
- ❌ Actual SMS sending (mock mode by design)

---

## 🎉 **Try It Now!**

1. Open Terminal: `tail -f /var/log/supervisor/backend.out.log | grep "🔑 OTP"`
2. Open Browser: http://localhost:3000
3. Register and look for OTP codes in terminal!

---

For complete documentation, see:
- `/app/TESTING_GUIDE.md` - Full testing guide
- `/app/PRODUCTION_GUIDE.md` - Production deployment guide
