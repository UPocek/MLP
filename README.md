# NewPresentations

This is New Presentations a fully automatic way to create beautiful
PowerPoint presentations with the power of our state of the art artificial
intelligence. You have an assignment in school or on job to create
PowerPoint presentation on a given topic let our AI take care of that for
you!

## Deployment

1. Install git and git-lfs [.](https://stackoverflow.com/questions/48734119/git-lfs-is-not-a-git-command-unclear)
1. Clone this repo with `git lfs clone https://github.com/UPocek/NewPresentations.git`
1. Create virtual envirement with `python -m venv venv`
1. Activate virtual envirement with `source venv/bin/activate`
1. Make sure you have Rust installed on your machine
1. Install needed dependencies with `pip install -r requirements.txt`
1. Run server from new_presentations folder with `gunicorn new_presentations.wsgi:application`
