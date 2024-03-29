from itertools import count
import os
from dotenv import load_dotenv
import time

import requests
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    if salary_from:
        return salary_from * 0.8


def count_average_salary(salaries):
    salaries_amount = sum(salaries)
    count = len(salaries)
    average_salary = int(salaries_amount / count) if count else 0
    return average_salary, count


def predict_rub_salary_hh(language):
    url = "https://api.hh.ru/vacancies/"
    salaries = []
    language_statistic = {}
    area_id = "1"
    days_period = 30
    per_page = 100
    for number_page in count(0):
        payload = {
            "per_page": per_page,
            "text": f"Программист {language}",
            "area": area_id,
            "period": days_period,
        }
        response = requests.get(url, params=payload)
        response.raise_for_status()
        page = response.json()
        if number_page >= page["pages"]:
            break
        for vacancy in page["items"]:
            salary_range = vacancy['salary']
            if not salary_range:
                continue
            if salary_range['currency'] != 'RUR':
                continue
            vacancy_salary = predict_salary(
                salary_range['from'],
                salary_range['to']
            )
            if vacancy_salary:
                salaries.append(vacancy_salary)
    average_salary, vacancies_processed = count_average_salary(salaries)
    vacancies_amount = page['found']
    language_statistic = {
        'vacancies_found' : vacancies_amount,
        'vacancies_processed' : vacancies_processed,
        'average_salary' : average_salary
    }
    return language_statistic


def predict_rub_salary_for_superJob(language, superjob_token):
    url = "https://api.superjob.ru/3.0/vacancies/"
    salaries = []
    language_statistic = {}
    page_number = 0
    vacancy_amount = 0
    more_pages = True
    town_id = 4
    professions_catalog = 48
    vacancies_number = 100
    while more_pages:
        headers = {
            'X-Api-App-Id': superjob_token
        }
        payload = {
            'town': town_id,
            'catalogues': professions_catalog,
            'page': page_number,
            'count': vacancies_number,
            'keyword': language
        }
        response = requests.get(
            url,
            headers=headers,
            params=payload
            )
        response.raise_for_status()
        page = response.json()
        for vacancy in page['objects']:
            if vacancy['currency'] == 'rub':
                vacancy_salary = predict_salary(
                    vacancy['payment_from'],
                    vacancy['payment_to']
                )
            if vacancy_salary:
                salaries.append(vacancy_salary)
        page_number += 1
        vacancy_amount += page['total']
        more_pages = page['more']
    average_salary, processed_vacancies = count_average_salary(salaries)
    language_statistic = {
        'vacancies_found' : vacancy_amount,
        'vacancies_processed' : processed_vacancies,
        'average_salary' : int(average_salary)
    }
    return language_statistic


def create_table(title, statistic):
    table_header = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]
    table = [
        table_header,
    ]
    for lang, params in statistic.items():
        table_raw = [
            lang,
            params['vacancies_found'],
            params['vacancies_processed'],
            params['average_salary'],
        ]
        table.append(table_raw)
    table = AsciiTable(table, title)
    return table.table


def main():
    load_dotenv()
    superjob_token = os.environ['SJ_TOKEN']
    programming_languages = [
        "Python",
        "C++",
        "Java",
        "GO",
        "Ruby",
        "PHP",
        "JavaScript",
        "C#",
        "C",
        "TypeScript"
    ]
    salary_statistic_hh = {}
    salary_statistic_sj = {}
    for language in programming_languages:
        salary_statistic_hh[language] = predict_rub_salary_hh(language)
        time.sleep(1)
        salary_statistic_sj[language] = predict_rub_salary_for_superJob(language, superjob_token)
        time.sleep(1)
    title_hh = "HeadHunter vacancies"
    print(create_table(title_hh, salary_statistic_hh))
    title_sj = "SuperJob vacancies"
    print(create_table(title_sj, salary_statistic_sj))


if __name__ == "__main__":
    main()
