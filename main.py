from flask import Flask
from flask import make_response
import os
from pygithub3 import Github
import urllib
import Image, ImageDraw, ImageFont
import cStringIO as StringIO

app = Flask(__name__)
imp_branch_bg = (93, 138, 209)
imp_branches = ["master"]

@app.route('/<string:cs_uuid>/<string:gh_user>/<string:gh_repo>')
def index(cs_uuid, gh_user, gh_repo):
    try:
        return process_req(cs_uuid, gh_user, gh_repo)
    except Exception as e:
        print e
        return str(e)

def process_req(cs_uuid, gh_user, gh_repo):
    oauth_token = os.environ['GH_TOKEN']
    gh = Github(token=oauth_token)
    branch_pages = gh.repos.list_branches(user=gh_user, repo=gh_repo)
    cs_url = "http://codeship.com/projects/%s/status?branch=%s"

    branch_names = []
    badges = []

    for branch_page in branch_pages:
        for branch in branch_page:
            branch_names.append(branch.name)

    print "Downloading images"
    for branch in branch_names:
        img = urllib.urlopen(cs_url % (cs_uuid, branch))
        b_data = img.read()
        stream = StringIO.StringIO(b_data)
        img_obj = Image.open(stream)
        badges.append((branch, img_obj))
        print "    Downloaded for %s" % branch
    print "Done downloading image"

    border_x = 10
    border_y = 10

    img_w = border_x
    img_h = border_y

    for badge in badges:
        img_h += badge[1].size[1] + border_y

    img_w = int(2.1*max([x[1].size[0] for x in badges]) + 3*border_x)

    image = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(image)
    cursor_x = border_x
    cursor_y = border_y
    font = ImageFont.truetype("opensans.ttf", 13)
    text_pad = (badges[0][1].size[1] - 13)/4

    for badge in badges:
        if badge[0] in imp_branches:
            draw.rectangle([(cursor_x, cursor_y), ((img_w - 3*border_x)/2 - border_x, cursor_y + badge[1].size[1])], imp_branch_bg)

        draw.text((cursor_x + border_x, cursor_y + text_pad), badge[0], (0, 0, 0), font=font)
        cursor_x += int(1.1*((img_w - 3*border_x)/2))

        image.paste(badge[1], (cursor_x, cursor_y))
        cursor_y += badge[1].size[1] + border_y
        cursor_x = border_x

    file = StringIO.StringIO()
    image.save(file, "PNG")

    file.seek(0)
    response = make_response(file.read())
    response.headers['Content-type'] = 'image/png'
    return response

app.debug = True

