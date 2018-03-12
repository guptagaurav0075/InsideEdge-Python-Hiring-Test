"""Main script for generating output.csv."""
import pandas as pd

PA_THRESHOLD = 25

def main():
    # Import raw CSV data
    raw_data = pd.read_csv('data/raw/pitchdata.csv')

    # Create Split Label Sets
    split_Set = {"vs_pitcher":['vs LHP', 'vs RHP'],"vs_hitter":['vs LHH', 'vs RHH']}

    # Create set of DataFrames to be tabulated
    data_frames = {'PitcherTeamId': split_Set["vs_hitter"], 'PitcherId': split_Set["vs_hitter"],'HitterTeamId': split_Set["vs_pitcher"], 'HitterId': split_Set["vs_pitcher"]}

    # Process set of DataFrames for each Split
    result_dataframes = []
    for subject in data_frames:
        subject_left_df, subject_right_df= split_dataframes_by_side(raw_data, subject)
        filtered_left, filtered_right = filter_dataframes_by_threshold(subject_left_df, subject_right_df, subject)

        data_frames_by_id = pd.concat([get_final_dataframe(get_stats(filtered_left), data_frames[subject][0]),
                                       get_final_dataframe(get_stats(filtered_right), data_frames[subject][1])])
        result_dataframes.append(data_frames_by_id)



    # Concatenate results and sort
    sorted_dataframes = pd.concat(result_dataframes).sort_values(['SubjectId', 'Stat', 'Split',
                                              'Subject'], ascending=True)

    # Output to CSV
    sorted_dataframes.to_csv('data/processed/output.csv', index=False)



def split_dataframes_by_side(data_frame, subject):
    opponent_side = "HitterSide" if subject.startswith("Pit") else "PitcherSide"
    score_cols = [subject, 'PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']

    subject_left_df = data_frame[score_cols][data_frame[opponent_side] == 'L']
    subject_right_df = data_frame[score_cols][data_frame[opponent_side] == 'R']

    return subject_left_df, subject_right_df



def filter_dataframes_by_threshold(df_left, df_right, subject):
    global PA_THRESHOLD
    filtered_left = df_left.groupby(subject).filter(lambda x: x.sum()['PA'] >= PA_THRESHOLD).groupby(
        subject).sum()
    filtered_right = df_right.groupby(subject).filter(lambda x: x.sum()['PA'] >= PA_THRESHOLD).groupby(
        subject).sum()

    return filtered_left, filtered_right


def get_average(record):
    return round(float(record['H']) / record['AB'], 3)



def get_on_base_percentage(record):
    return round(float(record['H'] + record['BB'] + record['HBP']) / (record['AB'] + record['BB'] + record['HBP'] + record['SF']), 3)


def get_slugging_percentage(record):
    return round(float(record['H'] + record['2B'] + record['3B'] * 2 + record['HR'] * 3) / record['AB'], 3)
    #return round(float(record['TB']/record['AB']),3)


def get_on_base_plus_slugging(record):
    return round(float(record['H'] + record['BB'] + record['HBP']) / (record['AB'] + record['BB'] + record['HBP'] + record['SF']) + float(record['H'] + record['2B'] + record['3B'] * 2 +record['HR'] * 3) / record['AB'], 3)
    # return round(get_on_base_percentage(record)+get_slugging_percentage(record),3)


def get_stats(filtered_side_dataframe):
    intermediate_side_dataframe = pd.DataFrame(index=filtered_side_dataframe.index)
    intermediate_side_dataframe['AVG'] = filtered_side_dataframe.apply(get_average, axis=1)
    intermediate_side_dataframe['OBP'] = filtered_side_dataframe.apply(get_on_base_percentage, axis=1)
    intermediate_side_dataframe['SLG'] = filtered_side_dataframe.apply(get_slugging_percentage, axis=1)
    intermediate_side_dataframe['OPS'] = filtered_side_dataframe.apply(get_on_base_plus_slugging, axis=1)

    return intermediate_side_dataframe


def get_final_dataframe(stats_side, split_val):
    stat_side_dataframes = []
    for stat in stats_side:
        stat_side_dataframes.append(stats_side[[stat]])

    final_data_frames = []
    for stat_side_dataframe in stat_side_dataframes:
        subject = stat_side_dataframe.index.name
        stat = stat_side_dataframe.columns[0]
        stat_side_dataframe.reset_index(level=0, inplace=True)
        final_dataframe = stat_side_dataframe.rename(index=str, columns={subject: 'SubjectId', stat: 'Value'})
        final_dataframe.insert(1, 'Stat', stat)
        final_dataframe.insert(2, 'Split', split_val)
        final_dataframe.insert(3, 'Subject', subject)

        final_data_frames.append(final_dataframe)

    return pd.concat(final_data_frames)

if __name__ == '__main__':
    main()
