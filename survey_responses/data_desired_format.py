import pandas as pd
import numpy as np
import sys
import re


# Keep only desired columns
def columns_to_keep(df, columns):
    # Getting all those columns from 'columns' that actually exist in 'df'
    existing_columns = [col for col in columns if col in df.columns]
    return df[existing_columns]


def pad_sublists(data, max_length):
    return [sublist + [None] * (max_length - len(sublist)) for sublist in data]


def condense_data(data):
    def process_question(i, item):
        if "BFxCH" in item:
            m1_m2_confq = bf_ch_confq
            m1_m2_value = bf_ch_value
        elif "HPxCH" in item:
            m1_m2_confq = hp_ch_confq
            m1_m2_value = hp_ch_value
        elif "HPxTR" in item:
            m1_m2_confq = hp_tr_confq
            m1_m2_value = hp_tr_value
        elif "TRxCH" in item:
            m1_m2_confq = tr_ch_confq
            m1_m2_value = tr_ch_value
        elif "TRxTR" in item:
            m1_m2_confq = tr_tr_confq
            m1_m2_value = tr_tr_value

        conf_values[i] = df.loc[index, m1_m2_confq]

        choice_ord[i] = df.loc[index, m1_m2_value + "_DO"]

        first_agent_rating = df.loc[index, m1_m2_value + "_1"]
        second_agent_rating = df.loc[index, m1_m2_value + "_2"]
        r0 = df.loc[index, m1_m2_value + "_DO"].split("|")[0]
        r1 = df.loc[index, m1_m2_value + "_DO"].split("|")[1]

        if "Alex" in r0:
            alex_value[i] = first_agent_rating
            ap5_value[i] = second_agent_rating
        elif "AP-5" in r0:
            ap5_value[i] = first_agent_rating
            alex_value[i] = second_agent_rating

    # Data from Qualtrics is very sparse since our survey has so many questions
    # this function converts it into a condensed form
    df = data.copy(deep=True)

    # Initialize empty lists to store values for new columns
    (
        tutorial_values,
        display_order_values,
        DO_values,
        traj_order_values,
        bf_ch,
        hp_ch,
        hp_tr,
        tr_ch,
        tr_tr,
        alex,
        ap5,
        choice_order,
        conf,
    ) = ([] for i in range(13))

    # Flag to indicate if we have not found the display order yet
    order_flag = True

    # Flag to indicate if we're in the last phase of processing
    last_phase = False

    # Iterate through each row
    for index, row in df.iterrows():
        tutorial_value = (
            display_order_value
        ) = (
            DO_value
        ) = (
            traj_order_value
        ) = (
            bf_ch_value
        ) = (
            hp_ch_value
        ) = (
            hp_tr_value
        ) = (
            tr_ch_value
        ) = (
            tr_tr_value
        ) = bf_ch_confq = hp_ch_confq = hp_tr_confq = tr_ch_confq = tr_tr_confq = None

        question_counter, conf_counter = 0, 0

        alex_value, ap5_value, choice_ord, conf_values = ([0] * 5 for i in range(4))

        # Start from 'Q4' column and find the next column with a value
        for column in df.columns[df.columns.get_loc("Q4") :]:
            if not pd.isnull(row[column]):
                # Extract corresponding 'tut' column name
                # i.e., which tutorial that participant was shown
                if column.startswith("tut-"):
                    tutorial_value = column

                # Getting the display order
                # i.e., the randomized order in which questions were displayed
                if column.endswith("_DO") and column.startswith("FL_"):
                    display_order_value = row[column]
                    if row[column].startswith("factual-cf-"):
                        q1, q2, q3, q4, q5 = display_order_value.split("|")
                    DO_value = column

                # Extracting the question IDs of the specific combination questions (BFxCH/HPxCH/HPxTR/..) the participant was shown
                # and IDs of associated confidence questions
                if column.endswith("_DO") and (
                    column.startswith("factual-full")
                    or column.startswith("factual-partial")
                ):
                    traj_order_value = row[column]
                elif column.endswith("BFxCH-questions_DO") and (
                    len(row[column].split("|")) == 2
                ):
                    bf_ch_value, bf_ch_confq = row[column].split("|")
                elif column.endswith("HPxCH-questions_DO") and (
                    len(row[column].split("|")) == 2
                ):
                    hp_ch_value, hp_ch_confq = row[column].split("|")
                elif column.endswith("HPxTR-questions_DO") and (
                    len(row[column].split("|")) == 2
                ):
                    hp_tr_value, hp_tr_confq = row[column].split("|")
                elif column.endswith("TRxCH-questions_DO") and (
                    len(row[column].split("|")) == 2
                ):
                    tr_ch_value, tr_ch_confq = row[column].split("|")
                elif column.endswith("TRxTR-questions_DO") and (
                    len(row[column].split("|")) == 2
                ):
                    tr_tr_value, tr_tr_confq = row[column].split("|")

                questions = [
                    bf_ch_value,
                    hp_ch_value,
                    hp_tr_value,
                    tr_ch_value,
                    tr_tr_value,
                ]

        if traj_order_value and len(traj_order_value.split("|")) == 10:
            traj_order_value_list = traj_order_value.split("|")
            counter = 0
            for i in range(0, len(traj_order_value_list), 2):
                choice_ord[counter] = df.loc[index, traj_order_value_list[i] + "_DO"]

                conf_values[counter] = df.loc[index, traj_order_value_list[i + 1]]
                conf_counter += 1

                first_agent_rating = df.loc[index, traj_order_value_list[i] + "_1"]
                second_agent_rating = df.loc[index, traj_order_value_list[i] + "_2"]
                r0 = df.loc[index, traj_order_value_list[i] + "_DO"].split("|")[0]
                r1 = df.loc[index, traj_order_value_list[i] + "_DO"].split("|")[1]

                if "Alex" in r0:
                    alex_value[counter] = first_agent_rating
                    ap5_value[counter] = second_agent_rating
                elif "AP-5" in r0:
                    ap5_value[counter] = first_agent_rating
                    alex_value[counter] = second_agent_rating

                counter += 1

        elif display_order_value and "|" in display_order_value:
            display_order_list = display_order_value.split("|")

            for i, item in enumerate(display_order_list):
                process_question(i, item)
                conf_counter += 1

        # Append values to lists
        tutorial_values.append(tutorial_value)
        display_order_values.append(display_order_value)
        DO_values.append(DO_value)
        traj_order_values.append(traj_order_value)
        bf_ch.append(bf_ch_value)
        hp_ch.append(hp_ch_value)
        hp_tr.append(hp_tr_value)
        tr_ch.append(tr_ch_value)
        tr_tr.append(tr_tr_value)
        alex.append(alex_value)
        ap5.append(ap5_value)
        choice_order.append(choice_ord)
        conf.append(conf_values)

    # Add new columns to the DataFrame
    df["tutorial"] = tutorial_values
    df["acra_display_order"] = display_order_values
    df["DO"] = DO_values
    df["factual_only_traj_display_order"] = traj_order_values
    df["BFxCH_traj"] = bf_ch
    df["HPxCH_traj"] = hp_ch
    df["HPxTR_traj"] = hp_tr
    df["TRxCH_traj"] = tr_ch
    df["TRxTR_traj"] = tr_tr

    max_length = 5

    # Pad sublists with None or NaN to make their lengths consistent
    padded_data_alex = pad_sublists(alex, max_length)
    padded_data_ap5 = pad_sublists(ap5, max_length)
    padded_data_choice_ord = pad_sublists(choice_order, max_length)
    padded_data_conf = pad_sublists(conf, max_length)

    # Convert padded list of lists to DataFrame with appropriate column names
    new_columns = [f"Alex_rating_Q{i+1}" for i in range(max_length)]
    new_df = pd.DataFrame(padded_data_alex, columns=new_columns)

    new_columns_ap5 = [f"AP5_rating_Q{i+1}" for i in range(max_length)]
    new_df_ap5 = pd.DataFrame(padded_data_ap5, columns=new_columns_ap5)

    new_columns_choice_ord = [f"agent_display_ord_Q{i+1}" for i in range(max_length)]
    new_df_choice_ord = pd.DataFrame(
        padded_data_choice_ord, columns=new_columns_choice_ord
    )

    new_columns_conf = [f"confidence_rating_Q{i+1}" for i in range(max_length)]
    new_df_conf = pd.DataFrame(padded_data_conf, columns=new_columns_conf)

    # Concatenate existing DataFrame with new DataFrame along columns axis
    df = pd.concat([df, new_df], axis=1)
    df = pd.concat([df, new_df_ap5], axis=1)
    df = pd.concat([df, new_df_choice_ord], axis=1)
    df = pd.concat([df, new_df_conf], axis=1)

    # Dropping sparse columns from which we have already extracted all relevant info
    df = drop_columns(df, "tut-fact-partial-Q3", "QID452")
    df = drop_columns(
        df, "FL_3_DO", "factual-cf-both-agents-full-biased_none-TRxTR-questions_DO"
    )

    # Write to a new CSV file
    # df.to_csv(file_name, index=False)
    return df


