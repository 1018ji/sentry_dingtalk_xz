# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import sentry_dingtalk_xz
from .forms import DingTalkOptionsForm
from sentry.plugins.bases.notify import NotificationPlugin

DING_TALK_API = 'https://oapi.dingtalk.com/robot/send?access_token={token}'


class DingTalkPlugin(NotificationPlugin):
    author = '1018ji'
    author_url = 'https://github.com/1018ji/sentry_dingtalk_xz'
    description = 'sentry extension which can send error to dingtalk'
    resource_links = [
        ('Source', 'https://github.com/1018ji/sentry_dingtalk_xz'),
        ('Bug Tracker', 'https://github.com/1018ji/sentry_dingtalk_xz/issues'),
        ('README', 'https://github.com/1018ji/sentry_dingtalk_xz/blob/master/README.md'),
    ]
    version = sentry_dingtalk_xz.VERSION

    slug = 'Ding Talk: robot'
    title = 'Ding Talk: robot'
    conf_key = slug
    conf_title = title
    project_conf_form = DingTalkOptionsForm

    def is_configured(self, project):
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, *args, **kwargs):
        if not self.is_configured(group.project):
            self.logger.info('dingtalk token config error')
            return None

        if self.should_notify(group, event):
            self.logger.info('send msg to dingtalk robot yes')
            self.send_msg(group, event, *args, **kwargs)
        else:
            self.logger.info('send msg to dingtalk robot no')
            return None

    def send_msg(self, group, event, *args, **kwargs):
        del args, kwargs

        error_title = u'【WARNING】捕获到来自【%s】的异常' % event.project.slug

        data = {
            "msgtype": 'markdown',
            "markdown": {
                "title": error_title,
                "text": u'#### {title} \n\n > {message} \n\n [更多详细信息]({url})'.format(
                    title=error_title,
                    message=event.message,
                    url=u'{url}events/{id}/'.format(
                        url=group.get_absolute_url(),
                        id=event.id
                    ),
                )
            }
        }

        requests.post(
            url=DING_TALK_API.format(token=self.get_option('access_token', group.project)),
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps(data).encode('utf-8')
        )
