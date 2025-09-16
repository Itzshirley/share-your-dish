<?php include("includes/header.php"); ?>
<div class="container">
    <h2>Contact Us 📩</h2>
    <p>We’d love to hear from you! Fill out the form below and we’ll get back to you soon.</p>

    <form action="contact_process.php" method="POST" class="form-box">
        <label>Your Name:</label>
        <input type="text" name="name" placeholder="Enter your name" required>

        <label>Email:</label>
        <input type="email" name="email" placeholder="Enter your email" required>

        <label>Message:</label>
        <textarea name="message" rows="5" placeholder="Write your message here..." required></textarea>

        <button type="submit" class="btn">Send Message</button>
    </form>
</div>
<?php include("includes/footer.php"); ?>

