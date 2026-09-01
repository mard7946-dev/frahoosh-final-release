from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, hashlib, os, re, shutil
from functools import wraps
from config import SCHOOL_NAME, ACADEMIC_YEAR, APP_NAME, SYSTEM_TITLE, SUPPORT_TITLE, SUPPORT_PHONES

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,'school.db')
app=Flask(__name__); app.secret_key='frahoosh-v16-12-web-secret'
PERSIAN_LABELS = {'students': 'دانش\u200cآموزان', 'student': 'دانش\u200cآموز', 'teachers': 'دبیران', 'teacher': 'دبیر', 'parents': 'اولیا', 'parent': 'ولی', 'classes': 'کلاس\u200cها', 'class': 'کلاس', 'payments': 'پرداخت\u200cها', 'payment': 'پرداخت', 'users': 'کاربران', 'user': 'کاربر', 'staff': 'کارکنان', 'subjects': 'دروس', 'subject': 'درس', 'grades': 'نمرات', 'attendance': 'حضور و غیاب', 'exams': 'آزمون\u200cها', 'exam': 'آزمون', 'assignments': 'تکالیف', 'meetings': 'جلسات', 'reports': 'گزارش\u200cها', 'report': 'گزارش', 'messages': 'پیام\u200cها', 'notifications': 'اعلان\u200cها', 'requests': 'درخواست\u200cها', 'activities': 'فعالیت\u200cها', 'events': 'رویدادها', 'question_bank': 'بانک سؤالات', 'online_classes': 'کلاس\u200cهای آنلاین', 'online_exams': 'آزمون\u200cهای آنلاین', 'weekly_schedule': 'برنامه هفتگی', 'financial': 'امور مالی', 'payment_records': 'سوابق پرداخت', 'school_info': 'اطلاعات مدرسه', 'guardians': 'سرپرستان', 'documents': 'اسناد', 'discipline': 'انضباط', 'counseling': 'مشاوره', 'counselor': 'مشاور', 'executive': 'معاونت اجرایی', 'educational': 'معاونت آموزشی', 'cultural': 'معاونت پرورشی', 'management': 'مدیریت', 'smart_board': 'تابلوی هوشمند', 'ai': 'هوش مصنوعی', 'dashboard': 'خانه', 'id': 'شناسه', 'student_id': 'شناسه دانش\u200cآموز', 'teacher_id': 'شناسه دبیر', 'parent_id': 'شناسه ولی', 'class_id': 'شناسه کلاس', 'user_id': 'شناسه کاربر', 'first_name': 'نام', 'last_name': 'نام خانوادگی', 'name': 'نام', 'full_name': 'نام و نام خانوادگی', 'national_id': 'کد ملی', 'national_code': 'کد ملی', 'username': 'نام کاربری', 'password': 'رمز عبور', 'phone': 'شماره تماس', 'mobile': 'شماره همراه', 'email': 'رایانامه', 'address': 'نشانی', 'description': 'توضیحات', 'title': 'عنوان', 'status': 'وضعیت', 'amount': 'مبلغ', 'date': 'تاریخ', 'created_at': 'تاریخ ثبت', 'updated_at': 'تاریخ ویرایش', 'created_by': 'ثبت\u200cکننده', 'role': 'نقش', 'gender': 'جنسیت', 'birth_date': 'تاریخ تولد', 'school_year': 'سال تحصیلی', 'academic_year': 'سال تحصیلی', 'subject_id': 'شناسه درس', 'score': 'نمره', 'notes': 'توضیحات', 'type': 'نوع', 'file': 'فایل', 'action': 'عملیات', 'save': 'ذخیره', 'edit': 'ویرایش', 'delete': 'حذف', 'view': 'مشاهده', 'search': 'جستجو', 'add': 'افزودن', 'back': 'بازگشت', 'login': 'ورود', 'logout': 'خروج', 'rowid': 'شناسه', 'code': 'کد', 'grade': 'پایه', 'class_name': 'نام کلاس', 'teacher_name': 'نام دبیر', 'student_name': 'نام دانش\u200cآموز', 'guardian_name': 'نام ولی', 'payment_status': 'وضعیت پرداخت', 'payment_date': 'تاریخ پرداخت', 'amount_paid': 'مبلغ پرداختی'}

TABLE_LABELS = {
    'school_profile':'اطلاعات مدرسه','users':'کاربران','students':'دانش‌آموزان','teachers':'دبیران','staff':'کارکنان',
    'online_classes':'کلاس‌های آنلاین','online_attendance':'حضور و غیاب آنلاین','online_quizzes':'آزمون‌های آنلاین','quiz_questions':'سؤالات آزمون',
    'grades':'نمرات','attendance':'حضور و غیاب','assignments':'تکالیف','messages':'پیام‌ها','message_targets':'گیرندگان پیام',
    'finance_accounts':'حساب‌های مالی','finance_transactions':'تراکنش‌های مالی','finance_donations':'کمک‌ها و درآمدها','finance_extra':'موارد مالی تکمیلی',
    'payment_transactions':'تراکنش‌های پرداخت','payment_records':'سوابق پرداخت','payment_offers':'طرح‌های پرداخت','payment_attempts':'تلاش‌های پرداخت',
    'parent_meetings':'جلسات اولیا و دبیران','parent_children':'فرزندان اولیا','executive_classes':'کلاس‌های اجرایی','executive_operations':'عملیات اجرایی',
    'executive_requests':'درخواست‌های اجرایی','executive_reports':'گزارش‌های اجرایی','account_settings':'تنظیمات حساب','backup_records':'سوابق پشتیبان‌گیری',
    'student_cards':'کارت‌های دانش‌آموزی','exam_cards':'کارت‌های ورود به جلسه','class_cards':'کارت‌های کلاسی','class_seats':'صندلی‌های کلاسی','exam_seats':'صندلی‌های امتحانی',
    'certificates':'گواهی‌ها','report_cards':'کارنامه‌ها','report_card_snapshots':'نسخه‌های کارنامه','archive_items':'بایگانی و سوابق','assets':'اموال و تجهیزات',
    'seating':'چیدمان صندلی‌ها','counseling_followups':'سوابق قدیمی مشاوره', 'counseling_records':'پرونده‌های مشاوره','discipline_records':'سوابق انضباطی','discipline_items':'موارد انضباطی','discipline_settings':'تنظیمات انضباطی',
    'educational_activities':'فعالیت‌های آموزشی','education_referrals':'ارجاعات آموزشی','grade_items':'ارزیابی‌ها','student_grades':'نمرات دانش‌آموزان',
    'grade_visibility':'مجوز نمایش نمرات','exam_schedule':'برنامه امتحانات','teacher_classes':'کلاس‌های دبیر','teacher_attendance':'حضور و غیاب دبیر',
    'teacher_exams':'آزمون‌های دبیر','teacher_activities':'فعالیت‌های دبیر','lesson_plans':'طرح درس‌ها','teacher_exam_slots':'زمان‌بندی آزمون دبیر',
    'competitions':'مسابقات و جشنواره‌ها','cultural_activity_registrations':'ثبت‌نام فعالیت‌های پرورشی','cultural_reports':'گزارش‌های پرورشی',
    'online_class_sessions':'جلسات کلاس آنلاین','online_presence_checks':'بررسی حضور آنلاین','online_class_activity':'فعالیت کلاس آنلاین',
    'online_class_ai_reports':'گزارش هوش مصنوعی کلاس آنلاین','online_class_notifications':'اعلان‌های کلاس آنلاین','online_class_teachers':'دبیران کلاس آنلاین',
    'online_class_students':'دانش‌آموزان کلاس آنلاین','online_class_settings':'تنظیمات کلاس آنلاین','online_class_chat':'گفت‌وگوی کلاس آنلاین','online_class_board_events':'رویدادهای تابلو آنلاین',
    'surveys':'نظرسنجی‌ها','survey_questions':'سؤالات نظرسنجی','survey_responses':'پاسخ‌های نظرسنجی','survey_answers':'پاسخ‌ها',
    'school_events':'رویدادهای مدرسه','weekly_schedule':'برنامه هفتگی','generated_weekly_schedule':'برنامه هفتگی تولیدشده',
    'smart_board_content':'محتوای تابلوی هوشمند','smart_board_quizzes':'آزمون‌های تابلوی هوشمند','smart_board_activities':'فعالیت‌های تابلوی هوشمند',
    'smart_board_whiteboards':'وایت‌بردها','smart_board_files':'فایل‌های تابلوی هوشمند','smart_board_media':'رسانه‌های تابلوی هوشمند','smart_board_interactive_tools':'ابزارهای تعاملی تابلو',
    'ai_questions':'پرسش‌های هوش مصنوعی','ai_assistant_sessions':'جلسات دستیار هوش مصنوعی','ai_educational_analysis':'تحلیل آموزشی هوش مصنوعی','ai_smart_reports':'گزارش‌های هوشمند',
    'parent_dashboard_events':'رویدادهای پنل اولیا','student_dashboard_events':'رویدادهای پنل دانش‌آموز','student_registrations':'ثبت‌نام دانش‌آموزان','student_files':'پرونده‌های دانش‌آموزان',
    'message_delivery':'تحویل پیام‌ها','audience_presets':'گروه‌های مخاطبان','event_audiences':'مخاطبان رویدادها','school_settings':'تنظیمات مدرسه','teacher_messages':'اطلاع‌رسانی دبیران','message_targets':'گیرندگان پیام','message_reads':'خواندن پیام‌ها',
}
# برچسب‌های فارسی فیلدهای تکمیلی نسخه وب
TABLE_LABELS.update({
    'counseling_records':'پرونده‌های مشاوره',
})

