# Frahoosh operational patch

This build addresses:
- Student registration for competitions/festivals/cultural activities.
- Payment-link generation through `FRAHOOSH_PAYMENT_URL` without storing card CVV/OTP.
- Operational reports with CSV export across major panels.
- Operational class/exam cards and classroom/exam seating in executive panel.
- Executive student file/search/edit access.
- Cultural activity fee support and festival management.

Before production payment, configure a real PSP/payment gateway callback on the server. Do not collect CVV2/OTP in the Frahoosh database.
