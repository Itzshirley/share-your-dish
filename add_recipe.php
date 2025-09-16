<?php
include("includes/header.php");
include("config.php");
session_start();

// Only allow logged-in users
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

$message = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $title = trim($_POST['title']);
    $description = trim($_POST['description']);
    $ingredients = trim($_POST['ingredients']);
    $instructions = trim($_POST['instructions']);
    $user_id = $_SESSION['user_id'];

    // Handle optional image upload
    $image = '';
    if (isset($_FILES['image']) && $_FILES['image']['error'] == 0) {
        $image_name = time() . '_' . $_FILES['image']['name'];
        move_uploaded_file($_FILES['image']['tmp_name'], 'uploads/' . $image_name);
        $image = $image_name;
    }

    $stmt = $conn->prepare("INSERT INTO recipes (user_id, title, description, ingredients, instructions, image) VALUES (?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("isssss", $user_id, $title, $description, $ingredients, $instructions, $image);

    if ($stmt->execute()) {
        $message = "Recipe added successfully!";
    } else {
        $message = "Error adding recipe.";
    }
}
?>

<div style="max-width:600px; margin:50px auto; background:#f9fff9; padding:20px; border-radius:8px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
    <h2 style="color:#2c7a7b;">Add a Recipe</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="text" name="title" placeholder="Recipe Title" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;">
        <textarea name="description" placeholder="Short Description" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;"></textarea>
        <textarea name="ingredients" placeholder="Ingredients" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;"></textarea>
        <textarea name="instructions" placeholder="Instructions" required style="width:100%; padding:10px; margin:10px 0; border-radius:5px; border:1px solid #ccc;"></textarea>
        <input type="file" name="image" style="margin:10px 0;">
        <button type="submit" style="background:#2c7a7b; color:white; padding:10px 15px; border:none; border-radius:5px; cursor:pointer;">Add Recipe</button>
    </form>
    <p style="color:green; margin-top:10px;"><?= $message ?></p>
</div>

<?php include("includes/footer.php"); ?>