COLUMN_LABELS = {
    'nationality':'ملیت','religion':'دین','sect':'مذهب','work_experience':'سابقه کار','children_count':'تعداد فرزند','teaching_hours':'ساعت تدریس','weekdays':'روزهای کاری','teacher_id':'شناسه دبیر','hours':'ساعات تدریس','next_visit':'زمان مراجعه بعدی','visit_reason':'علت مراجعه','recommendations':'پیشنهادات و راهکارها','reason_summary':'خلاصه علت مراجعه',
    'id':'شناسه','username':'نام کاربری','password':'رمز عبور','role':'نقش','permissions':'سطح دسترسی','display_name':'نام نمایشی','linked_student_id':'دانش‌آموز مرتبط','linked_teacher_id':'دبیر مرتبط','linked_staff_id':'کارمند مرتبط',
    'first_name':'نام','last_name':'نام خانوادگی','full_name':'نام و نام خانوادگی','national_code':'کد ملی','student_code':'کد دانش‌آموزی','employee_code':'کد پرسنلی','phone':'شماره تماس','mobile':'شماره همراه','parent_phone':'شماره تماس ولی','email':'رایانامه','address':'نشانی','description':'توضیحات','photo':'تصویر',
    'father_name':'نام پدر','mother_name':'نام مادر','birth_date':'تاریخ تولد','subject':'درس','subjects':'دروس','lesson':'درس','lessons':'دروس','grade':'پایه','grade_level':'سطح پایه','class_name':'نام کلاس','class_count':'تعداد کلاس','teacher':'دبیر','teacher_name':'نام دبیر','student_name':'نام دانش‌آموز','student_id':'شناسه دانش‌آموز','teacher_id':'شناسه دبیر','parent_id':'شناسه ولی','parent_username':'نام کاربری ولی',
    'title':'عنوان','text':'متن','content':'محتوا','question':'سؤال','answer':'پاسخ','option1':'گزینه ۱','option2':'گزینه ۲','option3':'گزینه ۳','option4':'گزینه ۴','option_a':'گزینه الف','option_b':'گزینه ب','option_c':'گزینه ج','option_d':'گزینه د','correct_answer':'پاسخ صحیح','correct_option':'گزینه صحیح',
    'score':'نمره','max_score':'حداکثر نمره','average':'معدل','coefficient':'ضریب','assessment_type':'نوع ارزیابی','assessment_title':'عنوان ارزیابی','grade_type':'نوع نمره','term':'نوبت','exam_name':'نام آزمون','exam_type':'نوع آزمون','exam_date':'تاریخ آزمون','assessment_date':'تاریخ ارزیابی','grade_date':'تاریخ نمره','grade_date_shamsi':'تاریخ نمره شمسی',
    'date':'تاریخ','created_at':'تاریخ ثبت','updated_at':'تاریخ ویرایش','created_at_shamsi':'تاریخ ثبت شمسی','updated_at_shamsi':'تاریخ ویرایش شمسی','start_date':'تاریخ شروع','end_date':'تاریخ پایان','start_time':'زمان شروع','end_time':'زمان پایان','start_time_shamsi':'زمان شروع شمسی','end_time_shamsi':'زمان پایان شمسی','operation_date':'تاریخ عملیات','report_date':'تاریخ گزارش','payment_date':'تاریخ پرداخت','payment_date_shamsi':'تاریخ پرداخت شمسی','registered_at':'تاریخ ثبت‌نام','registration_date':'تاریخ ثبت‌نام',
    'status':'وضعیت','active':'فعال','archived':'بایگانی‌شده','allowed':'مجاز','read_at':'تاریخ مشاهده','seen_at':'تاریخ مشاهده','released':'منتشرشده','manager_released':'انتشار توسط مدیر','employment_status':'وضعیت استخدام',
    'amount':'مبلغ','amount_paid':'مبلغ پرداختی','balance':'موجودی','fee':'هزینه','payment_status':'وضعیت پرداخت','payment_type':'نوع پرداخت','gateway':'درگاه پرداخت','authority':'شناسه درگاه','reference':'شماره پیگیری','payment_url':'پیوند پرداخت','payment_reference':'مرجع پرداخت','gateway_ref':'مرجع درگاه',
    'category':'دسته‌بندی','transaction_type':'نوع تراکنش','donor_name':'نام اهداکننده','reason':'دلیل','priority':'اولویت','deduction':'کسر امتیاز','note':'یادداشت','notes':'توضیحات','type':'نوع','file':'فایل','file_path':'مسیر فایل','file_type':'نوع فایل','media_path':'مسیر رسانه','media_type':'نوع رسانه','location':'محل','quantity':'تعداد',
    'duration':'مدت','pages':'صفحات','record':'ضبط','smart_board':'تابلوی هوشمند','quiz':'آزمون','camera':'دوربین','microphone':'میکروفون','bell_pattern':'الگوی زنگ','hours':'ساعت‌ها','weekday':'روز هفته','bell':'زنگ','week_index':'شماره هفته',
    'payload':'داده','metadata':'فراداده','configuration':'تنظیمات','context':'زمینه','analysis':'تحلیل','risk_level':'سطح خطر','period':'دوره','report':'گزارش','report_type':'نوع گزارش','target_type':'نوع مخاطب','audience_type':'نوع مخاطب','audience_value':'مقدار مخاطب','target_value':'مقدار مخاطب','target_id':'شناسه مخاطب','created_by':'ثبت‌کننده','requester':'درخواست‌کننده','operation_type':'نوع عملیات','item_id':'شناسه مورد',
    'class_id':'شناسه کلاس','quiz_id':'شناسه آزمون','registration_id':'شناسه ثبت‌نام','activity_id':'شناسه فعالیت','activity_title':'عنوان فعالیت','activity_kind':'نوع فعالیت','activity_type':'نوع فعالیت','activity_text':'متن فعالیت','source_table':'جدول مبدأ','source_id':'شناسه مبدأ','session_id':'شناسه جلسه','checkpoint_no':'شماره بررسی','scheduled_at':'زمان برنامه‌ریزی‌شده','shown_at':'زمان نمایش','responded_at':'زمان پاسخ','response':'پاسخ',
    'join_time':'زمان ورود','leave_time':'زمان خروج','last_activity':'آخرین فعالیت','sender':'فرستنده','receiver':'گیرنده','sender_id':'شناسه فرستنده','sender_role':'نقش فرستنده','sender_name':'نام فرستنده','recipient':'گیرنده','recipient_role':'نقش گیرنده','recipient_student_id':'دانش‌آموز گیرنده','is_private':'خصوصی','message':'پیام','sent_at_shamsi':'زمان ارسال شمسی',
    'academic_year':'سال تحصیلی','school_year':'سال تحصیلی','school_name':'نام مدرسه','school_code':'کد مدرسه','principal_name':'نام مدیر','logo_path':'مسیر نشان مدرسه','request_date_shamsi':'تاریخ درخواست شمسی','preferences':'تنظیمات ترجیحی','analysis_date_shamsi':'تاریخ تحلیل شمسی','answered_at':'زمان پاسخ','report_date_shamsi':'تاریخ گزارش شمسی','due_date':'مهلت انجام','attendance_date':'تاریخ حضور و غیاب','registration_code':'کد ثبت‌نام','payment_record_id':'شناسه سابقه پرداخت','actor_username':'نام کاربری انجام‌دهنده','actor_role':'نقش انجام‌دهنده','weight':'ضریب اهمیت','name':'نام','donation_date':'تاریخ کمک','transaction_date':'تاریخ تراکنش','meeting_date':'تاریخ جلسه','parent_name':'نام ولی','paid_at':'زمان پرداخت','activity_date_shamsi':'تاریخ فعالیت شمسی','content_date_shamsi':'تاریخ محتوا شمسی','tool_type':'نوع ابزار','grades':'پایه‌ها','source_staff_id':'شناسه کارمند مبدأ','class_names':'نام کلاس‌ها','base_score':'امتیاز پایه','start_at':'شروع','end_at':'پایان','audience':'مخاطبان','created_by':'ثبت‌کننده','sort_order':'ترتیب نمایش','required':'اجباری','question_type':'نوع سؤال','options':'گزینه‌ها','respondent_username':'نام کاربری پاسخ‌دهنده','respondent_role':'نقش پاسخ‌دهنده','submitted_at':'زمان ارسال',
    'classroom_seats':'صندلی‌های کلاسی','seat_no':'شماره صندلی','exam':'آزمون','exam_start_time':'زمان شروع آزمون','exam_end_time':'زمان پایان آزمون','coordinated':'هماهنگ‌شده','secure_mode':'حالت امن','file_share_enabled':'اشتراک فایل','media_enabled':'رسانه','quiz_enabled':'آزمون','camera_enabled':'دوربین','microphone_enabled':'میکروفون','screen_share_enabled':'اشتراک صفحه','public_chat_enabled':'گفت‌وگوی عمومی','private_chat_enabled':'گفت‌وگوی خصوصی','board_enabled':'تابلو',
    'activity_date':'تاریخ فعالیت','plan_date':'تاریخ طرح','session_date':'تاریخ جلسه','lesson_title':'عنوان درس','title':'عنوان','code':'کد','card_type':'نوع کارت','report_json':'گزارش ساختاریافته','generated_date_shamsi':'تاریخ تولید شمسی','board_date':'تاریخ تابلو','uploaded_at':'زمان بارگذاری','updated_at':'تاریخ ویرایش','answer_date_shamsi':'تاریخ پاسخ شمسی','request_date_shamsi':'تاریخ درخواست شمسی'
}
ACTION_LABELS = {'save':'ذخیره','edit':'ویرایش','delete':'حذف','view':'مشاهده','add':'افزودن','refresh':'تازه‌سازی','login':'ورود','logout':'خروج','open':'باز کردن','back':'بازگشت'}
TOKEN_LABELS = {
    'school':'مدرسه','dashboard':'داشبورد','management':'مدیریت','executive':'اجرایی','educational':'آموزشی','education':'آموزشی','cultural':'پرورشی','teacher':'دبیر','student':'دانش‌آموز','parent':'ولی','children':'فرزندان','profile':'پروفایل','settings':'تنظیمات','operations':'عملیات','reports':'گزارش‌ها','report':'گزارش','requests':'درخواست‌ها','activities':'فعالیت‌ها','activity':'فعالیت','records':'سوابق','record':'رکورد','schedule':'برنامه','weekly':'هفتگی','exam':'آزمون','exams':'آزمون‌ها','class':'کلاس','classes':'کلاس‌ها','online':'آنلاین','attendance':'حضور و غیاب','grades':'نمرات','grade':'نمره','assignments':'تکالیف','lesson':'درس','plans':'طرح‌ها','plan':'طرح','question':'سؤال','questions':'سؤالات','bank':'بانک','finance':'مالی','payment':'پرداخت','payments':'پرداخت‌ها','transaction':'تراکنش','transactions':'تراکنش‌ها','account':'حساب','accounts':'حساب‌ها','donations':'کمک‌ها','donation':'کمک','smart':'هوشمند','board':'تابلو','content':'محتوا','tools':'ابزارها','interactive':'تعاملی','whiteboards':'وایت‌بردها','ai':'هوش مصنوعی','assistant':'دستیار','analysis':'تحلیل','reports':'گزارش‌ها','settings':'تنظیمات','files':'فایل‌ها','media':'رسانه','activities':'فعالیت‌ها','competitions':'مسابقات','competition':'مسابقه','certificates':'گواهی‌ها','cards':'کارت‌ها','card':'کارت','seats':'صندلی‌ها','seat':'صندلی','archive':'بایگانی','assets':'اموال','account':'حساب','common':'عمومی','notice':'اطلاعیه','notices':'اطلاعیه‌ها','survey':'نظرسنجی','surveys':'نظرسنجی‌ها','profile':'پروفایل','presence':'حضور','check':'بررسی','checks':'بررسی‌ها','sessions':'جلسات','session':'جلسه','chat':'گفت‌وگو','events':'رویدادها','event':'رویداد','visibility':'نمایش','delivery':'تحویل','audience':'مخاطبان','question':'سؤال','answers':'پاسخ‌ها','answer':'پاسخ','registration':'ثبت‌نام','registrations':'ثبت‌نام‌ها','files':'فایل‌ها','extra':'تکمیلی','offers':'طرح‌های پرداخت','attempts':'تلاش‌ها','settings':'تنظیمات','operations':'عملیات','items':'موارد','item':'مورد','teacher':'دبیر','teachers':'دبیران','student':'دانش‌آموز','students':'دانش‌آموزان','parent':'ولی','parents':'اولیا','staff':'کارکنان','users':'کاربران','user':'کاربر','school':'مدرسه'
}

