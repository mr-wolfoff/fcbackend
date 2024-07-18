## FastAPI + SQLModel backend for test task for FS Community

This test task uses Postgres as a DB. Fill in DATABASE_URI env to make it work. 

### Quickstart
1.  <b>Start the App</b>:
  - Using Python:
    `python asgi.py`

2. <b>Use Openapi at</b>: `http://localhost:8080/#/`

## Task:  

Add a review system to the backend. Review is given by some user to another user, it has 3 grades: Great/Some Problems/Bad + a text review field. This system should be capable of: adding/creating a review from one user to another user, updating and deleting the review; retrieving all the reviews user got and all the reviews user gave. 

- launch a new local Postgres instance and add its URI to .env 
- Add a new model for reviews of the users. It should contain user_id_from, user_id_to, rating, review_text fields. Other fileds are optional and based on your descision. (new folder reviews in api/public)
- Add new cruds to work with reviews on DB-level and add views to work with reviews from API. (see task description for details) 
- Keep the structure of the code as in other parts of API (like user).
- Add tests and describe how to run tests to check that the API works as intended. (there are no tests in the project now, suggest how testing can work)
