# REFERENCE CARD - Battery Indicator Implementation

## 📌 Quick Reference

### Component Usage

```vue
<!-- Tarjeta de Dispositivo (Pequeño) -->
<BatteryIndicator 
  :level="batteryLevel" 
  size="small" 
/>

<!-- Dashboard (Mediano) -->
<BatteryIndicator 
  :level="batteryLevel" 
  size="medium" 
  :show-text="true"
/>

<!-- Uso Personalizado (Grande) -->
<BatteryIndicator 
  :level="85" 
  size="large" 
  :show-text="true"
/>
```

### Props API

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `level` | Number | 100 | Battery level 0-100 |
| `size` | String | 'small' | 'small', 'medium', 'large' |
| `showText` | Boolean | true | Show percentage text |

### Color Classes

```scss
.battery-full   { color: #4ade80 }   // > 60%
.battery-medium { color: #eab308 }   // 31-60%
.battery-low    { color: #f97316 }   // 11-30%
.battery-critical { color: #ef4444 } // ≤ 10%
```

### Data Structure

```javascript
// Device object with battery
{
  id: 1,
  name: "Dispositivo Embalse",
  battery: 85,      // 0-100
  bateria: 85,      // Compatibility
  status: "connected",
  sensors: { ph: 7.2, temperature: 22.5, conductivity: 650 }
}

// Dashboard response with battery
{
  ph: {...},
  temperature: {...},
  conductivity: {...},
  metadata: {...},
  battery: 85       // NEW FIELD
}
```

---

## 🔧 Configuration

### Backend (FastAPI)

**File:** `backend_fastapi/main.py`

```python
# DashboardResponse Model (line 289)
class DashboardResponse(BaseModel):
    battery: int = Field(default=100, ge=0, le=100)

# Endpoint Response (line 562)
@app.get("/api/dashboard")
def get_dashboard_data():
    # ...
    return DashboardResponse(
        # ...
        battery=reading.get("bateria", 100)
    )
```

### Frontend (Vue.js)

**Files:**
- `src/components/BatteryIndicator.vue` (NEW)
- `src/components/DeviceCard.vue` (MODIFIED)
- `src/components/DeviceDashboard.vue` (MODIFIED)
- `src/services/ArduinoConfig.js` (MODIFIED)

---

## 🎨 Styling

### Light Mode
```css
.battery-full      { color: #4ade80 }   /* Green */
.battery-medium    { color: #eab308 }   /* Yellow */
.battery-low       { color: #f97316 }   /* Orange */
.battery-critical  { color: #ef4444 }   /* Red */
```

### Dark Mode
```css
html[data-theme='dark'] .battery-full       { color: #86efac }
html[data-theme='dark'] .battery-medium     { color: #facc15 }
html[data-theme='dark'] .battery-low        { color: #fb923c }
html[data-theme='dark'] .battery-critical   { color: #fca5a5 }
```

---

## 📡 API Endpoints

### POST: Send Sensor Reading with Battery

```http
POST /api/sensors/readings
Content-Type: application/json

{
  "ph": 7.2,
  "temperature": 22.5,
  "conductivity": 650,
  "bateria": 85
}

HTTP/1.1 201 Created
{
  "status": "success",
  "message": "Lectura guardada",
  "id": "66...",
  "data": {...}
}
```

### GET: Dashboard Data with Battery

```http
GET /api/dashboard

HTTP/1.1 200 OK
{
  "ph": {
    "value": 7.2,
    "min": 6.0,
    "max": 8.5,
    "safeMax": 8.0,
    "lastUpdated": "2026-05-18T10:30:45Z",
    "status": "stable"
  },
  "temperature": {...},
  "conductivity": {...},
  "metadata": {
    "systemStatus": "operational",
    "arduinoConnected": true,
    "lastSync": "2026-05-18T10:30:45Z",
    "uptime": 3600,
    "activeSensors": 3
  },
  "battery": 85
}
```

---

## 🔄 Update Cycle

```
┌─ updateSensorData() [every 2s]
│   └─ fetchDashboardData()
│       └─ GET /api/dashboard
│           └─ { battery: 85, ... }
│               └─ loadDashboardFromApi()
│                   └─ devices.value[0].battery = 85
│                       └─ Vue Reactivity
│                           └─ BatteryIndicator renders
└─ [Repeat every 2000ms]
```

---

## 🐛 Debugging

### Console Commands

```javascript
// Check battery level
console.log(selectedDevice.value.battery)  // Current level
console.log(batteryLevel.value)             // Computed value

// Simulate battery change
devices.value[0].battery = 50
// Watch: Color should change to yellow

// Check API response
fetch('/api/dashboard')
  .then(r => r.json())
  .then(d => console.log('Battery:', d.battery))

// Monitor updates
setInterval(() => {
  console.log('Battery:', devices.value[0].battery)
}, 1000)
```

### Browser DevTools

**Network Tab:**
- Monitor `/api/dashboard` requests
- Verify `battery` field is present
- Check response every 2 seconds

**Elements Tab:**
- Inspect `.battery-indicator` element
- Check applied CSS classes
- Verify color values

**Console:**
- Look for errors related to BatteryIndicator
- Verify component lifecycle
- Check data mutations

---

## 📊 Testing Checklist

### Visual Tests
- [ ] Green ✅ (> 60%)
- [ ] Yellow ⚠️ (31-60%)
- [ ] Orange 🟠 (11-30%)
- [ ] Red 🔴 (≤ 10%)

### Functional Tests
- [ ] Updates every 2 seconds
- [ ] Responds to API data
- [ ] Shows percentage
- [ ] Handles edge cases (0%, 100%)

### UI Tests
- [ ] Visible in device cards
- [ ] Visible in dashboard
- [ ] Responsive on mobile
- [ ] Works in dark mode

### Integration Tests
- [ ] Backend sends battery
- [ ] Frontend receives battery
- [ ] Data persists in MongoDB
- [ ] Real Arduino data works

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Component not visible | Check import, verify device has battery property |
| Wrong color | Verify battery level, check CSS |
| Not updating | Check updateInterval, verify API endpoint |
| Errors in console | Check component syntax, verify props |
| Dark mode issue | Clear cache, check theme variable |

---

## 📁 File Locations

```
src/
├── components/
│   ├── BatteryIndicator.vue      ✨ NEW
│   ├── DeviceCard.vue             📝 MODIFIED
│   ├── DeviceDashboard.vue        📝 MODIFIED
│   └── [other components]
│
└── services/
    └── ArduinoConfig.js           📝 MODIFIED

backend_fastapi/
└── main.py                        📝 MODIFIED

Documentation/
├── BATTERY_INDICATOR_IMPLEMENTATION.md
├── BATTERY_INDICATOR_QUICK_START.md
├── BATTERY_INDICATOR_ARCHITECTURE.md
├── BATTERY_INDICATOR_TESTING.md
└── BATTERY_INDICATOR_SUMMARY.md
```

---

## 🎓 Learning Resources

### File Size Reference
- BatteryIndicator.vue: ~130 lines
- Total modifications: ~200+ lines
- Total documentation: ~1000+ lines

### Import Statement
```vue
<script setup>
import BatteryIndicator from './BatteryIndicator.vue'
</script>
```

### Computed Usage
```vue
<script setup>
const batteryLevel = computed(() => {
  const level = selectedDevice.value?.battery || 100
  return Math.min(100, Math.max(0, level))
})
</script>
```

---

## 📞 Quick Links

| Document | Purpose |
|----------|---------|
| BATTERY_INDICATOR_IMPLEMENTATION.md | Technical details |
| BATTERY_INDICATOR_QUICK_START.md | User guide |
| BATTERY_INDICATOR_ARCHITECTURE.md | System design |
| BATTERY_INDICATOR_TESTING.md | Test procedures |

---

## ✅ Verification

To verify implementation:

1. **Frontend:**
   ```bash
   npm run dev
   # Check: Device cards show battery icon
   # Check: Dashboard shows battery in info section
   ```

2. **Backend:**
   ```bash
   curl http://localhost:8000/api/dashboard | jq '.battery'
   # Output: 85 (or similar number)
   ```

3. **Database:**
   ```javascript
   db.sensor_readings.findOne()
   // Check: Contains "bateria" field
   ```

---

**Version:** 1.0.0  
**Last Updated:** May 18, 2026  
**Status:** ✅ Production Ready
