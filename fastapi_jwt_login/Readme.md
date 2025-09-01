# JWT tokens

## About JWT

JWT means "JSON Web Tokens".
It's a standard to codify a JSON object in a long dense string without spaces. It looks like this:
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

you can create a token with an expiration of, let's say, 1 week. And then when the user comes back the next day with the token, you know that user is still logged in to your system.

After a week, the token will be expired and the user will not be authorized and will have to sign in again to get a new token. And if the user (or a third party) tried to modify the token to change the expiration, you would be able to discover it, because the signatures would not match.

We need to install PyJWT to generate and verify the JWT tokens in Python.
Make sure you create a virtual environment, activate it, and then install pyjwt:

> pip install pyjwt

If you are planning to use digital signature algorithms like RSA or ECDSA, you should install the cryptography library dependency pyjwt[crypto].

## Password hashing

"Hashing" means converting some content (a password in this case) into a sequence of bytes (just a string)

Whenever you pass exactly the same content (exactly the same password) you get exactly the same gibberish.

But you cannot convert from the gibberish back to the password.

## Why use password hashing

If your database is stolen, the thief won't have your users' plaintext passwords, only the hashes.
So, the thief won't be able to try to use that password in another system (as many users use the same password everywhere, this would be dangerous).

## Install passlib

PassLib is a great Python package to handle password hashes.
It supports many secure hashing algorithms and utilities to work with them.
The recommended algorithm is "Bcrypt"

> pip install "passlib[bcrypt]"
