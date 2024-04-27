from collections import UserDict
from datetime import datetime, timedelta
from functools import wraps
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Помилка вводу: {e}"
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен складатися з 10 цифр.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            super().__init__(value)
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте DD.MM.YYYY.")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            phone_to_edit.value = new_phone
        else:
            raise ValueError("Старий номер телефону не знайдено.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today().date()
            birthday_date = datetime.strptime(self.birthday.value, '%d.%m.%Y').date()
            delta = birthday_date - today
            return delta.days if delta.days >= 0 else (birthday_date.replace(year=today.year + 1) - today).days
        return None

    def __str__(self):
        return f"Ім'я контакту: {self.name.value}, телефони: {'; '.join(p.value for p in self.phones)}, день народження: {self.birthday.value if self.birthday else 'Не вказано'}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        days = 7
        today = datetime.today().date()
        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday_this_year = datetime.strptime(record.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year = self.find_next_weekday(birthday_this_year, 0)
                    upcoming_birthdays.append((name, birthday_this_year.strftime('%d.%m.%Y')))

        return upcoming_birthdays

    def find_next_weekday(self, birthday_date, weekday):
        days_ahead = weekday - birthday_date.weekday()
        if days_ahead <= 0: 
            days_ahead += 7
        return birthday_date + timedelta(days_ahead)

@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError("Будь ласка, вкажіть ім'я та номер телефону.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message

def change_contact(name, old_phone, new_phone, book):
    record = book.find(name)
    if record:
        if old_phone in [phone.value for phone in record.phones]:
            record.edit_phone(old_phone, new_phone)
            return f"Телефонний номер змінено для контакту {name}."
        else:
            return f"Старий телефонний номер не знайдено для контакту {name}."
    else:
        return f"Контакт {name} не знайдено."

@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise IndexError("Будь ласка, вкажіть ім'я.")
    name = args[0]
    record = book.find(name)
    if record:
        return '; '.join([phone.value for phone in record.phones])
    else:
        return "Контакт не знайдено."

@input_error
def show_all_contacts(book):
    if not book:
        return "Контакти не знайдено."
    return "\n".join([str(record) for record in book.values()])

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise IndexError("Будь ласка, вкажіть ім'я та дату народження.")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"День народження додано для контакту {name}."
    else:
        return f"Контакт {name} не знайдено."

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise IndexError("Будь ласка, вкажіть ім'я.")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"День народження {name}: {record.birthday.value}"
    else:
        return f"Контакт {name} не знайдено або день народження не вказано."

@input_error
def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"День народження {name} на {birthday}" for name, birthday in upcoming_birthdays])
    else:
        return "Немає майбутніх днів народження."

def main():
    book = load_data()

    print("Ласкаво просимо до помічника-бота!")
    while True:
        user_input = input("Введіть команду: ")
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("До побачення!")
            save_data(book)  # Зберегти дані перед виходом з програми
            break

        elif command == "hello":
            print("Як я можу вам допомогти?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            if len(args) != 3:
                print("Будь ласка, введіть ім'я, старий телефон та новий телефон.")
            else:
                name, old_phone, new_phone = args
                print(change_contact(name, old_phone, new_phone, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Неправильна команда.")

if __name__ == "__main__":
    main()
