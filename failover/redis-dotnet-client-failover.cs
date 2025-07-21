using StackExchange.Redis;
using Polly;
using Polly.CircuitBreaker;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public class RedisFailoverClient
{
    private readonly List<string> _endpoints;
    private int _currentEndpointIndex = 0;
    private ConnectionMultiplexer _redis;
    private IDatabase _db;

    private readonly AsyncCircuitBreakerPolicy _circuitBreaker;

    public RedisFailoverClient(List<string> endpoints)
    {
        if (endpoints == null || endpoints.Count == 0)
            throw new ArgumentException("At least one Redis endpoint must be provided.");

        _endpoints = endpoints;

        // Define the circuit breaker: open after 3 consecutive failures, stays open for 10 seconds
        _circuitBreaker = Policy
            .Handle<RedisConnectionException>()
            .CircuitBreakerAsync(3, TimeSpan.FromSeconds(10),
                onBreak: (ex, breakDelay) =>
                {
                    Console.WriteLine($"Circuit opened: {ex.Message}, retrying after {breakDelay.TotalSeconds}s...");
                },
                onReset: () => Console.WriteLine("Circuit closed."),
                onHalfOpen: () => Console.WriteLine("Circuit half-open: testing connection..."));

        ConnectToRedis().Wait();
    }

    private async Task ConnectToRedis()
    {
        for (int i = 0; i < _endpoints.Count; i++)
        {
            try
            {
                string endpoint = _endpoints[_currentEndpointIndex];
                Console.WriteLine($"Attempting connection to Redis at {endpoint}");

                _redis = await ConnectionMultiplexer.ConnectAsync(endpoint);
                _db = _redis.GetDatabase();

                Console.WriteLine($"Connected to Redis at {endpoint}");
                return;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Connection failed at {_endpoints[_currentEndpointIndex]}: {ex.Message}");
                _currentEndpointIndex = (_currentEndpointIndex + 1) % _endpoints.Count;
            }
        }

        throw new Exception("All Redis endpoints failed to connect.");
    }

    public async Task<string> GetValueAsync(string key)
    {
        return await _circuitBreaker.ExecuteAsync(async () =>
        {
            try
            {
                return await _db.StringGetAsync(key);
            }
            catch (RedisConnectionException)
            {
                await HandleFailover();
                throw;
            }
        });
    }

    public async Task SetValueAsync(string key, string value)
    {
        await _circuitBreaker.ExecuteAsync(async () =>
        {
            try
            {
                await _db.StringSetAsync(key, value);
            }
            catch (RedisConnectionException)
            {
                await HandleFailover();
                throw;
            }
        });
    }

    private async Task HandleFailover()
    {
        Console.WriteLine("Handling failover...");
        _currentEndpointIndex = (_currentEndpointIndex + 1) % _endpoints.Count;
        await ConnectToRedis();
    }
}

