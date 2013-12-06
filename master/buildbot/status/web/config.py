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


from twisted.web import html
import urllib, time
from twisted.python import log
from twisted.internet import defer
from buildbot.status.web.base import HtmlResource, BuildLineMixin, \
    path_to_build, path_to_slave, path_to_builder, path_to_change, \
    path_to_root, ICurrentBox, build_get_class, \
    map_branches, path_to_authzfail, ActionResource, \
    getRequestCharset


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

        #TODO: read the config file
        ctx['config_str'] = 'DUMMY CONFIG TEXT'

        template = req.site.buildbot_service.templates.get_template(
            "config.html")
        defer.returnValue(template.render(**ctx))


#/reconfig
class ReconfigResource(ActionResource):

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

        #TODO write the config file to a temp thing
        #TODO test the config file for validity
        #TODO save the old config as backup
        #TODO move the config file to be the master
        #TODO restart buildbot

        # send the user back to the config page

        defer.returnValue(path_to_root(req) + "config")
