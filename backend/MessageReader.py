import pandas as pd
from sklearn.model_selection import train_test_split
class MessageReader:
    def __init__(self) -> None:
        self.shot = []
        self.validation = []

    def read_messages_from_csv(self, csv_file_name: str) -> None:
        df = pd.read_csv(csv_file_name)

        df.columns = df.columns.str.lower()

        shot_data = pd.DataFrame()
        valid_data = pd.DataFrame()

        for category in df['category'].unique():
            category_data = df[df['category'] == category]

            shot, valid = train_test_split(
                category_data, test_size=.75, random_state=42)

            shot_data = pd.concat([shot_data, shot])

            valid_data = pd.concat([valid_data, valid])

        self.shot = shot_data.to_dict('records')
        self.validation = valid_data.to_dict('records')


if __name__ == '__main__':
    m = MessageReader()
    m.read_messages_from_csv('./message_list.csv')
    print(m.shot)
