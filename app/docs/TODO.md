## USER ROUTE

- create a change password endpoint via OTP sent to emaail.
- on user update endpoint, fix with a condition on email update, password is required to proceed with the operation, then send a confirmation mail to the new email.
- add the background task to check for deactivated account >= 30 days for cleanup.

## MIDDLEWARE/INFRA

- create and register an auth middleware to validates the JWT token from cookies and attach the user to the request.state object.
- procced with the resend free tier setup for emails / find and register a free provider.
- implement rate limiter
- initialize a centralize logger with levels set

## TESTS

- Write unit tests for the auth endpoints.

## PAYSTACK
- Set up Paystack service with the relevant endpoints for use