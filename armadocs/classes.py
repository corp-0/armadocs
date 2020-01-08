#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import json
from armadocs.markdown import IndexPage, FunctionPage


class YAMLGenerator:
    root_directory = str()
    yaml_data = dict()
    functions = dict()
    total_count_fnc = 0

    def __init__(self):
        self.root_directory = os.getcwd()
        self.ask_branch()
        self.ask_index_page()
        self.ask_docs_folder()
        self.ask_github_repo()

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
            choice = input(
                "Environment variable that stores the current branch being built in your CI:\n>> "
            )
            branch_environ = choice

        self.yaml_data["branch"] = branch
        self.yaml_data["branch_environ"] = branch_environ

    def ask_travis(self):
        choice = input("Are you using Travis as CI service? [y/n]\n>> ")
        if choice.lower() == "y":
            return True
        else:
            return False

    def ask_index_page(self):
        choice = input("Do you want to generate an index page? [y/n]\n>> ")
        if choice.lower() == "y":
            self.yaml_data["index_page"] = "fnc_index.md"
        else:
            self.yaml_data["index_page"] = None

    def ask_docs_folder(self):
        choice = input("Where do you want to generate your docs? [default: docs/]\n>> ")
        if choice == "":
            self.yaml_data["docs_folder"] = "docs"
        else:
            self.yaml_data["docs_folder"] = choice

    def ask_github_repo(self):
        choice = input(
            "What's your github repo? [ex: https://github.com/user/repo]\n>> "
        )
        self.yaml_data["github_repo"] = choice

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
                    rel_path = (os.path.join(root, file)).replace(
                        f"{self.root_directory}\\", ""
                    )
                    if len(rel_path.split("\\")) > 2:
                        category = rel_path.split("\\")[-3]
                        subcategory = rel_path.split("\\")[-2]
                    else:
                        category = rel_path.split("\\")[-2]
                        subcategory = None

                    fnc_name = ((file.replace("fn_", "")).split("."))[0]

                    if not category in self.functions.keys():
                        self.functions[category] = [
                            {
                                "function": fnc_name,
                                "rel_path": rel_path,
                                "subcategory": subcategory,
                            }
                        ]
                    else:
                        self.functions[category].append(
                            {
                                "function": fnc_name,
                                "rel_path": rel_path,
                                "subcategory": subcategory,
                            }
                        )
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


class DocGenerator:
    yaml_data = None

    def __init__(self):
        try:
            with open(".armadocs.yml", "r", encoding="UTF-8") as f:
                self.yaml_data = f.read()
                self.yaml_data = yaml.load(self.yaml_data)
        except Exception as e:
            print("Something went wrong!")
            print(str(e))
            print("Abruptly terminating script!")
            quit()
        else:
            print("YAML file read succesfully!")

    def generate_documentation(self):
        self.create_docs_folder()
        if self.yaml_data["index_page"] != None:
            self.generate_index_page()

        for category in self.yaml_data["functions"]:
            for fnc in self.yaml_data["functions"][category]:
                
                try:
                    self.generate_fnc_page(fnc)
                except:
                    print(f'error at: {fnc["function"]}. Maybe the function is not documented?')

            
        print("Documentation generated!")

    def create_docs_folder(self):
        docs_folder = os.path.join(os.getcwd(), self.yaml_data["docs_folder"])
        os.makedirs(docs_folder, exist_ok=True)
        self.docs_folder = docs_folder

        return docs_folder

    def generate_index_page(self):
        print("Generating index page...")
        index_file = os.path.join(
            os.path.abspath(self.yaml_data["docs_folder"]), self.yaml_data["index_page"]
        )
        if os.path.isfile(index_file):
            os.remove(index_file)

        IndexPage(
            functions=self.yaml_data["functions"],
            path=index_file,
            repo=self.yaml_data["github_repo"],
        )

    def generate_fnc_page(self, fnc):
        print(f'Generating function page: {fnc["function"]}')
        function_file = os.path.join(
            os.path.abspath(self.yaml_data["docs_folder"]),
            f'{fnc["function"]}.md'
        )
        if os.path.isfile(function_file):
            os.remove(function_file)
        
        FunctionPage(
            function=fnc,
            path=function_file
        )

