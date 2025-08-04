# KidQuest Finance Module - Test Cases Documentation

## Test Suite Overview
**Module**: Finance Tracker (KidQuest)  
**Test File**: `test_finance.py`  
**APIs Tested**:  
- `/api/finance/transaction`  
- `/api/finance/transactions/<user_id>`  
- `/api/finance/goal`  
- `/api/finance/goals/<user_id>`  
**Authentication**: JWT Bearer Token Required  

---

## 1. Transaction Endpoint Test Cases

### Test Case 1.1: Get Transactions - Empty List for New User  
**API**: `/api/finance/transactions/<user_id>`  
**Inputs**:
- Method: GET  
- URL: `/api/finance/transactions/{valid_user_id}`  
- Headers: `Authorization: Bearer {jwt_token}`  

**Expected Output**:
```json
{
  "success": true,
  "transactions": []
}
```  
**Result**: Success ✅  

---

### Test Case 1.2: Add and Retrieve a Transaction  
**API**: `/api/finance/transaction`  
**Inputs**:
- Method: POST  
- Headers: `Authorization: Bearer {jwt_token}`  
- Body:
```json
{
  "user_id": {valid_user_id},
  "amount": 20.0,
  "type": "income",
  "description": "Allowance"
}
```  

**Expected Output (POST)**:
```json
{
  "success": true,
  "transaction": {
    "amount": 20.0,
    ...
  }
}
```

**Expected Output (GET)**:
```json
{
  "success": true,
  "transactions": [
    {
      "description": "Allowance",
      ...
    }
  ]
}
```  

**Result**: Success ✅  

---

### Test Case 1.3: Unauthorized Transaction Add Attempt  
**API**: `/api/finance/transaction`  
**Inputs**:
- Method: POST  
- Headers: `Authorization: Bearer {jwt_token}`  
- Body:
```json
{
  "user_id": 999,
  "amount": 50,
  "type": "expense",
  "description": "Fake try"
}
```  

**Expected Output**:
```json
{
  "error": "Unauthorized"
}
```  
**Status**: 403  
**Result**: Success ✅  

---

## 2. Savings Goals Endpoint Test Cases

### Test Case 2.1: Get Saving Goals - Empty List for New User  
**API**: `/api/finance/goals/<user_id>`  
**Inputs**:
- Method: GET  
- URL: `/api/finance/goals/{valid_user_id}`  
- Headers: `Authorization: Bearer {jwt_token}`  

**Expected Output**:
```json
{
  "success": true,
  "goals": []
}
```  
**Result**: Success ✅  

---

### Test Case 2.2: Add and Retrieve a Goal  
**API**: `/api/finance/goal`  
**Inputs**:
- Method: POST  
- Headers: `Authorization: Bearer {jwt_token}`  
- Body:
```json
{
  "user_id": {valid_user_id},
  "label": "Buy a bike",
  "target_amount": 100.0
}
```  

**Expected Output (POST)**:
```json
{
  "success": true,
  "goal": {
    "label": "Buy a bike",
    "current_amount": 0,
    ...
  }
}
```

**Expected Output (GET)**:
```json
{
  "success": true,
  "goals": [
    {
      "target_amount": 100.0,
      ...
    }
  ]
}
```  

**Result**: Success ✅  

---

### Test Case 2.3: Unauthorized Goal Add Attempt  
**API**: `/api/finance/goal`  
**Inputs**:
- Method: POST  
- Headers: `Authorization: Bearer {jwt_token}`  
- Body:
```json
{
  "user_id": 999,
  "label": "Illegal save",
  "target_amount": 9999.0
}
```  

**Expected Output**:
```json
{
  "error": "Unauthorized"
}
```  
**Status**: 403  
**Result**: Success ✅