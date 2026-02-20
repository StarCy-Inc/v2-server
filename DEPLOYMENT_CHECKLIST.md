# Deployment Checklist

## Pre-Deployment

### APNs Setup
- [ ] Created APNs Auth Key in Apple Developer Portal
- [ ] Downloaded `.p8` file (saved securely)
- [ ] Noted Key ID
- [ ] Noted Team ID
- [ ] Verified Bundle ID matches app

### Backend Setup
- [ ] Ran `./setup.sh` successfully
- [ ] Created `.env` file from `.env.example`
- [ ] Added APNs credentials to `.env`
- [ ] Copied `.p8` file to backend directory
- [ ] Tested locally with `python main.py`
- [ ] Ran `python test_backend.py` - all tests passed

### iOS App
- [ ] Updated `backendURL` in `BackendPushService.swift`
- [ ] Tested on real device (not simulator)
- [ ] Verified push permissions granted
- [ ] Confirmed device registration in backend logs
- [ ] Tested with app closed - Dynamic Island still rotates

## Local Development Deployment

### Requirements
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` configured
- [ ] `.p8` file in place

### Testing
- [ ] Server starts without errors
- [ ] Health check responds: `curl http://localhost:8000/`
- [ ] Device registration works
- [ ] Push notifications received on device
- [ ] Content rotates every 20 seconds
- [ ] Logs show successful updates

### Environment
```bash
ENVIRONMENT=development
APNS_URL=https://api.sandbox.push.apple.com
```

## Production Deployment

### Server Selection

#### Option 1: VPS (DigitalOcean, AWS, Linode)
- [ ] Created server (Ubuntu 22.04 recommended)
- [ ] Configured firewall (allow port 8000 or 443)
- [ ] Setup SSH access
- [ ] Installed Python 3.8+
- [ ] Installed pip and venv

#### Option 2: Cloud Platform (Railway, Render, Fly.io)
- [ ] Created account
- [ ] Connected GitHub repo
- [ ] Configured environment variables
- [ ] Set up custom domain (optional)

#### Option 3: Docker
- [ ] Built Docker image
- [ ] Tested container locally
- [ ] Pushed to registry (Docker Hub, etc.)
- [ ] Deployed to server

### File Transfer (VPS only)
```bash
# Upload backend files
scp -r backend/ user@server:/opt/starcy-backend

# Upload .p8 file separately (secure)
scp AuthKey_*.p8 user@server:/opt/starcy-backend/
```

### Environment Configuration
- [ ] Created production `.env` file
- [ ] Set `ENVIRONMENT=production`
- [ ] Updated `APNS_URL` to production
- [ ] Verified all credentials
- [ ] Set secure permissions: `chmod 600 .env`

