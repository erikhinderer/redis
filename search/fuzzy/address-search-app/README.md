# Redis Fuzzy Search - Node.js Property Address Example

## Example Node.js app using Redis Enterprise Fuzzy Search to determine a property address by querying fuzzy matches from address records.

## ✅ Assumptions:
-Redis Enterprise with Redis Search (RediSearch) is enabled.

-Addresses are stored with searchable fields like address, city, state, etc.

-Fuzzy search works via FT.SEARCH using the ~ operator.

   ## 📁 Project Structure:
   address-search-app/
├── index.js
├── package.json
└── .env

