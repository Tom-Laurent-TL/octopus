# API Key Security Features

## Overview

This document describes the advanced security features available in the Octopus API key management system.

## 🛡️ Security Features

### 1. Rate Limiting

**Protection against brute force attacks and abuse.**

#### Global Rate Limits
- **Default**: 100 requests/minute per IP address
- **Authentication**: 10 requests/minute per IP address
- **Key Creation**: 5 requests/minute per IP address

#### How it Works
- Rate limits are applied per IP address
- Exceeding the limit returns HTTP 429 (Too Many Requests)
- Limits reset after the time window expires

#### Configuration
Rate limits are configured in `app/main.py` and `app/core/security.py` using `slowapi`.

---

### 2. Audit Logging

**Complete audit trail for all API key operations.**

#### What's Logged
- **Key Operations**: create, update, delete, deactivate, rotate
- **Authentication**: successful and failed attempts
- **Details**: Who performed the action, from which IP, when, and what changed

#### Database Schema
```sql
api_key_audit_logs
├── id (Primary Key)
├── api_key_id (Foreign Key - which key was affected)
├── action (create, update, delete, deactivate, rotate, auth_success, auth_failed)
├── performed_by_key_id (Foreign Key - which key performed the action)
├── performed_by_ip (IP address of the request)
├── details (JSON with additional context)
└── timestamp (When the action occurred)
```

#### Accessing Audit Logs

**Via API:**
```bash
# Get all audit logs
curl -H "Octopus-API-Key: your-admin-key" \
  http://localhost:8000/api/v1/api-keys/audit-logs/

# Filter by key ID
curl -H "Octopus-API-Key: your-admin-key" \
  "http://localhost:8000/api/v1/api-keys/audit-logs/?api_key_id=1"

# Filter by action
curl -H "Octopus-API-Key: your-admin-key" \
  "http://localhost:8000/api/v1/api-keys/audit-logs/?action=delete"
```

**Via Database:**
```python
from app.features.api_keys.service import AuditService

# Get logs for a specific key
logs = AuditService.get_audit_logs(db, api_key_id=1)

# Get logs for specific action
delete_logs = AuditService.get_audit_logs(db, action="delete")
```

---

### 3. Monitoring & Alerting

**Structured logging for failed authentication attempts.**

#### What's Monitored
- **Failed Authentication**: Invalid, inactive, or expired keys
- **IP Restrictions**: Attempts from non-whitelisted IPs
- **Successful Authentication**: Track usage patterns

#### Log Format
```json
{
  "level": "WARNING",
  "message": "Failed authentication attempt",
  "extra": {
    "ip": "192.168.1.100",
    "key_prefix": "octopus_abc...",
    "reason": "invalid_or_inactive"
  }
}
```

#### Log Levels
- `INFO`: Successful authentication
- `WARNING`: Failed authentication attempts
- `ERROR`: System errors

#### Integration
Logs are compatible with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **CloudWatch**
- **Datadog**

---

### 4. IP Whitelisting

**Restrict API keys to specific IP addresses.**

#### Use Cases
- Production systems with static IPs
- Internal tools
- Partner integrations
- High-security environments

#### How to Use

**Create key with IP restrictions:**
```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Octopus-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Server",
    "scopes": "read,write",
    "allowed_ips": "192.168.1.10,192.168.1.11,10.0.0.5"
  }'
```

**Update existing key:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/api-keys/1" \
  -H "Octopus-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "allowed_ips": "192.168.1.10"
  }'
```

#### Format
- Comma-separated list of IP addresses
- Supports IPv4 and IPv6
- No CIDR notation (yet)

#### Behavior
- If `allowed_ips` is null/empty → No IP restrictions
- If `allowed_ips` is set → Only listed IPs can use the key
- Non-whitelisted IPs receive HTTP 403

---

### 5. Key Expiration Management

**Automatic handling of expired keys and notifications.**

#### Expiration Policies

**Set expiration on creation:**
```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Octopus-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Temporary Access",
    "scopes": "read",
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

**Update expiration:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/api-keys/1" \
  -H "Octopus-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "expires_at": "2026-01-31T23:59:59Z"
  }'
```

#### Get Expiring Keys

```bash
# Get keys expiring in next 7 days (default)
curl -H "Octopus-API-Key: your-admin-key" \
  http://localhost:8000/api/v1/api-keys/expiring/

# Get keys expiring in next 30 days
curl -H "Octopus-API-Key: your-admin-key" \
  "http://localhost:8000/api/v1/api-keys/expiring/?days=30"
```

#### Automatic Cleanup

```bash
# Deactivate all expired keys
curl -X POST "http://localhost:8000/api/v1/api-keys/cleanup-expired/" \
  -H "Octopus-API-Key: your-admin-key"
```

**Returns:**
```json
{
  "deactivated_count": 3,
  "message": "Deactivated 3 expired key(s)"
}
```

#### Automation
Set up a cron job or scheduled task:

```bash
# Daily cleanup at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/v1/api-keys/cleanup-expired/ \
  -H "Octopus-API-Key: $MASTER_KEY"
```

---

### 6. Key Rotation

**Best practice for maintaining security.**

#### Why Rotate Keys?
- **Security Best Practice**: Limit exposure window
- **Compliance**: Some regulations require regular rotation
- **Breach Response**: Quick recovery if key is compromised

#### How it Works
1. Create new key with same properties as old key
2. Deactivate old key
3. Return new key value (only shown once)
4. Log rotation in audit trail

#### Rotate via API

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/1/rotate" \
  -H "Octopus-API-Key: your-admin-key"
```

