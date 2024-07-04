import json
import boto3
import io
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


########## FUNCTIONS I NEED
def insert_error_df(ColumnPos, ColumnName, Desc1, WrongV, Desc2, df):
    # params 'ColumnPosition': int 'ColumnName': '', 'Description': '', 'WrongValue': 'A', 'SuggestedChange': ''

    new_value = {
        "ColumnPosition": ColumnPos,
        "ColumnName": ColumnName,
        "Description": Desc1,
        "WrongValue": WrongV,
        "SuggestedChange": Desc2,
    }

    df_new_row = pd.DataFrame([new_value])

    # Append the new row to the DataFrame
    df = pd.concat([df, df_new_row], ignore_index=True)

    return df


def find_header_row(xls_file):  # , tab_name):
    """
    Find the header row in the specified tab_name of the xls_file.
    """
    # Read the Excel file and select the specified tab
    # xlsx_data = pd.read_excel(io.BytesIO(xlsx_content), sheet_name=selected_tab)

    # Iterate through each row to find the first row where all columns have a non-null value
    for index, row in xls_file.iterrows():  # ponia df
        if row.notnull().all():
            return index, row[0], row[1], row  # Return the index of the header row

    return None  # If no header row is found


def read_and_filter_excel(df, my_range, my_row):

    df_temp = df.iloc[my_row:]

    # Assuming 'df' is your original DataFrame and 'my_list' is the list of column indices
    df_result = df_temp.iloc[:, my_range].copy()
    df_result.columns = df_temp.columns[my_range]

    return df_result


def analyse_multilines(my_def, main_df):
    # 1st - multiple line in header

    multiple_lines = len(
        [element for element in my_def.iloc[0] if "\n" in str(element)]
    )
    if multiple_lines > 0:
        message1 = "Multiple Lines are not accepted as headers"
        message2 = "Make sure there are no multiple lines in the whole document"
        main_df = insert_error_df(
            0, "General Error", message1, "MultiLines", message2, main_df
        )

    return main_df


def invoke_lambda(function_name, payload):
    """
    Invokes a Lambda function with the given payload.
    """
    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(FunctionName=function_name, Payload=payload)

    return response


###########################
def lambda_handler(event, context):

    query_params = event["queryStringParameters"]
    s3_bucket = "inova-input"  # record["s3"]["bucket"]["name"]
    s3_key = query_params["fileid"]  # record["s3"]["object"]["key"]

    # debajo lo que he borrado
    try:
        ########## VARS AND SET UPs ##############
        number_list = []
        Errors_df = pd.DataFrame()

        parts = s3_key.split("___")
        selected_tab = parts[0]
        remaining = parts[1]
        remaining_parts = remaining.split("_")
        diagCol = int(remaining_parts[0])
        # print(remaining_parts[1])
        my_list = remaining_parts[1].split(".")[:-1]

        # Check if the S3 object exists
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=s3_bucket, Key=s3_key)

        xlsx_content = obj["Body"].read()
        xlsx_data = pd.read_excel(
            io.BytesIO(xlsx_content), sheet_name=selected_tab, header=None
        )

        ############ MAIN CODE #############

        header_row, first_col_value, second_col_value, all_row = find_header_row(
            xlsx_data
        )

        if header_row is not None:
            # print(f"Header row found at index {header_row}: First column: {first_col_value}, Second column: {second_col_value}")

            if header_row > 0:
                message1 = "Header is found in row:" + str(header_row + 1)
                message2 = "Delete all rows above 1 to " + str(header_row)
                Errors_df = insert_error_df(
                    0, "General Error", message1, None, message2, Errors_df
                )

            else:
                message1 = "No headers found in the excel"
                message2 = "make sure row 0 has all the headers with no empty tittle"
                Errors_df = insert_error_df(
                    0, "General Error", message1, None, message2, Errors_df
                )

            ### managing selected columns
            print("my_list[0]")
            print(my_list[0])
            if my_list[0] != "all":
                number_list = [int(num) for num in my_list]
            else:
                number_list = range(1, len(all_row))

            print("number_list")
            print(str(number_list))

            df_filtered = read_and_filter_excel(xlsx_data, number_list, header_row)

            ### Check multilines ######
            Errors_df = analyse_multilines(df_filtered, Errors_df)

            ## Now we need to call a function for each column
            ## keep in mind that there is extra code to do in
            ## * the first column that should be PK () --> check_pk(my_def, main_df) using currently_in_first_column)
            ## * the diagn column that should be binary --> check_pk(my_def, main_df)
            ## * all that packed in a funct like:
            ## main_df, col_val = process_colunn(column_name, column_data, main_df, diag_column, col_val) #

            ### Invoke N Lambda functions in parallel #######
            with ThreadPoolExecutor(max_workers=len(number_list)) as executor:
                # with concurrent.futures.ThreadPoolExecutor() as executor:

                futures = []
                merged_result = {}
                currently_in_first_column = 1

                for index, (column_name, column_data) in enumerate(df_filtered.items()):

                    payload = {
                        "order": number_list[index],
                        "column": column_name,
                        "data": column_data.tolist(),
                        "diag": diagCol,
                        "pk": currently_in_first_column,
                        # ,df_errors?
                    }
                    currently_in_first_column = 0
                    futures.append(
                        executor.submit(
                            invoke_lambda,
                            "inova-ProcessStudies_column-sam",
                            json.dumps(payload),
                        )
                    )

                # Collect the responses from the 'aaa' Lambda function calls
                responses = []
                responses.append(Errors_df.to_json(orient="records"))
                # for future in futures.as_completed(futures):
                for future in as_completed(futures):
                    try:
                        response = future.result()
                        lambda_answer = json.load(response["Payload"])

                        if lambda_answer["statusCode"] == 5227:
                            responses.append(lambda_answer["body"])

                    except Exception as e:
                        # Handle any exceptions that occurred during the calls
                        print(f"Error  Lambda function: {e}")

                combined_list = []
                for json_str in responses:
                    combined_list.extend(json.loads(json_str))

            final_json = json.dumps(combined_list, indent=2)
            print(final_json)

            # Delete the obtained file from the S3 bucket
            s3.delete_object(Bucket=s3_bucket, Key=s3_key)
            print(f"Deleted file: {s3_key}")
            ####################################
            return {
                "statusCode": 200,
                "body": json.dumps(final_json),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
            }

    except Exception as e:
        print(f"Error Studies: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps("Error processing file"),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }
