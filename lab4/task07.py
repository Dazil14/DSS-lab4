"""
Task 7 - The class design decides what happens on delete      (QOG'OZDA - faqat javoblar, kod yo'q)

7.1  Bog'langan juftliklar va munosabat turi:
       Order   --> Customer   association    (maydon `customer`; mijoz buyurtmadan mustaqil yashaydi)
       Order   <>-> OrderLine composition    (Order.add() qatorni O'ZI yaratadi, qator buyurtma bilan birga yo'qoladi)
       OrderLine --> Product  association    (maydon `product`; mahsulot qatordan keyin ham yashaydi)
       Order   --> Courier    association    (maydon `courier`, assign() orqali keyin beriladi)
       Catalog <>-> Product   aggregation    (Catalog ro'yxat ushlaydi, lekin mahsulotlar katalogsiz ham mavjud)
       Order   - - > Product  dependency     (add(product, qty) faqat parametr: narxni o'qiydi, saqlamaydi)
       SmsGateway - - > Order dependency     (order_shipped(order) faqat parametr)

7.2  Multiplicity (chap - o'ng):
       Customer 1  ---  0..*  Order       (buyurtma aynan bitta mijozniki; mijozda 0 yoki ko'p buyurtma)
       Order    1  <>-  1..*  OrderLine   (buyurtmada kamida bitta qator)
       OrderLine 0..* ---  1  Product     (qator aynan bitta mahsulotga; mahsulot ko'p qatorda)
       Order   0..*  ---  0..1 Courier    (buyurtmada ko'pi bilan bitta kuryer; assign'gacha 0)
       Catalog  0..* <>-  0..* Product    (mahsulot bir nechta katalogda bo'lishi mumkin)
     Kod hali ta'minlamaydi: Order'dagi 1..* - bo'sh buyurtma (0 qator) yaratib bo'ladi; yana Order(None)
     bilan "1 mijoz" ham buziladi.

7.3  ON DELETE tanlovi (lifetime test: "qism butun bilan birga yo'qoladimi?"):
       order_lines.order_id   -> CASCADE   (composition: qator buyurtmasiz ma'nosiz, yo'qoladi - test: ha)
       order_lines.product_id -> RESTRICT  (association: mahsulot qator bilan yo'qolmaydi; sotilgan tarixni
                                            o'chirib bo'lmaydi, shuning uchun mahsulot o'rniga "arxivlanadi")
       orders.customer_id     -> RESTRICT  (association, multiplicity 1: buyurtma mijozsiz bo'lmaydi; moliyaviy
                                            yozuvlar saqlanishi kerak, mijoz kerak bo'lsa anonimlashtiriladi)
       orders.courier_id      -> SET NULL  (association, multiplicity 0..1: buyurtma kuryerdan oldin ham mavjud
                                            va kuryer ketsa ham yashaydi; faqat bog'lanish bo'shaydi)

7.4  `unit_price` - bu nusxa emas, BOSHQA fakt: Product.price = "hozirgi narx" (o'zgaradi), OrderLine.unit_price =
     "sotilgan paytdagi narx" (tarix, hech qachon o'zgarmaydi). Agar qator narxni Product'dan o'qisa, narx
     o'zgargach eski buyurtmalarning summasi ham o'zgarib ketardi (Task 8'dagi kabi "to'lagan summa mos kelmaydi").
     DRY bir xil BILIMning takrorlanishini taqiqlaydi, bu yerda esa ikki xil bilim bor.
"""

# Done when (tekshiruv):
#   [x] har bir juftlikka munosabat va multiplicity berilgan (7.1, 7.2)
#   [x] har bir ON DELETE tanlovi lifetime test bilan izohlangan (7.3)
