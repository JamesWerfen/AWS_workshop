import json
import pandas as pd
from collections import Counter


### FUNCTIONS I NEED ###
def check_unique_values(
    column_values, percent
):  # this functions returns 1 if stadistically this is free text
    # if more the unique values are more than percent% (default 20)
    # column_values = df.iloc[:, column_index]
    # oldtotal_unique_values = len(set(column_values[1:])) #Calcula el número total de valores únicos
    # oldvalue_counts = len(column_values[1:]) #Crea una serie que contiene el recuento de cada valor único en la columna.
    my_series = pd.Series(column_values[1:])
    total_unique_values = my_series.nunique()

    # Create a series that contains the count of each unique value in the list
    value_counts = my_series.value_counts()

    single_occurrence_percentage = (value_counts == 1).sum() / total_unique_values * 100

    # Calculate the percentage of unique values that appear only once
    if total_unique_values > 0:
        # Esto cuenta cuántos valores únicos tienen una frecuencia de 1 / total de valores unicos
        single_occurrence_percentage = (
            (value_counts == 1).sum() / total_unique_values * 100
        )
    else:
        single_occurrence_percentage = 0

    # Check if the percentage exceeds percent%
    if single_occurrence_percentage > percent:
        return 1
    else:
        return 0


def analyze_column(order, column, main_df):  # , ColumnValues):
    total_values = len(column) - 1
    float_count = 0
    int_count = 0
    datetime_count = 0
    string_count = 0
    #####
    float_percent = 0
    int_percent = 0
    datetime_percent = 0
    string_percent = 0
    most_common_values = 0
    list_strings = []
    list_odd = []
    l_constant_odd_words = [
        "-",
        "/",
        "-",
        "not",
        "image",
        "nan",
        "no ",
        "cbc",
        "lbc",
        "ooc",
        "ss",
        "rll",
        "nd",
        "ns",
        "*",
    ]
    list_accepted = ["ssc"]
    #####

    for value_ori in column[1:]:

        value = value_ori
        """
        value = str(value_ori).replace('----','')
        value = str(value).replace('not tested','')
        value = str(value).replace('NO IMAGE','')
        value = str(value).replace('no information','')
        value = str(value).replace('NO RESULT','')
        value = str(value).replace('nan','')
        if str(value)== 'SS':
           pepe = 1        
        value = str(value).replace('lbc','')
        value = str(value).replace('LBC','')
        value = str(value).replace('lcbc','')
        value = str(value).replace('LCBC','')      
        value = str(value).replace('ooc','')
        value = str(value).replace('OOC','')                          
        value = str(value).replace('ss','')
        value = str(value).replace('SS','')           
        value = str(value).replace('LCBMFI','')           
        value = str(value).replace('RLLSE','')           
        value = str(value).replace('ND','') 
        value = str(value).replace('NS','')                
        value = str(value).replace('***','')
        value = str(value).replace('**','')                
        """
        try:
            int(value)
            int_count += 1
        except ValueError:
            # antes if str(value[-2:]) == '.0':
            if str(value)[-2:] == ".0":
                int_count += 1
            else:
                try:
                    import math

                    if math.isnan(float(value)):
                        float_count -= 1
                        string_count += 1
                    #    value = 'nan'
                    #    raise ValueError
                    # else:
                    float(value)
                    float_count += 1
                except ValueError:
                    # try:
                    #    pd.to_datetime(value)
                    #    datetime_count += 1
                    # except ValueError:
                    if str(value) == "":
                        total_values = total_values - 1
                    else:
                        if value not in list_strings:
                            list_strings.append(value)

                        if (
                            value.lower() not in list_accepted
                            and value not in list_odd
                            and any(
                                word in value.lower() for word in l_constant_odd_words
                            )
                        ):
                            list_odd.append(value)

                        if "\n" in str(value):
                            message1 = "Multi line value not accepted"
                            message2 = "Convert it to simple line"
                            main_df = insert_error_df(
                                order, column[0], message1, value_ori, message2, main_df
                            )

                        string_count += 1

        float_percent = (float_count / total_values) * 100
        int_percent = (int_count / total_values) * 100
        datetime_percent = (datetime_count / total_values) * 100
        string_percent = (string_count / total_values) * 100

        most_common_values = Counter(column).most_common(8)

    if (string_percent >= 100) and len(
        list_odd
    ) > 0:  # todo string en vez de no dar error sugiero que miren los odd si es que parece categorizada
        if (
            check_unique_values(column, 20) == 0
        ):  # 20 is the percentage I set for free text
            # seems categorized column I suggest only odds
            message1 = "Review this field"
            message2 = "it might be not a categorized value and consider set it as null"
            for elementodd in list_odd:
                main_df = insert_error_df(
                    order, column[0], message1, elementodd, message2, main_df
                )
        # else no error because it is considered free text

    if (float_percent + int_percent > 0) and (string_percent > 0):
        if string_percent < 50:
            message1 = "Text found in numeric field"
            message2 = "we suggest to leave this value null"
            # print(list_strings)
            for elemento in list_strings:
                main_df = insert_error_df(
                    order, column[0], message1, elemento, message2, main_df
                )
        """ caso con muuucha letra y algunos numeros, no dare de momento error asumiendo texto libre.
            else:
                if check_unique_values(column, 20) == 0: #checks % of unique values ... and compare if it is more that xx% (returns 0 or 1)                                    
                    message1 = 'Text found in numeric field'
                    message2 = 'we suggest to leave this value null'
                    #print(list_strings)
                    for elemento in list_strings:
                        main_df = insert_error_df(colnam, str(column.iloc[0]),message1, elemento, message2, main_df)                     
            """
    # calculate ColumnValues
    # my_list = list(column.unique()[1:11])

    # Esto devuelve la lista de valores de la columna distintos creoColumnValues[colnam] = my_list

    # return {
    #    'float_percent': float_percent,
    #    'int_percent': int_percent,
    #    'datetime_percent': datetime_percent,
    #    'string_percent': string_percent,
    #    'most_common_values': most_common_values
    # } , main_df#de momento lo comento, ColumnValues
    return main_df


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
    # no va df = df.append(df_new_row, ignore_index=True)
    df = pd.concat([df, df_new_row], ignore_index=True)

    # Append the new row to the DataFrame
    # old df = pd.concat([df, df_new_row], ignore_index=True)

    return df