def drop_columns(data, start, stop):
    start_index = data.columns.get_loc(start)
    end_index = data.columns.get_loc(stop)

    # Remove columns between start and end index
    return data.drop(data.columns[start_index : end_index + 1], axis=1)


# Get the number after 'traj-'
def extract_traj_number(cell_value):
    if pd.isna(cell_value):
        return None
    elif len(cell_value) <= 3:
        return int(cell_value)
    elif len(cell_value) == 4:
        return int(cell_value.split("-")[0])
    elif len(cell_value) == 5:
        return int(cell_value.split("-")[0])

    match = re.search(r"traj-(\d+)", cell_value)
    return int(match.group(1)) if match else None


def extract_responsibilities(file_path, series_number):
    responsibilities = {"Agent 0": None, "Agent 1": None}
    series_found = False
    agent = None

    with open(file_path, "r") as file:
        lines = file.readlines()

    for idx, line in enumerate(lines, 1):
        if f"Trajectory {series_number}" in line:
            series_found = True
            line_number = idx

            ag0_line = lines[line_number + 2]
            responsibility = float(ag0_line.split(":")[1].strip())
            responsibilities["Agent 0"] = responsibility

            ag1_line = lines[line_number + 48]

            if "Agent 1" in ag1_line:
                ag1_line = lines[line_number + 49]
                responsibility = float(ag1_line.split(":")[1].strip())
                responsibilities["Agent 1"] = responsibility

            elif "Degree of responsibility:" in ag1_line:
                responsibility = float(ag1_line.split(":")[1].strip())
                responsibilities["Agent 1"] = responsibility

        if series_found:
            return responsibilities

    return responsibilities