### Dependencies Installation
```bash
cd /opt/starcy-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Systemd Service (VPS only)
- [ ] Created service file: `/etc/systemd/system/starcy-backend.service`
- [ ] Configured auto-start
- [ ] Enabled service: `sudo systemctl enable starcy-backend`
- [ ] Started service: `sudo systemctl start starcy-backend`
- [ ] Verified status: `sudo systemctl status starcy-backend`

### HTTPS Setup (Recommended)
- [ ] Installed nginx
- [ ] Configured reverse proxy
- [ ] Obtained SSL certificate (Let's Encrypt)
- [ ] Updated iOS app with HTTPS URL

### Monitoring
- [ ] Setup log rotation
- [ ] Configured monitoring (optional: Datadog, New Relic)
- [ ] Setup alerts for errors
- [ ] Created health check endpoint monitoring

## iOS App Production Build

### Configuration
- [ ] Updated `backendURL` to production URL
- [ ] Changed to production bundle ID (if different)
- [ ] Verified push notification entitlements
- [ ] Tested with TestFlight build

### Testing
- [ ] Installed TestFlight build
- [ ] Verified device registration
- [ ] Confirmed push notifications work
- [ ] Tested with app closed
- [ ] Verified 24/7 rotation

## Security Checklist

### Backend
- [ ] `.env` file not committed to git
- [ ] `.p8` file not committed to git
- [ ] Secure file permissions (600 for sensitive files)
- [ ] HTTPS enabled (production)
- [ ] API authentication added (optional)
- [ ] Rate limiting configured (optional)

### APNs
- [ ] Using correct environment (sandbox vs production)
- [ ] JWT tokens expire and regenerate
- [ ] Device tokens validated
- [ ] Invalid tokens removed

### Server
- [ ] Firewall configured
- [ ] SSH key authentication only
- [ ] Regular security updates
- [ ] Backup strategy in place

## Performance Checklist

### Backend
- [ ] Scheduler running correctly
- [ ] Updates sent every 20 seconds
- [ ] No memory leaks
- [ ] CPU usage acceptable (<20%)
- [ ] Network bandwidth reasonable

### APNs
- [ ] Push latency <3 seconds
- [ ] Success rate >95%
- [ ] No rate limiting errors
- [ ] Token refresh working

### iOS
- [ ] Live Activity updates smoothly
- [ ] No crashes or errors
- [ ] Battery impact minimal
- [ ] Content displays correctly

## Monitoring & Logging

### Backend Logs
- [ ] Logs rotating properly
- [ ] Error logs monitored
- [ ] Success rate tracked
- [ ] Device count tracked

### Key Metrics
- [ ] Active devices count
- [ ] Update success rate
- [ ] APNs latency
- [ ] Error rate
- [ ] Server uptime

### Alerts
- [ ] Server down alert
- [ ] High error rate alert
- [ ] APNs failure alert
- [ ] Disk space alert

## Post-Deployment

### Verification
- [ ] Health check responds: `curl https://your-domain.com/`
- [ ] Devices endpoint works: `curl https://your-domain.com/devices`
- [ ] iOS app connects successfully
- [ ] Push notifications delivered
- [ ] Content rotates correctly
- [ ] Logs show no errors

### Documentation
- [ ] Updated README with production URL
- [ ] Documented deployment process
- [ ] Created runbook for common issues
- [ ] Shared credentials securely (1Password, etc.)

### Backup
- [ ] Backend code backed up
- [ ] `.env` file backed up securely
- [ ] `.p8` file backed up securely
- [ ] Database backed up (if applicable)

## Rollback Plan

### If Issues Occur
1. [ ] Stop production server
2. [ ] Revert to previous version
3. [ ] Check logs for errors
4. [ ] Fix issues locally
5. [ ] Test thoroughly
6. [ ] Redeploy

### Emergency Contacts
- [ ] Server provider support
- [ ] Apple Developer support
- [ ] Team members

## Maintenance Schedule

### Daily
- [ ] Check server status
- [ ] Review error logs
- [ ] Monitor active devices

### Weekly
- [ ] Review performance metrics
- [ ] Check disk space
- [ ] Update dependencies (if needed)

### Monthly
- [ ] Security updates
- [ ] Backup verification
- [ ] Performance optimization
- [ ] Cost review

## Cost Tracking

### Monthly Costs
- [ ] Server hosting: $____
- [ ] Domain (if applicable): $____
- [ ] SSL certificate (if paid): $____
- [ ] Monitoring tools: $____
- [ ] Total: $____

### Optimization
- [ ] Right-sized server instance
- [ ] Efficient resource usage
- [ ] No unnecessary services

## Success Criteria

### Technical
- [x] Server uptime >99%
- [x] Push success rate >95%
- [x] Update latency <3s
- [x] No critical errors

### User Experience
- [x] Dynamic Island rotates 24/7
- [x] Content always fresh
- [x] No app crashes
- [x] Minimal battery impact

### Business
- [x] Cost within budget
- [x] Scalable to more users
- [x] Easy to maintain
- [x] Documented properly

## Sign-Off

- [ ] Technical lead approved
- [ ] Testing completed
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Team trained

**Deployment Date**: _______________

**Deployed By**: _______________

**Production URL**: _______________

**Notes**: _______________

---

## Quick Reference

### Start Server
```bash
sudo systemctl start starcy-backend
```

### Stop Server
```bash
sudo systemctl stop starcy-backend
```

### View Logs
```bash
sudo journalctl -u starcy-backend -f
```

### Check Status
```bash
sudo systemctl status starcy-backend
```

### Test Health
```bash
curl https://your-domain.com/
```

### List Devices
```bash
curl https://your-domain.com/devices
```

---

**Ready for production!** 🚀
