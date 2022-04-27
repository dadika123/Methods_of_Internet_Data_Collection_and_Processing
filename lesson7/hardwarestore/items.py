# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Compose


def parse_number(value: str):
    value = value.strip()
    val_int = value.replace(' ', '')
    if val_int.isnumeric():
        value = int(val_int)
    else:
        partition = value.partition('.')
        if partition[0].isnumeric() and partition[1] == '.' and partition[2].isnumeric():
            value = float(value)
        else:
            value_small = value.lower()
            if value_small == 'да' or value_small == 'присутствует':
                value = True
            elif value_small == 'нет' or value_small == 'отсутствует':
                value = False
            else:
                val_range = re.findall(r'от\s+(\d+\s*\d*)\s+до\s+(\d+\s*\d*)', value_small)
                if val_range:
                    value = list(map(parse_number, val_range[0]))
    return value


def extract_properties(properties):
    par_dict = {}
    for key, value in zip(*[iter(properties)] * 2):
        value = value.split('×') if '×' in value else value
        value = value.split(',') if ',' in value else value
        if isinstance(value, list) and len(value) > 1:
            value = list(map(parse_number, value))
        else:
            value = parse_number(value)
        par_dict.update({key: value})
    return par_dict


class HardwarestoreItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(parse_number),
                         output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    properties = scrapy.Field(input_processor=Compose(extract_properties),
                              output_processor=TakeFirst())