def get_path(bias, base_path):
    if str(bias) == "0":
        return base_path + "biased_0/N5/"
    elif str(bias) == "1":
        return base_path + "biased_1/N5/"
    elif bias == "none":
        return base_path + "biased_none/N5/"


def wide_to_long_format(data):
    cols = [
        "ResponseId",
        "Duration (in seconds)",
        "PROLIFIC_PID",
        "num_counterfactuals",
        "info",
        "CF",
        "bias",
        "agent-CF",
        "acra_display_order",
        "factual_only_traj_display_order",
        "traj_number",
        "Alex_rating",
        "AP5_rating",
        "confidence",
        "BFxCH_traj",
        "HPxCH_traj",
        "HPxTR_traj",
        "TRxCH_traj",
        "TRxTR_traj",
    ]

    new_df_cols = [
        "ResponseId",
        "Duration (in seconds)",
        "PROLIFIC_PID",
        "num_counterfactuals",
        "info",
        "CF",
        "bias",
        "agent-CF",
        "acra_assigned",
        "acra_display_order",
        "factual_only_traj_display_order",
        "traj_number",
        "Alex_rating",
        "AP5_rating",
        "confidence",
    ]

    df = pd.DataFrame(columns=new_df_cols)

    for index, row in data.iterrows():
        factual = 0

        for i in range(5):
            q = "Q" + str(i + 1)
            alex = row["Alex_rating_" + q]
            ap5 = row["AP5_rating_" + q]
            conf = row["confidence_rating_" + q]

            if row["CF"] in ["2-CF", "1-CF"]:
                traj = row["acra_display_order"].split("|")[i].split("-")[-2]
                traj_num = row[traj + "_traj"]

                row["acra_assigned"] = traj

                values = [
                    row["ResponseId"],
                    row["Duration (in seconds)"],
                    row["PROLIFIC_PID"],
                    row["num_counterfactuals"],
                    row["info"],
                    row["CF"],
                    row["bias"],
                    row["agent-CF"],
                    row["acra_assigned"],
                    row["acra_display_order"],
                    row["factual_only_traj_display_order"],
                    traj_num,
                    alex,
                    ap5,
                    conf,
                ]

                new_row = pd.DataFrame([values], columns=new_df_cols)

                df = pd.concat([df, new_row], ignore_index=True)

            elif row["CF"] == "factual":
                traj_num = (
                    row["factual_only_traj_display_order"].split("|")[factual]
                    # .split("-", 1)
                )
                factual += 2
                row["acra_assigned"] = " "

                values = [
                    row["ResponseId"],
                    row["Duration (in seconds)"],
                    row["PROLIFIC_PID"],
                    row["num_counterfactuals"],
                    row["info"],
                    row["CF"],
                    row["bias"],
                    row["agent-CF"],
                    row["acra_assigned"],
                    row["acra_display_order"],
                    row["factual_only_traj_display_order"],
                    traj_num,
                    alex,
                    ap5,
                    conf,
                ]

                new_row = pd.DataFrame([values], columns=new_df_cols)

                df = pd.concat([df, new_row], ignore_index=True)

    return df


