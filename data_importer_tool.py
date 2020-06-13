import pprint
from pymongo import MongoClient


def create_class():
    my_class = {}
    print("Enter class name")
    my_class["name"] = input()
    print("Enter source book name")
    source_book = input()
    print("Enter source book page number")
    source_page = int(input())
    my_class["source"] = {"book": source_book, "page": source_page}
    print("Enter hit die number. Ex 10 for d10 etc..")
    my_class["die"] = int(input())
    print("Enter the armor proficiencies separated by spaces:")
    raw_armors = input()
    my_class["armor_profs"] = raw_armors.split(" ") if raw_armors else []
    print("Enter the weapon proficiencies separated by spaces:")
    raw_weapons = input()
    my_class["weapon_profs"] = raw_weapons.split(" ") if raw_weapons else []
    print("Enter the tool proficiencies separated by spaces:")
    raw_tools = input()
    my_class["tool_profs"] = raw_tools.split(" ") if raw_tools else []
    print("Enter saving throw proficiencies, separated by spaces:")
    raw_saves = input()
    my_class["saving_profs"] = raw_saves.split(" ") if raw_saves else []
    print("Enter skill proficiencies in the following format skill1,skill2:#OfChoices separated by spaces:")
    raw_skills = input()
    my_class["skill_profs"] = []
    if raw_skills:
        groups = raw_skills.split(" ")
        for group in groups:
            parts = group.split(":")
            my_class["skill_profs"].append({"skills": parts[0].split(","), "choose": parts[1]})
    print("Enter starting equipment in this format: choice1/choice2.choice1/choice2")
    raw_equipment = input()
    my_class["starting_equipment"] = []
    if raw_equipment:
        groups = raw_equipment.split(".")
        for group in groups:
            my_class["starting_equipment"].append(group.split("/"))

    print("Now its time for features")
    my_class["features"] = []
    _is_done = ""
    while not _is_done:
        feature = {}
        print("Enter feature name:")
        feature["name"] = input()
        desc = []
        print("Enter feature description")
        while True:
            line = input()
            if line:
                desc.append(line)
            else:
                break
        feature["desc"] = '\n'.join(desc)

        print("If the feature has limited uses enter 1, else enter 0:")
        has_limits = True if int(input()) == 1 else False

        if has_limits:
            print("If the uses vary per level, enter each level separated by a space, else just enter the limit")
            raw_limit = input()
            if len(raw_limit) > 5:
                feature["limit"] = list(map(int, raw_limit.split(" ")))
            else:
                feature["limit"] = int(raw_limit)

            print("Enter the reset duration: lr, sr, or dawn")
            feature["limit_reset"] = input()

        my_class["features"].append(feature)
        print("If you need another feature, press enter, else enter any value.")
        _is_done = input()

    pp = pprint.PrettyPrinter()
    print("Check if this is correct\n")
    pp.pprint(my_class)
    return my_class


mongoC = MongoClient()
db = mongoC.ddb_db

print("1. Create class\nEnter selection: ")
selection = int(input())

if selection == 1:
    created_class = create_class()
    db.classes.insert_one(created_class)
    print("Created and Saved a new class")
