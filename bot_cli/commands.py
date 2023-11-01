from print_util import print_error, print_success, print_info
from address_book_classes import Name, Phone, Birthday, Record, AddressBook
from notes_classes import Notes
from error_handlers import (
    add_contact_error,
    delete_contact_error,
    change_contact_error,
    show_phones_error,
    contact_not_found_error,
    add_birthday_error,
    show_birthday_error,
    max_period_error,
    CommandError,
    ContactAlreadyExistsError,
    ContactNotFoundError,
    search_error,
    note_error_handler,
)
import colorama
from colorama import Fore
from constants import (
    FILE_PATH,
    MAX_PERIOD,
    MIN_PERIOD,
    DEFAULT_PERIOD,
    COMMANDS,
    MIN_NOTE_LEN,
)

# Initialize colorama
colorama.init(autoreset=True)

address_book = AddressBook()


def help():
    """
    Prints out available commands
    prints list of bot commands
    """
    sorted_commands = dict(sorted(COMMANDS.items(), key=lambda item: item[0]))
    formatted_commands = ""

    for key, value in sorted_commands.items():
        formatted_commands += f">>> {key: <40}: {value: <}\n"

    print(Fore.MAGENTA + formatted_commands)


def parse_input(user_input: str):
    """
    Parse input command
    Prints available commands in case of empty input
    @return - command and arguments
    """
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
    except ValueError:
        return "help", ""

    return cmd, *args


@add_contact_error
def add_contact(args: list[str, str]):
    """
    adds a new contact with phone number
    or adds a new phone number to exist contact
    prints command result
    """
    try:
        name, phone = args
        name = Name(name)
    except:
        raise CommandError

    try:
        phone = Phone(phone)
    except:
        raise ValueError

    if address_book.find(name):
        contact = address_book.find(name)

        if not phone.value in contact.get_phones():
            record: Record = contact.add_phone(phone)
        else:
            raise ContactAlreadyExistsError
    else:
        record: Record = Record(name, phone)
        address_book.add_record(record)

    address_book.save_contacts(FILE_PATH)
    print(Fore.GREEN + f"Contact added successfully: {name} {phone}")


@contact_not_found_error
@delete_contact_error
def delete_contact(args):
    """
    delete exist contact
    prints command result
    """
    try:
        name = Name(args[0])
    except:
        raise CommandError

    if address_book.find(name):
        address_book.delete(name)
    else:
        raise ContactNotFoundError

    address_book.save_contacts(FILE_PATH)
    print(Fore.GREEN + f"Contact '{name}' deleted successfully")


@contact_not_found_error
@change_contact_error
def change_phone(args: list[str, str, str]):
    """
    change exist contact phone number on new one
    prints command result
    """
    try:
        name, old_phone, new_phone = args
        name = Name(name)
    except:
        raise CommandError
    try:
        old_phone = Phone(old_phone)
        new_phone = Phone(new_phone)
    except:
        raise ValueError

    if address_book.find(name):
        record: Record = address_book.find(name)

        if old_phone.value in record.get_phones():
            record.edit_phone(old_phone, new_phone)
        else:
            raise KeyError

        address_book.save_contacts(FILE_PATH)
        print(Fore.GREEN + f"Contact '{name}' updated successfully")
    else:
        raise ContactNotFoundError


@search_error
def search_contacts(args):
    """Finds all records stored in the address book if any attribute of the record match the search string"""
    try:
        search_str = args[0]
        search_result = []
        for r in address_book.get_records():
            if str(r).casefold().find(search_str) > 0:
                search_result.append(r)
        if len(search_result) > 0:
            print("\n".join([str(r) for r in search_result]))
        else:
            print("No results found!")
    except (ValueError, IndexError) as e:
        raise CommandError


@contact_not_found_error
@show_phones_error
def show_phones(args):
    """
    show exist contact phone numbers
    prints command result
    """
    try:
        name = Name(args[0])
    except:
        raise CommandError

    if address_book.find(name):
        print(
            Fore.GREEN
            + f"{name.value}: {', '.join(address_book.find(name).get_phones())}"
        )
    else:
        raise ContactNotFoundError


