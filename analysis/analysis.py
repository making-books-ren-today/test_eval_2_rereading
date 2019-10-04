"""

Analysis.py - initial analyses for dhmit/rereading

"""
from ast import literal_eval
import csv
from pathlib import Path
from statistics import stdev
import unittest


def load_data_csv(csv_path: Path):
    """
    Takes the path to a csv file, reads it, and returns its
    content as a list of OrderedDicts
    :param Path csv_path: path to the CSV file
    :return: List[dict]
    """
    out_data = []
    with open(str(csv_path)) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row['views'] = literal_eval(row['views'])
            for header_name in ('id', 'student_id', 'scroll_ups'):
                row[header_name] = int(row[header_name])
            row = dict(row)
            out_data.append(row)
    return out_data


def get_sentiments() -> dict:
    """
    Returns a dictionary of sentiment scores, with the keys being the word and the values being
    their score

    :return: dict mapping words to their sentiment scores
    """
    sentiment_path = Path('data', 'sentiments.txt')

    sentiments = dict()
    with open(sentiment_path, 'r') as file:
        word = file.readline()

        # We want to handle each word individually, rather than as a whole set
        while word:

            # This particular file starts lines with '#' for non-sentiment comments, so skip them
            if word[0] == '#' or word[0] == '\t':
                word = file.readline()
                continue

            # All words use tabs to define the different parts of the data
            attributes = word.split('\t')

            # Pull out the word from the line
            data = attributes[4]
            data = data.split('#')
            new_word = data[0]
            positive_score = float(attributes[2])
            negative_score = float(attributes[3])

            # If the word is already in the dictionary, pick the larger value
            # This is not optimal, but standardizes data
            if new_word in sentiments:
                if abs(sentiments[new_word]) > abs(positive_score) and abs(sentiments[new_word]) > \
                        abs(negative_score):
                    word = file.readline()
                    continue

            # Find the largest sentiment score for the word, and define negative sentiments
            # as negative values (if there's a tie, the sentiment is 0)
            if positive_score == negative_score:
                score = 0
            elif positive_score > negative_score:
                score = float(positive_score)
            else:
                score = -float(negative_score)

            sentiments[new_word] = score

            word = file.readline()

    return sentiments


def question_sentiment_analysis(student_data, question_text):
    """
    Takes in a list of student response dicts, and a question prompt (or a substring of one) and
    returns the average sentiment score and standard deviation for all responses to that question

    :param student_data: list of dicts
    :param question_text: question string or substring
    :return: tuple in the form (average, standard_dev)
    """

    sentiments = get_sentiments()

    # Set up data for calculating data
    num_scores = 0
    sentiment_sum = 0
    score_list = list()

    for response in student_data:

        if question_text in response['question']:
            words = response['response'].lower().split()

            # Find the sentiment score for each word, and add it to our data
            for word in words:
                # Ignore the word if it's not in the sentiment dictionary
                if word in sentiments:
                    sentiment_sum += sentiments[word]
                    num_scores += 1
                    score_list.append(sentiments[word])

    average = sentiment_sum / num_scores
    standard_dev = stdev(score_list)

    return average, standard_dev


def word_time_relations(student_data: list) -> dict:
    """
    Takes a list of dicts representing student data and aggregates case-insensitive responses
    into a dictionary, with the response as the key and the average time (across all similar
    responses) viewing the story as the value.

    :param student_data: list of dicts obtained from load_data_csv
    :return: dict, responses as keys and values as average view times for that response
    """

    # First gather all responses in an easy-to-handle format of dict(response: times)
    responses = dict()
    for response_data in student_data:

        # Find total time spent looking at story
        total_time = 0
        for view in response_data['views']:
            total_time += view

        # Add this time to the response dictionary (case-insensitive)
        response = response_data['response'].lower()
        if response not in responses:
            responses[response] = [total_time]
        else:
            responses[response].append(total_time)

    # Now compute the average time for each response and add them to a new dictionary
    averages = dict()
    for response in responses:
        times = responses[response]
        total = sum(times)
        average = total / len(times)
        averages[response] = average

    return averages


