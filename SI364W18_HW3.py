## SI 364 - Winter 2018
## HW 3

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, validators
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

############################
# Application configurations
############################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecurebutitsok'
## DONE 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## DONE Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/hongjisuHW3"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################

# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand) # Add migrate command to manager


#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################

## DONE 364: Set up the following Model classes, as described, with the respective fields (data types).


class Tweet(db.Model):
    __tablename__ = 'tweets'
    tweetId = db.Column(db.Integer, primary_key=True)
    tweetText = db.Column(db.String(280))
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    
    def __repr__(self):
        return "Tweet {} (ID: {})".format(self.tweetText,self.userId)

class User(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(64),unique=True)
    displayName = db.Column(db.String(124))
    tweets = db.relationship('Tweet',backref='User')


    def __repr__(self):
        return "{} | ID: {}".format(self.userName,self.userId)

## The following relationships should exist between them:
# Tweet:User - Many:One

# - Tweet
## -- id (Integer, Primary Key)
## -- text (String, up to 280 chars)
## -- user_id (Integer, ID of user posted -- ForeignKey)

## Should have a __repr__ method that returns strings of a format like:
#### {Tweet text...} (ID: {tweet id})

# - User
## -- id (Integer, Primary Key)
## -- username (String, up to 64 chars, Unique=True)
## -- display_name (String, up to 124 chars)
## ---- Line to indicate relationship between Tweet and User tables (the 1 user: many tweets relationship)

## Should have a __repr__ method that returns strings of a format like:
#### {username} | ID: {id}


########################
##### Set up Forms #####
########################


class tweetForm(FlaskForm):
    text = StringField('Enter the text of the tweet (no more than 280 chars):', [validators.DataRequired(message="text field cannot be blank"), validators.Length(max=280, message= "text must not exceed 280")])
    username = StringField('Enter the username of the twitter user (no "@"!):', [
                                    validators.Regexp('^[^@]+$', message="Username must not contain @"),
                                    validators.Length(max=64, message="Username must be at most 64"),
                                    validators.DataRequired(message="username cannot be blank")
                                    ])
    display_name = StringField('Enter the display name for the twitter user (must be at least 2 words):', [
                                   validators.Regexp('.*[^\s]+[\s]+[^\s]+.*', message="displayname must be at least 2 words"),
                                   validators.DataRequired(message="displayname cannot be blank")
                                   ])

    submit = SubmitField('Submit')

# DONE 364: Fill in the rest of the below Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

## -- text: tweet text (Required, should not be more than 280 characters)
## -- username: the twitter username who should post it (Required, should not be more than 64 characters)
## -- display_name: the display name of the twitter user with that username (Required, + set up custom validation for this -- see below)

# HINT: Check out index.html where the form will be rendered to decide what field names to use in the form class definition



# TODO 364: Set up custom validation for this form such that:
# - the twitter username may NOT start with an "@" symbol (the template will put that in where it should appear)
# - the display name MUST be at least 2 words (this is a useful technique to practice, even though this is not true of everyone's actual full name!)


##### Helper functions
### For database additions / get_or_create functions
def get_or_create_tweet(db_session, tweetText_in, userId_in):
    tweet = db_session.query(Tweet).filter_by(tweetText=tweetText_in,userId=userId_in).first()
    if tweet:
        return tweet
    else:
        tweet = Tweet(tweetText=tweetText_in, userId=userId_in)
        db_session.add(tweet)
        db_session.commit()
        flash("tweet succesfully added")

def get_or_create_user(db_session, userName_in, displayName_in):
    user = db_session.query(User).filter_by(userName=userName_in).first()
    if user:
        return user
    else:
        user = User(userName=userName_in,displayName=displayName_in)
        db_session.add(user)
        db_session.commit()
        return user


def sortTweet(text_in):
    score = 0
    for t in text_in:
        if t != ' ':
            score +=1
    return score

# DONE 364: Make sure to check out the sample application linked in the readme to check if yours is like it!


###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############

## DONE 364: Fill in the index route as described.

# A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
# Some code already exists at the end of this view function -- but there's a bunch to be filled in.
## HINT: Check out the index.html template to make sure you're sending it the data it needs.
## We have provided comment scaffolding. Translate those comments into code properly and you'll be all set!