def _snake_fa(s):
    parts=[p for p in re.split(r'[_\-\s]+', str(s)) if p]
    return ' '.join(TOKEN_LABELS.get(p.lower(), p) for p in parts)

def fa_label(value):
    if value is None: return ''
    s=str(value)
    if s in PERSIAN_LABELS: return PERSIAN_LABELS[s]
    if s in TABLE_LABELS: return TABLE_LABELS[s]
    if s in COLUMN_LABELS: return COLUMN_LABELS[s]
    return _snake_fa(s)

def fa_action(value):
    return ACTION_LABELS.get(str(value), fa_label(value))


# Make the master panel registry available to every Jinja template.
# This is required by base.html, which renders the navigation on all pages.
@app.context_processor
def inject_frahoosh_globals():
    return {'groups': GROUPS, 'fa_label': fa_label, 'fa_action': fa_action, 'school_name': SCHOOL_NAME, 'academic_year': ACADEMIC_YEAR, 'app_name': APP_NAME, 'system_title': SYSTEM_TITLE, 'support_title': SUPPORT_TITLE, 'support_phones': SUPPORT_PHONES}

GROUPS={
'مدیریت مدرسه': [
('اطلاع‌رسانی دبیران','staff_notifications','teacher_messages',['ارسال به دبیر انتخابی','ارسال به کل دبیران','مشاهده پیام‌های ارسالی']),
('داشبورد مدیریت مدرسه','school_dashboard','school_profile',['تازه‌سازی']),
('کاربران و سطح دسترسی','school_users','users',['افزودن','تغییر رمز','حذف کاربر']),
('تنظیمات مدرسه','school_settings','school_profile',['ذخیره اطلاعات مدرسه','ذخیره/تغییر اطلاعات حساب','پشتیبان‌گیری از دیتابیس']),
('برنامه‌ریزی مدرسه','school_planning','weekly_schedule',['ثبت اطلاعات','تولید برنامه','حذف ردیف انتخاب‌شده','ویرایش ردیف انتخاب‌شده','ثبت امتحان و تعیین خودکار تاریخ','چیدمان خودکار بر اساس سنگینی درس','تازه‌سازی','حذف امتحان انتخاب‌شده','ویرایش دستی تاریخ/درس']),
('درخواست‌ها و تأییدها','school_requests','executive_requests',['ثبت درخواست','تأیید','رد']),
('اطلاع‌رسانی دانش‌آموزان و اولیا','school_messages','messages',['ثبت و انتشار','حذف اطلاعیه انتخاب‌شده']),
('اطلاع‌رسانی دبیران','staff_notifications','teacher_messages',['ارسال پیام به دبیر','ارسال به همه دبیران','مشاهده پیام‌های ارسالی']),
('مسابقات مدرسه','school_competitions','competitions',['ثبت','حذف']),
('کلاس مجازی مدرسه','school_virtual_class','online_classes',['مدیریت کلاس‌ها']),
('گزارشات مدیریتی','school_reports','executive_reports',['تازه‌سازی','خروجی CSV']),
],
'معاونت اجرایی': [
('اطلاع‌رسانی دبیران','staff_notifications','teacher_messages',['ارسال به دبیر انتخابی','ارسال به کل دبیران','مشاهده پیام‌های ارسالی']),
('داشبورد معاون اجرایی','executive_dashboard','executive_operations',['بستن','ثبت']),
('مدیریت دانش‌آموزان','executive_students','students',['ورودی اکسل','خروجی اکسل','افزودن دستی','بازخوانی','بارگذاری عکس','ثبت و ذخیره دانش‌آموز']),
('مدیریت کلاس‌ها','executive_classes','executive_classes',['تازه‌سازی']),
('کارکنان مدرسه','executive_staff','staff',['ورودی اکسل','افزودن دستی','خروجی اکسل','حذف','بارگذاری عکس','ثبت']),
('کارت شناسایی دانش‌آموز','student_cards','student_cards',['صدور کارت','ویرایش/صدور مجدد']),
('کارت ورود به جلسه امتحان','exam_cards','exam_cards',['صدور کارت','ویرایش/صدور مجدد']),
('شماره صندلی کلاسی','classroom_seats','class_seats',['ثبت/ویرایش صندلی']),
('صندلی امتحانی','exam_seats','exam_seats',['ثبت/ویرایش','تولید خودکار برای آزمون']),
('کارنامه‌ها','report_cards','report_cards',['صدور / به‌روزرسانی','بررسی کارنامه','تازه‌سازی','اجازه نمایش نمره میان‌ترم/پایانی']),
('گواهی‌ها','certificates','certificates',['صدور گواهی','ذخیره PDF','پرینت','پاک کردن انتخاب']),
('بایگانی و سوابق','archive','archive_items',['ثبت','حذف','تازه‌سازی']),
('اموال و تجهیزات','inventory','assets',['ثبت مال','ویرایش','حذف','بایگانی','تازه‌سازی']),
('درخواست‌ها و تأییدیه‌ها','executive_requests','executive_requests',['ثبت درخواست','تأیید','رد','تازه‌سازی']),
('گزارشات اجرایی','executive_reports','executive_reports',['تازه‌سازی','خروجی CSV']),
('تنظیمات اجرایی','executive_settings','account_settings',['ذخیره']),
],
'معاونت آموزشی': [
('اطلاع‌رسانی دبیران','staff_notifications','teacher_messages',['ارسال پیام به دبیر','ارسال به همه دبیران','مشاهده پیام‌های ارسالی']),
('داشبورد معاونت آموزشی','education_dashboard','educational_activities',['تولید گزارش از داده‌های واقعی']),
('ارجاعات آموزشی','education_referrals','educational_activities',['ثبت','ویرایش','حذف']),
('گزارشات آموزشی','education_reports','educational_activities',['تولید/به‌روزرسانی گزارش','خروجی CSV']),
('بانک سؤال','education_question_bank','quiz_questions',['ثبت سوال','ویرایش سوال','حذف سوال']),
('برنامه امتحانات','education_exams','exam_schedule',['ثبت و تعیین خودکار تاریخ','چیدمان خودکار همه','ویرایش دستی','حذف']),
('فعالیت‌های فوق‌برنامه','education_extracurricular','educational_activities',['ثبت','ویرایش','حذف']),
('ارزیابی‌ها','education_evaluations','grade_items',['ثبت','ویرایش','حذف']),
('جشنواره خوارزمی','education_khwarizmi','competitions',['ثبت','ویرایش','حذف']),
('حضور و غیاب آموزشی','education_attendance','attendance',['ثبت','ویرایش','تازه‌سازی']),
],
'معاونت پرورشی': [
('اطلاع‌رسانی دبیران','staff_notifications','teacher_messages',['ارسال پیام به دبیر','ارسال به همه دبیران','مشاهده پیام‌های ارسالی']),
('داشبورد پرورشی','cultural_dashboard','cultural_activity_registrations',['ثبت','ویرایش','تازه‌سازی']),
('استعدادها','cultural_talents','cultural_activity_registrations',['ثبت','ویرایش','حذف']),
('جشنواره‌ها','cultural_festivals','competitions',['ثبت','ویرایش','حذف']),
('مسابقات','cultural_competitions','competitions',['ثبت','ویرایش','حذف']),
('گزارشات پرورشی','cultural_reports','cultural_reports',['ثبت','ویرایش','تازه‌سازی']),
('اردوها','cultural_trips','cultural_activity_registrations',['ثبت','ویرایش','حذف']),
('مراسم','cultural_ceremonies','cultural_activity_registrations',['ثبت','ویرایش','حذف']),
('قرآن','cultural_quran','cultural_activity_registrations',['ثبت','ویرایش','حذف']),
],
'مشاوره': [
('اطلاع‌رسانی دبیران','staff_notifications','teacher_messages',['ارسال به دبیر انتخابی','ارسال به کل دبیران','مشاهده پیام‌های ارسالی']),
('پنل مشاوره','advisor_dashboard','counseling_records',['ثبت پرونده','ویرایش','حذف','تازه‌سازی']),
('پرونده مشاوره','counseling_file','counseling_records',['ثبت پرونده','ویرایش','حذف','تازه‌سازی']),
('گزارش مشاوره','counseling_reports','counseling_records',['تولید گزارش','خروجی CSV']),
],
'دبیران': [
('خانه دبیر','teacher_home','teacher_classes',['تازه‌سازی']),
('اطلاع‌رسانی دبیران','teacher_notifications','teacher_messages',['مشاهده پیام‌ها','علامت‌گذاری به عنوان خوانده‌شده']),
('پروفایل دبیر','teacher_profile','teachers',['ویرایش','تازه‌سازی']),
('کلاس‌های من','teacher_classes','teacher_classes',['ثبت','ویرایش','حذف','تازه‌سازی']),
('نمرات','teacher_grades','grades',['ثبت','ویرایش','حذف','تازه‌سازی']),
('تکالیف','teacher_assignments','assignments',['ثبت','ویرایش','حذف','تازه‌سازی']),
('طرح درس','teacher_lesson_plan','lesson_plans',['ثبت','ویرایش','حذف','تازه‌سازی']),
('بانک سؤال دبیر','teacher_question_bank','quiz_questions',['ثبت سوال','ویرایش سوال','حذف سوال']),
('کلاس آنلاین دبیر','teacher_online_classes','online_classes',['ثبت','ویرایش','حذف','ورود به کلاس']),
('آزمون آنلاین دبیر','teacher_online_exams','online_quizzes',['ثبت','ویرایش','حذف']),
('حضور و غیاب دبیر','teacher_attendance','teacher_attendance',['ثبت','ویرایش','تازه‌سازی']),
('پیشرفت دانش‌آموز','teacher_student_progress','student_grades',['تازه‌سازی','گزارش']),
('انضباط','teacher_discipline','discipline_records',['ثبت','ویرایش','حذف']),
('جلسات','teacher_meetings','parent_meetings',['ثبت','ویرایش','حذف']),
('درخواست جلسات','teacher_meeting_requests','parent_meetings',['ثبت','تأیید','رد']),
('جلسات اولیا','teacher_parent_meetings','parent_meetings',['ثبت','ویرایش','حذف']),
('ارجاعات','teacher_referrals','educational_activities',['ثبت','ویرایش','حذف']),
('تقویم','teacher_calendar','weekly_schedule',['تازه‌سازی']),
('گزارش عملکرد دبیر','teacher_reports','teacher_activities',['تولید گزارش عملکرد دبیر']),
],
'دانش‌آموزان': [
('پنل دانش‌آموز','student_dashboard','students',['تازه‌سازی']),
('پروفایل','student_profile','students',['ویرایش','تازه‌سازی']),
('نمرات','student_grades','student_grades',['تازه‌سازی']),
('حضور و غیاب','student_attendance','attendance',['تازه‌سازی']),
('تکالیف','student_assignments','assignments',['تازه‌سازی']),
('پیام‌ها','student_messages','messages',['تازه‌سازی']),
('نمودار پیشرفت','student_charts','student_grades',['تازه‌سازی']),
('کلاس آنلاین','student_online_classes','online_classes',['ورود به کلاس']),
('خوارزمی','student_khwarizmi','competitions',['ثبت درخواست','تازه‌سازی']),
('مسابقات فرهنگی','student_cultural_competitions','competitions',['ثبت درخواست','تازه‌سازی']),
('ورزش مدرسه','student_school_sports','cultural_activity_registrations',['ثبت','تازه‌سازی']),
],
'اولیا': [
('پنل اولیا','parent_dashboard','parent_children',['تازه‌سازی']),
('فرزندان من','parent_children','parent_children',['اعمال انتخاب','افزودن فرزند','حذف فرزند','تازه‌سازی']),
('پروفایل فرزند','parent_child_profile','students',['تازه‌سازی']),
('وضعیت دانش‌آموز','parent_student_status','student_grades',['تازه‌سازی']),
('تحلیل دانش‌آموز','parent_student_analysis','student_grades',['تازه‌سازی']),
('گزارش ماهانه','parent_monthly_report','student_grades',['تازه‌سازی']),
('وضعیت زنده','parent_live_status','online_presence_checks',['تازه‌سازی']),
('جلسه با دبیر','parent_teacher_meeting','parent_meetings',['ثبت درخواست ملاقات','تازه‌سازی']),
('پیام‌های مدرسه','parent_school_messages','messages',['تازه‌سازی']),
('پرداخت‌ها','parent_payments','payment_records',['ثبت پرداخت/اعلام پرداخت','تازه‌سازی']),
('پیشنهادها','parent_suggestion','executive_requests',['ثبت','تازه‌سازی']),
],
'مالی': [
('پنل مالی','finance_dashboard','finance_transactions',['ثبت تراکنش','ویرایش','تازه‌سازی','گزارش مالی']),
('تراکنش‌ها','finance_transactions','finance_transactions',['ثبت','ویرایش','حذف','تازه‌سازی']),
('حساب‌ها','finance_accounts','finance_accounts',['ثبت','ویرایش','حذف']),
('کمک‌ها و درآمدها','finance_donations','finance_donations',['ثبت','ویرایش','حذف']),
('موارد مالی تکمیلی','finance_extra','finance_extra',['ثبت','ویرایش','حذف']),
('پرداخت‌های آنلاین','online_payments','payment_transactions',['اتصال به درگاه شاپرک']),
],
'کلاس و آزمون آنلاین': [
('کلاس‌های آنلاین','online_classes','online_classes',['ثبت','ویرایش','حذف','ورود به کلاس']),
('حضور آنلاین','online_attendance','online_attendance',['ثبت','تازه‌سازی']),
('آزمون‌های آنلاین','online_quizzes','online_quizzes',['ثبت','ویرایش','حذف']),
('سؤال‌های آزمون','quiz_questions','quiz_questions',['ثبت سوال','ویرایش سوال','حذف سوال']),
],
'تابلوی هوشمند': [
('محتوای تابلو','smart_board_content','smart_board_content',['ذخیره محتوا','ثبت فایل','ثبت رسانه','ثبت آزمون','ثبت فعالیت']),
('ابزارهای تعاملی','smart_board_tools','smart_board_interactive_tools',['ثبت ابزار تعاملی']),
('فعالیت‌های تابلو','smart_board_activities','smart_board_activities',['ثبت','ویرایش','حذف']),
('وایت‌بردها','smart_board_whiteboards','smart_board_whiteboards',['ثبت','ویرایش','حذف']),
],
'هوش مصنوعی': [
('پنل هوش مصنوعی','ai_dashboard','ai_assistant_sessions',['ایجاد جلسه','پرسش و پاسخ']),
('پرسش‌های هوش مصنوعی','ai_questions','ai_questions',['ثبت','حذف']),
('تحلیل آموزشی','ai_educational_analysis','ai_educational_analysis',['تولید تحلیل']),
('گزارش هوشمند','ai_smart_reports','ai_smart_reports',['تولید گزارش']),
],
'عمومی': [
('خانه','home','school_profile',['بازگشت به داشبورد']),
('حضور و غیاب','attendance','attendance',['ثبت','ویرایش','تازه‌سازی']),
('انضباط','discipline','discipline_records',['ثبت مورد انضباطی']),
('نظرسنجی‌ها','surveys','surveys',['شرکت در نظرسنجی انتخاب‌شده','مدیریت نظرسنجی']),
('گزارش‌های عمومی','common_reports','executive_reports',['تولید/به‌روزرسانی گزارش','خروجی CSV']),
('اطلاعیه‌ها','notice_board','messages',['ثبت و انتشار','حذف اطلاعیه انتخاب‌شده']),
('کارکنان','staff','staff',['ثبت','ویرایش','حذف','تازه‌سازی']),
],
}

