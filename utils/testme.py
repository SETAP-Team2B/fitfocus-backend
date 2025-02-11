import json

value = '{"data": "[{\\"model\\": \\\"auth.user\\", \\\"pk\\": 2, \\\"fields\\": {\\"password\\": \\\"pbkdf2_sha256$870000$MaQoy5BV4tmag6e36QwFOr$RcYh4R8HLuAhH+L5km5WF2pTDeW9feoGP1x6Q7IomWs=\\", \\\"last_login\\": null, \\\"is_superuser\\": false, \\\"username\\": \\\"dev012\\", \\\"first_name\\": \\\"Gbenga\\", \\\"last_name\\": \\\"Dev\\", \\\"email\\": \\\"test@myport.ac.uk\\", \\\"is_staff\\": false, \\\"is_active\\": true, \\\"date_joined\\": \\\"2025-02-11T21:24:29.910Z\\", \\\"groups\\": [], \\\"user_permissions\\": []}}]"}'
print(json.loads(value))
