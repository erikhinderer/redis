# Redis Data Distribution Best Practices

Redis Data Distribution Best Practices for Distributed Systems Archtectures

Redis Data Distribution Best Practices (TLDR)
Run two separate Redis deployments (or processes) under your installer: a read-only product-owned Knowledge-
Base (KB) instance that you ship preloaded (dump.rdb) and a separate runtime instance for short/long memory that
your product writes to and persists. Use application-level routing (two endpoints or a proxy) so KB updates never
overwrite runtime data. This keeps installs fast and upgrades safe.