TABLES=set()
for items in GROUPS.values():
    for _,_,t,_ in items: TABLES.add(t)

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def hashpw(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()


def ensure_schema():
    c=db(); cur=c.cursor()
    # افزونه‌های پیام‌رسانی و گیرندگان؛ همه گیرندگان به صورت رکورد مستقل ذخیره می‌شوند.
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_user_id INTEGER,
        sender_name TEXT,
        title TEXT NOT NULL DEFAULT '',
        body TEXT NOT NULL DEFAULT '',
        audience_type TEXT NOT NULL DEFAULT 'teacher_selected',
        audience_value TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS message_targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER NOT NULL,
        target_role TEXT NOT NULL DEFAULT '',
        target_id INTEGER,
        read_at TEXT,
        FOREIGN KEY(message_id) REFERENCES messages(id) ON DELETE CASCADE
    )""")
    # سازگاری با نسخه‌ای که قبلاً target_type/target_value داشت
    mt_cols={r[1] for r in cur.execute("PRAGMA table_info(message_targets)").fetchall()}
    if 'target_role' not in mt_cols:
        cur.execute("ALTER TABLE message_targets ADD COLUMN target_role TEXT NOT NULL DEFAULT ''")
    if 'target_id' not in mt_cols:
        cur.execute("ALTER TABLE message_targets ADD COLUMN target_id INTEGER")
    if 'read_at' not in mt_cols:
        cur.execute("ALTER TABLE message_targets ADD COLUMN read_at TEXT")
    mt_cols={r[1] for r in cur.execute("PRAGMA table_info(message_targets)").fetchall()}
    if 'target_type' in mt_cols:
        cur.execute("UPDATE message_targets SET target_role=target_type WHERE COALESCE(target_role,'')=''")
    if 'target_value' in mt_cols:
        cur.execute("UPDATE message_targets SET target_id=CAST(target_value AS INTEGER) WHERE target_id IS NULL AND target_value GLOB '[0-9]*'")
    # سازگاری با جدول messages نسخه‌های قدیمی (sender/receiver/text)
    msg_cols={r[1] for r in cur.execute("PRAGMA table_info(messages)").fetchall()}
    msg_add={
        'sender_user_id':'INTEGER','sender_name':'TEXT','title':'TEXT NOT NULL DEFAULT ''','body':'TEXT NOT NULL DEFAULT ''',
        "audience_type":"TEXT NOT NULL DEFAULT 'teacher_selected'","audience_value":"TEXT DEFAULT ''"
    }
    for name,typ in msg_add.items():
        if name not in msg_cols:
            cur.execute(f"ALTER TABLE messages ADD COLUMN {name} {typ}")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_message_targets_role_id ON message_targets(target_role,target_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_message_targets_message ON message_targets(message_id)")
    # فیلدهای تکمیلی دانش‌آموزان و کارکنان در نسخه‌های قبلی ممکن است وجود نداشته باشند.
    def add_cols(table, cols):
        existing={r['name'] for r in cur.execute(f'PRAGMA table_info("{table}")').fetchall()}
        for name, typ in cols:
            if name not in existing:
                cur.execute(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {typ}')
    add_cols('students',[('nationality','TEXT'),('religion','TEXT'),('sect','TEXT')])
    add_cols('staff',[('work_experience','TEXT'),('employee_code','TEXT'),('national_code','TEXT'),('religion','TEXT'),('sect','TEXT'),('children_count','INTEGER'),('employment_status','TEXT'),('teaching_hours','REAL')])
    add_cols('weekly_schedule',[('teacher_id','INTEGER'),('teacher','TEXT'),('hours','REAL'),('weekdays','TEXT')])
    add_cols('counseling_records',[('student_name','TEXT'),('visit_reason','TEXT'),('recommendations','TEXT'),('next_visit','TEXT'),('reason_summary','TEXT')])
    # پیکربندی واقعی ظرفیت کلاس‌های مدرسه؛ مبنای برنامه‌ریزی هفتگی
    cur.execute('''CREATE TABLE IF NOT EXISTS school_class_config (
        id INTEGER PRIMARY KEY CHECK(id=1),
        total_classes INTEGER NOT NULL DEFAULT 0,
        grade7_classes INTEGER NOT NULL DEFAULT 0,
        grade8_classes INTEGER NOT NULL DEFAULT 0,
        grade9_classes INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute('INSERT OR IGNORE INTO school_class_config(id,total_classes,grade7_classes,grade8_classes,grade9_classes) VALUES(1,9,3,3,3)')
    c.commit(); c.close()

ensure_schema()

def ensure_admin():
    c=db(); cur=c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, permissions TEXT, linked_student_id INTEGER, linked_teacher_id INTEGER, linked_staff_id INTEGER, display_name TEXT DEFAULT '')")
    row=cur.execute("SELECT * FROM users WHERE username=?",('0053409531',)).fetchone()
    if row is None:
        old=cur.execute("SELECT * FROM users WHERE username='admin'").fetchone()
        if old:
            cur.execute("UPDATE users SET username=?,password=?,role='manager',permissions='all',display_name=? WHERE id=?",('0053409531',hashpw('h0053409531'),old['display_name'] or 'مدیر دبیرستان',old['id']))
        else:
            cur.execute("INSERT INTO users(username,password,role,permissions,display_name) VALUES(?,?,?,?,?)",('0053409531',hashpw('h0053409531'),'manager','all','مدیر دبیرستان'))
    else:
        cur.execute("UPDATE users SET password=?,role='manager',permissions='all' WHERE username=?",(hashpw('h0053409531'),'0053409531'))
    c.commit(); c.close()
ensure_admin()

def ensure_web_schema():
    """افزونه‌های داده‌ای موردنیاز نسخه وب؛ بدون حذف داده‌های موجود."""
    c=db(); cur=c.cursor()
    additions={
        "students": [("nationality", "TEXT DEFAULT \"ایرانی\""), ("religion", "TEXT DEFAULT \"\""), ("sect", "TEXT DEFAULT \"\"")],
        "staff": [("work_experience", "TEXT DEFAULT \"\""), ("employee_code", "TEXT DEFAULT \"\""), ("national_code", "TEXT DEFAULT \"\""), ("religion", "TEXT DEFAULT \"\""), ("sect", "TEXT DEFAULT \"\""), ("children_count", "INTEGER DEFAULT 0"), ("employment_status", "TEXT DEFAULT \"موظف\""), ("teaching_hours", "REAL DEFAULT 0")],
        "weekly_schedule": [("teacher_id", "INTEGER"), ("weekdays", "TEXT DEFAULT \"\"")],
    }
    for table, cols in additions.items():
        existing={r["name"] for r in cur.execute(f"PRAGMA table_info(\"{table}\")").fetchall()}
        for name, decl in cols:
            if name not in existing:
                cur.execute(f"ALTER TABLE \"{table}\" ADD COLUMN \"{name}\" {decl}")
    cur.execute("""CREATE TABLE IF NOT EXISTS counseling_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL DEFAULT '',
        visit_reason TEXT NOT NULL DEFAULT '',
        recommendations TEXT DEFAULT '',
        next_visit TEXT DEFAULT '',
        reason_summary TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.commit(); c.close()

