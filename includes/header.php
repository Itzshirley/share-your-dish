<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Share Your Dish</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
    <div class="logo">
        <a href="uploads/SYDlogo.png" target="_blank">
            <img src="uploads/SYDlogo.png" alt="Share Your Dish Logo">
        </a>
    </div>
    <nav>
        <ul class="nav-links">
            <li><a href="index.php" class="btn-nav">Home</a></li>
            <li><a href="about.php" class="btn-nav">About</a></li>
            <li><a href="recipes.php" class="btn-nav">Browse Recipes</a></li>
            <li><a href="login.php" class="btn-nav">Login</a></li>
            <li><a href="contact.php" class="btn-nav">Contact</a></li>
        </ul>
        <div class="hamburger">☰</div>
    </nav>
</header>

<script>
    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
</script>