def compute_total_view_time(student_data):
    """
    Given a list of student response dicts,
    return the total time (across all users) spent reading the text

    :param student_data: list, student response dicts
    :return: float, the total time all users spent reading the text
    """
    total_view_time = 0
    for row in student_data:
        for view_time in row.get('views'):
            total_view_time += view_time
    return total_view_time


def get_word_frequency_differences(student_data):
    """
    Looks over the data and compares responses from people who have read the text vs.
    people who have not read the text before this exercise
    :return: a list of word frequency differences, by increasing order of frequency differences
    """

    # Iterate through all data, and separate ids of students who have vs. have not read the text
    yes_id = []
    no_id = []

    for response in student_data:
        if 'Have you encountered this text before' in response['question'] \
                and 'This is an ad.' in response['context']:
            if 'yes' not in response['response'].lower():
                no_id.append(response['student_id'])
            else:
                yes_id.append(response['student_id'])

    # Iterate through all responses, store words and word frequencies of yes vs. no responses as
    # keys and values in 2 dictionaries

    yes_responses = dict()
    no_responses = dict()

    for element in student_data:
        if 'In one word' in element['question'] and 'This is an ad' in element['context']:
            response = element['response'].lower()
            if element['student_id'] in yes_id:
                if response in yes_responses:
                    yes_responses[response] += 1
                else:
                    yes_responses[response] = 1
            else:
                if response in no_responses:
                    no_responses[response] += 1
                else:
                    no_responses[response] = 1

    # Iterate through yes_responses and no_responses, store words and frequency differences as keys
    # and values of a dictionary
    diff_responses = dict()

    for word in yes_responses:
        if word in no_responses:
            diff_responses[word] = yes_responses[word] - no_responses[word]
        else:
            diff_responses[word] = yes_responses[word]
    for word in no_responses:
        if word not in yes_responses:
            diff_responses[word] = - no_responses[word]

    # Convert diff_responses from a dictionary to a list of tuples
    diff_responses_list = []
    for word in diff_responses:
        diff_responses_list.append((word, diff_responses[word]))

    # Order diff_responses and return ordered list
    ordered_responses = sorted(diff_responses_list, key=lambda x: x[1])
    return ordered_responses


def run_analysis():
    """
    Runs the analytical method on the reading data

    :return: None
    """
    csv_path = Path('data', 'rereading_data_2019-09-13.csv')
    student_data = load_data_csv(csv_path)
    response_groups_freq_dicts = get_response_groups_frequencies(student_data)
    show_response_groups(response_groups_freq_dicts)
    total_view_time = compute_total_view_time(student_data)
    print(f'The total view time of all students was {total_view_time}.')



def context_vs_read_time(student_data):
    """compares average viewtimes, given different context (ad vs story)
    :param student_data: list, student response dicts
    :return a tuple of the average ad view and the average story view
    """
    ad_sum = 0
    ad_count = 0
    story_sum = 0
    story_count = 0

    for dicti in student_data:
        if dicti['context'] == "This is an ad.":
            if not len(dicti["views"]) == 0:
                for view in dicti["views"]:
                    ad_sum = ad_sum + view
            ad_count += 1
        elif dicti["context"] == "This is actually a short story.":
            if not len(dicti["views"]) == 0:
                for view in dicti["views"]:
                    story_sum = story_sum + view
            story_count += 1

    if ad_count == 0:
        average_ad_view = 0
    else:
        average_ad_view = ad_sum / ad_count
    if story_count == 0:
        average_story_view = 0
    else:
        average_story_view = story_sum / story_count

    return average_ad_view, average_story_view


