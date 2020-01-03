#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import json


class YAMLGenerator:
    root_directory = str()
    yaml_data = dict()
    functions = dict()
    total_count_fnc = 0


    def __init__(self):
        self.root_directory = os.getcwd()
        self.ask_branch()
        
        print(f"root directory: {self.root_directory}")
        print("Trying to find functions...")

        if os.path.isdir(f"{self.root_directory}\\addons\\"):
            self.find_functions(f"{self.root_directory}\\addons\\")
        else:
            self.ask_fnc_dir()

        self.write_yaml()

    def ask_branch(self):
        choice = input("What branch you want to trigger the documentation build?:\n>> ")
        branch = choice
        
        if self.ask_travis():
            branch_environ = "TRAVIS_BRANCH"
        else:
            choice = input("Environment variable that stores the current branch being built in your CI:\n>> ")
            branch_environ = choice

        self.yaml_data["branch"] = branch
        self.yaml_data["branch_environ"] = branch_environ

    def ask_travis(self):
        choice = input("Are you using Travis as CI service? [y/n]\n>> ")
        if choice.lower() == "y":
            return True
        else:
            return False
            
    def ask_fnc_dir(self):
        choice = input("Where are your functions located? Enter its directory\n>> ")
        if not os.path.isdir(choice):
            print(f"{choice} is not a valid directory.")
            self.ask_fnc_dir()
        else:
            self.find_functions(os.path.abspath(choice))

    def find_functions(self, directory):
        print(directory)
        for root, dirs, files in os.walk(directory, topdown=True):
            for file in files:
                if "fn_" in file:
                    self.total_count_fnc += 1
                    # full_path = (os.path.join(root, file)).split("\\")
                    rel_path = (os.path.join(root, file)).replace(f"{self.root_directory}\\", "")
                    if len(rel_path.split('\\')) > 2:
                        category = (rel_path.split("\\")[-3])
                        subcategory = (rel_path.split("\\")[-2])
                    else:
                        category = (rel_path.split("\\")[-2])
                        subcategory = None

                    fnc_name = ((file.replace("fn_", "")).split("."))[0]

                    if not category in self.functions.keys():
                        self.functions[category] = [
                            {
                                "function": fnc_name,
                                "rel_path": rel_path,
                                "subcategory": subcategory,
                            }]
                    else:
                        self.functions[category].append(
                            {
                                "function": fnc_name,
                                "rel_path": rel_path,
                                "subcategory": subcategory,
                            })
        for key in self.functions.keys():
            counter = 0
            print(f"\n{key}:")
            for element in self.functions[key]:
                counter += 1
                print(f"{counter}.- {element['function']}")
        print(f"\n{self.total_count_fnc} function(s) found!")

        if self.functions:
            self.yaml_data["functions"] = self.functions

    def write_yaml(self):
        try:
            with open(".armadocs.yml", "w", encoding="UTF-8") as f:
                data = yaml.dump(self.yaml_data)
                f.write(data)
        except Exception as e:
            print("Something went wrong!")
            print(str(e))
        else:
            print("All done. You can go finetune your armadoc.yml file if needed.")


class DocGenerator():
    yaml_data = None

    def __init__(self):
        try:
            with open(".armadocs.yml", "r", encoding="UTF-8") as f:
                self.yaml_data = f.read()
                self.yaml_data = yaml.load(self.yaml_data)
        except Exception as e:
            print("Something went wrong!")
            print(str(e))
        else:
            print("YAML file read succesfully!")