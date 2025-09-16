# Use official PHP image with Apache
FROM php:8.2-apache

# Copy project files into the container
COPY . /var/www/html/

# Enable mysqli extension
RUN docker-php-ext-install mysqli

# Expose port 80
EXPOSE 80
