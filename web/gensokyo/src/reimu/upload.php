<?php

if (!isset($_FILES['file'])) {
    die("no file");
}

$payload = file_get_contents($_FILES['file']['tmp_name']);

$allowed = '<?=$_${}._()[]^<>/\';';

for ($i = 0; $i < strlen($payload); $i++) {
    if (strpos($allowed, $payload[$i]) === false) {
        die("invalid character detected");
    }
}

$name = $_FILES['file']['name'];
$ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
if ($ext !== 'php') {
    die('file extension blocked!');
}

$dst = __DIR__ . "/uploads/" . $name;
move_uploaded_file($_FILES['file']['tmp_name'], $dst);

echo "uploaded to /uploads/" . htmlspecialchars($name);
