"""
Class Notes will have the following data format:
{"notes": [
   {
   Note: "text",
   Tags: ['one', 'two']
   }
]

Classes:
- Field (Base class) - import from adddress_book_classes
- Note (Field) - Field for the note text - notes are single strings.
- Tag (Field) - Tags as an array, so there can be multiple tags.
- Notes (UserDict) - The regular dictionary will have the same format as above.

Important notes:
- {"Note": note, "Tags": tags} - returns notes in this format.
If the "Tags" field is empty, it returns an empty array. You'll need to handle the conversion to something else in the handler.
If a search command (by text/tag) doesn't find a match, it should return an empty array.

Available methods for Notes class:
- __init__ - Initializes the notebook with the base format: {"notes": []}
- add_note(self, note) - Adds a note.
- remove_note(self, index) - Removes by index (deletes both the note and its tags).
- replace_note(self, index, new_note) - Replaces the TEXT of the note; position and tags remain the same.
- update_note(self, index, add_note_text) - Appends to the note; separated by ";"
- find_note_by_index(self, index) - Searches by index and returns {"Note": note, "Tags": tags} // note - a string + tags - a list of strings.
- find_note_by_subtext(self, sub_text) - Searches for matches by text - at least 3 letters; returns [{"Note": note, "Tags": tags}].
- show_notes(self) - Returns all notes with tags = [{index: {"Note": note, "Tags": tags}}, {index: {"Note": note, "Tags": tags}}] - make sure to pay attention to the indexes for retrieval.
- add_tag(self, index, tag) - Adds a tag; make sure to provide the note index.
- remove_tag(self, note_index, tag) - Specify which tag to remove from which note.
- change_tag(self) - Not implemented; unsure if tag editing is required.
"""
from collections import UserDict
from address_book_classes import Field
from constants import FILE_PATH_NOTES
import os
import json


class Note(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Tag(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Notes(UserDict):
    def __init__(self):
        super().__init__()
        self.data = {"notes": []}

    def add_note(self, note):
        notes_ = self.data["notes"]
        n = Note(note)
        notes_.append({"note": n, "tags": []})
        return len(notes_), n

    def remove_note(self, index):
        del self.data["notes"][index - 1]

    def change_note(self, index, new_note):
        self.data["notes"][index - 1]["note"] = Note(new_note)

    def update_note(self, index, add_note_text):
        current_note = self.find_note_by_index(index)
        current_note_text = str(current_note["Note"])
        update_note_text = current_note_text + "; " + add_note_text
        self.change_note(index, update_note_text)

    def find_note_by_index(self, index):
        data = self.data["notes"][index - 1]
        note = str(data["note"])
        tags = [str(tag) for tag in data["tags"]]
        return {"Note": note.capitalize(), "Tags": tags}

    def find_note_by_subtext(self, sub_text):
        searched_note = []
        for data in self.data["notes"]:
            note = str(data["note"]).casefold()
            tags = [str(tag) for tag in data["tags"]]
            if sub_text.casefold() in note:
                searched_note.append({"Note": note.capitalize(), "Tags": tags})
        return searched_note

    def show_notes(self):
        notes = []
        for index, data in enumerate(self.data["notes"]):
            note = str(data["note"])
            tags = [str(tag) for tag in data["tags"]]
            notes.append({index: {"Note": note.capitalize(), "Tags": tags}})

        return notes

    def add_tag(self, index, tag):
        self.data["notes"][index - 1]["tags"].append(Tag(tag))

    def remove_tag(self, note_index, tag):
        tags = [str(tag) for tag in self.data["notes"][note_index - 1]["tags"]]
        tag_index = tags.index(tag)
        del self.data["notes"][note_index - 1]["tags"][tag_index]

    def find_notes_by_tag(self, tag):
        searched_note = []
        for data in self.data["notes"]:
            note = str(data["note"]).casefold()
            tags = [str(tag).casefold() for tag in data["tags"]]
            if tag.casefold() in tags:
                searched_note.append({"Note": note.capitalize(), "Tags": tags})
        return searched_note

    def change_tag(self):
        pass  # зробити редагування конретного тега? не впевнений шо треба

    def to_json(self):
        serialized_data = {
            "notes": [{"note": str(data["note"].value), "tags": [str(tag.value) for tag in data["tags"]]} for data in
                      self.data["notes"]]
        }
        return serialized_data

    @classmethod
    def from_json(cls, data):
        notes_instance = cls()
        notes_instance.data = {"notes": []}

        for note_data in data:
            note_value = note_data["note"]
            tags = note_data["tags"]
            notes_instance.data["notes"].append({"note": Note(note_value), "tags": [Tag(tag) for tag in tags]})

        return notes_instance

    def save_notes(self, path):
        serialized_data = self.to_json()
        with open(path, "w") as file:
            json.dump(serialized_data["notes"], file, indent=4)

    def load_notes(self, path):
        with open(path, "r") as file:
            data = json.load(file)
            notes = Notes.from_json(data)
            self.data = notes.data

    def __str__(self):
        notes = []
        for index, note in enumerate(self.data["notes"]):
            notes.append({index: note["tags"]})
        return str(notes)


if __name__ == "__main__":
    notes = Notes()
    notes.add_note("My first note")
    notes.add_note("My second note")
    notes.add_note("My third note")
    print(notes.show_notes())
    notes.add_tag(1, "TTT")
    notes.add_tag(1, "AAA")
    notes.add_tag(1, "BBB")
    notes.add_tag(2, "BBB")
    print(notes.show_notes())
    notes.remove_tag(1, "TTT")
    print(notes.show_notes())
    notes.update_note(1, "additional info")
    print(notes.show_notes())
    notes.remove_note(1)
    # ++
    print(notes.show_notes())
    print(notes.show_notes())
    print(f"here is your note by index: {notes.find_note_by_index(1)}")
    notes.change_note(1, "Replaced note")
    print(f"here is your by text: {notes.find_note_by_subtext('third')}")
    print(f"here is your by tag: {notes.find_notes_by_tag('BBB')}")
    notes.add_tag(1, "DDD")
    print(f"Old notes:\n{notes.show_notes()}")
    print("Save notes to json file")
    notes.save_notes(FILE_PATH_NOTES)
    print("Load notes from json file")
    notes.load_notes(FILE_PATH_NOTES)
    print(f"New notes:\n{notes.show_notes()}")

