# Redis Client Failover for Redis Enterprise Active / Active Clusters

### Example C# and Python apps for a Redis Enterprise Active / Active Cluster

## ✅ Assumptions:
-Redis Enterprise HA with Active / Active is deployed.

## 🛡 Features:

✅ Circuit breaker handles repeated failures and prevents flooding failing servers.

✅ Failover logic switches endpoints on failure.

✅ Simple retry logic built on top of Polly.

✅ Easily extensible with exponential backoff, logging, or metrics.
