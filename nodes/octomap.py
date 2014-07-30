#!/usr/bin/env python
# Copyright (C) 2014 Aldebaran Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from distutils.version import LooseVersion

import rospy

from octomap_msgs.msg import Octomap

from nao_driver import NaoNode
from nao_driver.boost.octomap_python import octomap_str_to_tuple

class NaoOctomap(NaoNode):
    def __init__(self):
        NaoNode.__init__(self)

        if self.getVersion() < LooseVersion('2.0'):
            rospy.loginfo('NAOqi version < 2.0, Octomap is not used')
            exit(0)

        self.connectNaoQi()

        # ROS initialization:
        rospy.init_node('nao_octomap')

        # Create ROS publisher
        self.pub = rospy.Publisher("octomap", Octomap, latch = True, queue_size=1)

        self.fps = 1

        rospy.loginfo("nao_octomap initialized")

    def connectNaoQi(self):
        '''(re-) connect to NaoQI'''
        rospy.loginfo("Connecting to NaoQi at %s:%d", self.pip, self.pport)

        self.navigationProxy = self.getProxy("ALNavigation")
        if self.navigationProxy is None:
            rospy.loginfo('Could not get access to the ALNavigation proxy')
            exit(1)
        res = self.navigationProxy._setObstacleModeForSafety(1)

    def main_loop(self):
        r = rospy.Rate(self.fps)
        octomap = Octomap()
        octomap.header.frame_id = '/odom'

        while not rospy.is_shutdown():
            octomap_bin = self.navigationProxy._get3DMap()
            octomap.binary, octomap.id, octomap.resolution, octomap.data = octomap_str_to_tuple(octomap_bin)

            octomap.header.stamp = rospy.Time.now()

            self.pub.publish(octomap)

            r.sleep()

if __name__ == '__main__':
    nao_octomap = NaoOctomap()
    nao_octomap.main_loop()
