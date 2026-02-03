# 🧪 Testing Guide - Burnout Score Checker

## ⚠️ Important Note About Email OTP

Since the **Resend API key is not yet configured**, email OTPs will not actually be sent to your inbox. However, you can still test the complete flow using the workarounds below.

---

## 🔧 Option 1: Check OTP in Backend Logs (Recommended for Testing)

### Steps:

1. **Register on the frontend** (http://localhost:3000)
   - Fill in your name, email, and mobile
   - Click "Continue"

2. **When asked for Email OTP**, open a terminal and run:
   ```bash
   # This will show the generated OTP codes in the logs
   tail -f /var/log/supervisor/backend.out.log | grep "OTP"
   ```

3. **Copy the 6-digit OTP** from the logs and paste it in the form

4. **For Mobile OTP**: Since SMS is in mock mode, **any 6-digit number will work** (e.g., "123456")

---

## 🔧 Option 2: Direct Database Query

If you need to find an OTP for a specific session:

```bash
# Connect to MongoDB
mongosh burnout_checker

# Find OTP for a session (replace SESSION_ID with your actual session ID)
db.otps.find({session_id: "YOUR_SESSION_ID"}).sort({created_at: -1}).limit(1)
```

---

## 🔧 Option 3: Add Temporary Debug Logging

To see OTP codes directly in backend response (TESTING ONLY):

1. Edit `/app/backend/otp_service.py`
2. Add logging of OTP code
3. Restart backend: `sudo supervisorctl restart backend`

---

## ✅ Complete Test Flow

### 1. Registration
- Name: Your Name
- Email: youremail@test.com
- Mobile: +1234567890
- Click "Continue"

### 2. Email OTP Verification
- Check backend logs for the OTP code
- Or check MongoDB directly
- Enter the 6-digit code
- Click "Verify Email"

### 3. Mobile OTP Verification
- Enter ANY 6-digit code (e.g., "123456")
- Click "Verify Mobile"

### 4. Assessment
- Answer all 7 questions
- Click "Get My Burnout Score"

### 5. Preview Results
- You should see your score and level
- Preview insight will be displayed

### 6. Payment Gate
- Click "Unlock Full Burnout Recovery Report"
- **You'll be redirected to Gumroad**

### 7. Testing Payment Return (Without Actually Paying)
To test the payment return flow without paying:

```bash
# Manually trigger payment return by visiting this URL in your browser
# Replace SESSION_ID with your actual session ID
http://localhost:3000/payment-return?payment=success&session_id=YOUR_SESSION_ID
```

This will:
- Confirm payment
- Generate AI report
- Display full report on screen
- (Email delivery will fail without Resend API key, but report will still show)

---

## 🔍 Checking Session Status

To see your current session status:

```bash
# Replace SESSION_ID with your actual session ID
curl http://localhost:8001/api/session/YOUR_SESSION_ID | python3 -m json.tool
```

---

## 📋 Finding Your Session ID

After registration, the session ID is:
1. Stored in browser memory (check browser console)
2. Visible in backend logs
3. Passed in URLs during payment return

To find it in logs:
```bash
tail -n 50 /var/log/supervisor/backend.out.log | grep "session:"
```

---

## 🐛 Troubleshooting

### Registration Shows "Failed"
- Check backend is running: `sudo supervisorctl status backend`
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
- Check frontend console (F12 in browser)

### Can't Get OTP Code
- Check backend logs: `tail -f /var/log/supervisor/backend.out.log`
- Or use MongoDB: `mongosh burnout_checker` then `db.otps.find().sort({created_at: -1}).limit(5)`
- Remember: Email OTP needs Resend API key to actually send emails

### Mobile OTP Not Working
- ANY 6-digit number should work (it's in mock mode)
- Try: 123456 or 000000

### Payment Return Not Triggering
- Make sure you use the correct URL format: `?payment=success&session_id=...`
- Check that session_id matches your actual session

---

## 🔐 When Resend API Key is Added

Once you add the Resend API key to `/app/backend/.env`:

1. Email OTPs will be sent to real inboxes
2. Full reports will be emailed automatically
3. No need to check logs for OTP codes

**To add Resend API key:**
```bash
# Edit the .env file
nano /app/backend/.env

# Update this line:
RESEND_API_KEY=re_your_actual_api_key_here
FROM_EMAIL=noreply@yourdomain.com

# Restart backend
sudo supervisorctl restart backend
```

---

## 📊 Test Data Examples

### Valid Registration Data:
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com",
  "mobile": "+12025551234"
}
```

### Assessment Answers Example:
```json
{
  "1": 2,  // Often
  "2": 3,  // Always
  "3": 2,  // Low
  "4": 2,  // Often
  "5": 2,  // Not very satisfied
  "6": 2,  // Poor
  "7": 2   // Sometimes
}
```

This should give a High burnout score (~71/100).

---

## ✅ Success Indicators

**Registration successful if:**
- Backend logs show: `User registered: [email], session: [id]`
- Frontend shows "Verify Your Email" page
- No error messages displayed

**OTP verified successfully if:**
- Backend logs show: `OTP verified for session [id]`
- Frontend moves to next step
- Green success message appears

**Assessment submitted if:**
- Backend logs show: `Assessment submitted for session [id]`
- Preview page shows your score
- Score is between 0-100

**Report generated if:**
- Backend logs show: `Report generated successfully`
- Full report appears on screen
- Report contains your name and specific insights

---

**Need Help?** Check `/app/PRODUCTION_GUIDE.md` for complete documentation.
