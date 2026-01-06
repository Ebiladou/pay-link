from typing import Dict, Any
from datetime import datetime

# move to using resend and an isolated templating for email towards deploymennt.

class EmailService:
    def __init__(self):
        ...
 
    def _log_email(self, to: str, subject: str, variables: Dict[str, Any]):
        print("\n" + "="*70)
        print(f"EMAIL: {subject}")
        print("="*70)
        print(f"To: {to}")
        print(f"From: PayLink")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if variables:
            print("\nVariables:")
            for key, value in variables.items():
                print(f"  {key}: {value}")
        
        print("="*70 + "\n")
        
        return f"mock_id_{to}"
    
    def send_verification_email(self, to: str, name: str, token: str):
        confirmation_link = f"confirm-email?token={token}"
        return self._log_email(
            to=to,
            subject="Verify Your PayLink Email",
            variables={
                "name": name,
                "token": token,
                "verification_link": confirmation_link
            }
        )
    
    def send_password_reset_email(self, to: str, name: str, token: str):
        reset_link = (f"reset-password?token={token}")
        return self._log_email(
            to=to,
            subject="Reset Your PayLink Password",
            variables={
                "name": name,
                "token": token,
                "reset_link": reset_link
            }
        )

email_service = EmailService()