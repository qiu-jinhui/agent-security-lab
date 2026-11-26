
def aggregate_person_name_parts(predictions, text):

    predictions = set(predictions)

    name_parts = sorted(
        [
            item for item in predictions
            if item[0] == "PERSON_NAME_PART"
        ],
        key=lambda x: x[1]
    )

    if not name_parts:
        return predictions

    groups = []
    current_group = [name_parts[0]]

    for item in name_parts[1:]:

        previous = current_group[-1]

        gap = text[previous[2]:item[1]]

        if gap.isspace() and gap:
            current_group.append(item)
        else:
            groups.append(current_group)
            current_group = [item]

    groups.append(current_group)

    # Remove original name parts from evaluation set.
    predictions = {
        item for item in predictions
        if item[0] != "PERSON_NAME_PART"
    }

    for group in groups:

        if len(group) >= 2:

            start = group[0][1]
            end = group[-1][2]

            predictions.add(
                ("PERSON", start, end)
            )

        else:
            # Do not invent a complete person span.
            predictions.add(group[0])

    return predictions
