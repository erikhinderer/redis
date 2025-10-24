
# Redis Python Client Failover for Redis Enterprise Active / Active Clusters

### Example Python app for a Redis Enterprise Active / Active Cluster

## ✅ Assumptions:
-Redis Enterprise HA with Active / Active is deployed.

## 📁 Project Structure:
```
address-search-app/
├── README.md
└── redis-python-client-failover.py
```

## 📦 Dependencies:
```
  pip install redis tenacity
```
## 🛡 Features:

✅ Failover logic switches endpoints on failure.

✅ Simple retry logic built on top of Tenacity

✅ TLS/CA: In production, validate certificates (ssl_cert_reqs="required" and provide CA certs).

✅ Auth: For Redis Enterprise, use the database username/password (often default plus a database password).

✅ Timeouts & attempts: Tune socket_timeout, retry stop_after_attempt, and backoff bounds to match your SLOs & member failover times.

✅ Circuit breaker: If you want stricter Polly-like circuit breaking, add pybreaker around execute() to temporarily short-circuit a repeatedly failing member before rotation; but for most Redis transient issues, exponential backoff + quick failover works well.

✅ Easily extensible with exponential backoff, logging, or metrics.
