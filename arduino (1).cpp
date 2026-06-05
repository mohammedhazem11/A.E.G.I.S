// --- SPHINX CYBER DYNAMICS - Updated Hardware Alert System ---

// 1. تعريف المنافذ حسب توصيلك الجديد بالظبط
int buzzerPin = 10;  // البازر
int red1 = 11;       // اللمبة الحمراء الأولى
int greenPin = 12;   // اللمبة الخضراء الأولى
int red2 = 13;       // اللمبة الحمراء التانية

// --- المنافذ الجديدة اللي إنت ضفتها ---
int green2 = 9;      // اللمبة الخضراء التانية
int red3 = 8;        // اللمبة الحمراء التالتة
int green3 = 7;      // اللمبة الخضراء التالتة

// متغير جديد بيحفظ حالة السيستم (شغال إنذار ولا لأ)
bool alarmActive = false; 

void setup() {
  Serial.begin(9600); 
  
  // إعداد كل المنافذ كمخرجات
  pinMode(buzzerPin, OUTPUT);
  pinMode(red1, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(red2, OUTPUT);
  pinMode(green2, OUTPUT);
  pinMode(red3, OUTPUT);
  pinMode(green3, OUTPUT);
  
  // --- الوضع الآمن (Safe Mode) أول ما السيستم يفتح ---
  digitalWrite(greenPin, HIGH); // الخضراء الأولى منورة
  digitalWrite(green2, HIGH);   // الخضراء التانية منورة
  digitalWrite(green3, HIGH);   // الخضراء التالتة منورة
  
  digitalWrite(red1, LOW);      // الحمراء الأولى مطفية
  digitalWrite(red2, LOW);      // الحمراء التانية مطفية
  digitalWrite(red3, LOW);      // الحمراء التالتة مطفية
  
  digitalWrite(buzzerPin, LOW); // البازر ساكت
}

void loop() {
  // 1. استقبال الأوامر من البايثون
  if (Serial.available() > 0) {
    char command = Serial.read(); 
    
    // لو البايثون بعت إشارة اختراق (حرف R)
    if (command == 'R') {
      alarmActive = true;            // فعل حالة الإنذار
      digitalWrite(greenPin, LOW);   // اطفي اللمبة الخضراء الأولى فوراً
      digitalWrite(green2, LOW);     // اطفي الخضراء التانية فوراً
      digitalWrite(green3, LOW);     // اطفي الخضراء التالتة فوراً
    }
    
    // لو البايثون بعت إشارة إيقاف (حرف S)
    else if (command == 'S') {
      alarmActive = false;           // وقف حالة الإنذار
      
      // --- الرجوع للوضع الآمن ---
      digitalWrite(red1, LOW);       // اطفي الحمراء الأولى
      digitalWrite(red2, LOW);       // اطفي الحمراء التانية
      digitalWrite(red3, LOW);       // اطفي الحمراء التالتة
      digitalWrite(buzzerPin, LOW);  // اطفي البازر
      
      digitalWrite(greenPin, HIGH);  // ارجع نور الخضراء الأولى تاني
      digitalWrite(green2, HIGH);    // ارجع نور الخضراء التانية تاني
      digitalWrite(green3, HIGH);    // ارجع نور الخضراء التالتة تاني
    }
  }

  // 2. تشغيل تأثير سارينة الإسعاف والفلاشر (طول ما حالة الإنذار شغالة)
  if (alarmActive == true) {
    digitalWrite(red1, HIGH);      // نور الحمراء الأولى
    digitalWrite(red3, HIGH);      // نور الحمراء التالتة (عشان الفلاشر)
    digitalWrite(red2, LOW);       // اطفي الحمراء التانية
    digitalWrite(buzzerPin, HIGH); // شغل البازر
    delay(250);                    // سرعة الفلاشر (ربع ثانية)
    
    digitalWrite(red1, LOW);       // اطفي الحمراء الأولى
    digitalWrite(red3, LOW);       // اطفي الحمراء التالتة
    digitalWrite(red2, HIGH);      // نور الحمراء التانية
    digitalWrite(buzzerPin, LOW);  // اطفي البازر (عشان يعمل تقطيع في الصوت)
    delay(250);                    // سرعة الفلاشر (ربع ثانية)
  }
}