# Extract agent responsibilities for a particular trajectory
def extract_responsibilities(file_path, series_number):
    responsibilities = {"Agent 0": None, "Agent 1": None}
    series_found = False
    agent = None

    with open(file_path, "r") as file:
        lines = file.readlines()

    for idx, line in enumerate(lines, 1):
        if f"Trajectory {series_number}" in line:
            series_found = True
            line_number = idx

            ag0_line = lines[line_number + 2]
            responsibility = float(ag0_line.split(":")[1].strip())
            responsibilities["Agent 0"] = responsibility

            ag1_line = lines[line_number + 48]

            if "Agent 1" in ag1_line:
                ag1_line = lines[line_number + 49]
                responsibility = float(ag1_line.split(":")[1].strip())
                responsibilities["Agent 1"] = responsibility

            elif "Degree of responsibility:" in ag1_line:
                responsibility = float(ag1_line.split(":")[1].strip())
                responsibilities["Agent 1"] = responsibility

        if series_found:
            return responsibilities

    return responsibilities


def get_actual_responsibility(data):
    base_path = "human-perceptions-of-accountable-ai-code-main/combinations_results/"

    for index, row in data.iterrows():
        traj = row["traj_number"]
        bias = row["bias"]

        if str(bias) == "0":
            path = base_path + "biased_0/N5/"
        elif str(bias) == "1":
            path = base_path + "biased_1/N5/"
        else:
            path = base_path + "biased_none/N5/"

        traj_number = extract_traj_number(traj)

        combos = ["BFxCH", "HPxCH", "HPxTR", "TRxCH", "TRxTR"]

        for combo in combos:
            file_path = path + combo + ".txt"
            responsibilities = extract_responsibilities(file_path, traj_number)

            col0 = combo + "_Alex_rating_traj"
            col1 = combo + "_AP5_rating_traj"

            data.loc[index, col0] = responsibilities["Agent 0"]
            data.loc[index, col1] = responsibilities["Agent 1"]

            # Agreement = ½[Ind{rA1(calculated) == rA1(reported)} + Ind{rA2(calculated) == rA2(reported)}]
            alex = (
                row["Alex_rating"]
                .replace("Low Responsibility", str(0))
                .replace("Medium Responsibility", str(0.5))
                .replace("High Responsibility", str(1))
            )
            ap5 = (
                row["AP5_rating"]
                .replace("Low Responsibility", str(0))
                .replace("Medium Responsibility", str(0.5))
                .replace("High Responsibility", str(1))
            )

            ag_alex = responsibilities["Agent 0"] == float(alex)
            ag_ap5 = responsibilities["Agent 1"] == float(ap5)

            ag_alex = float(ag_alex)
            ag_ap5 = float(ag_ap5)

            # Calculate the final value
            agreement = 0.5 * (ag_alex + ag_ap5)
            col_ag = combo + "_agreement"

            data.loc[index, col_ag] = agreement

        data.loc[index, "trajectory"] = traj_number

    return data


def main():
    ## Read in responses from Qualtrics
    data = pd.read_csv(str(sys.argv[1]))

    base_file = "cleaned_data/" + str(sys.argv[2]) + "_condensed_data_"
    file_name = base_file + "all_wide_format.csv"
    df_all_cols = condense_data(data)

    # Write dataframe with all data in condensed form
    df_all_cols.to_csv(file_name, index=False)

    necessary_cols = [
        "ResponseId",
        "Duration (in seconds)",
        "PROLIFIC_PID",
        "num_counterfactuals",
        "info",
        "CF",
        "bias",
        "agent-CF",
        "acra_display_order",
        "factual_only_traj_display_order",
        "Alex_rating_Q1",
        "Alex_rating_Q2",
        "Alex_rating_Q3",
        "Alex_rating_Q4",
        "Alex_rating_Q5",
        "AP5_rating_Q1",
        "AP5_rating_Q2",
        "AP5_rating_Q3",
        "AP5_rating_Q4",
        "AP5_rating_Q5",
        "confidence_rating_Q1",
        "confidence_rating_Q2",
        "confidence_rating_Q3",
        "confidence_rating_Q4",
        "confidence_rating_Q5",
        "BFxCH_traj",
        "HPxCH_traj",
        "HPxTR_traj",
        "TRxCH_traj",
        "TRxTR_traj",
    ]

    ## Select only the required columns to keep
    df_filtered = df_all_cols.loc[:, necessary_cols]

    df = wide_to_long_format(df_filtered)

    resp_file = base_file + "with_responsibilities_long_format.csv"
    df_resp = get_actual_responsibility(df)

    df_resp.to_csv(resp_file, index=False)


if __name__ == "__main__":
    main()
