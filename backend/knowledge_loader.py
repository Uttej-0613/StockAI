def load_knowledge():

    knowledge = []

    try:
        with open("../data/knowledge.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    knowledge.append(line)

    except Exception as e:
        print("Error loading knowledge file:", e)

    return knowledge