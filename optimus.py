"""
Tutorial - Hello World

The most basic (working) CherryPy application possible.
"""

# Import CherryPy global namespace
import cherrypy
from cherrypy import tools
from json import JSONEncoder
from membase_builds import BuildQuery


encoder = JSONEncoder()

def jsonify_tool_callback(*args, **kwargs):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    response.body = encoder.iterencode(response.body)

cherrypy.tools.jsonify = cherrypy.Tool('before_finalize', jsonify_tool_callback, priority=30)

class Optimus:
    """ Sample request handler class. """

    @cherrypy.expose
    def index(self):
        site_dir = os.path.join(os.path.abspath("."), u"site")
        return open(os.path.join(site_dir, u'index.html'))

    @cherrypy.tools.jsonify()
    def query_enterprise(self,deliverable_type,os_architecture,build_version = None,product="membase-server-enterprise"):
        print deliverable_type,os_architecture,build_version
        builds,changes = BuildQuery().get_latest_builds()
        filtered = []
        for build in builds:
            if build.product == product:
                filtered.append(build)

        answer_build = None
        sorted_by_number =  sorted(filtered,
                      key=lambda build: build.time,reverse=True)
        for build in sorted_by_number:
            if build.url.find('git describe') != -1:
                continue
            if build.deliverable_type == deliverable_type\
               and build.architecture_type == os_architecture:
                if build_version:
                    if build.product_version == build_version:
                        answer_build = build
                        break
                else:
                    answer_build = build
                    break

        if answer_build:
            print answer_build.json()
            return [answer_build.json()]
        return []


    query_enterprise.exposed = True
    # Expose the index method through the web. CherryPy will never
    # publish methods that don't have the exposed attribute set to True.
    index.exposed = True

import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'server.conf')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.quickstart(Optimus(), config=tutconf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(Optimus(), config=tutconf)
