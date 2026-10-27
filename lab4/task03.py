"""
Task 3 - From the product owner's message to CRC cards      (QOG'OZDA - faqat javoblar, kod yo'q)

3.1  Fe'llar: books (band qiladi), works (ishlaydi), moved (ko'chiriladi), charged (undiriladi),
     confirms (tasdiqlaydi), sends (yuboradi).
     Otlar guruhlari:
       Class ............ Patient, Dentist, Procedure, Appointment, ReminderService
       Attribute ........ Procedure: name, duration, price | Dentist: working hours, treatment room |
                          Patient: name, phone (SMS uchun) | Appointment: start time, status |
                          qoida konstantalari: "24 hours", "50 000 sum" (jarima)
       Actor ............ Receptionist (tizimdan tashqarida turib "confirm" ni bosadi), Patient (tizimdan foydalanadi)
       Event with data .. Appointment (bemor + shifokor + muolaja + vaqt), SMS reminder (kimga, qachon, qaysi matn),
                          "fee" - Appointment'ning ko'chirish qoidasi natijasi
       Vague (so'rash kerak):
                          "system" (aynan qaysi modul?), "evening before" (soat nechada? qaysi vaqt zonasida?),
                          "working hours" (har kun bir xilmi? tanaffus bormi?), "moved" (kim ko'chiradi? boshqa
                          shifokorga ham mumkinmi?), "treatment room" (xonani bir necha shifokor ulashadimi?),
                          "confirms" (tasdiqlanmasa nima bo'ladi?)

3.2  CRC kartalar (har birida <= 4 mas'uliyat):

     +--------------------------------------------------------------+
     | Patient                                                      |
     |  1. Ism va telefon raqamini biladi                           |
     |  2. SMS uchun telefon raqamini beradi                        |
     |  Collaborators: Appointment                                  |
     +--------------------------------------------------------------+
     | Procedure                                                    |
     |  1. Nomi, davomiyligi va narxini biladi                      |
     |  2. O'z qoidalarini himoya qiladi (duration > 0, price >= 0) |
     |  Collaborators: Appointment                                  |
     +--------------------------------------------------------------+
     | Dentist                                                      |
     |  1. Xonasi va ish vaqtini biladi                             |
     |  2. Slot ish vaqtiga tushishini tekshiradi                   |
     |  3. O'zining barcha appointment'larini saqlaydi              |
     |  4. Yangi slot band vaqt bilan kesishsa rad etadi            |
     |  Collaborators: Appointment, Procedure (davomiylik)          |
     +--------------------------------------------------------------+
     | Appointment                                                  |
     |  1. Patient, Dentist, Procedure, boshlanish vaqti, statusni  |
     |     biladi                                                   |
     |  2. Ko'chirish jarimasini hisoblaydi (24 soatgacha bepul,    |
     |     keyin 50 000 sum)                                        |
     |  3. O'zini yangi vaqtga ko'chiradi (Dentist tekshiradi)      |
     |  4. Tasdiqlanadi (draft -> confirmed)                        |
     |  Collaborators: Patient, Dentist, Procedure                  |
     +--------------------------------------------------------------+
     | ReminderService                                              |
     |  1. Ertaga boshlanadigan appointment'larni topadi            |
     |  2. SMS matnini tuzadi                                       |
     |  3. SmsGateway orqali yuboradi                               |
     |  Collaborators: Appointment, Patient, SmsGateway (tashqi)    |
     +--------------------------------------------------------------+

3.3  Ikki marta band qilishni tekshiradi: Dentist - faqat u shifokorning BARCHA appointment'lari va ish vaqtini
     biladi (Appointment faqat o'zini biladi, Patient boshqa bemorlarni bilmaydi). Ma'lumot: o'z appointment'lari
     ro'yxati + ish vaqti.
     50 000 sum jarimani hisoblaydi: Appointment - boshlanish vaqti (starts_at) shu yerda; qoida "starts_at - now >= 24 soat"
     bo'yicha ishlaydi. Ma'lumot: starts_at va hozirgi vaqt.

3.4  Ha, qaror o'zgaradi: avval Receptionist faqat aktor edi (tugma bosadi, tizim uni eslab qolmaydi). Auditor "kim
     tasdiqlagan" deb so'ragani uchun inson MA'LUMOTGA aylanadi: Receptionist klass (id, ism) bo'ladi.
     Kartalarda: yangi karta Receptionist (1. id va ismini biladi, 2. tasdiqlovchi shaxs sifatida Appointment'ga beriladi);
     Appointment kartasi o'zgaradi: "tasdiqlanadi va KIM va QACHON tasdiqlaganini eslab qoladi (confirmed_by,
     confirmed_at)", collaborators'ga Receptionist qo'shiladi. Statusni o'zgartirish qarori baribir Appointment'da qoladi.

3.5  Yo'q. Appointment o'z vaqti va bemorini biladi, lekin SMS qanday va qachon ketishini bilmasligi kerak: aks holda
     biznes ma'lumoti SMS-provayderga bog'lanib qoladi va "email bilan ogohlantir" talabi Appointment'ni buzadi.
     SMS'ni ReminderService yuboradi (u ertangi appointment'larni topadi va SmsGateway'ni chaqiradi).
     Munosabatlar: ReminderService --> Appointment = dependency (ro'yxatni vaqtincha o'qiydi, saqlamaydi);
     ReminderService --> SmsGateway = association (maydonda ushlaydi, tashqaridan beriladi). Appointment
     ReminderService'ni umuman bilmaydi.
"""

# Done when (tekshiruv):
#   [x] har bir ot guruhga qo'yilgan (3.1)
#   [x] hech bir kartada 4 tadan ortiq mas'uliyat yo'q (eng ko'pi: Dentist va Appointment - 4 tadan)
#   [x] har bir "kim qaror qiladi" javobi ishlatadigan ma'lumotni nomlaydi (3.3, 3.4, 3.5)
