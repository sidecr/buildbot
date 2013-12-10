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

import os
import shutil
import subprocess
import datetime

from twisted.python import log
from twisted.web.util import redirectTo
from twisted.internet import defer
from buildbot.status.web.base import HtmlResource
from buildbot.status.web.base import path_to_root
from buildbot.status.web.base import path_to_authzfail
from buildbot.status.web.base import ActionResource

CONFIG_DIR = 'config'
PROJECTS_PATH = os.path.join(CONFIG_DIR, 'sidecar_projects.yaml')
PROJECTS_FILENAME_TEMPLATE = 'sidecar_projects.%s.yaml'
PROJECTS_BACKUP_PATH = PROJECTS_PATH+'.BACKUP'


#/config
class ConfigResource(HtmlResource):
    pageTitle = "Projects Config"
    addSlash = True

    @defer.inlineCallbacks
    def content(self, req, ctx):
        res = yield self.getAuthz(req).actionAllowed('reconfig', req)
        if not res:
            defer.returnValue(redirectTo(path_to_authzfail(req), req))
            return

        ctx['success'] = req.args.get('success', [None])[0]

        with open(PROJECTS_PATH, 'r') as config_file:
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

        config_text = req.args.get("config_text")[0]
        config_text = config_text.replace('\r', '')

        timestr = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        new_config_filename = PROJECTS_FILENAME_TEMPLATE % timestr
        new_config_path = os.path.join(CONFIG_DIR, new_config_filename)

        log.msg('Backing up old link to projects file...')

        shutil.move(PROJECTS_PATH, PROJECTS_BACKUP_PATH)
        try:
            log.msg('Writing new projects file: %s ...' % new_config_path)
            with open(new_config_path, 'w') as config_file:
                config_file.write(str(config_text))
            log.msg('Linking the new projects file...')
            os.symlink(new_config_filename, PROJECTS_PATH)
            log.msg(os.readlink(PROJECTS_PATH))
            log.msg('Checking configuration validity...')
            result = subprocess.check_output(['buildbot', 'checkconfig'],
                                             stderr=subprocess.STDOUT)
            log.msg(result)
            log.msg('Reconfiguring buildbot...')
            subprocess.call(['buildbot', 'reconfig'])
            log.msg('Buildbot reconfiguring!')
            success = '1'
            try:
                os.remove(PROJECTS_BACKUP_PATH)
            except IOError as exc:
                log.msg(str(exc))
        except (subprocess.CalledProcessError, IOError) as exc:
            log.msg(str(exc))
            if hasattr(exc, 'output'):
                log.msg(exc.output)
            log.msg('Reverting the symlink to the last backup.')
            os.remove(PROJECTS_PATH)
            shutil.move(PROJECTS_BACKUP_PATH, PROJECTS_PATH)
            success = '0'

        path = "%sconfig?success=%s" % (path_to_root(req), success)
        defer.returnValue(path)
