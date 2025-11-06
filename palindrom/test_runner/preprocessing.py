## version 1.0

from test_runner.configs import configs
import re
regex_loop = r"( *)((for|while).*:)\n( *)"

regex_def = r"( *)(def.*:)"

loop_counter = 0


def inject_loop(match):
    global loop_counter
    out = f"{match.group(1)}{match.group(2)}\n" + \
        f"{match.group(4)}{configs['loop_name']}[{loop_counter}] += 1\n" + \
        f"{match.group(4)}"

    # f"{match.group(1)}{match.group(3)}{configs["loop_name"]}[{loop_counter}] += 1\n" + \

    loop_counter += 1
    return out


def inject_global(match):
    out = match.group(0) + "\n" + \
        match.group(1) + \
        "    global {array}\n".format(array=configs["loop_name"])
    return out


def process(original="main.py", destination="temp.py"):
    result = ""
    with open(original, "r") as file:
        result = file.read()

    result = re.sub(regex_loop, inject_loop, result)

    result = re.sub(regex_def, inject_global, result)

    init = "{array} = [0] * {var}\n".format(
        array=configs["loop_name"], var=loop_counter)
    result = init + result

    with open(destination, "w") as file:
        file.write(result)

    return result
