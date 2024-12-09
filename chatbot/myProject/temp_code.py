def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n // 2):
        if n % i == 0:
            return False
    return True

# Test the function
number = 15
if is_prime(number):
    print(f"{number} is a prime number")
else:
    print(f"{number} is not a prime number")