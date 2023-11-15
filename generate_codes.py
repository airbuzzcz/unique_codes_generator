import csv
import string
import argparse
import random
from datetime import datetime
import os
import time
from datetime import datetime, timedelta


class CodeGenerator:
    RECOMMENDED_CHARS = "2345679ACDEFGHJKLMNPRSTUVXYZ"

    def __init__(self, codes_count, codes_length, prefix=None, suffix=None):
        """
        Initializes a UniqueCodeGenerator object with the given parameters.

        Args:
            codes_count (int): The number of unique codes to generate.
            codes_length (int): The length of each unique code.
            prefix (str, optional): A prefix to add to each generated code. Defaults to None.
            suffix (str, optional): A suffix to add to each generated code. Defaults to None.

        Raises:
            ValueError: If codes_count or codes_length are not integers, or if they are less than 1.
        """
        try:
            self.codes_count = int(codes_count)
            self.codes_length = int(codes_length)
        except ValueError:
            raise ValueError("Codes_count and codes_length must be integers.")
        except TypeError:
            raise ValueError("Codes_count and codes_length must be integers.")
        if self.codes_count < 1:
            raise ValueError("Codes_count and codes_length must be greater than 0.")
        if self.codes_length < 1:
            raise ValueError("Codes_count and codes_length must be greater than 0.")
        self.charset = ""
        self.codes_set = set()
        self.encoding = ""
        self.prefix = prefix
        self.suffix = suffix
        self.filename_base = ""
        self.filename_ext = ""
        self.maxlines = 0
        self.save_directory = ""

    def build_character_set(self, charset, case, omit, add, custom_chars):
        if case == "lower":
            alphaSet = string.ascii_lowercase
        elif case == "mixed":
            alphaSet = string.ascii_letters
        elif case == "upper":
            alphaSet = string.ascii_uppercase
        else:
            raise ValueError(f"Invalid case: {case}.")

        if charset == "recommended":
            self.charset = self.RECOMMENDED_CHARS
        elif charset == "numeric":
            self.charset = string.digits
        elif charset == "alpha":
            self.charset = alphaSet
        elif charset == "alphanumeric":
            self.charset = string.digits + alphaSet
        elif charset == "custom":
            if custom_chars:
                # Check for duplicate characters
                if len(custom_chars) != len(set(custom_chars)):
                    raise ValueError(
                        "Custom character set contains duplicate characters."
                    )
                # Check for invalid characters
                invalid_chars = [
                    char for char in custom_chars if char not in string.printable
                ]
                if invalid_chars:
                    raise ValueError(
                        f"Invalid characters in custom character set: {', '.join(invalid_chars)}"
                    )
                self.charset = custom_chars
            else:
                raise ValueError("Custom character set is empty.")
        else:
            raise ValueError(f"Invalid charset: {self.charset}.")

        if omit is not None:
            invalid_chars = [char for char in omit if char not in string.printable]
            if invalid_chars:
                raise ValueError(
                    f"Invalid characters in omit character set: {', '.join(invalid_chars)}"
                )
            else:
                self.charset = "".join(
                    char for char in self.charset if char not in omit
                )

        if add is not None:
            invalid_chars = [char for char in add if char not in string.printable]
            if invalid_chars:
                raise ValueError(
                    f"Invalid characters in add character set: {', '.join(invalid_chars)}"
                )
            else:
                self.charset += add

        if not self.charset:
            raise ValueError("Used character set is empty.")

    def build_file(
        self, filename, maxlines=None, encoding="utf-8", save_directory="codes"
    ):
        filename_base, filename_ext = os.path.splitext(filename)

        if filename_ext == "":
            filename_ext = ".csv"

        self.filename_base = filename_base
        self.filename_ext = filename_ext

        if maxlines is None:
            self.maxlines = self.codes_count
        else:
            self.maxlines = int(maxlines)

        if self.maxlines < 1:
            raise ValueError("Maxlines must be an integer greater than 0.")

        self.encoding = encoding

        self.save_directory = save_directory

    def __generate_codes(self):
        probability = self.__check_probability()

        if probability > 1:
            raise ValueError(
                f"Cannot generate {self.codes_count} codes of length {self.codes_length} from a character set of length {len(self.charset)}."
            )

        codes_generated = 0
        start_time = time.time()

        while codes_generated < self.codes_count:
            code = "".join(
                random.choice(self.charset) for _ in range(self.codes_length)
            )
            if self.prefix is not None:
                code = self.prefix + code
            if self.suffix is not None:
                code = code + self.suffix
            if code in self.codes_set:
                continue
            else:
                self.codes_set.add(code)
                codes_generated += 1

                self.__update_progress(codes_generated, self.codes_count, start_time)

    def __check_probability(self):
        chars_number = len(self.charset)
        combinations = chars_number**self.codes_length
        probability = self.codes_count / combinations
        return probability

    def __update_progress(self, current, total, start_time):
        progress = current / total
        progressbar_length = 50
        num_chars = int(progress * progressbar_length)
        progress_bar = (
            "│" + "█" * num_chars + "─" * (progressbar_length - num_chars) + "│"
        )
        progress_codes = f"{current}/{total}"

        elapsed_time = time.time() - start_time

        if progress > 0:
            remaining_time = (elapsed_time / progress) - elapsed_time
        else:
            remaining_time = 0

        remaining_time = str(timedelta(seconds=remaining_time)).split(".")[0]

        print(
            f"\r{progress_bar} {progress_codes} remaining time: {remaining_time}",
            end="",
            flush=True,
        )

    def __save_codes(self):
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        codes_list = list(self.codes_set)
        num_files = (len(codes_list) - 1) // self.maxlines + 1

        for file_index in range(num_files):
            start_index = file_index * self.maxlines
            end_index = (file_index + 1) * self.maxlines

            if num_files > 1:
                output_file_name = (
                    f"{self.filename_base}_{file_index + 1}{self.filename_ext}"
                )
            else:
                output_file_name = f"{self.filename_base}{self.filename_ext}"

            file_path = os.path.join(self.save_directory, output_file_name)

            try:
                with open(
                    file_path,
                    "w",
                    newline="",
                    encoding=self.encoding,
                ) as csvfile:
                    csv_writer = csv.writer(csvfile)
                    for code in codes_list[start_index:end_index]:
                        csv_writer.writerow(code.split())
            except IOError:
                raise ValueError("Could not write into the file.")

    def run(self):
        self.__generate_codes()
        self.__save_codes()