ensure_web_schema()

def safe_back_url(default='/dashboard'):
    ref=request.referrer or ''
    return ref if ref.startswith('/') else default

def login_required(f):
    @wraps(f)
    def w(*a,**kw):
        if 'user_id' not in session: return redirect(url_for('login'))
        return f(*a,**kw)
    return w

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username','').strip(); p=request.form.get('password','')
        c=db(); row=c.execute('SELECT * FROM users WHERE username=?',(u,)).fetchone(); c.close()
        ok=row and (row['password']==hashpw(p) or (u=='0053409531' and p=='h0053409531'))
        if ok:
            session['user_id']=row['id']; session['username']=u; session['role']=row['role']; session['display_name']=row['display_name'] or 'کاربر'; return redirect(url_for('dashboard'))
        flash('نام کاربری یا رمز عبور اشتباه است.','error')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html',groups=GROUPS)

@app.route('/modules/<group>')
@login_required
def group_page(group):
    if group not in GROUPS: return 'گروه یافت نشد',404
    return render_template('group.html',group=group,items=GROUPS[group],back_url=safe_back_url(url_for('dashboard')))



@app.route('/module/school_messages', methods=['GET','POST'])
@login_required
def school_messages():
    c=db()
    try:
        role=session.get('role','')
        can_send=role in ('manager','admin','executive','educational','cultural','principal','deputy')
        if request.method=='POST' and can_send:
            title=request.form.get('title','').strip(); body=request.form.get('body','').strip(); audience=request.form.get('audience','student_selected'); value=request.form.get('audience_value','').strip()
            if not title or not body:
                flash('عنوان و متن پیام الزامی است.','error')
            else:
                targets=[]
                if audience=='student_selected':
                    sid=value
                    if sid.isdigit(): targets=[('student',int(sid))]
                elif audience=='student_class':
                    targets=[('student',r['id']) for r in c.execute('SELECT id FROM students WHERE class_name=?',(value,)).fetchall()]
                elif audience=='student_grade':
                    targets=[('student',r['id']) for r in c.execute('SELECT id FROM students WHERE grade=?',(value,)).fetchall()]
                elif audience=='student_all':
                    targets=[('student',r['id']) for r in c.execute('SELECT id FROM students').fetchall()]
                elif audience=='parent_student':
                    if value.isdigit():
                        targets=[('parent',r['id']) for r in c.execute("SELECT id FROM users WHERE (role='parent' OR role='ولی' OR role='guardian') AND linked_student_id=?",(int(value),)).fetchall()]
                elif audience in ('parent_selected','parent_class','parent_grade','parent_all'):
                    if audience=='parent_selected':
                        if value.isdigit(): targets=[('parent',int(value))]
                    else:
                        students=[]
                        if audience=='parent_class': students=c.execute('SELECT id FROM students WHERE class_name=?',(value,)).fetchall()
                        elif audience=='parent_grade': students=c.execute('SELECT id FROM students WHERE grade=?',(value,)).fetchall()
                        else: students=c.execute('SELECT id FROM students').fetchall()
                        ids=[r['id'] for r in students]
                        if ids:
                            marks=','.join('?'*len(ids)); params=tuple(ids)
                            targets=[('parent',r['id']) for r in c.execute(f"SELECT id FROM users WHERE (role='parent' OR role='ولی' OR role='guardian') AND linked_student_id IN ({marks})",params).fetchall()]
                # unique recipients
                targets=list(dict.fromkeys(targets))
                if not targets:
                    flash('برای این مخاطب، گیرنده‌ای پیدا نشد.','error')
                else:
                    cur=c.execute("INSERT INTO messages(sender_user_id,sender_name,title,body,audience_type,audience_value) VALUES(?,?,?,?,?,?)",
                                  (session.get('user_id'),session.get('display_name',''),title,body,audience,value))
                    mid=cur.lastrowid
                    c.executemany("INSERT INTO message_targets(message_id,target_role,target_id) VALUES(?,?,?)",[(r,tid) for r,tid in targets])
                    c.commit(); flash(f'پیام برای {len(targets)} گیرنده ارسال شد.','success')
        students=[dict(r) for r in c.execute('SELECT id,first_name,last_name,grade,class_name FROM students ORDER BY last_name,first_name').fetchall()]
        classes=[r['class_name'] for r in c.execute("SELECT DISTINCT class_name FROM students WHERE class_name IS NOT NULL AND TRIM(class_name)<>'' ORDER BY class_name").fetchall()]
        grades=[r['grade'] for r in c.execute("SELECT DISTINCT grade FROM students WHERE grade IS NOT NULL AND TRIM(grade)<>'' ORDER BY grade").fetchall()]
        parents=[dict(r) for r in c.execute("SELECT id,display_name,linked_student_id FROM users WHERE role IN ('parent','ولی','guardian') ORDER BY display_name").fetchall()]
        sent=[dict(r) for r in c.execute("""SELECT m.*,COUNT(mt.id) recipients,SUM(CASE WHEN mt.read_at IS NOT NULL THEN 1 ELSE 0 END) read_count
             FROM messages m LEFT JOIN message_targets mt ON mt.message_id=m.id
             WHERE m.audience_type LIKE 'student_%' OR m.audience_type LIKE 'parent_%'
             GROUP BY m.id ORDER BY m.id DESC LIMIT 100""").fetchall()]
        return render_template('school_messages.html',title='اطلاع‌رسانی دانش‌آموزان و اولیا',group='مدیریت مدرسه',can_send=can_send,students=students,parents=parents,classes=classes,grades=grades,sent=sent,
                               back_url=safe_back_url(url_for('group_page',group='مدیریت مدرسه')))
    finally: c.close()

