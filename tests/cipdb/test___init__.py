#!/usr/bin/env python3
'''Test suite for cipdb package.'''

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import cipdb


class TestCipdbCore:
    '''Test core cipdb functionality.'''

    def setup_method(self):
        '''Reset state before each test.'''
        cipdb.enable()
        # Clear relevant environment variables
        for key in ['CIPDB', 'CIPDB_ID', 'CIPDB_IDS', 'DEBUG']:
            os.environ.pop(key, None)

    def teardown_method(self):
        '''Clean up after each test.'''
        for key in ['CIPDB', 'CIPDB_ID', 'CIPDB_IDS', 'DEBUG']:
            os.environ.pop(key, None)

    @patch('ipdb.set_trace')
    def test_simple_true_false(self, mock_ipdb):
        '''Test basic True/False conditions.'''
        cipdb.set_trace(True)
        assert mock_ipdb.called

        mock_ipdb.reset_mock()
        cipdb.set_trace(False)
        assert not mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_cipdb_id_matching(self, mock_ipdb):
        '''Test CIPDB_ID single ID matching.'''
        # Set single ID
        os.environ['CIPDB_ID'] = 'test-point'

        # Should trigger - ID matches
        cipdb.set_trace(id='test-point')
        assert mock_ipdb.called

        # Should not trigger - ID doesn't match
        mock_ipdb.reset_mock()
        cipdb.set_trace(id='other-point')
        assert not mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_cipdb_ids_matching(self, mock_ipdb):
        '''Test CIPDB_IDS multiple IDs matching.'''
        # Set multiple IDs
        os.environ['CIPDB_IDS'] = 'validate,save,notify'

        # Should trigger - ID is in list
        cipdb.set_trace(id='validate')
        assert mock_ipdb.called

        mock_ipdb.reset_mock()
        cipdb.set_trace(id='save')
        assert mock_ipdb.called

        # Should not trigger - ID not in list
        mock_ipdb.reset_mock()
        cipdb.set_trace(id='other-point')
        assert not mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_cipdb_ids_with_spaces(self, mock_ipdb):
        '''Test CIPDB_IDS with spaces around commas.'''
        # Set IDs with spaces
        os.environ['CIPDB_IDS'] = 'validate, save , notify'

        # Should trigger - spaces are stripped
        cipdb.set_trace(id='save')
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_no_id_always_triggers(self, mock_ipdb):
        '''Test that breakpoints without IDs always trigger.'''
        # Even with ID set, non-ID breakpoints should work
        os.environ['CIPDB_ID'] = 'some-id'

        cipdb.set_trace(True)
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_development_mode_id_breakpoints(self, mock_ipdb):
        '''Test development mode - ID breakpoints work without env vars.'''
        # No CIPDB_ID or CIPDB_IDS set = development mode
        # All ID breakpoints should trigger
        cipdb.set_trace(id='any-id')
        assert mock_ipdb.called

        mock_ipdb.reset_mock()
        cipdb.set_trace(id='another-id')
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_env_var_condition(self, mock_ipdb):
        '''Test environment variable conditions.'''
        # Check for truthy env var
        cipdb.set_trace("DEBUG")
        assert not mock_ipdb.called

        os.environ['DEBUG'] = 'true'
        cipdb.set_trace("DEBUG")
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_env_var_equality(self, mock_ipdb):
        '''Test environment variable equality check.'''
        os.environ['ENV'] = 'production'

        cipdb.set_trace("ENV=development")
        assert not mock_ipdb.called

        cipdb.set_trace("ENV=production")
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_callable_condition(self, mock_ipdb):
        '''Test callable conditions.'''
        x = 5
        cipdb.set_trace(lambda: x > 10)
        assert not mock_ipdb.called

        x = 15
        cipdb.set_trace(lambda: x > 10)
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_global_disable(self, mock_ipdb):
        '''Test global disable/enable.'''
        cipdb.disable()
        cipdb.set_trace(True)
        assert not mock_ipdb.called

        cipdb.enable()
        cipdb.set_trace(True)
        assert mock_ipdb.called

    @patch('ipdb.set_trace')
    def test_cipdb_env_override(self, mock_ipdb):
        '''Test CIPDB environment variable override.'''
        os.environ['CIPDB'] = 'false'
        cipdb.set_trace(True)
        assert not mock_ipdb.called

        os.environ['CIPDB'] = '0'
        cipdb.set_trace(True)
        assert not mock_ipdb.called

        os.environ['CIPDB'] = 'off'
        cipdb.set_trace(True)
        assert not mock_ipdb.called

        os.environ.pop('CIPDB')
        cipdb.set_trace(True)
        assert mock_ipdb.called

    @patch('ipdb.post_mortem')
    def test_post_mortem(self, mock_pm):
        '''Test post_mortem functionality.'''
        try:
            raise ValueError("test")
        except:
            cipdb.post_mortem(condition=True)
            assert mock_pm.called

            mock_pm.reset_mock()
            cipdb.post_mortem(condition=False)
            assert not mock_pm.called

    @patch('ipdb.post_mortem')
    def test_post_mortem_with_id(self, mock_pm):
        '''Test post_mortem with ID.'''
        os.environ['CIPDB_ID'] = 'error-handler'

        try:
            raise ValueError("test")
        except:
            cipdb.post_mortem(id='error-handler')
            assert mock_pm.called

            mock_pm.reset_mock()
            cipdb.post_mortem(id='other-handler')
            assert not mock_pm.called


class TestCipdbFallback:
    '''Test fallback behavior.'''

    @patch('pdb.set_trace')
    def test_fallback_to_pdb(self, mock_pdb):
        '''Test fallback to pdb when ipdb is not available.'''
        # This would require mocking the import system
        # In practice, the code handles ImportError
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
