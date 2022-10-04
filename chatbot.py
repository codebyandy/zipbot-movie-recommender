
# PA6, CS124, Stanford, Winter 2019
# v.1.0.3
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import random
import re


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.RESPONSES_REQUIRED = 5
        self.text_recommendation = [
            "I recommend you see '%s'.",
            "I think you'd like '%s'!",
            "Zipbot thinks you would enjoy watching: '%s'!",
            "Beep boop... your next favorite will be... '%s'!"
        ]
        self.text_dislike = [
            "I understand you did not like '%s'.",
            "Oh, so you didn't like '%s'? Okay!",
            "You didn't like '%s'!?! I really liked it! But okay, user.",
            "I didn't like '%s' either. Noted!"
        ]
        self.text_like = [
            "I understand you liked '%s'.",
            "I loved '%s', too!! You have great taste.",
            "It sounds like you liked '%s'. Thanks.",
            "'%s' was amazing! I've noted that you liked it."
        ]
        self.text_neutral = [
            "Hmm... I can't tell how you felt about '%s'. Tell me more.",
            "I'm not sure I understood how you felt about '%s'. Can you elaborate?",
            "Sorry, I couldn't understand how you felt about '%s'. Tell me more!"
        ]
        self.name = 'zipbot'
        self.greetings = ['hello', 'hi', 'howdy', 'greetings', 'sup', "what's up", 'salutations', 'hey', 'meow']

        self.disambiguate_flag = False
        self.disambiguating_matches = []
        self.movie_to_disambiguate = ''
        self.original_sentiment = 0

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.rec_counter = 0
        self.response_counter = 0
        self.user_preferences = np.zeros((len(self.titles), 1))
        self.recommendations = None
        self.correction = -1
        self.correction_sentiment = 0
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        greeting_message = "Hello, I'm %s. Please tell me about a movie you've seen, and I'll recommend a movie to you!" % self.name

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message                                 #
        ########################################################################

        goodbye_message = "I hope you've had as much fun as I did! " + random.choice([
            "See you later, alligator! :)",
            "See you soon, big baboon! :)",
            "See you after a while, crocodile! :)",
            "Toodaloo, kangaroo! :)",
            "Till then, penguin! :)",
            "Out the door, dinosaur! :)"
        ])

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    ### TODO: ANDY
    def clean(self, line):
        match = re.search("[,.?]", line)
        if match:
            line = line[:match.start()]

        if "my " in line:
            line = line.replace("my", "your")
        elif "your " in line:
            line = line.replace("your", "my")
        if " me" in line:
            line = line.replace("me", "you")
        elif " you" in line and " your" not in line:
            line = line.replace("you", "me")
        return line
    ###

    def process(self, line):
        """Process a line of input from the REPL and generate a response.

        This is the method that is called by the REPL loop directly with user
        input.

        You should delegate most of the work of processing the user's input to
        the helper functions you write later in this class.

        Takes the input string from the REPL and call delegated functions that
          1) extract the relevant information, and
          2) transform the information into a response to the user.

        Example:
          resp = chatbot.process('I loved "The Notebook" so much!!')
          print(resp) // prints 'So you loved "The Notebook", huh?'

        :param line: a user-supplied line of text
        :returns: a string containing the chatbot's response to the user input
        """
        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #

        ########################################################################
        response = ''
        if self.correction != -1:
            corrected_title = self.titles[self.correction][0]
            if 'yes' in line.lower() or 'y' == line.lower() or 'i did' in line.lower() or 'yea' == line.lower() or 'yeah' in line.lower():
                ### TODO - Akanksha & Anjali made some changes here
                if self.user_preferences[self.correction] != 0:
                    response += "You've already told me about this movie! Please tell me about another one."  
                else:
                    response += self.get_sentiment_response(corrected_title, self.correction_sentiment, self.correction)
            else:
                response += "I'm going to assume you didn't mean " + corrected_title + ". Please tell me about another movie, then!"
            self.correction = -1
        elif self.response_counter == self.RESPONSES_REQUIRED:
            if 'yes' in line.lower() or 'y' == line.lower() or 'i did' in line.lower() or 'yea' == line.lower() or 'yeah' in line.lower():
                if self.rec_counter == len(self.titles):
                    response += 'That is all the recommendations we have for you today. Type :quit to end the session.'
                else:
                    movie_rec = self.titles[self.recommendations[self.rec_counter]][0]
                    self.rec_counter += 1
                    # warn ahead of time that we've reached the end of recommendations
                    response += random.choice(self.text_recommendation) % movie_rec + ' Would you like another recommendation? Please type yes/:quit.'
            else:
                response += random.choice([
                    "I didn't understand. Please type yes/:quit.",
                    "I'm ready to give a recommendation now! Do you want one? Please type yes/:quit."
                ])
        else:
            ### TODO Akanksha & Anjali
            if self.disambiguate_flag:
                disambiguated = self.disambiguate(line, self.disambiguating_matches)
                if len(disambiguated) > 1:
                    self.movie_to_disambiguate += ' ' + line
                    response += self.disambiguation_dialogue(self.movie_to_disambiguate, disambiguated)
                elif len(disambiguated) == 0:
                    ### TODO Add Kyle's stuff if we decompose?
                    self.movie_to_disambiguate += ' ' + line
                    response += "I found no matches for '%s'. Please try again!" % self.movie_to_disambiguate
                    self.disambiguate_flag = False
                else:
                    response += self.get_sentiment_response(self.titles[disambiguated[0]][0], self.original_sentiment, disambiguated[0])
                    self.disambiguate_flag = False
            else:
                movie_titles = self.extract_titles(line)
                input_sentiment = self.extract_sentiment(line)
                if len(movie_titles) == 0:
                    line = line.lower()
                    if 'how is your day' in line or 'how are you' in line:
                        response += " I am doing great!"
                    elif 'your name' in line or 'who are you' in line and 'who are your' not in line:
                        response += random.choice([
                            " I am Zipbot.",
                            " My momma named me Zipbot.",
                            " Me Zipbot."
                        ])
                    elif any([re.search('(?:^|\W)' + greeting + '(?:\W|$)', line) for greeting in self.greetings]):
                        response += random.choice([
                            " Hello there!",
                            " Howdy!",
                            " Lovely to meet you!",
                            " Hi!"
                        ])
                    elif 'can you' in line:
                        selected = re.search("can you (.*)", line)
                        response += (" I see that you need me to %s." % self.clean(
                            selected.group(1)))
                        response += " I'm sorry, but I only know how to recommend movies! Please tell me about a movie, and put the movie title in quotes. I can indeed do different languages. If you have the release year, put that in parentheses. I'll ask for clarification if I need it."
                    elif 'what is' in line or 'when is' in line or 'where is' in line:
                        selected = re.search("(what |when |where )is (.*)", line)
                        response += " I'm unsure %s is. Sorry about that." % (selected.group(1) + self.clean(selected.group(2)))
                    elif 'what are' in line or 'when are' in line or 'where are' in line:
                        selected = re.search("(what |when |where )are (.*)", line)
                        response += " I'm unsure %s are. Sorry about that." % (selected.group(1) + self.clean(selected.group(2)))
                    elif 'who is' in line:
                        selected = re.search("who is (.*)", line)
                        response += (" I have talked to %s before. They liked \"%s\". Maybe you will like it too! If you tell me about your preferences, I can give you a better recommendation." % (
                            self.clean(selected.group(1)), random.choice(self.titles)[0]))
                    elif 'who are' in line:
                        selected = re.search("who are (.*)", line)
                        response += (" I have talked to %s before. They liked \"%s\". Maybe you will like it too! If you tell me about your preferences, I can give you a better recommendation." % (
                            self.clean(selected.group(1)), random.choice(self.titles)[0]))
                    elif "i'm" in line or "i am" in line:
                        selected = re.search("(?:i'm|i am) ([^\.]*)", line)
                        response += (" It sounds like you are %s. I see. Maybe it is time to watch a movie! I can help you find a movie to watch!" % self.clean(selected.group(1)))
                    elif '?' in line:
                        response += "Sorry I don't have an answer to your question. Tell me about movies instead and I can help you find a movie to watch!"
                    else:
                        response += random.choice([
                            " Sorry, I want to talk about movies.",
                            " Interesting. Thanks for letting me know. Let's get back on topic.",
                            " I'm really glad you shared that with me. As a thanks, let me recommend you a movie.",
                            " Hm, let's put a pin in that. I would like to talk about movies now.",
                            " I hear you. Can you remind me about it tomorrow? I want to share a recommendation with you."
                        ])
                        response += " If you were trying to tell me about a movie, please put the title in quotes."
                elif input_sentiment == 0:
                    response += random.choice(self.text_neutral) % movie_titles[0]
                elif len(movie_titles) > 1:
                    response += "Please tell me about one movie at a time."
                else:
                    matches = self.find_movies_by_title(movie_titles[0])
                    if len(matches) == 0:
                        ### TODO: KYLE
                        response += "I found no matches for the movie '" + movie_titles[0] + "'."
                        if not self.creative:
                            response += " Please try again."
                        else:
                            mispells = self.find_movies_closest_to_title(movie_titles[0])
                            if len(mispells) == 0:
                                response += " Please try again."
                            elif len(mispells) == 1:
                                response = "Did you happen to mean " + self.titles[mispells[0]][0] + "? Please type yes/no."
                                self.correction = mispells[0]
                                self.correction_sentiment = self.extract_sentiment(line)
                            else:
                                response += " However, I found some close matches:\n"
                                for mispell in mispells:
                                    response += " " + self.titles[mispell][0] + "\n"
                                response += "If you meant one of these, please try again!"
                        ###

                    elif len(matches) > 1:
                        self.movie_to_disambiguate = movie_titles[0]
                        self.original_sentiment = input_sentiment
                        response += self.disambiguation_dialogue(self.movie_to_disambiguate, matches)

                    else:
                        # user has already indicated preference for movie
                        if self.user_preferences[matches[0]] != 0:
                              response += "You've already told me about this movie! Please tell me about another one."  
                        else:
                            title = self.titles[matches[0]][0]
                            ### TODO Akanksha and Anjali
                            response += self.get_sentiment_response(title, input_sentiment, matches[0])

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    ### TODO: KYLE (and Akanksha and Anjali)
    def get_sentiment_response(self, title, sentiment, movie_id):
        response = ''
        if sentiment < 0:
            response += random.choice(self.text_dislike) % title
        else:
            response += random.choice(self.text_like) % title
        self.response_counter += 1
        self.user_preferences[movie_id] = sentiment
        if self.response_counter == self.RESPONSES_REQUIRED:
            self.recommendations = self.recommend(self.user_preferences, self.ratings, len(self.titles))
            response += " Would you like a recommendation now? Please type yes/:quit."
        else:
            response += " Please tell me about another movie."
        return response
    ###

    @staticmethod
    def preprocess(text):
        """Do any general-purpose pre-processing before extracting information
        from a line of text.

        Given an input line of text, this method should do any general
        pre-processing and return the pre-processed string. The outputs of this
        method will be used as inputs (instead of the original raw text) for the
        extract_titles, extract_sentiment, and extract_sentiment_for_movies
        methods.

        Note that this method is intentially made static, as you shouldn't need
        to use any attributes of Chatbot in this method.

        :param text: a user-supplied line of text
        :returns: the same text, pre-processed
        """
        ########################################################################
        # TODO: Preprocess the text into a desired format.                     #
        # NOTE: This method is completely OPTIONAL. If it is not helpful to    #
        # your implementation to do any generic preprocessing, feel free to    #
        # leave this method unmodified.                                        #
        ########################################################################

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return text

    def extract_titles(self, preprocessed_input):
        """Extract potential movie titles from a line of pre-processed text.

        Given an input text which has been pre-processed with preprocess(),
        this method should return a list of movie titles that are potentially
        in the text.

        - If there are no movie titles in the text, return an empty list.
        - If there is exactly one movie title in the text, return a list
        containing just that one movie title.
        - If there are multiple movie titles in the text, return a list
        of all movie titles you've extracted from the text.

        Example:
          potential_titles = chatbot.extract_titles(chatbot.preprocess(
                                            'I liked "The Notebook" a lot.'))
          print(potential_titles) // prints ["The Notebook"]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: list of movie titles that are potentially in the text
        """
        pattern = '"([^"]*)"'
        return re.findall(pattern, preprocessed_input)

    def find_movies_by_title(self, title):
        """ Given a movie title, return a list of indices of matching movies.

        - If no movies are found that match the given title, return an empty
        list.
        - If multiple movies are found that match the given title, return a list
        containing all of the indices of these matching movies.
        - If exactly one movie is found that matches the given title, return a
        list
        that contains the index of that matching movie.

        Example:
          ids = chatbot.find_movies_by_title('Titanic')
          print(ids) // prints [1359, 2716]

        :param title: a string containing a movie title
        :returns: a list of indices of matching movies

        Year: any 4 digit sequence with () or spaces or nothing at the beginning or end of the input > 1800
        """
        original_title = title
        title = title.lower()
        pattern_year_begin = "^\(?((?:18|19|20)\d\d)\)? "
        pattern_year_end = " \(?((?:18|19|20)\d\d)\)?$"
        pattern_article = "^(the|an|a|la|el|il|le|l'|les|die|das|der|det|i|une|lo|los|un|una|kimi ni|den|jie|en) "

        # Extract year from input if it exists
        match_year_begin = re.search(pattern_year_begin, title)
        match_year_end = re.search(pattern_year_end, title)
        year = None
        if match_year_end:
            year = match_year_end.group(1)
            title = title[:match_year_end.start()]
        elif match_year_begin:
            year = match_year_begin.group(1)
            title = title[match_year_end.end():]

        # Extract article from input if it exists
        match_article = re.search(pattern_article, title)
        # article = None
        if match_article:
            # article = match_article.group(1)
            title = title[match_article.end():]
        results = []

        # Search database for matching titles
        end_pattern = " (?:\(.*\) )?\(\d\d\d\d.*\)$"
        for i in range(len(self.titles)):
            database_title, _ = self.titles[i]
            database_title = database_title.lower()
            # starter mode
            if not self.creative:
                # Single-word edge case
                if original_title.find(' ') == -1:
                    end_match = re.search(end_pattern, database_title)
                    if end_match:
                        database_title_shaved = database_title[:end_match.start()]
                    else:
                        database_title_shaved = database_title
                    if database_title_shaved not in [title, title + ', the', title + ', a', title + ', an']:
                        continue

                if title in database_title:
                    add = True
                    if year and year not in database_title:
                        add = False
                    # if article and article not in database_title:
                    #    add = False
                    if add:
                        results.append(i)

            # creative mode
            ### TODO Anjali & Akanksha
            else:
                add = True
                title_tokens = title.split()
                for token in title_tokens:
                    token_pattern = "(?:^|\W)" + token + "\W"
                    # middle_token = '\W' + token + '\W'
                    # start_token = '^' + token + '\W'
                    # if original_title.find(' ') == -1:
                    middle_matches = re.findall(token_pattern, database_title)
                    # start_matches = re.findall(start_token, database_title)
                    if not(middle_matches):
                        add = False
                if title in database_title:
                    if year and year not in database_title:
                        add = False
                    # if article and article not in database_title:
                    #    add = False
                    if add:
                        results.append(i)
        return results

    ### TODO: KYLE
    def remove_year(self, line):
        """
        Removes a year from the beginning or end of a line.
        Returns the line with the year removed and the year, if found
        """
        pattern_year_begin = "^\(?((?:18|19|20)\d\d)\)? "
        pattern_year_end = " \(?((?:18|19|20)\d\d)\)?$"

        # Extract year from input if it exists
        match_year_begin = re.search(pattern_year_begin, line)
        match_year_end = re.search(pattern_year_end, line)
        year = None
        if match_year_end:
            year = match_year_end.group(1)
            line = line[:match_year_end.start()]
        elif match_year_begin:
            year = match_year_begin.group(1)
            line = line[match_year_end.end():]

        return line, year

    def remove_article(self, line):
        """
        Removes an article from the beginning of a line.
        Returns the line with the article removed and the article, if found
        """
        pattern_article = "^(the|an|a|la|el|il|le|l'|les|die|das|der|det|i|une|lo|los|un|una|kimi ni|den|jie|en) "
        match_article = re.search(pattern_article, line)
        article = None
        if match_article:
            article = match_article.group(1)
            line = line[match_article.end():]

        return line, article
    ###

    def extract_sentiment(self, preprocessed_input):
        """Extract a sentiment rating from a line of pre-processed text.

        You should return -1 if the sentiment of the text is negative, 0 if the
        sentiment of the text is neutral (no sentiment detected), or +1 if the
        sentiment of the text is positive.

        As an optional creative extension, return -2 if the sentiment of the
        text is super negative and +2 if the sentiment of the text is super
        positive.

        Example:
          sentiment = chatbot.extract_sentiment(chatbot.preprocess(
                                                    'I liked "The Titanic"'))
          print(sentiment) // prints 1

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a numerical value for the sentiment of the text
        """
        preprocessed_input = preprocessed_input.lower()

        # Slice out all titles
        titles = self.extract_titles(preprocessed_input)
        for title in titles:
            preprocessed_input = preprocessed_input.replace(title, "")

        # Find negation words
        negation_words = ['never', 'n\'t', 'not']
        negate = False
        for negation_word in negation_words:
            if negation_word in preprocessed_input:
                negate = True

        # Find extreme words
        ## TODO:ANJALI
        extreme_words = ['r+e+a+l+l+y+', 't+r+u+l+y+', 'e+x+t+r+e+m+e+l+y+', 'v+e+r+y+']
        strong_words = ['vile', 'hate', 'despise', 'adore', 'love', 'obsess', 'enrage', 'excellent', 'agony', 'tramp',
                        'repulsive', 'shameful', 'depress', 'thoughtless', 'great', 'terrible']

        #one or more for any of the characters
        extreme = False
        for extreme_word in extreme_words:
            extreme_matches = re.findall(extreme_word, preprocessed_input)
            if extreme_matches:
                extreme = True

        if '!' in preprocessed_input:
            extreme = True

        # Convert sentence to sets of forms
        sentence_tokens = preprocessed_input.split()
        tokens = []
        for token in sentence_tokens:
            s = set()
            s.add(''.join(c for c in token if c.isalnum()))
            tokens.append(s)

        # Create new forms
        for token in tokens:
            new_forms = set()
            for form in token:
                # loved -> love, lov
                if form.endswith('ed'):
                    new_forms.add(form[:-2] + 'e')
                    new_forms.add(form[:-2])
                    new_forms.add(form[:-3] + 'y')

                # lovely -> love, lov
                if form.endswith('ly') and form != "really":
                    new_forms.add(form[:-2] + 'e')
                    new_forms.add(form[:-2])

                # loves -> love
                if form.endswith('s'):
                    new_forms.add(form[:-1])

                # hating -> hate, hat
                # batting -> bat, bate, batt
                if form.endswith('ing'):
                    new_forms.add(form[:-3] + 'e')
                    new_forms.add(form[:-3])
                    new_forms.add(form[:-4])
            for new_form in new_forms:
                token.add(new_form)

        # Calculate total sentiment
        total_sentiment = 0
        for token in tokens:
            sentiment = 0
            for form in token:
                if form in strong_words:
                    extreme = True
                if form in self.sentiment:
                    sentiment = 1 if self.sentiment[form] == 'pos' else -1

            total_sentiment += sentiment

        if negate:
            total_sentiment = -total_sentiment

        if total_sentiment == 0:
            return 0

        ## TODO:ANJALI
        if self.creative and extreme:
            return 2 if total_sentiment > 0 else -2


        return 1 if total_sentiment > 0 else -1

    def extract_sentiment_for_movies(self, preprocessed_input):
        """Creative Feature: Extracts the sentiments from a line of
        pre-processed text that may contain multiple movies. Note that the
        sentiments toward the movies may be different.

        You should use the same sentiment values as extract_sentiment, described

        above.
        Hint: feel free to call previously defined functions to implement this.

        Example:
          sentiments = chatbot.extract_sentiment_for_text(
                           chatbot.preprocess(
                           'I liked both "Titanic (1997)" and "Ex Machina".'))
          print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """
        pass

    ### TODO: KYLE
    def find_movies_closest_to_title(self, title, max_distance=3):
        """Creative Feature: Given a potentially misspelled movie title,
        return a list of the movies in the dataset whose titles have the least
        edit distance from the provided title, and with edit distance at most
        max_distance.

        - If no movies have titles within max_distance of the provided title,
        return an empty list.
        - Otherwise, if there's a movie closer in edit distance to the given
        title than all other movies, return a 1-element list containing its
        index.
        - If there is a tie for closest movie, return a list with the indices
        of all movies tying for minimum edit distance to the given movie.

        Example:
          # should return [1656]
          chatbot.find_movies_closest_to_title("Sleeping Beaty")

        :param title: a potentially misspelled title
        :param max_distance: the maximum edit distance to search for
        :returns: a list of movie indices with titles closest to the given title
        and within edit distance max_distance
        """
        title = title.lower()
        title, year = self.remove_year(title)
        pattern_paren_group_end = " \(.*\)?$"

        title, article = self.remove_article(title)
        if article:
            title = title + ', ' + article

        results = []
        min_dist = 9999
        for i in range(len(self.titles)):
            database_title, _ = self.titles[i]
            database_title = database_title.lower()
            database_title, database_year = self.remove_year(database_title)

            # Remove all end paren groups from database title
            # "Nights of Cabiria (Notti di Cabiria, Le)" -> "Nights of Cabiria"
            found = re.search(pattern_paren_group_end, database_title)
            while found:
                database_title = database_title[:found.start()]
                found = re.search(pattern_paren_group_end, database_title)

            dist = self.edit_distance(title, database_title)

            if dist <= max_distance:
                add = True
                if year and database_year and year != database_year:
                    add = False

                # Only maintain list of min-dist candidates
                if add:
                    if dist < min_dist:
                        min_dist = dist
                        results = [i]
                    elif dist == min_dist:
                        results.append(i)

        return results
    ###

    def edit_distance(self, s1, s2):
        n = len(s1)
        m = len(s2)
        distance = np.zeros((n + 1, m + 1))
        distance[:, 0] = np.arange(n + 1)
        distance[0, :] = np.arange(m + 1)

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                sub_cost = 0 if s1[i - 1] == s2[j - 1] else 2
                distance[i][j] = min(distance[i - 1][j] + 1,
                                     distance[i][j - 1] + 1,
                                     distance[i - 1][j - 1] + sub_cost)
        return distance[n][m]

    ### TODO Akanksha and Anjali
    def disambiguation_dialogue(self, original_movie, matches):
        response = ''
        response += "I found multiple matches for '%s': \n" % original_movie
        for i in range(len(matches)):
            match = matches[i]
            response += " " + str(i + 1) + ". " + self.titles[match][0] + "\n"
        response += "Please clarify which movie you are referring to."
        if self.creative:
            self.disambiguate_flag = True
            self.disambiguating_matches = matches
        return response

    ### TODO Akanksha and Anjali
    def disambiguate(self, clarification, candidates):
        """Creative Feature: Given a list of movies that the user could be
        talking about (represented as indices), and a string given by the user
        as clarification (eg. in response to your bot saying "Which movie did
        you mean: Titanic (1953) or Titanic (1997)?"), use the clarification to
        narrow down the list and return a smaller list of candidates (hopefully
        just 1!)

        - If the clarification uniquely identifies one of the movies, this
        should return a 1-element list with the index of that movie.
        - If it's unclear which movie the user means by the clarification, it
        should return a list with the indices it could be referring to (to
        continue the disambiguation dialogue).

        Example:
          chatbot.disambiguate("1997", [1359, 2716]) should return [1359]

        :param clarification: user input intended to disambiguate between the
        given movies
        :param candidates: a list of movie indices
        :returns: a list of indices corresponding to the movies identified by
        the clarification
        """
        results = []
        
        # flip = False

        # generate all combinations of substring matches
        clarify_tokens = clarification.split()
        num_extraneous_allowed = len(clarify_tokens) // 2
        all_substrings = []
        for i in range(len(clarify_tokens)):
            to_append = ''
            for j in range(i, len(clarify_tokens)):
                to_append += ' ' + clarify_tokens[j].lower()
                to_append = to_append.strip()
                all_substrings.append(to_append)
        all_substrings = sorted(all_substrings, key=lambda string: len(string), reverse=True)
        all_substrings = [substring for substring in all_substrings if len(substring.split()) > num_extraneous_allowed]
        # find the database_title that has the longest matching substring. If multiple, return all
        # excludes extraneous words "the goblet of fire one" --> the goblet of fire
        max_len = 0
        for substring in all_substrings:
            if len(substring.split()) < max_len:
                break
            for candidate in candidates:
                database_title = self.titles[candidate][0].lower()
                clarify_pattern = "(?:^|\W)" + substring + "\W"
                # middle_clarify = '\W' + substring + '\W'
                # start_clarify = '^' + substring + '\W'
                middle_matches = re.findall(clarify_pattern, database_title)
                # start_matches = re.findall(start_clarify, database_title)
                if middle_matches:
                    if candidate not in results:
                        results.append(candidate)
                    max_len = len(substring)
        # no substring matches
        if len(results) == 0:
            if clarification.isdigit():
                list_num = int(clarification) - 1  # 0 indexing
                if list_num < len(candidates):
                    results.append(candidates[list_num])

        # no substring matches, not given a number

        # recent_words = ['new', 'recent', 'late']
        # old_words = ['old', 'original']
        #
        # if 'least' in clarification:
        #     flip = True
        #
        # for word in recent_words:
        #     if word in clarification
        return results

    ############################################################################
    # 3. Movie Recommendation helper functions                                 #
    ############################################################################

    @staticmethod
    def binarize(ratings, threshold=2.5):
        """Return a binarized version of the given matrix.

        To binarize a matrix, replace all entries above the threshold with 1.
        and replace all entries at or below the threshold with a -1.

        Entries whose values are 0 represent null values and should remain at 0.

        Note that this method is intentionally made static, as you shouldn't use
        any attributes of Chatbot like self.ratings in this method.

        :param ratings: a (num_movies x num_users) matrix of user ratings, from
         0.5 to 5.0
        :param threshold: Numerical rating above which ratings are considered
        positive

        :returns: a binarized version of the movie-rating matrix
        """
        binarized_ratings = np.copy(ratings)
        neg = (binarized_ratings <= threshold) & (binarized_ratings != 0)
        binarized_ratings[binarized_ratings > threshold] = 1
        binarized_ratings[neg] = -1
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        u_mag = np.linalg.norm(u)
        v_mag = np.linalg.norm(v)
        if u_mag == 0 or v_mag == 0:
            return 0

        similarity = np.dot(u, v) / (u_mag * v_mag)
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        """Generate a list of indices of movies to recommend using collaborative
         filtering.

        You should return a collection of `k` indices of movies recommendations.

        As a precondition, user_ratings and ratings_matrix are both binarized.

        Remember to exclude movies the user has already rated!

        Please do not use self.ratings directly in this method.

        :param user_ratings: a binarized 1D numpy array of the user's movie
            ratings
        :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
          `ratings_matrix[i, j]` is the rating for movie i by user j
        :param k: the number of recommendations to generate
        :param creative: whether the chatbot is in creative mode

        :returns: a list of k movie indices corresponding to movies in
        ratings_matrix, in descending order of recommendation.
        """
        # Create list of indices the user has rated
        user_rated_movies = np.where(user_ratings != 0)[0]

        # Create predicted_ratings array of same size as user_ratings
        predicted_ratings = np.zeros(user_ratings.shape)

        # Predict ratings for each movie the user hasn't seen
        for i in range(len(predicted_ratings)):
            if i in user_rated_movies:
                continue

            predicted_rating = 0
            # Grab unrated movie row from utility matrix
            unrated_movie = ratings_matrix[i, :]

            # Calculate similarity with each movie the user has rated
            for movie_index in user_rated_movies:
                rated_movie = ratings_matrix[movie_index, :]
                similarity = self.similarity(rated_movie, unrated_movie)
                predicted_rating += similarity * user_ratings[movie_index]

            # Predicted rating is sum of similarity * rating scores
            predicted_ratings[i] = predicted_rating

        # Calculate indices of top k predicted ratings
        # recommendations = self.get_top_k_idx(predicted_ratings, k)

        predicted_ratings_and_indexes = enumerate(predicted_ratings, start=0)
        predicted_ratings_and_indexes = sorted(predicted_ratings_and_indexes, key=lambda x: x[1], reverse=True)

        recommendations = []
        for index, score in predicted_ratings_and_indexes:
            if score != 0:
                recommendations.append(index)
            if len(recommendations) == k:
                break

        return recommendations

    def get_top_k_idx(self, arr, k):
        top_k_idx = np.argpartition(arr, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-arr[top_k_idx])]
        return top_k_idx_sorted

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        """
        Return debug information as a string for the line string from the REPL

        NOTE: Pass the debug information that you may think is important for
        your evaluators.
        """
        debug_info = 'debug info'
        return debug_info

    ############################################################################
    # 5. Write a description for your chatbot here!                            #
    ############################################################################
    def intro(self):
        """Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        """
        return """
        Zipbot recommends movies to you. 
        Tell me about your movie preferences and I will tell you what movie to watch next!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')