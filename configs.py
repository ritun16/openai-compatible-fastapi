DB_NAME = "users.db"
SUPPORTED_DOMAINS = ["gmail.com"]
MASKED_API_KEY_LEN = 5

time_period = 60 # In Seconds
num_request = 2 # Number of request that a user can make in 60 seconds


OTP_EMAIL_HTML = """<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Email</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #333333;
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .otp {{
            font-weight: bold;
            font-size: 20px;
            color: #0073e6;
        }}

        .footer {{
            font-size: 12px;
            color: #777777;
            margin-top: 20px;
        }}
    </style>
</head>

<body>
    <div class="container">
        <h2>Your OTP Code</h2>
        <p>Your One-Time Password (OTP) is: <span class="otp">{generated_otp}</span></p>
        <p>This OTP is valid for only 10 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
    </div>
</body>

</html>"""