@app.route('/module/student_messages', methods=['GET','POST'])
@login_required
def student_messages():
    c=db()
    try:
        u=c.execute('SELECT * FROM users WHERE id=?',(session.get('user_id'),)).fetchone()
        sid=u['linked_student_id'] if u else None
        rows=[]
        if sid:
            rows=[dict(r) for r in c.execute("SELECT m.*,mt.read_at FROM message_targets mt JOIN messages m ON m.id=mt.message_id WHERE mt.target_role='student' AND mt.target_id=? ORDER BY m.id DESC",(sid,)).fetchall()]
        return render_template('inbox.html',title='پیام‌های دانش‌آموز',rows=rows,back_url=safe_back_url(url_for('group_page',group='دانش‌آموزان')))
    finally: c.close()

@app.route('/module/parent_school_messages', methods=['GET','POST'])
@login_required
def parent_school_messages():
    c=db()
    try:
        uid=session.get('user_id')
        rows=[dict(r) for r in c.execute("SELECT m.*,mt.read_at FROM message_targets mt JOIN messages m ON m.id=mt.message_id WHERE mt.target_role='parent' AND mt.target_id=? ORDER BY m.id DESC",(uid,)).fetchall()]
        return render_template('inbox.html',title='پیام‌های مدرسه',rows=rows,back_url=safe_back_url(url_for('group_page',group='اولیا')))
    finally: c.close()

