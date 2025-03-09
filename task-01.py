from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a 10-digit number.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            if date_obj > datetime.today().date():
                raise ValueError("Birthday cannot be in the future.")
            self.value = value
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return f"Phone number {old_phone} changed to {new_phone}."
        return "Old phone number not found."

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(
                    record.birthday.value, "%d.%m.%Y"
                ).date()
                birthday = birthday_date.replace(year=today.year)

                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)

                days_until_birthday = (birthday - today).days

                if 0 <= days_until_birthday <= days:
                    if birthday.weekday() in (5, 6):
                        birthday += timedelta(days=(7 - birthday.weekday()))

                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "birthday": birthday.strftime("%d.%m.%Y"),
                        }
                    )

        return upcoming_birthdays

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
    def wrapper(args, book):
        try:
            return func(args, book)
        except IndexError:
            return "Not enough arguments provided."
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)

    return wrapper


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)

    if record:
        record.add_phone(phone)
        return f"Added phone {phone} to {name}."
    else:
        new_record = Record(name)
        new_record.add_phone(phone)
        book.add_record(new_record)
        return f"New contact {name} added with phone {phone}."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)

    if not record:
        return f"Contact {name} not found."

    return record.change_phone(old_phone, new_phone)


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)

    if not record:
        return f"Contact {name} not found."

    return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"


@input_error
def show_all(args, book):
    if not book.data:
        return "No contacts in the address book."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)

    if not record:
        return f"Contact {name} not found."

    record.add_birthday(birthday)
    return f"Birthday for {name} added successfully."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)

    if not record:
        return f"Contact {name} not found."

    if not record.birthday:
        return f"No birthday set for {name}."

    return f"{name}'s birthday is on {record.birthday.value}."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays this week."

    result = "Upcoming birthdays:\n"
    for entry in upcoming_birthdays:
        result += f"{entry['name']} - {entry['birthday']}\n"

    return result.strip()


def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args


def main():
    book = AddressBook.load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            AddressBook.save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
