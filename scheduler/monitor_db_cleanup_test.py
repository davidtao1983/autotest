#!/usr/bin/python

import common
import logging, unittest
from autotest_lib.frontend import setup_django_environment
from autotest_lib.database import database_connection
from autotest_lib.frontend.afe import frontend_test_utils, models
from autotest_lib.scheduler import monitor_db_cleanup
from autotest_lib.client.common_lib import host_protections

class UserCleanupTest(unittest.TestCase, frontend_test_utils.FrontendTestMixin):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self._frontend_common_setup()
        self._database = (
            database_connection.DatabaseConnection.get_test_database())
        self._database.connect(db_type='django')
        self.cleanup = monitor_db_cleanup.UserCleanup(self._database, 1)


    def tearDown(self):
        self._frontend_common_teardown()


    def test_reverify_dead_hosts(self):
        for i in (0, 1, 2):
            self.hosts[i].status = models.Host.Status.REPAIR_FAILED
            self.hosts[i].save()

        self.hosts[1].locked = True
        self.hosts[1].save()

        self.hosts[2].protection = host_protections.Protection.DO_NOT_VERIFY
        self.hosts[2].save()

        self.god.stub_with(self.cleanup, '_should_reverify_hosts_now',
                           lambda : True)
        self.cleanup._reverify_dead_hosts()

        tasks = models.SpecialTask.objects.all()
        self.assertEquals(len(tasks), 1)
        self.assertEquals(tasks[0].host.id, 1)
        self.assertEquals(tasks[0].task, models.SpecialTask.Task.VERIFY)


if __name__ == '__main__':
    unittest.main()