def process(document):
    # transform json document elements into array of lines of text
    body = document["body"]

    lines = []
    for p in body["content"]:
        if "paragraph" in p:
            style = p["paragraph"]["paragraphStyle"]
            line = {
                "text": "",
                "style": style["namedStyleType"],
                "indent": 0,
                "bullet": 0,
            }
            if "indentStart" in style:
                if "magnitude" in style["indentStart"]:
                    line["indent"] = style["indentStart"]["magnitude"] // 36
            if "bullet" in p["paragraph"]:
                if line["style"] != "NORMAL_TEXT":
                    raise Exception('ERROR: bulleted item is not of "normal_text" type')
                line["bullet"] = 1
            for e in p["paragraph"]["elements"]:
                line["text"] += e["textRun"]["content"].strip()
            lines.append(line)

    return lines


def get_picture(lines):
    # text comes after word 'PICTURE: ' and starts after first empty line
    picture = ""
    for lix, l in enumerate(lines):
        l = l["text"]
        if "PICTURE:" in l:
            picture = l.split("PICTURE: ")[1]
            continue
        if picture and l == "":
            i_pic_end = lix
            break
        if picture:
            picture += l

    return picture, i_pic_end


def get_i_choices(lines, i_pic_end):
    i_choices = []
    for lix, l in enumerate(lines[i_pic_end + 1 :]):
        if not l["text"].split():
            continue
        if l["style"] == "HEADING_4" and not l["bullet"]:
            # first word is all caps indicating a choice
            i_choices.append(lix + i_pic_end + 1)

    return i_choices


def get_choices(lines, i_choices):
    choices = []
    for ix, i in enumerate(i_choices[:-1]):
        choice = {"text": "", "days": "", "outcomes": []}
        # get choice name and duration
        if "DAYS" in lines[i]["text"]:
            # days may not be specified
            choice["text"] = lines[i]["text"].split(" (")[0]
            choice["days"] = int(lines[i]["text"].split(" (")[1].replace(" DAYS)", ""))
        else:
            choice["text"] = lines[i]["text"]

        # get outcomes
        outcome = {}
        for lix, l in enumerate(lines[i : i_choices[ix + 1]]):
            if l["indent"] == 1:
                # comment
                if l["bullet"]:
                    if outcome:
                        choice["outcomes"].append(outcome)
                    outcome = {
                        "comment": l["text"],
                    }
            elif l["indent"] == 2:
                # text
                if l["bullet"]:
                    # start of text
                    k1, k2 = "POST-MISSION-FAILED:", "POST-MISSION:"
                    if k1 in l["text"]:
                        outcome["post-mission-failed"] = l["text"].replace(k1, "")
                    elif k2 in l["text"]:
                        outcome["post-mission"] = l["text"].replace(k2, "")
                    else:
                        outcome["text"] = l["text"]
                else:
                    outcome["text"] += l["text"] if l["text"] else "\n"
        outcome["text"] = outcome["text"].strip()
        choice["outcomes"].append(outcome)

        choices.append(choice)

    return choices


def parse(document):
    parsed = {"title": document["title"].strip()}

    try:
        lines = process(document)
    except Exception as e:
        print(e)
        return

    picture, i_pic_end = get_picture(lines)
    parsed["picture"] = picture

    i_choices = get_i_choices(lines, i_pic_end)
    # add index representing end of final choice
    i_choices += [len(lines)]

    # value of 'text' appears between picture and first choice
    parsed["text"] = " ".join([l["text"] for l in lines[i_pic_end + 1 : i_choices[0]]])

    choices = get_choices(lines, i_choices)
    parsed["choices"] = choices

    return parsed
