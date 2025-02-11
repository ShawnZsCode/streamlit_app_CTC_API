# from core.main_entry import main
import asyncio

# asyncio.run(main())
from ctc.api_sessions import (
    get_sessions,
    get_active_session,
    set_active_session,
    RevitSessions,
    RevitSession,
)

from utils.file_utils import write_file_json

if __name__ == "__main__":
    #     import asyncio

    #     sessions: RevitSessions = asyncio.run(get_sessions())
    #     print(sessions)
    #     port = sessions["Sessions"][0]["Port"]
    #     asyncio.run(set_active_session(Port=port))
    #     session_active = asyncio.run(get_active_session())
    #     print(session_active)
    from typing import List
    from ctc.data_models.categories import RevitCategories, RevitCategory
    from ctc.data_models.families import RevitFamily
    from ctc.data_models.elements import RevitElement
    from ctc.api_sessions import get_active_session
    from ctc.api_categories import get_categories
    from ctc.api_famlies import get_families
    from ctc.api_elements import get_elements
    from datetime import datetime
    from ctc.data_models.parameters import ParameterSimple

    # from utils.file_utils import read_file_csv
    import csv

    # print(read_file_json("data/definitions.json"))
    # print(read_file_csv("ctc/Category_2025.csv"))
    session = asyncio.run(get_active_session())
    project: RevitCategories = asyncio.run(get_categories())

    for category in project.Categories:
        # Get the families for the category
        result_val = asyncio.run(
            get_families(
                session=session,
                category=category,
            )
        )
        c = project.get_category_index(category)
        project.Categories[c] = result_val["result"]

        # Get the elements for the category
        result_val = asyncio.run(
            get_elements(
                session=session,
                category=category,
            )
        )
        project.Categories[c] = result_val["result"]

    category_doors = project.get_category_by_name("doors")
    # door_param_list = category_doors.get_parameter_list()
    # print(category.model_dump())
    sub_folder = datetime.now().strftime("%Y%m%d")
    write_file_json(
        stream=project.model_dump(),
        file_name=f"{session.Port}_{session.RevitVersion}_{session.ActiveProject}",
        folder=f"{sub_folder}",
    )
