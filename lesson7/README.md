# Lesson 7. Scrapy. Files Parsing
### Collect data of some category from [leroymerlin.ru](https://leroymerlin.ru/) using [Scrapy](https://scrapy.org/) and save data to DB.

##### Run script:

To parse leroymerlin.ru run with the corresponding category, e.g., "lyustry" `scrapy crawl leroymerlin -a category=lyustry`

###### Collected data example:
```json
[
  {
    "_id": {
      "$oid": "6203b50da83a9cfed1d302eb"
    },
    "name": "Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный",
    "price": 3735,
    "url": "https://leroymerlin.ru/product/svetilnik-nastenno-potolochnyy-inspire-amber-6-lamp-18-m-cvet-chernyy-85113378/",
    "photos": [
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/0.jpg",
        "checksum": "f1663ab8897a62368008ea1c87ed93e4",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_01.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/1.jpg",
        "checksum": "c30d46661e0060c293ec1e247c0258e4",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_02.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/2.jpg",
        "checksum": "3f93fff09cc4bf7fc18d0710985634ae",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_03.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/3.jpg",
        "checksum": "9a6118bbffaff06b3720ee464950ccaa",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_04.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/4.jpg",
        "checksum": "a529adb9a58f38efab7a4f4f8fc52182",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_05.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/5.jpg",
        "checksum": "e051d33ab3a07ca7e8cc048ca570d110",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_06.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/6.jpg",
        "checksum": "ecf0f1f51b29e3e5bbfe1ab762b91e09",
        "status": "downloaded"
      },
      {
        "url": "https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/85113378_drw.jpg",
        "path": "leroymerlin/lyustry/Светильник настенно-потолочный Inspire Amber 6 ламп 18 м² цвет черный/7.jpg",
        "checksum": "f2a45e62c8965b347ddf7c82584fafa7",
        "status": "downloaded"
      }
    ],
    "properties": {
      "Максимальная площадь освещения (в м²)": 18,
      "Коллекция для публикации": "Amber",
      "Диаметр (см)": 52,
      "Габариты (ДхШхВ), см": [
        52,
        36,
        23
      ],
      "Длина (см)": 52,
      "Ширина (см)": 36,
      "Высота (см)": 23,
      "Вес, кг": 2.23,
      "Напряжение (В)": [
        110,
        240
      ],
      "Тип цоколя": "E27",
      "Количество лампочек": 6,
      "Совместимый тип лампы": [
        "Люминесцентный",
        "Накаливания",
        "Светодиодный (LED)",
        "Филаментный (LED)"
      ],
      "Форма подходящей лампочки": [
        "Свеча",
        "Груша",
        "Шар малый",
        "Спираль"
      ],
      "Максимально допустимая мощность лампы (Вт)": 60,
      "Цветовая палитра": "Черный",
      "Основной материал": "Стекло",
      "Материал конструкции": "Железо",
      "Материал плафонов/абажура": "Стекло",
      "Стиль": "Нео-классика",
      "Функции": false,
      "Особенности продукта": false,
      "Степень защиты от пыли и воды (IP)": "IP20",
      "Марка": "INSPIRE",
      "Страна производства": "Китай",
      "Гарантия (лет)": 5,
      "Подходит для низкого потолка (до 2,5 м)": true
    }
  }
]
```
