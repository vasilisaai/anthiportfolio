from flask import Flask, render_template
from flask_frozen import Freezer
from flask_flatpages import FlatPages
import re
from datetime import datetime


import markdown
import os

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FREEZER_RELATIVE_URLS = DEBUG

app = Flask(__name__)

freezer = Freezer(app)
app.config.from_object(__name__)
pages = FlatPages(app)

GLOBAL_POST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'portfolio/global_post')

app.config.from_object(__name__)

def get_all_posts_from_directory(directory):
    posts = []
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            posts.append({
                'filename': filename,
            })
    return posts

@freezer.register_generator
def globalpostpost():
    """Generate URLs for all Global Post article pages."""
    posts = get_all_posts_from_directory(GLOBAL_POST_DIR)
    for post in posts:
        # globalpostpost(post_filename=...)
        yield {'post_filename': post['filename']}

def get_post(post_filename, DIR):
    post_path = os.path.join(DIR, post_filename)
    
    with open(post_path, 'r') as file:
        lines = file.readlines()
        dt = markdown.markdown(lines[2].strip())
        clean_date = re.sub(r"<.*?>", "", dt).strip()
        date = datetime.strptime(clean_date, "%y/%m/%d")
        date = date.strftime("%b. %-d, %Y")
        title = markdown.markdown(lines[4].strip())  # Title is the first line (Markdown heading)
        country = markdown.markdown(lines[5].strip())  # Title is the first line (Markdown heading)
        preview = ' '.join(lines[6:]).strip()  # Get a preview from the next few lines
        normalized = re.sub(r' {2,}\n', '\n\n', preview)
        preview_html = markdown.markdown(normalized)
    return date, title, country, preview, preview_html

def load_posts(directory, file_extension=".md"):
    posts = []
    for post_filename in os.listdir(directory):
        if post_filename.endswith(file_extension):
            date, title, country, preview, preview_html = get_post(post_filename, directory)
            posts.append({
                'filename': post_filename,                
                'date': date,
                'title': title,
                'country': country,
                'preview': preview,
                'preview_html': preview_html
            })

    # Now sort using this function
    

    return posts
    
def show_post(post_filename, directory):
    if not post_filename.endswith('.md'):
        return {}

    date, title, country, preview, preview_html = get_post(post_filename, directory)

    post = {
        'filename': post_filename,
        'date': date,
        'title': title,
        'country': country,
        'preview': preview,
        'preview_html': preview_html
    }

    return post


@app.route('/portfolio/globalpost/')
def fashion():
    posts = load_posts(GLOBAL_POST_DIR)  # Use the helper function to load posts from the directory
    return render_template('writing.html', posts=posts, header_text="Global Post",
        subheader_text="Concise reports on global news written for the Global Post, the largest daily newsletter devoted to world news..",
        publication="GLOBAL POST")

@app.route('/portfolio/globalpost/post/<post_filename>/')
def globalpostpost(post_filename):
    post = show_post(post_filename, GLOBAL_POST_DIR)
    return render_template('post.html', post_filename=post_filename, post=post, header_text="Art Listings")

@app.route('/resume/')
def resume():
    return render_template('resume.html')


@app.route('/contact/')
def contact():
    return render_template('contact.html')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    freezer.freeze()
    app.run(debug=True, port=5001)