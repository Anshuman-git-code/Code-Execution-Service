# Base Image
FROM python:3.10-alpine

# Create an unprivileged user for security
RUN adduser --disabled-password --gecos '' sandbox

# Switch to the new user
USER sandbox

# Default command (overridden when running the container)
CMD ["python3"]