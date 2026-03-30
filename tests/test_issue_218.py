"""Test for issue #218: Monitor shutdown should not raise RuntimeError"""

from yojenkins.monitor.monitor import Monitor


class TestMonitorGracefulShutdown:
    def test_all_threads_off_sets_flag(self):
        m = Monitor()
        m.all_threads_enabled = True
        m.all_threads_off()
        assert m.all_threads_enabled is False

    def test_threads_list_initialized(self):
        m = Monitor()
        assert hasattr(m, '_threads')
        assert m._threads == []

    def test_all_threads_off_clears_thread_list(self):
        m = Monitor()
        m._threads = ['fake_thread']
        # Mock thread with join
        class FakeThread:
            def join(self, timeout=None):
                pass
        m._threads = [FakeThread()]
        m.all_threads_off()
        assert m._threads == []