def main():
    parser = argparse.ArgumentParser(
        description="Generate unique codes and save them to a CSV file."
    )

    parser.add_argument(
        "count",
        help="Number of codes to generate (required)",
    )
    parser.add_argument("length", help="Length of each code (required)")
    parser.add_argument(
        "--charset",
        choices={"recommended", "alphanumeric", "alpha", "numeric", "custom"},
        default="recommended",
        help="Character set for code generation",
    )
    parser.add_argument(
        "--omit", help="Characters to be removed from the selected character set"
    )
    parser.add_argument(
        "--add", help="Characters to be added to the selected character set"
    )
    parser.add_argument("--prefix", help="Add a prefix to each code")
    parser.add_argument("--suffix", help="Add a suffix to each code")
    parser.add_argument(
        "--case",
        choices={"upper", "lower"},
        default="upper",
        help="Letter case of alpha characters",
    )
    parser.add_argument("--filename", help="Output file name")
    parser.add_argument(
        "--encoding", default="utf-8", help="Encoding of the output file"
    )
    parser.add_argument("--maxlines", type=int, help="Maximum number of codes per file")

    args = parser.parse_args()

    if args.charset.lower() == "custom":
        custom_charset = input("Enter a custom character set: ")
        if not custom_charset:
            print("Custom character set cannot be empty.")
            return
    else:
        custom_charset = None

    if args.filename is not None:
        filename = args.filename
    else:
        filename = "codes_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"

    try:
        cg = CodeGenerator(args.count, args.length, args.prefix, args.suffix)

        cg.build_character_set(
            args.charset, args.case, args.omit, args.add, custom_charset
        )

        cg.build_file(filename, args.maxlines, args.encoding)

        cg.run()

    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\nCodes saved successfully.")


if __name__ == "__main__":
    main()