@app.route('/module/teacher_notifications', methods=['GET','POST'])
@login_required
def teacher_notifications():
    c=db()
    try:
        role=session.get('role','')
        sender_roles=('manager','admin','executive','educational','cultural','principal','deputy','counselor','مشاور','معاون','مدیر')
        can_send=role in sender_roles
        if request.method=='POST' and can_send:
            title=request.form.get('title','').strip(); body=request.form.get('body','').strip()
            audience=request.form.get('audience','teacher_selected')
            selected=[int(x) for x in request.form.getlist('teacher_ids') if x.isdigit()]
            if not title or not body:
                flash('عنوان و متن پیام الزامی است.','error')
            else:
                # دبیران از «کارکنان مدرسه» می‌آیند؛ فقط نقش‌های آموزشی قابل انتخاب‌اند.
                teacher_rows=c.execute("""SELECT id FROM staff
                    WHERE role LIKE '%دبیر%' OR role LIKE '%معلم%' OR role='teacher' OR role='مدرس'""").fetchall()
                if audience=='teacher_all':
                    selected=[r['id'] for r in teacher_rows]
                    if not selected:
                        flash('هیچ دبیری در کارکنان مدرسه ثبت نشده است. ابتدا دبیران را در بخش کارکنان مدرسه ثبت کنید.','error')
                if not selected:
                    if audience=='teacher_selected':
                        flash('حداقل یک دبیر را انتخاب کنید یا «کل دبیران» را بزنید.','error')
                else:
                    cur=c.execute("""INSERT INTO messages
                        (sender_user_id,sender_name,title,body,audience_type,audience_value)
                        VALUES(?,?,?,?,?,?)""",
                        (session.get('user_id'),session.get('display_name',''),title,body,audience,','.join(map(str,selected))))
                    mid=cur.lastrowid
                    c.executemany("INSERT INTO message_targets(message_id,target_role,target_id) VALUES(?,?,?)",
                                  [(mid,'teacher',tid) for tid in selected])
                    c.commit(); flash(f'پیام برای {len(selected)} دبیر ارسال شد.','success')

        # انتخاب دبیر مستقیماً از کارکنان مدرسه
        teachers=[dict(r) for r in c.execute("""SELECT id,first_name,last_name,employee_code,national_code
            FROM staff WHERE role LIKE '%دبیر%' OR role LIKE '%معلم%' OR role='teacher' OR role='مدرس'
            ORDER BY last_name,first_name""").fetchall()]
        sent=[]
        if can_send:
            sent=[dict(r) for r in c.execute("""SELECT m.*, COUNT(mt.id) recipients,
                SUM(CASE WHEN mt.read_at IS NOT NULL THEN 1 ELSE 0 END) read_count
                FROM messages m LEFT JOIN message_targets mt ON mt.message_id=m.id
                WHERE m.audience_type IN ('teacher_selected','teacher_all')
                GROUP BY m.id ORDER BY m.id DESC LIMIT 100""").fetchall()]

        inbox=[]
        if role in ('teacher','دبیر'):
            # حساب دبیر می‌تواند به رکورد staff یا teachers متصل باشد؛ هر دو حالت پشتیبانی می‌شود.
            u=c.execute('SELECT linked_teacher_id,linked_staff_id FROM users WHERE id=?',(session.get('user_id'),)).fetchone()
            ids=[]
            if u:
                if u['linked_teacher_id'] is not None: ids.append(int(u['linked_teacher_id']))
                if u['linked_staff_id'] is not None: ids.append(int(u['linked_staff_id']))
            if ids:
                marks=','.join('?'*len(ids))
                inbox=[dict(r) for r in c.execute(f"""SELECT m.*,mt.id target_row_id,mt.read_at
                    FROM message_targets mt JOIN messages m ON m.id=mt.message_id
                    WHERE mt.target_role='teacher' AND mt.target_id IN ({marks})
                    ORDER BY m.id DESC LIMIT 100""",tuple(ids)).fetchall()]

        return render_template('teacher_notifications.html',title='اطلاع‌رسانی دبیران',group='دبیران',teachers=teachers,sent=sent,inbox=inbox,
            can_send=can_send,back_url=safe_back_url(url_for('group_page',group='دبیران')))
    finally:
        c.close()

@app.post('/module/teacher_notifications/read/<int:target_id>')
@login_required
def teacher_notification_read(target_id):
    c=db()
    try:
        role=session.get('role','')
        if role not in ('teacher','دبیر'):
            return redirect(url_for('teacher_notifications'))
        u=c.execute('SELECT linked_teacher_id,linked_staff_id FROM users WHERE id=?',(session.get('user_id'),)).fetchone()
        ids=[]
        if u:
            if u['linked_teacher_id'] is not None: ids.append(int(u['linked_teacher_id']))
            if u['linked_staff_id'] is not None: ids.append(int(u['linked_staff_id']))
        if ids:
            marks=','.join('?'*len(ids))
            c.execute(f"UPDATE message_targets SET read_at=CURRENT_TIMESTAMP WHERE id=? AND target_role='teacher' AND target_id IN ({marks})",(target_id,*ids))
            c.commit()
        return redirect(safe_back_url(url_for('teacher_notifications')))
    finally:
        c.close()

@app.route('/module/staff_notifications', methods=['GET','POST'])
@login_required
def staff_notifications():
    return teacher_notifications()