@contact_not_found_error
@add_birthday_error
def add_birthday(args):
    """
    add birthday to exist contact
    prints command result
    """
    try:
        name, birthday = args
        name = Name(name)
    except:
        raise CommandError

    try:
        birthday = Birthday(birthday)
    except:
        raise ValueError

    if address_book.find(name):
        record: Record = address_book.find(name)
        record.add_birthday(birthday)
    else:
        raise ContactNotFoundError

    address_book.save_contacts(FILE_PATH)
    print(Fore.GREEN + "Birthday added successfully")


@contact_not_found_error
@show_birthday_error
def show_birthday(args):
    """
    show birthday of exist user
    prints command result
    """
    try:
        name = args[0]
        name = Name(name)
    except:
        raise CommandError

    if address_book.find(name):
        record: Record = address_book.find(name)
    else:
        raise ContactNotFoundError

    if record.birthday:
        birthday = record.show_birthday()
    else:
        raise ValueError

    print(Fore.GREEN + f"{name} birthday: {birthday}")


def show_all_contacts():
    """
    show all exist contacts
    prints command result
    """
    if address_book.data:
        result = list()
        for record in address_book.data.values():
            result.append(str(record))
        print(Fore.LIGHTBLUE_EX + "\n".join(result))
    else:
        print(Fore.LIGHTBLUE_EX + "No contacts have been added yet")


@max_period_error
def birthdays(args):
    if args:
        try:
            period = int(args[0])
            if (period < MIN_PERIOD) or (period > MAX_PERIOD):
                raise ValueError
        except:
            raise ValueError
    else:
        period = DEFAULT_PERIOD

    get_birthdays_per_week = address_book.get_birthdays_per_week(period)

    if get_birthdays_per_week:
        result = "Next week birthdays:\n" + "-" * 10 + "\n"
        result += "\n".join(
            [
                f"{day}: {celebrate_users}"
                for day, celebrate_users in get_birthdays_per_week.items()
            ]
        )
        result += "\n" + "-" * 10
        print(Fore.YELLOW + result)
    else:
        print(Fore.YELLOW + "There is no one to celebrate birthday next week")


@note_error_handler
def add_note(notebook: Notes, args):
    text = " ".join(args)
    if text.isspace() or len(text) < MIN_NOTE_LEN:
        raise ValueError(
            f"Note cannot be empty and must be more than {MIN_NOTE_LEN} characters long"
        )
    note_id, _ = notebook.add_note(text)
    print_success(f"Note with id {note_id} created successfully")


# command, index, text = args[0], args[1], " ".join(args[2:])
@note_error_handler
def update_note(notebook: Notes, args):
    index, text = args[0], " ".join(args[1:])
    notebook.update_note(int(index), text)
    print_success("Note successfully updated")


@note_error_handler
def replace_note(notebook: Notes, args):
    index, text = args[0], " ".join(args[1:])
    notebook.replace_note(int(index), text)
    print_success("Note successfully replaced")


@note_error_handler
def remove_note(notebook: Notes, args):
    index = args[0]
    notebook.remove_note(int(index))
    print_success("Note successfully removed")


@note_error_handler
def note_by_id(notebook: Notes, args):
    index = args[0]
    note = notebook.find_note_by_index(int(index))
    if note["Tags"]:
        str_tags = " ".join(note["Tags"])
        print_success(f"Note: {note['Note']}\n Tags:{str_tags}")
    else:
        print_success(f"Note: {note['Note']}")


@note_error_handler
def note_by_text(notebook: Notes, args):
    # find_note_by_subtext
    text = " ".join(args)
    notes = notebook.find_note_by_subtext(text)
    if not notes:
        print_info("No matches found for: '{text}'")
    output = []
    for note in notes:
        if note["Tags"]:
            str_tags = " ".join(note["Tags"])
            note_string = f"Note: {note['Note']}\n Tags:{str_tags}"
        else:
            note_string = f"Note: {note['Note']}"
        output.append(note_string)
    output_string = "\n".join(output)
    print_success(output_string)
