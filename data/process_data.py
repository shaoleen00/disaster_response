import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    IN:
        messages_filepath: messages filepath
        categories_filepath: categories filepath
    OUT:
        dataframe with messages and correctly categories
    """ 
    df = pd.merge(
        pd.read_csv(messages_filepath),
        pd.read_csv(categories_filepath),
        how='inner',
        left_on='id',
        right_on='id'
    )
    return df
    
    


def clean_data(df):
    """
    IN:
        messages and categories dataframe to be clean
    OUT:
        clean dataframe
    """ 
    # create a dataframe of the 36 individual category columns
    categories = df.categories.str.split(';', expand=True)
    category_colnames = list(item for item in map(lambda x: x.split('-')[0],categories.iloc[0,:].values))
    categories.columns = category_colnames
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x: x.split('-')[-1])
        # convert column from string to numeric
        categories[column] = categories[column].astype('int')
        # normalize categories to be binary
        categories[column] = categories[column].apply(lambda x: 1 if x >= 1 else 0)
    # drop the original categories column from `df`
    df.drop(columns=['categories'], inplace=True)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.merge(
        df,
        categories,
        how='inner',
        left_index=True,
        right_index=True
    )
    # drop duplicates
    df.drop_duplicates(inplace=True)
    return df
    

def save_data(df, database_filename):
    """
    IN:
        df: clean dataframe to be saved
        database_filename: database filepath
    OUT:
        None
    """
    engine = create_engine('sqlite:///database_filename')
    df.to_sql('Message', engine, index=False, if_exists='replace')  


def main():
     """
    IN:
        messages_filepath: messages filepath
        categories_filepath: categories filepath
        database_filepath: database filepath
    OUT:
        None
    """
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
