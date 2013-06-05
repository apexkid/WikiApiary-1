<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    date_default_timezone_set('America/Chicago');
    $date_filter = date('Y-m-d H:i:s', strtotime('-3 months'));

    $stmt = $conn->prepare('SELECT capture_date, users, activeusers FROM statistics WHERE website_id = :id AND capture_date > :date_filter');
    $stmt->execute(array('id' => $id, 'date_filter' => $date_filter));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s, %s\n",
		'capture_date', 'users', 'activeusers');
        foreach($result as $row) {
            printf ("%s, %s, %s\n",
		$row['capture_date'], $row['users'], $row['activeusers']);
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
