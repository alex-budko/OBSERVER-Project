import pandas as pd
from sklearn.model_selection import train_test_split

class MessageReader:
    def __init__(self) -> None:
        # Initializes two empty lists to store shot and validation data
        self.shot = []
        self.validation = []

    def read_messages_from_csv(self, csv_file_name: str) -> None:
        # Reads a CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_name)
        
        # Makes all column names lowercase for easier handling
        df.columns = df.columns.str.lower()

        # Initializes two empty pandas DataFrame to store shot and validation data
        shot_data = pd.DataFrame()
        valid_data = pd.DataFrame()

        # Iterates through each unique category in the data
        for category in df['category'].unique():
            # Filters the data to include only rows of the current category
            category_data = df[df['category'] == category]
            
            # Splits the category data into a shot and validation set (75% validation, 25% shot)
            shot, valid = train_test_split(
                category_data, test_size=.75, random_state=42)

            # Concatenates the shot data of the current category with the rest of the shot data
            shot_data = pd.concat([shot_data, shot])
            
            # Concatenates the validation data of the current category with the rest of the validation data
            valid_data = pd.concat([valid_data, valid])

        # Converts the pandas DataFrame to a list of dictionary records
        self.shot = shot_data.to_dict('records')
        self.validation = valid_data.to_dict('records')


if __name__ == '__main__':
    # Creates a new MessageReader object
    m = MessageReader()
    
    # Reads the messages from a CSV file
    m.read_messages_from_csv('./message_list.csv')
    
    # Prints the shot data
    print(m.shot)
