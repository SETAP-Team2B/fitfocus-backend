
## Code Contribution Guidelines

We welcome contributions from the community. However, to maintain a consistent and high-quality codebase, please ensure your contributions adhere to the following guidelines.

### Code Acceptance Criteria

- **Safety:** The code must be safe, secure, and free of vulnerabilities.
- **Project Layout:** Follow the existing project layout and do not introduce unnecessary deviations.
- **Coding Patterns:** Maintain consistency with the existing code patterns. Do not deviate from established patterns.
- **Branching:** Do not push to the main branch directly. Create a new branch for every feature or fix and submit a Pull Request.
- **Naming Conventions:**
  - Use `snake_case` for variables, functions, and method names. 
  - Use `CamelCase` for class names.
- **Functional Code:** Ensure that your code is tested and working correctly before submitting a Pull Request. No failing tests or runtime errors should exist.

### Branching and Workflow

- Master Branch: Protected; no direct pushes allowed(Do not push to master!).
- Feature Branches: For new features and bug fixes, create a new branch from main, named appropriately, e.g., feature/your-feature-name.
- Pull Requests: Once the feature branch is ready, submit a Pull Request for code review. Your PR should include tests for new functionality, if applicable.

### Available APIs
##### Sign up API
- Endpoint: 
`http://127.0.0.1:8000/onboarding/create-user/`
- Success response(Sample):
```json
{
    "data": {
        "username": "dev017",
        "first_name": "Gbenga",
        "last_name": "Dev",
        "email": "test06@myport.ac.uk"
    }
}
```
- Error Response(Sample):
```json
{
    "code": 400,
    "message": "'first_name' is missing"
}
```

#### Login API
- Endpoint:
http://127.0.0.1:8000/onboarding/login-user/
- Request Body :
```json
{
    "username": "dev017",
    "password": "securepassword123"
}
```
- Success Response:
```json
{
    "data": {
        "username": "dev017",
        "first_name": "Gbenga",
        "last_name": "Dev",
        "email": "test06@myport.ac.uk",
        "token": "abc123xyz"
    }
}
```
- Error Response (Invalid Credentials):
```json
{
    "code": 400,
    "message": "Invalid username or password"
}
```
- Error Response (Missing Fields):
```json
{
    "code": 400,
    "message": "'password' is missing"
}
```