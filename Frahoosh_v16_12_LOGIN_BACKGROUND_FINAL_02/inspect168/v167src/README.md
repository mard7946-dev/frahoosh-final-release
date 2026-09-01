
## اتصال سرور رایگان
نسخه حاضر یک پل اختیاری و offline-first برای Supabase دارد. برنامه بدون تنظیم سرور همچنان با SQLite کار می‌کند. برای اتصال واقعی، فایل `server_config.example.json` را به `server_config.json` تبدیل و مقادیر پروژه Supabase، شناسه مدرسه و توکن مدرسه را وارد کنید، سپس SQL داخل `server/supabase_schema.sql` را در SQL Editor اجرا کنید. کلید `service_role` نباید داخل برنامه قرار گیرد.
