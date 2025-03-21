# Dokumentation der Trivia API

## GET `/categories`

Fetches a dictionary of categories.

**Request Arguments:** None  
**Returns:**
```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

---

## GET `/questions?page=<int>`

Fetches paginated questions (10 per page), total questions, and categories.

**Request Arguments:**  
- `page` (optional) – integer, default is 1

**Returns:**
```json
{
  "success": true,
  "questions": [
    {
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "answer": "Maya Angelou",
      "difficulty": 2,
      "category": 4
    },
    ...
  ],
  "total_questions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

---

## GET `/categories/<int:category_id>/questions`

Fetches all questions for a specific category.

**Request Arguments:**  
- `category_id` – integer

**Returns:**
```json
{
  "success": true,
  "questions": [
    {
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
      "answer": "Apollo 13",
      "difficulty": 4,
      "category": 5
    }
  ],
  "total_questions": 3,
  "current_category": 5
}
```

---

## DELETE `/questions/<int:id>`

Deletes a question by ID.

**Request Arguments:**  
- `id` – integer

**Returns:**
```json
{
  "success": true,
  "deleted": 2
}
```

---

## POST `/questions`

Creates a new question.

**Request Body:**
```json
{
  "question": "What is my cat's name?",
  "answer": "Schubiger",
  "difficulty": 2,
  "category": 1
}
```

**Returns:**
```json
{
  "success": true,
  "created": 24,
  "total_questions": 20,
  "questions": [...]
}
```

---

## POST `/questions/search`

Searches for questions using a search term.

**Request Body:**
```json
{
  "searchTerm": "cat"
}
```

**Returns:**
```json
{
  "success": true,
  "questions": [
    {
      "id": 24,
      "question": "What is my cat's name?",
      "answer": "Schubiger",
      "difficulty": 2,
      "category": 1
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

---

## POST `/quizzes`

Fetches a random question from a given category excluding all questions not relevant.

**Request Body:**
```json
{
  "previous_questions": [5, 10],
  "quiz_category": {
    "id": 4,
    "type": "History"
  }
}
```

**Returns:**
```json
{
  "success": true,
  "question": {
    "id": 12,
    "question": "Who invented Peanut Butter?",
    "answer": "George Washington Carver",
    "difficulty": 2,
    "category": 4
  }
}
```
