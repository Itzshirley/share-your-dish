<?php
include("includes/header.php");
include("config.php");
session_start();
$message = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = trim($_POST['username']);
    $email = trim($_POST['email']);
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT);

    $check = $conn->prepare("SELECT id FROM users WHERE username=? OR email=?");
    $check->bind_param("ss", $username, $email);
    $check->execute();
    $check->store_result();

    if ($check->num_rows > 0) {
        $message = "Username or email already exists.";
    } else {
        $stmt = $conn->prepare("INSERT INTO users (username, email, password) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $username, $email, $password);
        if ($stmt->execute()) {
            header("Location: login.php");
            exit;
        } else {
            $message = "Error creating account.";
        }
    }
}
?>

<div class="form-container" style="background:#f9fff9; padding:20px; border-radius:8px; max-width:400px; margin:50px auto; box-shadow:0 0 10px rgba(0,0,0,0.1);">
    <h2 style="color:#2c7a7b;">Sign Up</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;">
        <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;">
        <input type="password" name="password" placeholder="Password" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;">
        <button type="submit" style="background:#2c7a7b; color:white; padding:10px 15px; border:none; border-radius:5px; cursor:pointer;">Sign Up</button>
    </form>
    <p style="color:red; margin-top:10px;"><?= $message ?></p>
</div>

<?php include("includes/footer.php"); ?>