#########################
def lambda_handler(event, context):

    print("evento debajo:")
    try:
        # Retrieve the parameters from the event
        order = event["order"]
        column = event["column"]
        data = event["data"]
        diag = event["diag"]
        v_pk = event["pk"]
    except:
        order = event["payload"]["order"]
        column = event["payload"]["column"]
        data = event["payload"]["data"]
        diag = event["payload"]["diag"]
        v_pk = event["payload"]["pk"]

    print("evento arriba:")
    df_errors = pd.DataFrame()

    # MAIN CODE
    #############################
    ## Check PK
    #############################
    if int(v_pk) == 1:
        # Check first row is unique
        if len(data) > len(set(data)):
            message1 = "Non Unique in First Row"
            message2 = "delete repeated values"
            df_errors = insert_error_df(1, data[0], message1, "", message2, df_errors)
    #############################
    ## Check Diagnosis Column
    #############################

    if int(column) == int(diag):

        unique_values = set(data[1:])
        # Check if the length of unique values is greater than 2

        if len(unique_values) > 2:
            message1 = "WARNING - TARGET column is NOT binary"
            message2 = "This will limit the classification model, excluding for example ROC curve plots"
            df_errors = insert_error_df(
                diag, data[0], message1, None, message2, df_errors
            )
    #############################
    ## Check Other things in Column
    #############################
    # dumm_analysis, df_errors = analyze_column(order, data, df_errors)#, ColumnValues):

    df_errors = analyze_column(order, data, df_errors)  # , ColumnValues):

    #############################
    # Prepare the response

    response_body = df_errors.to_json(orient="records")  # df_errors.values.tolist()

    print("END")
    response = {
        "statusCode": 5227,
        "body": response_body,  # json.dumps(response_body)
        #'body': json.dumps({
        #    'message': 'Parameters received successfully',
        #    'pk': v_pk,
        #    'order': order,
        #    'column': column,
        #    'data': data,
        #    'diag': diag
        # })
    }

    return response