**Response:**
```json
{
  "id": 5,
  "key": "octopus_new_key_value_here",
  "name": "Production Key (rotated)",
  "scopes": "read,write",
  "is_active": true,
  "created_at": "2025-11-02T10:00:00Z",
  ...
}
```

#### Rotation Workflow

**Zero-Downtime Rotation:**

1. **Rotate key** - Creates new key, old key still works
2. **Update applications** - Deploy new key to all services
3. **Verify** - Ensure all services use new key
4. **Old key auto-deactivated** - Rotation automatically deactivates old key

**Emergency Rotation:**

If a key is compromised:
```bash
# Immediately deactivate
curl -X POST "http://localhost:8000/api/v1/api-keys/1/deactivate" \
  -H "Octopus-API-Key: your-admin-key"

# Create replacement
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Octopus-API-Key: your-admin-key" \
  -d '{"name": "Replacement Key", "scopes": "read,write"}'
```

#### Automated Rotation

**Option 1: Scheduled Task**
```python
# rotate_keys.py
import requests
import schedule
import time

def rotate_production_key():
    response = requests.post(
        "http://api.example.com/api/v1/api-keys/1/rotate",
        headers={"Octopus-API-Key": os.environ["ADMIN_KEY"]}
    )
    new_key = response.json()["key"]
    # Store new key securely
    update_secret_manager(new_key)

# Rotate every 90 days
schedule.every(90).days.do(rotate_production_key)

while True:
    schedule.run_pending()
    time.sleep(86400)  # Check daily
```

**Option 2: API Script**
```bash
#!/bin/bash
# rotate-keys.sh

# Rotate all production keys
for KEY_ID in 1 2 3; do
  echo "Rotating key $KEY_ID..."
  curl -X POST "http://localhost:8000/api/v1/api-keys/$KEY_ID/rotate" \
    -H "Octopus-API-Key: $MASTER_KEY"
done
```

---

## 🔒 Best Practices

### 1. Rate Limiting
- ✅ Keep default limits for production
- ✅ Monitor 429 errors to detect attacks
- ✅ Adjust limits based on legitimate usage patterns

### 2. Audit Logging
- ✅ Regularly review audit logs
- ✅ Set up alerts for suspicious patterns
- ✅ Retain logs per compliance requirements
- ✅ Export logs to SIEM for analysis

### 3. Monitoring
- ✅ Set up alerts for failed auth attempts
- ✅ Monitor authentication patterns
- ✅ Track key usage by IP and time
- ✅ Alert on unusual access patterns

### 4. IP Whitelisting
- ✅ Use for production systems with static IPs
- ✅ Keep whitelist updated when infrastructure changes
- ✅ Don't use for development/testing keys
- ✅ Document which IPs are authorized

### 5. Expiration
- ✅ Set expiration for temporary access
- ✅ Use longer expiration for production keys (90-365 days)
- ✅ Run cleanup regularly (daily recommended)
- ✅ Alert team when keys are expiring

### 6. Rotation
- ✅ Rotate keys every 90 days minimum
- ✅ Rotate immediately if compromised
- ✅ Automate rotation for production keys
- ✅ Test rotation process before emergency

---

## 📊 Security Metrics

### Track These KPIs
1. **Failed Authentication Rate**: < 1% of total requests
2. **Key Rotation Frequency**: Every 90 days
3. **Expired Keys**: 0 active expired keys
4. **IP Violations**: Monitor for unauthorized access attempts
5. **Audit Log Retention**: Meet compliance requirements

### Dashboard Queries

**Failed authentications in last 24h:**
```sql
SELECT COUNT(*) 
FROM api_key_audit_logs 
WHERE action = 'auth_failed' 
  AND timestamp > NOW() - INTERVAL '24 hours';
```

**Most used keys:**
```sql
SELECT api_key_id, COUNT(*) as usage_count
FROM api_key_audit_logs 
WHERE action = 'auth_success'
  AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY api_key_id
ORDER BY usage_count DESC;
```

**Keys not rotated in 90 days:**
```sql
SELECT id, name, created_at
FROM api_keys
WHERE is_active = true
  AND created_at < NOW() - INTERVAL '90 days';
```

---

## 🚨 Incident Response

### Compromised Key
1. **Immediate**: Deactivate the key
2. **Investigate**: Check audit logs for unauthorized actions
3. **Assess**: Determine scope of access
4. **Remediate**: Rotate all keys, review logs
5. **Document**: Record incident and response

### Unusual Activity
1. **Review**: Audit logs and authentication patterns
2. **Identify**: Source IP and affected keys
3. **Block**: Add IP restrictions if needed
4. **Alert**: Notify security team
5. **Monitor**: Watch for continued attempts

---

## 🔍 Security Checklist

### Initial Setup
- [ ] Configure rate limits
- [ ] Set up audit log retention
- [ ] Configure logging aggregation
- [ ] Set up monitoring alerts
- [ ] Document key owners
- [ ] Create rotation schedule

### Ongoing
- [ ] Review audit logs weekly
- [ ] Rotate production keys quarterly
- [ ] Run cleanup script daily
- [ ] Monitor failed auth attempts
- [ ] Update IP whitelists as needed
- [ ] Review expiring keys monthly

### Incident Response
- [ ] Documented process for compromised keys
- [ ] Contact list for security team
- [ ] Backup admin key in secure location
- [ ] Tested recovery procedures
- [ ] Incident logging system

---

## 📚 Additional Resources

- [API Key Management Guide](API_KEY_MANAGEMENT.md)
- [Best Practices](BEST_PRACTICES.md)
- [Project Structure](PROJECT_STRUCTURE.md)

