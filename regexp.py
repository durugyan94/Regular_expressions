import re
import csv
from pprint import pprint

from operator import itemgetter
from itertools import groupby
from collections import defaultdict


def organize_fio(
    fio: str,
    lastname_pattern: re.Pattern,
    surname_pattern: re.Pattern
) -> (str):
    """_summary_

    Args:
        fio (_type_): _description_

    Returns:
        _type_: _description_
    """
    lastname: str = None
    firstname: str = None
    surname: str = None
    fio_list = fio.strip().split(" ")

    assert len(fio_list) < 4, f"ФИО должно состоять из не более чем 3-х элементов, а получено {fio_list}"

    for idx in range(0, len(fio_list)):
        if surname_pattern.search(fio_list[idx]):
            surname = fio_list[idx]
            fio_list[idx] = ""
        elif lastname_pattern.search(fio_list[idx]):
            lastname = fio_list[idx]
            fio_list[idx] = ""
        elif re.search(r'\b[А-Я]{1}[а-я]+\b', fio_list[idx]):
            firstname = fio_list[idx]

    return lastname, firstname, surname


def organize_phone_num(phone_num: str) -> str:
    """_summary_

    Args:
        phone_num (str): _description_

    Returns:
        str: _description_
    """
    phone_pattern = re.compile(
        "".join(
            [
                r'(?P<prefix>\+?)',
                r'\s?(?P<scode>(?:7|8)?)\s?',
                r'(?:\s|\-|\()?(?P<rcode>\d{3})(?:\s|\-|\))?',
                r'\s?(?P<phnumber>[\d]{3}[\s\-]?(?:\d{4}|\d{2}[\s\-]?\d{2}))\s?',
                r'(?:\s|\-|\()?(до[бп]{1}[ав|ол]{0,2})?(\.?\:?\s)?(?P<addnumber>[\d]+)?(?:\-|\()?'
            ]
        )
    )
    m = phone_pattern.search(phone_num)
    mgroups = m.groupdict() if m else {}

    res = []
    for k, v in mgroups.items():
        match k:
            case "scode":
                res.insert(0, "+7")
            case "rcode":
                res.insert(1, f"({v})")
            case "phnumber":
                phm = re.match(
                    r'(\d{1,3})\D?(\d{2})\D?(\d{2})', v
                )
                if phm is not None:
                    res.insert(2, "-".join(phm.groups()))
            case "addnumber":
                if v is not None:
                    res.insert(3, f" доб.{v}")

    return res


def main():
    with open("phonebook_raw.csv", encoding="utf8") as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)
    pprint(contacts_list)

    # TODO 1: выполните пункты 1-3 ДЗ
    # Фамилия - основные варианты:
    # начинается с одной русской большой буквы: \b[А-Я]{1}
    # далее следуют прописные русские буквы от одной и более: [а-я]+
    # а заканчивается одним из окончаний: (?:ов|ев|ин|кий|кая|цев) вкл. женские [ая]{0,2}
    # r'' - что б отдельно не экранировать спец символы
    lastname_pattern = re.compile(
        r'\b[А-Я]{1}[а-я]+(?:ов|ев|ин|кий|кая|цев)[ая]{0,2}\b'
    )
    surname_pattern = re.compile(
        r'\b[А-Я]{1}[а-я]+(?:ев|ов)(?:ич|на)\b'
    )

    organazed_contact_list = []
    for n, row in enumerate(contacts_list, start=0):
        new_row = row

        if n > 0:
            person: str = " ".join(row[0:3])
            phone: str = row[-2]

            fio: tuple = organize_fio(person, lastname_pattern, surname_pattern)
            phn: list = organize_phone_num(phone)

            new_row[0:3] = fio
            new_row[-2] = "".join(phn)

        organazed_contact_list.append(row)

    new_contact_list_dict = []
    for rows in organazed_contact_list[1:]:
        new_contact_list_dict.append(
            {
                k: v for k, v in zip(
                    organazed_contact_list[0], [row for row in rows], strict=False
                )
            }
        )
    contact_list_by_person = defaultdict(list)
    new_contact_list_dict.sort(
        key=itemgetter("lastname", "firstname")
    )
    for person, items in groupby(
        new_contact_list_dict, key=itemgetter("lastname", "firstname")
    ):
        for row in items:
            contact_list_by_person[
                "_".join(person)
            ].append({k: v for k, v in row.items()})
    new_contact_list = []
    new_contact_dict = defaultdict(dict)
    for rows in contact_list_by_person.values():
        for data in rows:
            new_contact_dict = {
                k: v if bool(v) else new_contact_dict.get(k, "") for k, v in data.items()
            }
        new_contact_list.append(new_contact_dict)

    # TODO 2: сохраните получившиеся данные в другой файл
    with open("phonebook.csv", mode="w", encoding="utf8") as f:
        csv_writer = csv.DictWriter(
            f,
            fieldnames=tuple(new_contact_list[0].keys()),
            delimiter=",",
            lineterminator="\n"
        )
        csv_writer.writeheader()
        csv_writer.writerows(new_contact_list)


if __name__ == "__main__":
    main()
