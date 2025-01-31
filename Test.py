# from core.main_entry import main

# asyncio.run(main())
from ctc.api_sessions import (
    get_sessions,
    get_active_session,
    set_active_session,
    RevitSessions,
)

if __name__ == "__main__":
    #     import asyncio

    #     sessions: RevitSessions = asyncio.run(get_sessions())
    #     print(sessions)
    #     port = sessions["Sessions"][0]["Port"]
    #     asyncio.run(set_active_session(Port=port))
    #     session_active = asyncio.run(get_active_session())
    #     print(session_active)

    from ctc.data_models.categories import RevitCategories, RevitCategory

    # from utils.file_utils import read_file_csv
    import csv

    # print(read_file_json("data/definitions.json"))
    # print(read_file_csv("ctc/Category_2025.csv"))
    file_path = "ctc/Category_2025.csv"
    with open(file_path, "r") as open_file:
        open_file = csv.DictReader(open_file)
        categories: RevitCategories = RevitCategories()
        for row in open_file:
            if row["IsObsolete"] == "FALSE":
                category = RevitCategory.model_validate(row)
                categories.Categories.append(category)
    print(categories.model_dump())
