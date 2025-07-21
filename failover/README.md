# Redis .NET Client Failover for Redis A/A Clusters

### Example C# app for a Redis Enterprise Active / Active Cluster

## ✅ Assumptions:
-Redis Enterprise HA with Active / Active is deployed.

## 📁 Project Structure:
```
address-search-app/
├── README.md
└── redis-dotnet-client-failover.cs
```

## 📦 Dependencies:
```
dotnet add package StackExchange.Redis
dotnet add package Polly
```
## ✅ Usage Example:
```
class Program
{
    static async Task Main(string[] args)
    {
        var redisEndpoints = new List<string>
        {
            "redis1.mycluster.local:6379",
            "redis2.mycluster.local:6379",
            "redis3.mycluster.local:6379"
        };

        var redisClient = new RedisFailoverClient(redisEndpoints);

        await redisClient.SetValueAsync("foo", "bar");
        string value = await redisClient.GetValueAsync("foo");

        Console.WriteLine($"Retrieved value: {value}");
    }
}
```
## 🛡 Features:

    ### Circuit breaker handles repeated failures and prevents flooding failing servers.

    ### Failover logic switches endpoints on failure.

    ### Simple retry logic built on top of Polly.

    ### Easily extensible with exponential backoff, logging, or metrics.
