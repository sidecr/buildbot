# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members


from twisted.web.util import redirectTo
from twisted.python import log
from twisted.internet import defer
from buildbot.status.web.base import HtmlResource
from buildbot.status.web.base import path_to_root
from buildbot.status.web.base import path_to_authzfail
from buildbot.status.web.base import ActionResource

CONFIG_FILENAME = 'sidecar_config.yaml'


#/config
class ConfigResource(HtmlResource):
    pageTitle = "Config"
    addSlash = True

    @defer.inlineCallbacks
    def content(self, req, ctx):
        res = yield self.getAuthz(req).actionAllowed('reconfig', req)
        if not res:
            defer.returnValue(redirectTo(path_to_authzfail(req), req))
            return

        with open(CONFIG_FILENAME, 'r') as config_file:
            ctx['config_str'] = config_file.read()

        template = req.site.buildbot_service.templates.get_template(
            "config.html")
        defer.returnValue(template.render(**ctx))

    def getChild(self, path, req):
        if path == "reconfig":
            return ReconfigActionResource()

        return super(ConfigResource, self).getChild(self, path, req)


#/config/reconfig
class ReconfigActionResource(ActionResource):

    def __init__(self):
        self.action = "reconfig"

    @defer.inlineCallbacks
    def performAction(self, req):
        res = yield self.getAuthz(req).actionAllowed('reconfig', req)
        if not res:
            defer.returnValue(redirectTo(path_to_authzfail(req), req))
            return

        config_text = req.args.get("config_text")
        log.msg(config_text)

        #TODO save the old config as backup
        #TODO write the config file to be the master
        #TODO test the config file for validity
        #TODO if bad
            #TODO  restore the old config
        #TODO: otherwise
            #TODO restart buildbot

        # send the user back to the config page

        defer.returnValue(path_to_root(req) + "config")
