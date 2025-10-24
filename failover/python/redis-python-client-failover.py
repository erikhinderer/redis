"""
Failover-ready Redis client for Redis Enterprise Active-Active (CRDB).

Requires:
  pip install redis tenacity

If you use TLS, add: ssl=True, ssl_cert_reqs=None (or set proper CA)
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import random
import time

import redis
from tenacity import (
    retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type, before_sleep_log
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("redis-failover")

@dataclass
class Endpoint:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False
    # add other redis.Connection kwargs as needed (socket_timeout, ssl_cert_reqs, etc.)

class FailoverRedis:
    """
    A thin wrapper that:
      - Keeps a rotating list of CRDB member endpoints
      - On connection/command errors, retries with exponential backoff + jitter
      - If a node stays unhealthy, fails over to the next endpoint
    """

    def __init__(self, endpoints: List[Endpoint], decode_responses: bool = True, socket_timeout: float = 2.5):
        if not endpoints:
            raise ValueError("At least one endpoint is required")
        # Shuffle once so not all clients stampede the same first endpoint
        self.endpoints: List[Endpoint] = endpoints[:]
        random.shuffle(self.endpoints)
        self.decode_responses = decode_responses
        self.socket_timeout = socket_timeout

        self._client: Optional[redis.Redis] = None
        self._active_idx = 0

    def _make_client(self, ep: Endpoint) -> redis.Redis:
        return redis.Redis(
            host=ep.host,
            port=ep.port,
            username=ep.username,
            password=ep.password,
            ssl=ep.ssl,
            decode_responses=self.decode_responses,
            socket_timeout=self.socket_timeout,
        )

    def _connect(self) -> redis.Redis:
        # Try current endpoint; on failure, try the rest
        last_err = None
        for i in range(len(self.endpoints)):
            idx = (self._active_idx + i) % len(self.endpoints)
            ep = self.endpoints[idx]
            client = self._make_client(ep)
            try:
                # lightweight health check
                client.ping()
                self._client = client
                self._active_idx = idx
                logger.info(f"Connected to Redis endpoint {ep.host}:{ep.port} (idx={idx})")
                return self._client
            except Exception as e:
                last_err = e
                logger.warning(f"Connect failed to {ep.host}:{ep.port}: {e!r}")
                continue
        # If none worked, raise the last error
        raise last_err if last_err else ConnectionError("No endpoints reachable")

    # Polly-like: retry with exponential backoff and jitter on transient errors
    def _retry_policy(self):
        return retry(
            reraise=True,
            stop=stop_after_attempt(5),  # original try + 4 retries = 5 total attempts
            wait=wait_random_exponential(multiplier=0.2, max=2.0),
            retry=retry_if_exception_type((redis.exceptions.TimeoutError,
                                           redis.exceptions.ConnectionError,
                                           OSError)),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )

    def _ensure_client(self) -> redis.Redis:
        if self._client is None:
            return self._connect()
        return self._client

    @_retry_policy(None)
    def execute(self, func, *args, **kwargs):
        """
        Execute a Redis call with retries. If the active endpoint is down,
        fail over to the next endpoint and retry.
        """
        client = self._ensure_client()
        try:
            return func(client, *args, **kwargs)
        except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError, OSError) as e:
            logger.warning(f"Command error from current endpoint: {e!r}. Attempting failover.")
            # mark current endpoint as bad and try the next one next time
            self._client = None
            self._active_idx = (self._active_idx + 1) % len(self.endpoints)
            # raise to trigger tenacity retry
            raise

    # Convenience wrappers

    def get(self, key: str):
        return self.execute(lambda c: c.get(key))

    def set(self, key: str, value, ex: Optional[int] = None, px: Optional[int] = None, nx: bool = False):
        return self.execute(lambda c: c.set(key, value, ex=ex, px=px, nx=nx))

    def incr(self, key: str):
        return self.execute(lambda c: c.incr(key))

    def json_set(self, key: str, path: str, obj):
        # If you’re using RedisJSON via redis.commands.json
        return self.execute(lambda c: c.json().set(key, path, obj))

    def close(self):
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
        self._client = None

# ---------- Example usage ----------

if __name__ == "__main__":
    # Replace with your CRDB member endpoints (often behind per-cluster endpoints or proxies)
    # Example: two members in different regions
    endpoints = [
        Endpoint(host="use1-crdb.myredis.example.com", port=6380, username="default", password="***", ssl=True),
        Endpoint(host="euw1-crdb.myredis.example.com", port=6380, username="default", password="***", ssl=True),
        # You can add more members if your Active-Active database spans more clusters
    ]

    r = FailoverRedis(endpoints)

    # Basic write + read with automatic failover/retry if a member blips
    key = "demo:aa:counter"
    for _ in range(5):
        val = r.incr(key)
        logger.info(f"{key} = {val}")
        time.sleep(0.1)

    got = r.get(key)
    logger.info(f"Final read: {key} = {got}")

    r.close()

