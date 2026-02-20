# StarCy Backend Server

Python backend server that sends push notifications to keep Dynamic Island Live Activity active 24/7.

## Features

- ✅ Keeps Live Activity alive with periodic push notifications
- ✅ Rotates Dynamic Island content every 20 seconds
- ✅ Supports multiple devices simultaneously
- ✅ Simple REST API for device registration
- ✅ APNs (Apple Push Notification service) integration

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get APNs Credentials

1. Go to [Apple Developer Portal](https://developer.apple.com/account/resources/authkeys/list)
2. Create a new APNs Auth Key
3. Download the `.p8` file
4. Note your Key ID and Team ID

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
APNS_KEY_ID=ABC123XYZ
APNS_TEAM_ID=TEAM123456
APNS_BUNDLE_ID=com.yourcompany.starcy
APNS_KEY_PATH=./AuthKey_ABC123XYZ.p8
ENVIRONMENT=development
```

### 4. Run Server

```bash
python main.py
```

Server will start on `http://0.0.0.0:8000`

## API Endpoints

### Health Check
```bash
GET /
```

### Register Device
```bash
POST /register
{
  "device_token": "device_push_token_here",
  "activity_id": "live_activity_id_here",
  "user_id": "optional_user_id"
}
```

### Unregister Device
```bash
POST /unregister?device_token=TOKEN
```

### Manual Update
```bash
POST /update
{
  "device_token": "device_push_token_here",
  "activity_id": "live_activity_id_here",
  "content_state": {
    "callStatus": "Ready",
    "transcript": "Hello!",
    ...
  }
}
```

### List Devices
```bash
GET /devices
```

## How It Works

1. **Device Registration**: iOS app registers device token and Live Activity ID
2. **Periodic Updates**: Server sends push notifications every 20 seconds
3. **Content Rotation**: Each update rotates between dashboard, news, weather, calendar
4. **Keep Alive**: Push notifications prevent iOS from terminating the Live Activity

## iOS Integration

Add this to your Swift code:

```swift
// Get device push token
func registerForPushNotifications() {
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
        guard granted else { return }
        DispatchQueue.main.async {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }
}

// Send token to backend
func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
    let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
    
    // Register with backend
    let url = URL(string: "http://YOUR_SERVER:8000/register")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body: [String: Any] = [
        "device_token": token,
        "activity_id": currentActivity?.id ?? "",
        "user_id": "user123"
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)
    
    URLSession.shared.dataTask(with: request).resume()
}
```

## Production Deployment

### Using Docker

```bash
docker build -t starcy-backend .
docker run -p 8000:8000 --env-file .env starcy-backend
```

### Using systemd (Linux)

Create `/etc/systemd/system/starcy-backend.service`:

```ini
[Unit]
Description=StarCy Backend Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/starcy-backend
Environment="PATH=/usr/local/bin"
ExecStart=/usr/local/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable starcy-backend
sudo systemctl start starcy-backend
```

## Troubleshooting

### Push notifications not working
- Check APNs credentials are correct
- Verify bundle ID matches your app
- Use sandbox URL for development builds
- Check device token is valid

### Content not rotating
- Check server logs for errors
- Verify scheduler is running
- Test manual update endpoint

### Live Activity stops after 30 minutes
- Ensure push notifications are being sent
- Check iOS device has internet connection
- Verify APNs token is not expired

## Notes

- APNs tokens expire after 1 hour - they're regenerated automatically
- Development builds use sandbox APNs URL
- Production builds use production APNs URL
- Maximum push notification rate: 1 per second per device