# NOTE: The index route should:
# - Show the Tweet form.
# - If you enter a tweet with identical text and username to an existing tweet, it should redirect you to the list of all the tweets and a message that you've already saved a tweet like that.
# - If the Tweet form is entered and validates properly, the data from the form should be saved properly to the database, and the user should see the form again with a message flashed: "Tweet successfully saved!"
# Try it out in the sample app to check against yours!

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize the form
    form = tweetForm()
    if form.validate_on_submit():
        text = form.text.data
        username = form.username.data
        display_name = form.display_name.data
        user = get_or_create_user(db.session, username, display_name)
        tweet = get_or_create_tweet(db.session, text, user.userId)
        if tweet:
            flash("you've already saved a tweet like that")
            return redirect(url_for('see_all_tweets'))


    
    # Get the number of Tweets

    # If the form was posted to this route,
    ## Get the data from the form

    ## Find out if there's already a user with the entered username
    ## If there is, save it in a variable: user
    ## Or if there is not, then create one and add it to the database

    ## If there already exists a tweet in the database with this text and this user id (the id of that user variable above...) ## Then flash a message about the tweet already existing
    ## And redirect to the list of all tweets

    ## Assuming we got past that redirect,
    ## Create a new tweet object with the text and user id
    ## And add it to the database
    ## Flash a message about a tweet being successfully added
    ## Redirect to the index page

    # PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    num_tweets = len(Tweet.query.all())
    return render_template("index.html", form = form, num_tweets=num_tweets) # DONE 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/all_tweets')
def see_all_tweets():
    all_tweets = [] # To be tuple list of title, genre
    tweets = Tweet.query.all()
    for s in tweets:
        user = User.query.filter_by(userId=s.userId).first()
        all_tweets.append((s.tweetText,user.userName))
    return render_template('all_tweets.html',all_tweets=all_tweets)
    # Replace with code
    # DONE 364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
    # HINT: Careful about what type the templating in all_tweets.html is expecting! It's a list of... not lists, but...
    # HINT #2: You'll have to make a query for the tweet and, based on that, another query for the username that goes with it...


@app.route('/all_users')
def see_all_users():
    all_users = [] # To be tuple list of title, genre
    users = User.query.all()
    for s in users:
        all_users.append((s.userName,s.displayName))
    return render_template('all_users.html',all_users=all_users)
    # Replace with code
    # DONE 364: Fill in this view function so it can successfully render the template all_users.html, which is provided.




@app.route('/longest_tweet')
def get_longest_tweet():
    longest_tweet = []
    tweets = Tweet.query.all()
    longest_tweet.append(tweets[0])
    for s in tweets:
        a = sortTweet(s.tweetText)
        b = sortTweet(longest_tweet[0].tweetText)
        if a>b:
            longest_tweet = []
            longest_tweet.append(s)
        elif sortTweet(s.tweetText) == sortTweet(longest_tweet[0].tweetText):
            list = []
            list.append(s.tweetText)
            list.append(longest_tweet[0].tweetText)
            list.sort()
            if list[1] == s.tweetText:
                longest_tweet = []
                longest_tweet.append(s)


    user = User.query.filter_by(userId=s.userId).first()
    username = user.userName
    return render_template('longest_tweet.html', tweetText = longest_tweet[0].tweetText, username=username)
# TODO 364
# Create another route (no scaffolding provided) at /longest_tweet with a view function get_longest_tweet (see details below for what it should do)
# TODO 364
# Create a template to accompany it called longest_tweet.html that extends from base.html.

# NOTE:
# This view function should compute and render a template (as shown in the sample application) that shows the text of the tweet currently saved in the database which has the most NON-WHITESPACE characters in it, and the username AND display name of the user that it belongs to.
# NOTE: This is different (or could be different) from the tweet with the most characters including whitespace!
# Any ties should be broken alphabetically (alphabetically by text of the tweet). HINT: Check out the chapter in the Python reference textbook on stable sorting.
# Check out /longest_tweet in the sample application for an example.

# HINT 2: The chapters in the Python reference textbook on:
## - Dictionary accumulation, the max value pattern
## - Sorting
# may be useful for this problem!


if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
