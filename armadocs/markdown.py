"""
Classes and methods related to generating Markdown files
"""

import os
import re
import yaml

class Markdown():
    """Class with methods for MD styling your text."""

    def heading(self, text, level=1):
        heading_level = "#" * level
        formatted_text = f"{heading_level} {text}"

        return formatted_text

    def bold(self, text):
        formatted_text = f"**{text}**"

        return formatted_text

    def italic(self, text):
        formatted_text = f"*{text}*"

        return formatted_text

    def bold_italic(self, text):
        formatted_text = f"***{text}***"

        return formatted_text

    def blockquote(self, text):
        formatted_text = f"> {text}"

        return formatted_text

    def list(self, text, ordered=False):

        if ordered:
            prefix = "1."
        else:
            prefix = "*"

        formatted_text = f"{prefix} {text}"

        return formatted_text

    def code(self, text):
        formatted_text = f"`{text}`"

        return formatted_text

    def link(self, text, url, title=None):
        if title is None:
            formatted_text = f"[{text}]({url})"
        else:
            formatted_text = f"[{text}]({url} {title})"

        return formatted_text

    def url(self, text):
        formatted_text = f"<{text}>"

        return formatted_text

    def image(self, url, text=str()):
        formatted_text = f"![{text}]({url})"

        return formatted_text

    def image_link(self, url, image_url, text=str()):
        formatted_text = f"[![{text}]({image_url})]({url})"

        return formatted_text


class IndexPage():
    """Class that generate your index page with the given functions.
    
    args:\n
        functions = dict, functions object read from the yml file
        path = str, the file to be written
        repo = str, url to your github repo
    """
    
    md = Markdown()

    def __init__(self, functions, path, repo):
        self.path = path
        self.repo = repo
        self.functions = functions
        self.write_file(self.md.heading("Functions library by category"))
        self.make_links()

    def make_links(self):
        for key in self.functions.keys():
            category = key.capitalize()
            category = self.md.heading(category, level=2)
            self.write_file(category)

            for element in self.functions[key]:
                fnc_name = element["function"]
                link = self.md.link(fnc_name, f"{self.repo}/wiki/{fnc_name}")
                listed = self.md.list(link)
                self.write_file(listed)


    def write_file(self, text):
        try:
            with open(self.path, 'a', encoding="UTF-8")as f:
                f.write(f"{text}\n")
        except Exception as e:
            print("Something went wrong!")
            print(str(e))
            raise e

class FunctionPage():
    """Class that analyzes the given data and docstring in your function file and generates
    an individual function page.
    
    args:\n
        function = dict, individual function in dict format
        path = str, file to be written"""

    md = Markdown()

    def __init__(self, function, path):
        self.function = function
        self.path = path
        self.function_name = self.function["function"]
        self.docstring = str()

        with open(".armadocs.yml", "r", encoding="UTF-8") as f:
            self.yaml_data = f.read()
            self.yaml_data = yaml.load(self.yaml_data)

        self.write_file(self.md.heading(self.function_name))
        self.find_docstring_data()
        self.find_code()
        self.find_arguments()
        try:
            self.write_file(self.find_author())
        except:
            pass
        self.find_headers()
        self.find_data_type()
        
        self.write_file(self.docstring)

    def find_docstring_data(self):
        sqf_file = self.function["rel_path"]
        sqf_data = str()

        with open(sqf_file, "r", encoding="UTF-8") as f:
            sqf_data = f.read()

        self.docstring = re.search(r"\/\*(.*)\*\/", sqf_data, re.S)
        self.docstring = self.docstring.group(1)
        splited = list()
        
        for text in self.docstring.split("\n"):
            text = re.sub(r"^\s+", "", text)
            
            if text.startswith("*"):
                text = text[1:]
            if text.startswith(" "):
                text = text[1:]
            if not text == "":
                splited.append(text)

        self.docstring = "\n".join(splited)
    
    def find_code(self):
        code_string = re.findall(r"\[.*\] call .*[;]?", self.docstring, re.I | re.M)

        for match in code_string:
            self.docstring = self.docstring.replace(match, self.md.code(match))

    def find_arguments(self):
        argument_string = re.findall(r"\d:", self.docstring, re.M)
        argument_var = re.findall(r"\d: (_\w+)", self.docstring, re.M)

        for match in argument_string:
            self.docstring = self.docstring.replace(match, self.md.list(match))

        arg_pos = 0
        for match in argument_var:
            self.docstring = re.sub(r"\d: (_\w+)",f"{str(arg_pos)}. " + self.md.bold(match), self.docstring)
            arg_pos +=1

    def find_headers(self):
        header_string = re.findall(r"^(\w+[ ]?\w+:)", self.docstring, re.M)

        for match in header_string:
            self.docstring = self.docstring.replace(match, self.md.heading(match, level=3))
    
    def find_data_type(self):
        data_string = re.findall(r"<.*>", self.docstring, re.M)

        for match in data_string:
            fixed = match.replace("<", "(")
            fixed = fixed.replace(">", ")")
            self.docstring = self.docstring.replace(match, fixed)

    def find_author(self):
        author_name = re.search(r"author: (.*)", self.docstring, re.IGNORECASE | re.MULTILINE)
        author_line = author_name.group(0)
        author_name = author_name.group(1)
        
        if not author_name is None:
            if "users" in self.yaml_data.keys():
                if author_name in self.yaml_data["users"]:
                    author_string = f'Code by [{author_name}]({self.yaml_data["users"][author_name]})'
                else:
                    author_string = f"Code by {author_name}"
            else:
                author_string = f"Code by {author_name}"

        else:
            author_name = "Code by ANON"
        
        self.docstring = re.sub(author_line, "", self.docstring)

        return author_string

    
    def write_file(self, text):
        try:
            with open(self.path, 'a', encoding="UTF-8") as f:
                f.write(f"{text}\n")

        except Exception as e:
            print("Something went wrong!")
            print(str(e))
            raise e
