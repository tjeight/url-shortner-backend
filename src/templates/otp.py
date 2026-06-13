OTP_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}

        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 8px;
            padding: 32px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}

        .otp {{
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            letter-spacing: 8px;
            color: #2563eb;
            margin: 24px 0;
        }}

        .footer {{
            margin-top: 24px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{app_name}</h2>
        </div>

        <p>Hello {user_name},</p>

        <p>
            Use the following One-Time Password (OTP) to verify your account.
            This OTP will expire in <strong>{expiry_minutes} minutes</strong>.
        </p>

        <div class="otp">{otp}</div>

        <p>
            If you did not request this OTP, please ignore this email.
        </p>

        <div class="footer">
            © {current_year} {app_name}. All rights reserved.
        </div>
    </div>
</body>
</html>
"""