@app.route('/module/<slug>',methods=['GET','POST'])
@login_required
def module(slug):
    """Safe generic Web renderer for every registered mother module.
    The previous version could raise a 500 while rendering a valid SQLite table.
    This route deliberately isolates DB/rendering errors so a module always opens.
    """
    found=None; group=None
    for g,items in GROUPS.items():
        for item in items:
            if item[1]==slug:
                found=item; group=g; break
        if found: break
    if not found:
        return 'ماژول یافت نشد',404

    title,_,table,actions=found

    # برنامه‌ریزی مدرسه: فرم تخصصی با انتخاب دبیر، ساعات کشویی و روزهای چندانتخابی
    if slug == 'school_planning':
        c=None
        try:
            c=db()
            class_config=dict(c.execute('SELECT * FROM school_class_config WHERE id=1').fetchone())
            if request.method=='POST':
                action=request.form.get('_action','')
                if action=='save_class_config':
                    total=int(request.form.get('total_classes') or 0)
                    g7=int(request.form.get('grade7_classes') or 0)
                    g8=int(request.form.get('grade8_classes') or 0)
                    g9=int(request.form.get('grade9_classes') or 0)
                    if min(total,g7,g8,g9) < 0:
                        flash('تعداد کلاس‌ها نمی‌تواند منفی باشد.','error')
                    elif total != g7+g8+g9:
                        flash('تعداد کل کلاس‌های مدرسه باید دقیقاً برابر مجموع کلاس‌های پایه‌های هفتم، هشتم و نهم باشد.','error')
                    else:
                        c.execute('''UPDATE school_class_config SET total_classes=?,grade7_classes=?,grade8_classes=?,grade9_classes=?,updated_at=CURRENT_TIMESTAMP WHERE id=1''',(total,g7,g8,g9))
                        c.commit(); flash('تعداد کلاس‌های مدرسه با موفقیت ثبت شد و مبنای برنامه‌ریزی قرار گرفت.','success')
                elif action=='delete':
                    rid=request.form.get('id','').strip()
                    if rid: c.execute('DELETE FROM weekly_schedule WHERE id=?',(rid,)); c.commit(); flash('ردیف برنامه حذف شد.','success')
                elif action=='save':
                    teacher_id=request.form.get('teacher_id','').strip()
                    teacher_row=c.execute('SELECT id, first_name, last_name FROM staff WHERE id=?',(teacher_id,)).fetchone() if teacher_id else None
                    teacher_name=((teacher_row['first_name'] or '')+' '+(teacher_row['last_name'] or '')).strip() if teacher_row else ''
                    weekdays=request.form.getlist('weekdays')
                    hours=request.form.get('hours','').strip()
                    if teacher_name and weekdays and hours:
                        selected_grade=request.form.get('grade','').strip()
                        grade_limits={'هفتم':int(class_config.get('grade7_classes') or 0),'هشتم':int(class_config.get('grade8_classes') or 0),'نهم':int(class_config.get('grade9_classes') or 0)}
                        requested_classes=int(request.form.get('class_count') or 1)
                        if selected_grade in grade_limits and grade_limits[selected_grade] > 0 and requested_classes > grade_limits[selected_grade]:
                            flash(f'تعداد کلاس انتخاب‌شده برای پایه {selected_grade} از ظرفیت ثبت‌شده مدرسه بیشتر است.','error')
                        else:
                            c.execute('''INSERT INTO weekly_schedule(teacher_id,teacher,hours,grade,class_count,subject,bell_pattern,class_names,weekdays) VALUES(?,?,?,?,?,?,?,?,?)''',
                                      (teacher_id,teacher_name,float(hours),selected_grade,requested_classes,request.form.get('subject',''),request.form.get('bell_pattern',''),request.form.get('class_names',''),'،'.join(weekdays)))
                            c.commit(); flash('برنامه دبیر با روزهای انتخاب‌شده ثبت شد.','success')
                    else:
                        flash('دبیر، ساعات و حداقل یک روز کاری را انتخاب کنید.','error')
            teachers=[dict(r) for r in c.execute('SELECT id,first_name,last_name,national_code FROM staff ORDER BY last_name,first_name').fetchall()]
            rows=[dict(r) for r in c.execute('SELECT * FROM weekly_schedule ORDER BY id DESC').fetchall()]
            layout=[]
            day_order=['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه']
            for day in day_order:
                day_rows=[]
                for r in rows:
                    if day in (r.get('weekdays') or '').replace('،',',').split(','):
                        rr=dict(r); rr['day']=day; day_rows.append(rr)
                layout.append((day,day_rows))
            return render_template('weekly_schedule.html',title=title,group=group,rows=rows,teachers=teachers,layout=layout,actions=actions,class_config=class_config,back_url=safe_back_url(url_for('group_page',group=group)))
        except Exception as exc:
            if c:
                try:c.rollback()
                except:pass
            return render_template('error.html',message='خطای برنامه‌ریزی مدرسه',detail=str(exc)),500
        finally:
            if c:
                try:c.close()
                except:pass

    # مدیریت دانش‌آموزان: فیلدهای هویتی تکمیلی
    if slug == 'executive_students':
        c=None
        try:
            c=db()
            if request.method=='POST':
                action=request.form.get('_action','')
                if action=='delete':
                    rid=request.form.get('id','').strip()
                    if rid: c.execute('DELETE FROM students WHERE id=?',(rid,)); c.commit(); flash('دانش‌آموز حذف شد.','success')
                elif action=='save':
                    fields=['first_name','last_name','national_code','student_code','grade','class_name','phone','parent_phone','father_name','mother_name','birth_date','email','address','nationality','religion','sect','description']
                    vals=[request.form.get(x,'') for x in fields]
                    c.execute('INSERT INTO students('+','.join(fields)+') VALUES('+','.join('?' for _ in fields)+')',vals); c.commit(); flash('اطلاعات دانش‌آموز ثبت شد.','success')
            rows=[dict(r) for r in c.execute('SELECT * FROM students ORDER BY id DESC LIMIT 100').fetchall()]
            return render_template('students_module.html',title=title,group=group,rows=rows,back_url=safe_back_url(url_for('group_page',group=group)))
        except Exception as exc:
            if c:
                try:c.rollback()
                except:pass
            return render_template('error.html',message='خطای مدیریت دانش‌آموزان',detail=str(exc)),500
        finally:
            if c:
                try:c.close()
                except:pass

    # کارکنان مدرسه: اطلاعات پرسنلی کامل و وضعیت استخدام کشویی
    if slug == 'executive_staff':
        c=None
        try:
            c=db()
            if request.method=='POST':
                action=request.form.get('_action','')
                if action=='delete':
                    rid=request.form.get('id','').strip()
                    if rid: c.execute('DELETE FROM staff WHERE id=?',(rid,)); c.commit(); flash('کارمند حذف شد.','success')
                elif action=='save':
                    fields=['first_name','last_name','role','national_code','employee_code','phone','work_experience','religion','sect','children_count','employment_status','teaching_hours','description']
                    vals=[request.form.get(x,'') for x in fields]
                    c.execute('INSERT INTO staff('+','.join(fields)+') VALUES('+','.join('?' for _ in fields)+')',vals); c.commit(); flash('اطلاعات کارکنان ثبت شد.','success')
            rows=[dict(r) for r in c.execute('SELECT * FROM staff ORDER BY id DESC LIMIT 100').fetchall()]
            return render_template('staff_module.html',title=title,group=group,rows=rows,back_url=safe_back_url(url_for('group_page',group=group)))
        except Exception as exc:
            if c:
                try:c.rollback()
                except:pass
            return render_template('error.html',message='خطای کارکنان مدرسه',detail=str(exc)),500
        finally:
            if c:
                try:c.close()
                except:pass

    # پرونده مشاوره: پیگیری‌های قدیمی عمداً از رابط حذف شده‌اند.
    if slug in ('advisor_dashboard','counseling_file','counseling_reports'):
        c=None
        try:
            c=db()
            if request.method=='POST':
                action=request.form.get('_action','')
                if action=='delete':
                    rid=request.form.get('id','').strip()
                    if rid: c.execute('DELETE FROM counseling_records WHERE id=?',(rid,)); c.commit(); flash('پرونده مشاوره حذف شد.','success')
                elif action=='save':
                    fields=['student_name','visit_reason','recommendations','next_visit','reason_summary']
                    vals=[request.form.get(x,'') for x in fields]
                    if request.form.get('student_name','').strip():
                        c.execute('INSERT INTO counseling_records('+','.join(fields)+') VALUES('+','.join('?' for _ in fields)+')',vals); c.commit(); flash('پرونده مشاوره ثبت شد.','success')
            rows=[dict(r) for r in c.execute('SELECT * FROM counseling_records ORDER BY id DESC LIMIT 100').fetchall()]
            return render_template('counseling_module.html',title=title,group=group,rows=rows,back_url=safe_back_url(url_for('group_page',group=group)))
        except Exception as exc:
            if c:
                try:c.rollback()
                except:pass
            return render_template('error.html',message='خطای پرونده مشاوره',detail=str(exc)),500
        finally:
            if c:
                try:c.close()
                except:pass

    cols=[]; rows=[]; exists=False; db_error=''
    c=None
    try:
        c=db()
        exists=c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone() is not None
        if exists:
            # PRAGMA is safe with quoted identifiers and works for all 95 mother tables.
            info=c.execute('PRAGMA table_info("%s")' % table.replace('"','""')).fetchall()
            cols=[str(r['name']) for r in info if r['name']]

            if request.method=='POST':
                action=request.form.get('_action','')
                if action=='delete' and 'id' in cols:
                    rid=request.form.get('id','').strip()
                    if rid:
                        c.execute('DELETE FROM "%s" WHERE id=?' % table.replace('"','""'),(rid,)); c.commit()
                        flash('رکورد حذف شد.','success')
                elif action=='save':
                    names=[col for col in cols if col!='id' and col in request.form]
                    vals=[request.form.get(col,'') for col in names]
                    if names:
                        q=','.join('"%s"' % n.replace('"','""') for n in names)
                        ph=','.join('?' for _ in names)
                        c.execute('INSERT INTO "%s" (%s) VALUES (%s)' % (table.replace('"','""'),q,ph),vals)
                        c.commit(); flash('رکورد ثبت شد.','success')

            qtable='"%s"' % table.replace('"','""')
            if 'id' in cols:
                cur=c.execute('SELECT * FROM %s ORDER BY id DESC LIMIT 100' % qtable)
            else:
                cur=c.execute('SELECT * FROM %s LIMIT 100' % qtable)
            # Convert sqlite.Row to plain dictionaries before Jinja rendering.
            rows=[dict(r) for r in cur.fetchall()]
    except Exception as exc:
        if c:
            try: c.rollback()
            except Exception: pass
        db_error=f'{type(exc).__name__}: {exc}'
    finally:
        if c:
            try: c.close()
            except Exception: pass

    return render_template('module.html',title=title,group=group,table=table,actions=actions,
                           cols=cols,rows=rows,exists=exists,db_error=db_error,back_url=safe_back_url(url_for('group_page', group=group)))

@app.errorhandler(500)
def internal_error(error):
    # Keep the Web usable instead of exposing Flask's generic 500 page.
    return render_template('error.html', message='خطای داخلی در اجرای این بخش رخ داد.', detail=str(error)), 500

@app.route('/management')
@login_required
def management(): return redirect(url_for('group_page',group='مدیریت مدرسه'))

if __name__=='__main__':
    app.run(host='127.0.0.1',port=5000,debug=False)
