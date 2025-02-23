
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
#### Sign up API
- Endpoint: 
`http://127.0.0.1:8000/onboarding/create-user/`
- Success response (Sample):
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
- Error Response (Sample):
```json
{
    "code": 400,
    "message": "'first_name' is missing"
}
```

#### Login API
- Endpoint:
`http://127.0.0.1:8000/onboarding/login-user/`
- Request Body:
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
    "message": "Invalid username or password."
}
```
- Error Response (Missing Fields):
```json
{
    "code": 400,
    "message": "'password' is missing"
}
```

#### Generate One-Time Password API
- Endpoint: 
`127.0.01:8000/onboarding/generate-otp/`
- Request Body (Sample 1):
```json
{
    "username": "spearmintage",
}
```
- Request Body (Sample 2):
```json
{
    "email": "test_email@gmail.com",
}
```
- Success Response:
```json
{
    "data": "OTP sent."
}
```
- Error Response (Invalid Username or Invalid Email):
```json
{
    "code": 400,
    "message": "Could not find associated user."
}
```
- Error Response (No Username/Password Entered):
```json
{
    "code": 400,
    "message": "No email or username was provided."
}
```
- Error Response (Email Failed to Send):
```json
{
    "code": 400,
    "message": "Email failed to send."
}
```


#### Validate One-Time Password API
- Endpoint: 
`127.0.01:8000/onboarding/validate-otp/`
- Request Body (Sample 1):
```json
{
    "username": "fit_test",
    "otp": 600100
}
```
- Request Body (Sample 2):
```json
{
    "email": "fitfocusup@gmail.com",
    "otp": 600100
}
```
- Success Response:
```json
{
    "data": "success"
}
```
- Error Response (Incorrect OTP):
```json
{
    "code": 400,
    "message": "The OTP you entered is incorrect."
}
```
- Error Response (Expired OTP):
```json
{
    "code": 400,
    "message": "The OTP has expired. Please request a new OTP."
}
```
- Error Response (Invalid Username/Password Entered):
```json
{
    "code": 400,
    "message": "Could not find associated user."
}
```
- Error Response (No Username/Password Entered):
```json
{
    "code": 400,
    "message": "No email or username was provided."
}
```
- Error Response (No OTP Entered):
```json
{
    "code": 400,
    "message": "No OTP was provided."
}
```
- Error Response (OTP Already Entered Before):
```json
{
    "code": 400,
    "message": "This OTP has already been entered before."
}
```


#### Reset Password API
- Endpoint: 
`127.0.01:8000/onboarding/reset-password/`
- Request Body (Sample 1):
```json
{
    "username": "fit_test",
    "new_password": "Password123!",
    "confirm_password": "Password123!"
}
```
- Request Body (Sample 2):
```json
{
    "email": "fitfocus_email_test@gmail.com",
    "new_password": "Password123!",
    "confirm_password": "Password123!"
}
```
- Success Response:
```json
{
    "data": "Password Successfully Changed"
}
```
- Error Response (User Not Found):
```json
{
    "code": 400,
    "message": "Could not find associated user."
}
```
- Error Response (No Email/Username Entered):
```json
{
    "code": 400,
    "message": "No email or username was provided."
}
```
- Error Response (No Password Entered):
```json
{
    "code": 400,
    "message": "No password entered."
}
```
- Error Response (No Confirmation Password Entered):
```json
{
    "code": 400,
    "message": "No password confirmation entered."
}
```
- Error Response (Passwords Do Not Match):
```json
{
    "code": 400,
    "message": "Passwords do not match."
}
```
- Error Response (Password = Current Password):
```json
{
    "code": 400,
    "message": "Cannot set new password to current password."
}
```
- Error Response (Password Not Strong Enough):
```json
{
    "code": 400,
    "message": "New password is too weak."
}
```
- Error Response (User Not Validated):
```json
{
    "code": 400,
    "message": "OTP not verified. Validate or request another."
}
```