def frequency_feelings(student_data):
    """ :param student_data: list, student response dicts
    :return a list of tuples of words that appear more than once, and how often they occur,
    in order of their frequency"""
    feelings = {}
    for dicti in student_data:
        if dicti['question'] == "In one word, how does this text make you feel?":
            lowercaseword = dicti['response'].lower()
            if feelings.get(lowercaseword, 0) == 0:
                feelings[lowercaseword] = 1
            else:
                feelings[lowercaseword] += 1

    frequentwords = []  # list of tuples in the format (frequency, word)
    for word in feelings:
        if feelings[word] > 1:
            frequentwords.append((word, feelings[word]))

    print(frequentwords)

    for i in range(len(frequentwords) - 1):
        for j in range(i + 1, len(frequentwords)):
            if (frequentwords[i])[1] < (frequentwords[j])[1]:
                frequentwords[i], frequentwords[j] = frequentwords[j], frequentwords[i]

    print(frequentwords)
    return frequentwords


def show_response_groups(response_groups_freq_dicts):
    """
    Given response_groups_freq_dicts list of dictionaries, prints the dicts in readable format

    :param response_groups_freq_dicts, lists of 4 dicts (one for each response
    group)
    mapping words to frequencies within that response group
    :return None
    """
    print(f'Word frequencies for Single view responses to ad context: ',
          response_groups_freq_dicts[0])
    print(f'Word frequencies for Single view responses to short story context: ',
          response_groups_freq_dicts[1])
    print(f'Word frequencies for Multiple view responses to ad context: ',
          response_groups_freq_dicts[2])
    print(f'Word frequencies for Multiple view responses to short story context: ',
          response_groups_freq_dicts[3])


def get_response_groups_frequencies(student_data: list):
    """"
    Given student_data,
    Returns lists of 4 frequency dicts, one for each response group,
     that map response words to frequencies for each response group.
    Response groups are based on single vs. multiple views and ad vs. short story
    context to the "In one word, how does this text make you feel?" question
    :param student_data, list of dicts
    :return: list of four dicts (one for each response group) mapping words
    to frequencies within that response group
    """
    people_with_multiple_views = []
    people_with_one_view = []

    for person_response in student_data:
        if len(person_response['views']) == 1:
            people_with_one_view.append(person_response)
        else:
            people_with_multiple_views.append(person_response)

    single_view_short_story_group, single_view_ad_group = \
        get_groups_by_context(people_with_one_view)
    multiple_view_short_story_group, multiple_view_ad_group = \
        get_groups_by_context(people_with_multiple_views)

    response_groups = [
        single_view_ad_group,
        single_view_short_story_group,
        multiple_view_ad_group,
        multiple_view_short_story_group,
    ]

    response_groups_freq_dicts = []
    for group_name in response_groups:
        freq_dict = find_word_frequency(group_name)
        response_groups_freq_dicts.append(freq_dict)
    return response_groups_freq_dicts


def get_groups_by_context(people_with_view_number):
    """
    :param people_with_view_number: list of responses for people with certain number of views
    :return: two lists, one for responses to short story context and one for ad context
    """
    short_story_context_group = []
    ad_context_group = []
    for person in people_with_view_number:
        if person['question'] == "In one word, how does this text make you feel?":
            response = person['response'].lower()
            if person['context'] == "This is actually a short story.":
                short_story_context_group.append(response)
            else:
                ad_context_group.append(response)
    return short_story_context_group, ad_context_group


def find_word_frequency(response_list):
    """
    :param response_list: list of single-word str
    :return: freq, dict mapping each unique word in response_list to number of appearances in
    response_list
    """
    freq = {}
    for word in response_list:
        if word not in freq:
            freq[word] = 1
        else:
            freq[word] += 1
    return freq


