<?php
include("includes/header.php");
include("config.php");
session_start();

if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

$user_id = $_SESSION['user_id'];
$username = $_SESSION['username'];

$sql = $conn->prepare("SELECT id, title, description FROM recipes WHERE user_id=? ORDER BY created_at DESC");
$sql->bind_param("i", $user_id);
$sql->execute();
$result = $sql->get_result();
?>

<div style="max-width:800px; margin:50px auto; background:#f9fff9; padding:20px; border-radius:8px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
    <h2 style="color:#2c7a7b;">Welcome, <?= htmlspecialchars($username) ?>!</h2>
    <a href="add_recipe.php" style="display:inline-block; margin:10px 0; background:#2c7a7b; color:white; padding:10px 15px; border-radius:5px; text-decoration:none;">+ Add a Recipe</a>

    <h3 style="margin-top:20px;">Your Recipes:</h3>
    <?php if ($result->num_rows > 0): ?>
        <ul>
            <?php while ($row = $result->fetch_assoc()): ?>
                <li><?= htmlspecialchars($row['title']) ?> - <?= htmlspecialchars($row['description']) ?></li>
            <?php endwhile; ?>
        </ul>
    <?php else: ?>
        <p>You have not added any recipes yet.</p>
    <?php endif; ?>
</div>

<?php include("includes/footer.php"); ?>
