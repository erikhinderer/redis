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