class TestAnalysisMethods(unittest.TestCase):
    """
    Test cases to make sure things are running properly
    """
    def setUp(self):
        test_data_path = Path('data', 'test_data.csv')
        self.test_student_data = load_data_csv(test_data_path)
        self.default_student_data = [  # model default values
            {
                'id': 0,
                'question': '',
                'context': '',
                'response': '',
                'views': [],
                'student_id': 0,
                'scroll_ups': 0,
            }
        ]
        sample_csv_path = Path('data', 'rereading_data_2019-09-13.csv')
        self.student_data = load_data_csv(sample_csv_path)

    def test_compute_total_view_time(self):
        """
        Test that the total view time equals the expected values.
        """
        total_view_time = compute_total_view_time(self.test_student_data)
        self.assertEqual(total_view_time, 6.385)

        # check we don't crash on the defaults from the model!
        total_view_time = compute_total_view_time(self.default_student_data)
        self.assertEqual(total_view_time, 0)

    def test_question_sentiment_analysis(self):
        """
        test that the average and standard deviation of test data equals the expected values
        """
        single_word_data = question_sentiment_analysis(self.test_student_data, 'one word')
        self.assertEqual(single_word_data, (-.75, 0))

        three_words_data = question_sentiment_analysis(self.test_student_data, 'three words')
        self.assertEqual(three_words_data, (0, 0))

    def test_get_sentiments(self):
        """
        test that the get_sentiments method returns the correct data for each word
        """

        sentiments = get_sentiments()
        competent_score = sentiments['competent']
        self.assertEqual(competent_score, 0.75)

        inefficient_score = sentiments['inefficient']
        self.assertEqual(inefficient_score, -0.5)

        length = len(sentiments)
        self.assertEqual(length, 89631)

    def test_context_vs_read_time(self):
        """
        test that the context_vs_read_time method returns the expected values
        """
        context_vs_read = context_vs_read_time(self.test_student_data)
        expected = (1.7546666666666664, 0.37366666666666665)
        self.assertEqual(context_vs_read, expected)
        # test that it still works with default values
        context_vs_read = context_vs_read_time(self.default_student_data)
        expected =(0,0)
        self.assertEqual(context_vs_read, expected)

    def test_frequency_feelings(self):
        """
        test that frequency_feelings method returns the expected values
        """
        frequency_feels = frequency_feelings(self.test_student_data)
        expected = [("sad", 2)]
        self.assertEqual(frequency_feels, expected)
        #test that it works with default values
        frequency_feels = frequency_feelings(self.default_student_data)
        expected = []
        self.assertEqual(frequency_feels, expected)

    def test_word_frequency_differences(self):
        """
        Test the word_frequency_differences function
        """

        word_frequency_differences = get_word_frequency_differences(self.test_student_data)
        expected = [('sad', -1)]
        self.assertEqual(word_frequency_differences, expected)

    def test_response_group_frequencies(self):
        """
        Tests get_response_groups_frequencies returns correct freq dictionaries when passed
        certain student data set
        """
        response_groups = get_response_groups_frequencies(self.student_data)
        expected = [
            {'sad': 2, 'bored': 1, 'annoyed': 2, 'fine': 1, 'melancholic': 1, 'suspicious': 1,
             'speculative': 1, 'depressed': 1, 'confused': 1},
            {'sad': 8, 'enticed': 1, 'ok': 1, 'inyrigu': 1, 'interested': 2, 'surprised': 1,
             'concerned': 1, 'helped': 1, 'depressed': 2, 'sad/curious': 1, 'intrigued': 1,
             'confused': 1, 'puzzled': 1},
            {'targeted': 1, 'confused': 3, 'informed': 2, 'weird': 1, 'comfortable': 1,
             'melancholy': 2, 'sad': 2, 'concerned': 1, 'uncomfortable': 1, 'curious': 1,
             'disappointed': 1, 'indifferent': 1, 'fine': 1, 'neutral': 1},
            {'somber': 1, 'mysterious': 1, 'curious': 1, 'sad': 1, 'interested': 1,
             'underwhelmed': 1, 'melancholy': 1, 'sadder': 1},
        ]
        self.assertEqual(expected, response_groups)

    def test_word_time_relations(self):
        """
        Test the word_time_relations function against the test data and an empty dataset
        """

        # Expected values for test_data.csv
        expected = {
            'sad': 1.72,
            'miscarriage': 1.4725,
            'no': 0,
            'yes': 0
        }
        test_result = word_time_relations(self.test_student_data)
        self.assertEqual(test_result, expected)

        # Expected dictionary for empty default data
        default_expected = {
            '': 0,
        }
        default_result = word_time_relations(self.default_student_data)
        self.assertEqual(default_result, default_expected)


if __name__ == '__main__':
    run_analysis()
    unittest.main()  # run the tests
