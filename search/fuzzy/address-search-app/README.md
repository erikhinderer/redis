# Redis Fuzzy Search - Node.js Property Address Example

### Example Node.js app using Redis Enterprise Fuzzy Search to determine a property address by querying fuzzy matches from address records.

## ✅ Assumptions:
-Redis Enterprise with Redis Search (RediSearch) is enabled.

-Addresses are stored with searchable fields like address, city, state, etc.

-Fuzzy search works via FT.SEARCH using the ~ operator.

## 📁 Project Structure:
```
address-search-app/
├── index.js
├── package.json
└── .env
```

## 📦 Dependencies:
```
npm init -y
npm install redis dotenv
```

## ⚙️ .env File Example:
```
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=yourpassword
REDIS_INDEX=address_idx
```

## 📝 index.js Example Code:
```
require('dotenv').config();
const { createClient } = require('redis');

const redis = createClient({
  socket: {
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT
  },
  password: process.env.REDIS_PASSWORD
});

async function searchAddress(query) {
  try {
    await redis.connect();

    const index = process.env.REDIS_INDEX;
    // Fuzzy search on 'address' field using the '~' operator
    const searchQuery = `@address:${query}~`;

    const result = await redis.ft.search(index, searchQuery, {
      LIMIT: {
        from: 0,
        size: 5
      }
    });

    if (result.total === 0) {
      console.log('No matching addresses found.');
    } else {
      console.log(`Found ${result.total} matching addresses:\n`);
      result.documents.forEach(doc => {
        console.log(`ID: ${doc.id}`);
        console.log(`Address: ${doc.value.address}`);
        console.log(`City: ${doc.value.city}`);
        console.log(`State: ${doc.value.state}`);
        console.log('---');
      });
    }

  } catch (err) {
    console.error('Error:', err);
  } finally {
    redis.quit();
  }
}

// Example usage:
const userInput = process.argv[2]; // Address input from command line
if (!userInput) {
  console.log('Usage: node index.js "<partial or misspelled address>"');
  process.exit(1);
}

searchAddress(userInput);
```

## 📢 Create Index Example in Redis Enterprise:
```
FT.CREATE address_idx ON HASH PREFIX 1 "addr:" SCHEMA address TEXT city TEXT state TEXT
```

## 📢 Create Records Example in Redis Enterprise:
```
HSET addr:1 address "123 Main Street" city "Springfield" state "IL"
HSET addr:2 address "124 Mane Stret" city "Springfield" state "IL"
```

## 🚀 Usage Example:
```
node index.js "Main Stret"
```
*Fuzzy search will find close matches like "Main Street" even with minor typos.

## 🔧 Notes:
-Adjust LIMIT in the search options based on expected results.

-You can enhance this with more advanced scoring, filtering by city/state, or REST API using Express.

