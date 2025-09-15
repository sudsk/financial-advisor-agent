# Financial Advisor Agent

## 🎯 Bank of Anthos API Endpoints Revealed

Based on the frontend code, here are the exact API endpoints our AI agents can integrate with:

## 📋 Complete API Reference

|Service|Endpoint|Purpose|Our Integration|
|-------|--------|-------|---------------|
|UserService|POST /loginUser| authentication|✅ User verification|
|UserService|GET /usersUser| profiles|✅ Budget Agent needs this|
|BalanceReader|GET /balancesAccount balances|✅ Investment Agent needs this|
|TransactionHistory|GET /transactionsTransaction| history|✅ Budget + Security |
|AgentsContacts|GET /contactsUser| contacts|✅ Nice-to-have for agents|
|LedgerWriter|POST /transactions|Create transactions|❌ Read-only for our demo|
