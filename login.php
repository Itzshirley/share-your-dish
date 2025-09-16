<?php
include("includes/header.php");
include("config.php");
session_start();
$message = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $email = trim($_POST['email']);
    $password = trim($_POST['password']);

    $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE email=?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $stmt->store_result();
    $stmt->bind_result($id, $username, $hashed_password);
    $stmt->fetch();

    if ($stmt->num_rows == 0) {
        $message = "Account not found. Please sign up.";
    } elseif (password_verify($password, $hashed_password)) {
        $_SESSION['user_id'] = $id;
        $_SESSION['username'] = $username;
        header("Location: myaccount.php");
        exit;
    } else {
        $message = "Incorrect password.";
    }
}
?>

<div class="form-container" style="background:#f9fff9; padding:20px; border-radius:8px; max-width:400px; margin:50px auto; box-shadow:0 0 10px rgba(0,0,0,0.1);">
    <h2 style="color:#2c7a7b;">Login</h2>
    <form method="POST">
        <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;">
        <input type="password" name="password" placeholder="Password" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;">
        <button type="submit" style="background:#2c7a7b; color:white; padding:10px 15px; border:none; border-radius:5px; cursor:pointer;">Login</button>
    </form>
    <p style="color:red; margin-top:10px;"><?= $message ?></p>
    <p style="margin-top:15px;">Don't have an account? <a href="signup.php" style="color:#2c7a7b; font-weight:bold;">Sign Up here</a></p>
</div>

<?php include("includes/footer.php"); ?>
