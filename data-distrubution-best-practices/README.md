# Redis Data Distribution Best Practices for Distributed Systems Archtectures

Redis Data Distribution Best Practices (TLDR)
Run two separate Redis deployments (or processes) under your installer: a read-only product-owned Knowledge-
Base (KB) instance that you ship preloaded (dump.rdb) and a separate runtime instance for short/long memory that
your product writes to and persists. Use application-level routing (two endpoints or a proxy) so KB updates never
overwrite runtime data. This keeps installs fast and upgrades safe.

Why (concise rationale)
An RDB snapshot is a point-in-time of the entire dataset the server holds — replacing dump.rdb or importing an
RDB into an existing server will overwrite (or otherwise affect) that serverʼs dataset. You cannot safely replace an
RDB on a running server without risking user/runtime keys.
Redis “logical DBs” are all part of the same in-memory dataset and are saved together in the same RDB file — they do
not give you separate persistence files per logical DB, so they do not solve the upgrade/overwrite risk. (Practically,
separate processes = separate persistence.)
Shipping a prebuilt dump.rdb is a good way to get fast first installs, but you must isolate the KB dataset from the
runtime dataset so future upgrades/restore actions do not wipe runtime data. Use an instance boundary for that
isolation.

Recommended pattern (detailed)
